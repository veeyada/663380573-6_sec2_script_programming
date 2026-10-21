# main.py
import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from config_parser import ConfigParser
from communication_agent import CommunicationAgent
from utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


def check_required_files(config, base_dir, known_context):
    """
    Checks that every attachment referenced by send_email tasks exists before the agent starts.
    Templated paths (e.g. "{attachment_path_1}") are resolved with the context values the agent seeds.
    """
    missing_files = []
    for task in config['tasks']:
        if task['type'] != 'send_email':
            continue
        for att_path in task.get('parameters', {}).get('attachments', []):
            try:
                resolved = att_path.format(**known_context) if '{' in att_path else att_path
            except (KeyError, IndexError):
                logger.warning(f"Cannot pre-check templated attachment path '{att_path}'; the agent will resolve it at runtime.")
                continue
            file_path = os.path.join(base_dir, resolved)
            if not os.path.exists(file_path):
                missing_files.append(file_path)
    return not missing_files, missing_files


def main():
    """
    Main entry point for the Agentic Communication Automator.
    Loads config and runs the agent.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'configs', 'comm_pipeline_config.json')

    try:
        for folder in (('data', 'reports'), ('data', 'attachments'), ('data', 'incoming_attachments'), ('reports',)):
            ensure_directory_exists(os.path.join(base_dir, *folder))

        logger.info(f"Loading configuration from: {config_file_path}")
        config = ConfigParser(config_file_path).load_config()

        files_exist, missing = check_required_files(config, base_dir, {
            "attachment_path_1": "data/reports/sales_report.pdf",
            "attachment_path_2": "data/reports/summary_data.xlsx",
        })
        if not files_exist:
            logger.critical(f"Required attachment files are missing: {', '.join(missing)}. "
                            f"Run 'python create_sample_data.py' first.")
            sys.exit(1)

        logger.info("Initializing Communication Agent...")
        agent = CommunicationAgent(config, base_dir)

        logger.info("Running Communication Agent workflow...")
        report_path = agent.run()
        logger.info(f"Communication automation process completed. Audit report: {report_path}")

    except FileNotFoundError as e:
        logger.critical(f"File system error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.critical(f"Configuration or environment variable error: {e}")
        logger.info("Please check the format and required fields in your config file and .env.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
