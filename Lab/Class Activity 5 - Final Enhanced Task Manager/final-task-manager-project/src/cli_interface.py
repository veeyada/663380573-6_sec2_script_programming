# final-task-manager-project/src/cli_interface.py
"""Command-line user interface. Contains no business logic."""
import datetime

from .task import DATE_FORMAT, ALLOWED_PRIORITIES

LINE = "=" * 40


class CLIInterface:
    """
    Handles all command-line interface interactions: displaying menus,
    taking user input, and displaying output.
    Does NOT contain business logic directly; calls methods on TaskManager.
    """

    def __init__(self, task_manager):
        self.manager = task_manager
        self.actions = {
            '1': self.add_normal_task,
            '2': self.add_due_date_task,
            '3': self.add_priority_task,
            '4': self.list_tasks,
            '5': self.complete_task,
            '6': self.delete_task,
            '7': self.search_tasks,
            '8': self.filter_tasks,
            '9': self.sort_tasks,
            '10': self.manage_tags,
        }

    # --- Menu ---
    def display_menu(self):
        print(f"\n{LINE}\n      Enhanced Task Manager Menu\n{LINE}")
        print(" 1. Add Normal Task")
        print(" 2. Add Due Date Task")
        print(" 3. Add Priority Task")
        print(" 4. List All Tasks")
        print(" 5. Complete Task")
        print(" 6. Delete Task")
        print(" 7. Search Tasks")
        print(" 8. Filter Tasks")
        print(" 9. Sort Tasks")
        print("10. Add/Remove Tag")
        print(" 0. Exit")
        print("-" * 40)

    def get_user_choice(self):
        return input("Enter your choice (0-10): ").strip()

    # --- Input helpers (all validate and re-prompt, never crash) ---
    def get_task_description(self):
        while True:
            description = input("Enter task description: ").strip()
            if description:
                return description
            print("[Error] Task description cannot be empty. Please try again.")

    def get_due_date_input(self):
        while True:
            date_str = input("Enter due date (YYYY-MM-DD): ").strip()
            date = self._parse_date(date_str)
            if date:
                return date
            print("[Error] Invalid date. Please use YYYY-MM-DD "
                  "(e.g., 2026-12-31).")

    def get_priority_input(self):
        while True:
            priority = input("Enter priority (High/Medium/Low): ").strip()
            priority = priority.capitalize()
            if priority in ALLOWED_PRIORITIES:
                return priority
            print("[Error] Invalid priority. Please enter High, Medium or Low.")

    def get_tags_input(self, prompt=None):
        prompt = prompt or ("Enter tags (comma-separated, e.g., "
                            "study,project,urgent - optional): ")
        tags_str = input(prompt).strip()
        return [tag.strip().lower() for tag in tags_str.split(',')
                if tag.strip()]

    def get_task_id_input(self, action):
        """Returns an int ID, or None if the input is not a number."""
        raw = input(f"Enter ID of task to {action}: ").strip()
        try:
            return int(raw)
        except ValueError:
            print("[Error] Invalid input. Please enter a number for Task ID.")
            return None

    def get_yes_no(self, prompt):
        """Returns True / False, or None when left blank."""
        while True:
            answer = input(prompt).strip().lower()
            if answer == "":
                return None
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False
            print("[Error] Please answer yes or no (or leave blank).")

    def get_optional_date(self, prompt):
        """Returns a date or None (blank). Re-prompts on invalid input."""
        while True:
            date_str = input(prompt).strip()
            if not date_str:
                return None
            date = self._parse_date(date_str)
            if date:
                return date
            print("[Error] Invalid date. Use YYYY-MM-DD or leave blank.")

    @staticmethod
    def _parse_date(date_str):
        try:
            return datetime.datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            return None

    def _display_tasks(self, tasks, title="Tasks"):
        if not tasks:
            print(f"\n[Info] No tasks found for: {title}.")
            return
        print(f"\n--- {title} (Total: {len(tasks)}) ---")
        for task in tasks:
            print(f"  * {task}")
        print("-" * 40)

    @staticmethod
    def _print_result(success, message):
        print(f"[{'Success' if success else 'Error'}] {message}")

    # --- Menu actions ---
    def add_normal_task(self):
        description = self.get_task_description()
        tags = self.get_tags_input()
        task = self.manager.add_normal_task(description, tags=tags)
        print(f"[Success] Normal Task '{task.description}' "
              f"added with ID {task.id}.")

    def add_due_date_task(self):
        description = self.get_task_description()
        due_date = self.get_due_date_input()
        tags = self.get_tags_input()
        task = self.manager.add_due_date_task(description, due_date, tags=tags)
        if task:
            print(f"[Success] Due Date Task '{task.description}' "
                  f"(Due: {task.due_date.strftime(DATE_FORMAT)}) "
                  f"added with ID {task.id}.")
        else:
            print("[Error] Failed to add Due Date Task. Please check your input.")

    def add_priority_task(self):
        description = self.get_task_description()
        priority = self.get_priority_input()
        tags = self.get_tags_input()
        task = self.manager.add_priority_task(description, priority, tags=tags)
        if task:
            print(f"[Success] Priority Task '{task.description}' "
                  f"(Priority: {task.priority}) added with ID {task.id}.")
        else:
            print("[Error] Failed to add Priority Task. Please check your input.")

    def list_tasks(self):
        self._display_tasks(self.manager.get_all_tasks(), "Your Tasks")

    def complete_task(self):
        task_id = self.get_task_id_input("complete")
        if task_id is not None:
            self._print_result(*self.manager.complete_task(task_id))

    def delete_task(self):
        task_id = self.get_task_id_input("delete")
        if task_id is None:
            return
        task = self.manager.get_task_by_id(task_id)
        if task is None:
            print(f"[Error] Task ID {task_id} not found.")
            return
        print(f"  {task}")
        if self.get_yes_no("Delete this task? (yes/no): ") is True:
            self._print_result(*self.manager.delete_task(task_id))
        else:
            print("[Info] Delete cancelled.")

    def search_tasks(self):
        keyword = input("Enter search keyword (in description or tags): ").strip()
        if not keyword:
            print("[Error] Search keyword cannot be empty.")
            return
        self._display_tasks(self.manager.search_tasks(keyword),
                            f"Search Results for '{keyword}'")

    def filter_tasks(self):
        print("\n--- Filter Tasks (leave any field blank to skip it) ---")
        status = self.get_yes_no("Completed? (yes/no): ")
        due_before = self.get_optional_date("Due on or before (YYYY-MM-DD): ")
        due_after = self.get_optional_date("Due on or after (YYYY-MM-DD): ")
        if due_before and due_after and due_after > due_before:
            print("[Warning] 'after' date is later than 'before' date - "
                  "no task can match.")

        while True:
            priority = input("Priority (High/Medium/Low): ").strip().capitalize()
            if not priority or priority in ALLOWED_PRIORITIES:
                break
            print("[Error] Please enter High, Medium, Low or leave blank.")

        tags = self.get_tags_input(
            "Tags (comma-separated, task must have ALL of them): ")

        results = self.manager.filter_tasks(
            status=status,
            due_date_before=due_before,
            due_date_after=due_after,
            priority_level=priority or None,
            contains_tags=tags or None,
        )
        self._display_tasks(results, "Filtered Tasks")

    def sort_tasks(self):
        criteria = self.manager.SORT_CRITERIA
        print("\n--- Sort Tasks ---")
        print(f"Available criteria: {', '.join(criteria)}")
        while True:
            criterion = input("Sort by (default: id): ").strip().lower() or "id"
            if criterion in criteria:
                break
            print(f"[Error] Unknown criterion. Choose from: {', '.join(criteria)}")
        reverse = self.get_yes_no("Descending order? (yes/no, default: no): ")
        reverse = bool(reverse)
        order = "Descending" if reverse else "Ascending"
        self._display_tasks(self.manager.sort_tasks(criterion, reverse),
                            f"Tasks sorted by {criterion} ({order})")

    def manage_tags(self):
        task_id = self.get_task_id_input("edit tags")
        if task_id is None:
            return
        task = self.manager.get_task_by_id(task_id)
        if task is None:
            print(f"[Error] Task ID {task_id} not found.")
            return
        print(f"  {task}")
        action = input("(a)dd or (r)emove a tag? ").strip().lower()
        if action not in ("a", "add", "r", "remove"):
            print("[Error] Please enter 'a' or 'r'.")
            return
        tag = input("Tag: ").strip()
        if action.startswith("a"):
            self._print_result(*self.manager.add_tag_to_task(task_id, tag))
        else:
            self._print_result(*self.manager.remove_tag_from_task(task_id, tag))

    # --- Main loop ---
    def run(self):
        print("Welcome to the Enhanced Task Manager!")
        while True:
            self.display_menu()
            try:
                choice = self.get_user_choice()
                if choice == '0':
                    print("Exiting Task Manager. Goodbye!")
                    break
                action = self.actions.get(choice)
                if action:
                    action()
                else:
                    print("[Error] Invalid choice. Please enter a number "
                          "between 0 and 10.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Task Manager. Goodbye!")
                break
            except OSError as e:
                print(f"[Error] Could not save tasks: {e}")
