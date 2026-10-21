"""
Main Entry Point: Task Manager CLI Application
Week 7: Building a Simple CLI Application, Error Handling & Project Structure
"""

import sys
import os

# Add the 'src' directory to sys.path so modules can be imported directly
SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import task_data
import task_logic


def display_menu() -> None:
    """Displays the interactive CLI menu options."""
    print("\n" + "=" * 34)
    print("        TASK MANAGER CLI          ")
    print("=" * 34)
    print("  1. Add New Task")
    print("  2. List All Tasks")
    print("  3. List Pending Tasks")
    print("  4. List Completed Tasks")
    print("  5. Search Tasks by Keyword")
    print("  6. Mark Task as Completed")
    print("  7. Delete Task")
    print("  8. Save and Exit")
    print("=" * 32)


def prompt_task_id(prompt_text: str) -> int:
    """
    Prompts the user for a task ID with error handling.

    Args:
        prompt_text: The prompt string to display to user.

    Returns:
        int: A valid integer task ID.

    Raises:
        ValueError: If the user input is not a valid integer.
    """
    raw_input = input(prompt_text).strip()
    # Remove leading '#' if user typed e.g. '#2'
    if raw_input.startswith("#"):
        raw_input = raw_input[1:]

    task_id = int(raw_input)
    if task_id <= 0:
        raise ValueError("Task ID must be a positive integer.")
    return task_id


def main() -> None:
    """Main application loop."""
    print("Welcome to Task Manager CLI!")
    print("Loading existing tasks from storage...")
    tasks = task_data.load_tasks()
    print(f"Loaded {len(tasks)} task(s) successfully.")

    try:
        while True:
            display_menu()
            choice = input("Enter choice (1-8): ").strip()

            if choice == "1":
                description = input("Enter task description: ").strip()
                if not description:
                    print("[Error] Description cannot be empty.")
                    continue

                priority = input("Enter priority (Low / Medium / High) [Default: Medium]: ").strip()
                if not priority:
                    priority = "Medium"

                tasks = task_logic.add_task(tasks, description, priority)
                # Auto-save after addition
                task_data.save_tasks(tasks)

            elif choice == "2":
                task_logic.list_tasks(tasks)

            elif choice == "3":
                task_logic.list_tasks(tasks, filter_status="pending")

            elif choice == "4":
                task_logic.list_tasks(tasks, filter_status="completed")

            elif choice == "5":
                kw = input("Enter search keyword: ").strip()
                task_logic.search_tasks(tasks, kw)

            elif choice == "6":
                try:
                    task_id = prompt_task_id("Enter ID of task to mark as completed: ")
                    tasks = task_logic.complete_task(tasks, task_id)
                    task_data.save_tasks(tasks)
                except ValueError as ve:
                    print(f"[Error] Invalid input: {ve}. Please enter a positive number (e.g. 1, 2, 3).")

            elif choice == "7":
                try:
                    task_id = prompt_task_id("Enter ID of task to delete: ")
                    confirm = input(f"Are you sure you want to delete Task #{task_id}? (y/N): ").strip().lower()
                    if confirm in ("y", "yes"):
                        tasks = task_logic.delete_task(tasks, task_id)
                        task_data.save_tasks(tasks)
                    else:
                        print("Deletion cancelled.")
                except ValueError as ve:
                    print(f"[Error] Invalid input: {ve}. Please enter a valid numerical ID.")

            elif choice == "8":
                print("\nSaving tasks to file...")
                success = task_data.save_tasks(tasks)
                if success:
                    print("[OK] All tasks saved successfully. Goodbye!")
                else:
                    print("[Warning] Could not confirm task save, please check file permissions.")
                break

            else:
                print("[Error] Invalid choice. Please select an option between 1 and 8.")

    except KeyboardInterrupt:
        # Graceful handling when user presses Ctrl+C
        print("\n\n[Notice] Application interrupted by user (Ctrl+C).")
        print("Emergency saving tasks before exit...")
        task_data.save_tasks(tasks)
        print("[OK] Tasks saved. Exiting safely.")
        sys.exit(0)


if __name__ == "__main__":
    main()
