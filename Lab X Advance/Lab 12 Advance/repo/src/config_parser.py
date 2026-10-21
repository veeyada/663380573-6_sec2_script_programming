# src/config_parser.py
import json
import os
from utils import setup_logging, resolve_env_placeholders

logger = setup_logging(__name__)

SUPPORTED_TASK_TYPES = {"send_email", "send_sms", "process_inbox"}
SUPPORTED_RULE_CONDITIONS = {"from_sender", "subject_contains", "body_contains", "has_attachments"}
SUPPORTED_RULE_ACTIONS = {
    "download_attachments_to", "allowed_extensions", "rename_template", "mark_as_read",
    "send_sms_alert", "alert_phone_numbers", "alert_carrier", "alert_message_template",
    "reply_with_template", "reply_subject_template",
}


class ConfigParser:
    """
    Parses and validates the communication automation configuration from a JSON file.
    ${ENV_VAR} placeholders are resolved from the environment (.env) after loading.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """Loads the configuration from the specified JSON file."""
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON format in config file: {e}")
            raise ValueError(f"Invalid JSON format in config file: {e}")

        self._validate_config()
        self.config = resolve_env_placeholders(self.config)
        logger.info(f"Configuration loaded successfully from {self.config_path}")
        return self.config

    def _validate_config(self):
        """
        Validates the loaded configuration to ensure required fields and task structures are present.
        """
        if "tasks" not in self.config:
            raise ValueError("Missing required field in config: 'tasks'")
        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        for i, task in enumerate(self.config["tasks"]):
            if "type" not in task:
                raise ValueError(f"Task {i} is missing 'type' field.")
            if "name" not in task:
                raise ValueError(f"Task {i} (type: {task['type']}) is missing 'name' field.")
            if task["type"] not in SUPPORTED_TASK_TYPES:
                logger.warning(f"Task {i} has unsupported type '{task['type']}'; the agent will skip it.")
                continue

            params = task.get("parameters")
            if not isinstance(params, dict):
                raise ValueError(f"Task {i} ({task['type']}) requires a 'parameters' object.")

            if task["type"] == "send_email":
                if not all(k in params for k in ["recipients", "subject_template", "body_template"]):
                    raise ValueError(f"Task {i} (send_email) requires 'recipients', 'subject_template', 'body_template' in parameters.")
                recipients = params["recipients"]
                if not isinstance(recipients, dict) or not isinstance(recipients.get("to"), list):
                    raise ValueError(f"Task {i} (send_email) 'recipients' must be an object with a 'to' list.")
                for field in ("cc", "bcc"):
                    if field in recipients and not isinstance(recipients[field], list):
                        raise ValueError(f"Task {i} (send_email) 'recipients.{field}' must be a list.")
                if "attachments" in params and not isinstance(params["attachments"], list):
                    raise ValueError(f"Task {i} (send_email) 'attachments' parameter must be a list.")

            elif task["type"] == "send_sms":
                if not all(k in params for k in ["phone_numbers", "message_template"]):
                    raise ValueError(f"Task {i} (send_sms) requires 'phone_numbers', 'message_template' in parameters.")
                if not isinstance(params["phone_numbers"], list):
                    raise ValueError(f"Task {i} (send_sms) 'phone_numbers' parameter must be a list.")

            elif task["type"] == "process_inbox":
                if "search_criteria" not in params:
                    raise ValueError(f"Task {i} (process_inbox) requires 'search_criteria' in parameters.")
                rules = params.get("rules", [])
                if not isinstance(rules, list):
                    raise ValueError(f"Task {i} (process_inbox) 'rules' parameter must be a list.")
                for j, rule in enumerate(rules):
                    unknown_if = set(rule.get("if", {})) - SUPPORTED_RULE_CONDITIONS
                    unknown_then = set(rule.get("then", {})) - SUPPORTED_RULE_ACTIONS
                    if unknown_if or unknown_then:
                        raise ValueError(f"Task {i} rule {j} has unknown keys: {sorted(unknown_if | unknown_then)}")

        logger.info("Configuration validated.")
