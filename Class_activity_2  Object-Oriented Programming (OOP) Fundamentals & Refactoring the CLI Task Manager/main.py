# my-oop-task-manager/main.py
"""Entry point: CLI menu that talks to a TaskManager object."""
import sys

from src.task_manager import TaskManager


def display_menu():
    """Prints the main menu."""
    print("\n--- OOP Task Manager Menu ---")
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Complete Task")
    print("4. Delete Task")
    print("5. Exit")
    print("-" * 26)


def ask_task_id(prompt):
    """Asks for a task ID; returns an int or None if the input is not a positive number."""
    raw = input(prompt).strip().lstrip("#")
    try:
        task_id = int(raw)
        if task_id <= 0:
            raise ValueError
        return task_id
    except ValueError:
        print("Invalid input. Please enter a valid task ID (a number).")
        return None


def main():
    manager = TaskManager()  # loads data/tasks.json into Task objects

    try:
        while True:
            display_menu()
            choice = input("Enter your choice (1-5): ").strip()

            if choice == '1':
                description = input("Enter task description: ").strip()
                if description:
                    manager.add_task(description)
                else:
                    print("Task description cannot be empty.")
            elif choice == '2':
                manager.list_tasks()
            elif choice == '3':
                task_id = ask_task_id("Enter ID of task to complete: ")
                if task_id is not None:
                    manager.complete_task(task_id)
            elif choice == '4':
                task_id = ask_task_id("Enter ID of task to delete: ")
                if task_id is not None:
                    manager.delete_task(task_id)
            elif choice == '5':
                print("Exiting Task Manager. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")
    except KeyboardInterrupt:
        print("\nExiting Task Manager. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
