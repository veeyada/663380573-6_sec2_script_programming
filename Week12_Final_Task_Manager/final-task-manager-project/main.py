# final-task-manager-project/main.py
import logging
import os
import sys

# Make the project root importable so 'src' is treated as a package
# (the modules inside src use relative imports like 'from .task import Task').
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.task_manager import TaskManager
from src.cli_interface import CLIInterface


def main():
    """
    Main entry point for the Enhanced Task Manager application.
    Initializes TaskManager and CLIInterface, then starts the CLI loop.
    Run with --debug to see log messages.
    """
    level = logging.INFO if "--debug" in sys.argv else logging.WARNING
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    manager = TaskManager()
    cli = CLIInterface(manager)
    cli.run()


if __name__ == "__main__":
    main()
