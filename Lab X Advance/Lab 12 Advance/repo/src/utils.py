# src/utils.py
import logging
import os
import re
from dotenv import load_dotenv
import json
import datetime

# Load environment variables from .env file
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Matches ${UPPER_CASE_NAME} placeholders used in the JSON config for secrets/env values.
# Lower-case ones such as "${sales_figure:.2f}" are left alone ("$" + a normal template field).
ENV_PLACEHOLDER_PATTERN = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")


def setup_logging(name, level=logging.INFO):
    """Sets up a logger for specific modules."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False  # Avoid printing every line twice via the root logger
    return logger


def get_env_variable(var_name):
    """Retrieves an environment variable, raising an error if not found."""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not set. Please check your .env file.")
    return value


def resolve_env_placeholders(value):
    """
    Recursively replaces ${ENV_VAR} placeholders in strings/lists/dicts with values from the
    environment, so credentials and personal addresses never have to be written into the config.
    """
    if isinstance(value, str):
        return ENV_PLACEHOLDER_PATTERN.sub(lambda m: get_env_variable(m.group(1)), value)
    if isinstance(value, list):
        return [resolve_env_placeholders(v) for v in value]
    if isinstance(value, dict):
        return {k: resolve_env_placeholders(v) for k, v in value.items()}
    return value


def ensure_directory_exists(path):
    """Ensures that a directory exists, creating it if necessary."""
    try:
        os.makedirs(path, exist_ok=True)
        logging.debug(f"Directory ensured: {path}")
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}")
        raise


def log_audit_entry(audit_log_list, status, message, task_type="N/A", details=None):
    """Adds an entry to the audit log list."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": status,
        "task_type": task_type,
        "message": message,
        "details": details if details else {}
    }
    audit_log_list.append(log_entry)
    if status == "ERROR" or status == "CRITICAL":
        logging.error(f"AUDIT LOG - {status}: {message} | Task: {task_type} | Details: {details}")
    elif status == "WARNING":
        logging.warning(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
    else:
        logging.info(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
