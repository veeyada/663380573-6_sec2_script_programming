# src/communication_agent.py
import os
import json
import datetime
import time
from utils import setup_logging, log_audit_entry, ensure_directory_exists, get_env_variable, get_optional_env
from email_tasks import EmailTasks
from sms_tasks import SMSTasks
from template_renderer import TemplateRenderer

logger = setup_logging(__name__)

class CommunicationAgent:
    def __init__(self, config, base_dir):
        self.config = config
        self.audit_log = []
        self.context = {}
        self.start_time = datetime.datetime.now()
        self.base_dir = base_dir

        try:
            sender_email = get_env_variable("SENDER_EMAIL")
            sender_app_password = get_env_variable("SENDER_APP_PASSWORD")
            smtp_server = get_env_variable("SMTP_SERVER")
            smtp_port = int(get_env_variable("SMTP_PORT"))
            imap_server = get_env_variable("IMAP_SERVER")

            # Addresses come from .env so the config never needs real emails written into it
            self.context["sender_email"] = sender_email
            self.context["test_recipient"] = get_optional_env("TEST_RECIPIENT_EMAIL", sender_email)
            # SMS gateway: a carrier address like 0812345678@carrier.example, or (default) your own inbox
            self.context["sms_gateway"] = get_optional_env("SMS_GATEWAY_ADDRESS", sender_email)
            self.context["student_name"] = get_optional_env("STUDENT_NAME", "")
            self.context["student_id"] = get_optional_env("STUDENT_ID", "")

            self.email_tasks = EmailTasks(smtp_server, smtp_port, imap_server, sender_email, sender_app_password)
            self.sms_tasks = SMSTasks(self.email_tasks)
            self.template_renderer = TemplateRenderer()
            logger.info("CommunicationAgent initialized with task handlers.")
        except ValueError as e:
            logger.critical(f"Agent initialization failed: Missing environment variables. {e}")
            raise

    def _update_context(self, key, value):
        self.context[key] = value

    def _render_template(self, template_string):
        try:
            return self.template_renderer.render(template_string, self.context)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"Template rendering failed: {e}", "template_render")
            raise

    def _process_task(self, task):
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        task_params = task.get("parameters", {})
        output_context_key = task.get("output_context_key")

        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type, task)

        try:
            success = False
            task_output_data = None

            if task_type == "send_email":
                recipients = {k: [self._render_template(r) for r in v] for k, v in task_params.get('recipients', {}).items()}
                subject = self._render_template(task_params.get("subject_template"))
                body = self._render_template(task_params.get("body_template"))

                attachments = [os.path.join(self.base_dir, self._render_template(att_path)) for att_path in task_params.get("attachments", [])]
                # Conditional attachments: only files that exist are attached
                missing = [a for a in attachments if not os.path.exists(a)]
                attachments = [a for a in attachments if os.path.exists(a)]
                if missing:
                    log_audit_entry(self.audit_log, "WARNING", f"Skipped missing attachment(s): {[os.path.basename(m) for m in missing]}", task_type)
                is_html = task_params.get("is_html", False)
                success = self.email_tasks.send_email(recipients, subject, body, attachments, is_html)
                if success: task_output_data = {"recipients": recipients, "subject": subject,
                                                "attachments": [os.path.basename(a) for a in attachments]}

            elif task_type == "send_sms":
                phone_numbers = [self._render_template(p) for p in task_params.get("phone_numbers", [])]
                message = self._render_template(task_params.get("message_template"))
                carrier_name = task_params.get("carrier_name")
                success = self.sms_tasks.send_sms(phone_numbers, message, carrier_name)
                if success: task_output_data = {"phone_numbers": phone_numbers, "message": message}

            elif task_type == "process_inbox":
                mailbox = task_params.get("mailbox", "INBOX")
                search_criteria = task_params.get("search_criteria", {})
                rules = task_params.get("rules", [])
                download_dir = os.path.join(self.base_dir, task_params.get("download_attachments_base_dir", "data/incoming_attachments"))

                rendered_sender = self._render_template(search_criteria.get("from_sender", "")) if search_criteria.get("from_sender") else None
                rendered_subject = self._render_template(search_criteria.get("subject_contains", "")) if search_criteria.get("subject_contains") else None

                # Give the mail server time to deliver the email we just sent to ourselves, then poll
                wait_seconds = task_params.get("wait_before_search_seconds", 0)
                poll_attempts = max(1, task_params.get("poll_attempts", 1))
                uids = []
                for attempt in range(1, poll_attempts + 1):
                    if wait_seconds:
                        logger.info(f"Waiting {wait_seconds}s for new mail (attempt {attempt}/{poll_attempts})...")
                        time.sleep(wait_seconds)
                    uids = self.email_tasks.search_emails(mailbox=mailbox, criteria=search_criteria.get("status", "UNSEEN"),
                                                          from_sender=rendered_sender, subject_contains=rendered_subject)
                    if uids:
                        break

                ignore_prefixes = [p.lower() for p in search_criteria.get("ignore_subject_prefixes", [])]
                processed = []
                for uid in uids:
                    email_info = self.email_tasks.fetch_email_content(uid=uid, mark_as_read=True, download_attachments_dir=download_dir)
                    if not email_info:
                        continue
                    if any(email_info['subject'].lower().startswith(p) for p in ignore_prefixes):
                        logger.info(f"Skipping UID {email_info['uid']} (reply/forward): '{email_info['subject']}'")
                        continue
                    log_audit_entry(self.audit_log, "INFO",
                                    f"Processed email UID {email_info['uid']} '{email_info['subject']}' "
                                    f"({len(email_info['attachments_meta'])} attachment(s) downloaded, marked as read)", task_type)
                    rule_context = {**self.context, **email_info,
                                    "attachment_names": ", ".join(a['filename'] for a in email_info['attachments_meta']) or "none"}
                    matched = []
                    for idx, rule in enumerate(rules, 1):
                        if_cond = rule.get("if", {})
                        then_act = rule.get("then", {})
                        subject_l, body_l = email_info['subject'].lower(), email_info['text_body'].lower()
                        condition_met = True
                        if "subject_contains" in if_cond and if_cond["subject_contains"].lower() not in subject_l: condition_met = False
                        if "body_contains" in if_cond and if_cond["body_contains"].lower() not in body_l: condition_met = False
                        if "has_attachments" in if_cond and if_cond["has_attachments"] != email_info['has_attachments']: condition_met = False
                        if "from_sender" in if_cond and self._render_template(if_cond["from_sender"]).lower() not in email_info['sender'].lower(): condition_met = False
                        if not condition_met:
                            continue

                        rule_name = rule.get("name", f"rule {idx}")
                        matched.append(rule_name)
                        logger.info(f"Rule '{rule_name}' matched for email UID {email_info['uid']}.")
                        if then_act.get("send_sms_alert"):
                            alert_msg = self.template_renderer.render(then_act.get("alert_message_template", "Urgent!"), rule_context)
                            phones = [self.template_renderer.render(p, rule_context) for p in then_act.get("alert_phone_numbers", [])]
                            ok = self.sms_tasks.send_sms(phones, alert_msg, then_act.get("alert_carrier"))
                            log_audit_entry(self.audit_log, "SUCCESS" if ok else "ERROR", f"[{rule_name}] SMS alert sent to {phones}: '{alert_msg}'", "sms_alert")
                        if "reply_with_template" in then_act:
                            reply_body = self.template_renderer.render(then_act["reply_with_template"], rule_context)
                            reply_subj = self.template_renderer.render(then_act.get("reply_subject_template", "Re: {subject}"), rule_context)
                            ok = self.email_tasks.send_email(recipients={'to': [email_info['sender_address']]}, subject=reply_subj, body=reply_body)
                            log_audit_entry(self.audit_log, "SUCCESS" if ok else "ERROR", f"[{rule_name}] Auto-reply sent: '{reply_subj}'", "auto_reply")
                    processed.append({"uid": email_info['uid'], "subject": email_info['subject'],
                                      "attachments": [a['filename'] for a in email_info['attachments_meta']], "matched_rules": matched})
                task_output_data = processed
                if not processed:
                    log_audit_entry(self.audit_log, "INFO", "No matching unread emails found.", task_type)
                success = True
            else:
                logger.warning(f"Unsupported task type: {task_type}")
                return

            if success and task_output_data is not None and output_context_key:
                self._update_context(output_context_key, task_output_data)

            log_audit_entry(self.audit_log, "SUCCESS" if success else "ERROR", f"Task '{task_name}' {'completed' if success else 'failed'}.", task_type)
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"An error occurred during task '{task_name}': {e}", task_type)
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)

    def _generate_audit_report(self, output_dir="reports"):
        ensure_directory_exists(output_dir)
        report_path = os.path.join(output_dir, f"audit_report_comm_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=4, ensure_ascii=False)
            logger.info(f"Audit report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")

    def run(self):
        logger.info("Starting Communication Agent run...")
        # Inject dummy context data
        self._update_context("report_name", "DailySalesSummary")
        self._update_context("report_date", datetime.date.today().strftime("%Y-%m-%d"))
        self._update_context("sales_figure", 12345.67)
        self._update_context("total_customers", 500)

        for task in self.config.get("tasks", []):
            self._process_task(task)

        ok = sum(1 for e in self.audit_log if e["status"] == "SUCCESS")
        bad = sum(1 for e in self.audit_log if e["status"] == "ERROR")
        log_audit_entry(self.audit_log, "INFO", f"Summary: {ok} action(s) succeeded, {bad} failed.", "agent_run_summary")
        self._generate_audit_report(os.path.join(self.base_dir, 'reports'))
        logger.info("Communication Agent finished.")
