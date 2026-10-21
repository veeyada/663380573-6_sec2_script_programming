# src/communication_agent.py
import os
import json
import time
import datetime
from utils import setup_logging, log_audit_entry, ensure_directory_exists, get_env_variable
from email_tasks import EmailTasks
from sms_tasks import SMSTasks
from template_renderer import TemplateRenderer

logger = setup_logging(__name__)


class CommunicationAgent:
    """
    An agent that orchestrates communication tasks (email, SMS, inbox processing) based on a
    structured configuration file, managing an internal context for dynamic values.
    """

    def __init__(self, config, base_dir):
        self.config = config
        self.audit_log = []
        self.context = {}  # Stores dynamic values for templating and task chaining
        self.start_time = datetime.datetime.now()
        self.base_dir = base_dir

        try:
            sender_email = get_env_variable("SENDER_EMAIL")
            sender_app_password = get_env_variable("SENDER_APP_PASSWORD")
            smtp_server = get_env_variable("SMTP_SERVER")
            smtp_port = int(get_env_variable("SMTP_PORT"))
            imap_server = get_env_variable("IMAP_SERVER")
        except ValueError as e:
            logger.critical(f"Agent initialization failed: Missing environment variables. {e}")
            raise

        self.email_tasks = EmailTasks(smtp_server, smtp_port, imap_server, sender_email, sender_app_password)
        self.sms_tasks = SMSTasks(self.email_tasks)  # SMS uses EmailTasks for the underlying send
        self.template_renderer = TemplateRenderer()

        # Task dispatcher: maps the config "type" to its handler
        self.task_handlers = {
            "send_email": self._handle_send_email,
            "send_sms": self._handle_send_sms,
            "process_inbox": self._handle_process_inbox,
        }
        logger.info("CommunicationAgent initialized with task handlers.")

    # --- Context helpers ---
    def _update_context(self, key, value):
        """Updates a value in the agent's context."""
        self.context[key] = value
        logger.debug(f"Context updated: '{key}' = {value}")

    def _get_context_value(self, key, default=None):
        return self.context.get(key, default)

    def _render_template(self, template_string, extra_context=None):
        """Renders a template using the agent context (plus optional per-email values)."""
        context = {**self.context, **extra_context} if extra_context else self.context
        try:
            return self.template_renderer.render(template_string, context)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"Template rendering failed: {e}", "template_render",
                            {"template": template_string})
            raise

    def _resolve_path(self, path):
        return path if os.path.isabs(path) else os.path.normpath(os.path.join(self.base_dir, path))

    # --- Task handlers: each returns (success, output_data) ---
    def _handle_send_email(self, params):
        recipients = {k: [self._render_template(r) for r in v] for k, v in params.get('recipients', {}).items()}
        subject = self._render_template(params.get("subject_template"))
        body = self._render_template(params.get("body_template"))
        html_body = self._render_template(params["html_body_template"]) if params.get("html_body_template") else None
        attachments = [self._resolve_path(self._render_template(p)) for p in params.get("attachments", [])]

        success, attached = self.email_tasks.send_email(recipients, subject, body, attachments,
                                                        params.get("is_html", False), html_body)
        output = {
            "recipients": recipients,
            "subject": subject,
            "attachments": [os.path.relpath(p, self.base_dir) for p in attached],
            "sent_at": datetime.datetime.now().isoformat(timespec='seconds'),
        }
        return success, output

    def _handle_send_sms(self, params):
        phone_numbers = [self._render_template(p) for p in params.get("phone_numbers", [])]
        message = self._render_template(params.get("message_template"))
        subject = self._render_template(params.get("subject_template", ""))
        success, sent_to = self.sms_tasks.send_sms(phone_numbers, message, params.get("carrier_name"), subject)
        return success, {"phone_numbers": phone_numbers, "gateways": sent_to, "message": message}

    def _search_inbox(self, params):
        """Searches with retries, since a just-sent email can take a few seconds to show up via IMAP."""
        mailbox = params.get("mailbox", "INBOX")
        criteria = params.get("search_criteria", {})
        from_sender = self._render_template(criteria["from_sender"]) if criteria.get("from_sender") else None
        subject_contains = criteria.get("subject_contains")
        if isinstance(subject_contains, list):
            subject_contains = [self._render_template(s) for s in subject_contains]
        elif subject_contains:
            subject_contains = self._render_template(subject_contains)

        statuses = [criteria.get("status", "UNSEEN")]
        if criteria.get("fallback_status"):
            statuses.append(criteria["fallback_status"])

        initial_wait = params.get("wait_seconds", 0)
        if initial_wait:
            logger.info(f"Waiting {initial_wait}s for incoming mail to arrive...")
            time.sleep(initial_wait)

        attempts = max(1, params.get("max_attempts", 1))
        for attempt in range(1, attempts + 1):
            for status in statuses:
                uids = self.email_tasks.search_emails(mailbox, status, from_sender, subject_contains)
                if uids:
                    log_audit_entry(self.audit_log, "INFO", f"Inbox search found {len(uids)} email(s)", "process_inbox",
                                    {"status": status, "from": from_sender, "subject_contains": subject_contains,
                                     "attempt": attempt})
                    return uids
            if attempt < attempts:
                logger.info(f"No matching emails yet (attempt {attempt}/{attempts}); retrying...")
                time.sleep(params.get("retry_interval_seconds", 10))
        return []

    def _rule_matches(self, conditions, email_info):
        """All conditions must hold (AND). Text comparisons are case-insensitive."""
        for key, expected in conditions.items():
            if key == "has_attachments":
                if bool(expected) != email_info["has_attachments"]:
                    return False
                continue
            needle = self._render_template(expected, email_info).casefold()
            if key == "from_sender":
                haystack = email_info["sender_address"]
            elif key == "subject_contains":
                haystack = email_info["subject"]
            elif key == "body_contains":
                haystack = email_info["text_body"] or email_info["html_body"]
            else:
                return False
            if needle not in haystack.casefold():
                return False
        return True

    def _apply_rule_actions(self, actions, email_info, msg, mailbox):
        """Runs the 'then' actions of a matched rule. Returns a list of action results."""
        results = []

        if actions.get("download_attachments_to"):
            target_dir = self._resolve_path(self._render_template(actions["download_attachments_to"], email_info))
            rename_template = actions.get("rename_template")

            def build_name(original):
                if not rename_template:
                    return original
                stem, ext = os.path.splitext(original)
                return self._render_template(rename_template, {**email_info, "filename": original, "stem": stem, "ext": ext})

            saved = self.email_tasks.save_attachments(msg, email_info, target_dir, actions.get("allowed_extensions"), build_name)
            results.append({"action": "download_attachments", "saved": [os.path.relpath(p, self.base_dir) for p in saved]})

        if actions.get("mark_as_read"):
            results.append({"action": "mark_as_read", "ok": self.email_tasks.mark_as_read(email_info["uid"], mailbox)})

        if actions.get("send_sms_alert"):
            message = self._render_template(
                actions.get("alert_message_template", "Urgent email received: {subject} from {sender}"), email_info)
            numbers = [self._render_template(p) for p in actions.get("alert_phone_numbers", [])]
            ok, sent_to = self.sms_tasks.send_sms(numbers, message, actions.get("alert_carrier"), "[SMS Alert]")
            results.append({"action": "send_sms_alert", "ok": ok, "gateways": sent_to, "message": message})

        if actions.get("reply_with_template"):
            reply_body = self._render_template(actions["reply_with_template"], email_info)
            reply_subject = self._render_template(actions.get("reply_subject_template", "Re: {subject}"), email_info)
            ok, _ = self.email_tasks.send_email({'to': [email_info['sender_address']]}, reply_subject, reply_body)
            results.append({"action": "reply", "ok": ok, "to": email_info['sender_address'], "subject": reply_subject})

        return results

    def _handle_process_inbox(self, params):
        mailbox = params.get("mailbox", "INBOX")
        rules = params.get("rules", [])
        processed = []

        uids = self._search_inbox(params)
        if not uids:
            logger.info("No emails found matching search criteria for inbox processing.")
            log_audit_entry(self.audit_log, "WARNING", "No emails matched the inbox search criteria.", "process_inbox")
            return True, {"processed_emails": []}  # Nothing to do is not a failure

        for uid in uids:
            email_info, msg = self.email_tasks.fetch_email_content(uid, mailbox)
            if not email_info:
                log_audit_entry(self.audit_log, "ERROR", f"Failed to fetch email UID {uid!r}", "process_inbox")
                continue

            summary = {k: email_info[k] for k in ("uid", "sender", "subject", "has_attachments")}
            summary["matched_rules"] = []
            for index, rule in enumerate(rules):
                rule_name = rule.get("name", f"rule_{index}")
                if not self._rule_matches(rule.get("if", {}), email_info):
                    logger.info(f"Rule '{rule_name}' did not match email UID {email_info['uid']}.")
                    continue
                logger.info(f"Rule '{rule_name}' matched for email UID {email_info['uid']}. Applying actions...")
                results = self._apply_rule_actions(rule.get("then", {}), email_info, msg, mailbox)
                summary["matched_rules"].append({"rule": rule_name, "results": results})
                log_audit_entry(self.audit_log, "INFO", f"Rule '{rule_name}' matched email '{email_info['subject']}'",
                                "process_inbox_rule", {"uid": email_info["uid"], "results": results})

            summary["attachments_meta"] = email_info["attachments_meta"]
            processed.append(summary)

        return True, {"processed_emails": processed, "count": len(processed)}

    # --- Orchestration ---
    def _process_task(self, task):
        """Dispatches a task to the appropriate handler and manages context."""
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        output_context_key = task.get("output_context_key")
        handler = self.task_handlers.get(task_type)

        if not handler:
            log_audit_entry(self.audit_log, "WARNING", f"Unsupported task type: {task_type}", task_type, task)
            return

        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type, task)
        try:
            success, output = handler(task.get("parameters", {}))
            if success and output is not None and output_context_key:
                self._update_context(output_context_key, output)
            if success:
                log_audit_entry(self.audit_log, "SUCCESS", f"Task '{task_name}' completed successfully.", task_type,
                                {"output_context_key": output_context_key, "output": output})
            else:
                log_audit_entry(self.audit_log, "ERROR", f"Task '{task_name}' failed.", task_type, {"output": output})
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"An error occurred during task '{task_name}': {e}", task_type,
                            {"error": str(e), "task_details": task})
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)

    def _send_error_notification(self):
        """Agent-level error alert: emails a summary when any task failed."""
        settings = self.config.get("error_notification", {})
        errors = [e for e in self.audit_log if e["status"] in ("ERROR", "CRITICAL")]
        if not settings.get("enabled") or not errors:
            return
        lines = [f"- [{e['timestamp']}] {e['task_type']}: {e['message']}" for e in errors]
        body = (f"The Communication Agent run {self.context.get('run_id')} finished with {len(errors)} error(s):\n\n"
                + "\n".join(lines) + "\n\nSee the JSON audit report for full details.")
        ok, _ = self.email_tasks.send_email({"to": settings.get("to", [self.email_tasks.sender_email])},
                                            f"[Agent Error] {len(errors)} error(s) in run {self.context.get('run_id')}", body)
        log_audit_entry(self.audit_log, "INFO" if ok else "ERROR",
                        f"Error notification {'sent' if ok else 'could not be sent'}", "error_notification")

    def _generate_audit_report(self, output_dir="reports"):
        """Generates a JSON audit report."""
        ensure_directory_exists(output_dir)
        report_path = os.path.join(output_dir, f"audit_report_comm_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        log_audit_entry(self.audit_log, "INFO", f"Audit report generated at {report_path}", "audit_report")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=4, ensure_ascii=False, default=str)
            logger.info(f"Audit report saved to: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")
            return None

    def run(self):
        """Executes all tasks defined in the configuration."""
        logger.info("Starting Communication Agent run...")
        log_audit_entry(self.audit_log, "INFO", "Communication Agent started.", "agent_run")

        # Simulated data that would come from an earlier agent (e.g. a Data/Report agent)
        self._update_context("run_id", self.start_time.strftime("%Y%m%d-%H%M%S"))
        self._update_context("sender_email", self.email_tasks.sender_email)
        self._update_context("report_name", "DailySalesSummary")
        self._update_context("report_date", datetime.date.today().strftime("%Y-%m-%d"))
        self._update_context("sales_figure", 12345.67)
        self._update_context("total_customers", 500)
        self._update_context("top_product", "Wireless Earbuds")
        self._update_context("attachment_path_1", "data/reports/sales_report.pdf")
        self._update_context("attachment_path_2", "data/reports/summary_data.xlsx")

        for task in self.config.get("tasks", []):
            self._process_task(task)

        self._send_error_notification()

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        statuses = [e["status"] for e in self.audit_log]
        log_audit_entry(self.audit_log, "INFO", f"Communication Agent finished in {duration:.2f} seconds.",
                        "agent_run_summary", {"success": statuses.count("SUCCESS"), "errors": statuses.count("ERROR")})
        logger.info(f"Communication Agent finished. Total time: {duration:.2f} seconds.")

        return self._generate_audit_report(os.path.join(self.base_dir, 'reports'))
