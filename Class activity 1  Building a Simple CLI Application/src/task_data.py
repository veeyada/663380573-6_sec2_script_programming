"""
Module: task_data.py
Description: Handles data persistence for the Task Manager CLI application.
             Responsible for loading and saving tasks in JSON format.
"""

import json
import os
from typing import List, Dict, Any

# Resolve absolute path to data/tasks.json relative to this module's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")


def load_tasks() -> List[Dict[str, Any]]:
    """
    Loads tasks from the JSON file.

    Returns:
        List[Dict[str, Any]]: A list of task dictionaries. If the file doesn't exist,
                              is empty, or is corrupted, returns an empty list gracefully.
    """
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
        except OSError as e:
            print(f"[Error] Could not create directory '{DATA_DIR}': {e}")
            return []

    # If the file does not exist yet, return an empty list
    if not os.path.exists(TASKS_FILE):
        return []

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                # Handle empty file case
                return []
            data = json.loads(content)
        # Valid JSON but wrong shape (e.g. a dict) -> keep only well-formed task dicts
        if not isinstance(data, list):
            print("[Warning] tasks.json does not contain a list of tasks. Starting with an empty task list.")
            return []
        valid = [t for t in data if isinstance(t, dict) and isinstance(t.get("id"), int)]
        if len(valid) < len(data):
            print(f"[Warning] Skipped {len(data) - len(valid)} malformed task record(s) in tasks.json.")
        return valid
    except json.JSONDecodeError as e:
        print(f"[Warning] tasks.json is corrupted or invalid JSON (Line {e.lineno}, Col {e.colno}).")
        print("          Starting with an empty task list to prevent crash.")
        return []
    except FileNotFoundError:
        print("[Warning] tasks.json was not found. Starting with an empty task list.")
        return []
    except PermissionError:
        print(f"[Error] Permission denied when reading '{TASKS_FILE}'.")
        return []
    except Exception as e:
        print(f"[Unexpected Error] An error occurred while loading tasks: {e}")
        return []


def save_tasks(tasks: List[Dict[str, Any]]) -> bool:
    """
    Saves the list of tasks to the JSON file.

    Args:
        tasks: List of task dictionaries to persist.

    Returns:
        bool: True if saving succeeded, False otherwise.
    """
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
        return True
    except PermissionError:
        print(f"[Error] Permission denied when writing to '{TASKS_FILE}'.")
        return False
    except OSError as e:
        print(f"[Error] Failed to save tasks to file: {e}")
        return False
    except Exception as e:
        print(f"[Unexpected Error] An error occurred while saving tasks: {e}")
        return False
