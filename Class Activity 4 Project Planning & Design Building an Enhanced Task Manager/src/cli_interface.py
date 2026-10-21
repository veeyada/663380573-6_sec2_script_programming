# src/cli_interface.py
"""
โมดูล cli_interface.py: ส่วนติดต่อผู้ใช้ผ่าน Command Line (User Interface Layer)
รับผิดชอบการแสดงผลเมนู, การรับข้อมูลจากผู้ใช้, และการตรวจสอบความถูกต้องของข้อมูลนำเข้า (Validation)
โดยไม่มี Business Logic ปะปน เพื่อปฏิบัติตามหลัก Separation of Concerns
"""

import datetime


class CLIInterface:
    """
    คลาสสำหรับติดต่อกับผู้ใช้งานผ่าน Command-Line Interface (CLI)
    ทำหน้าที่เป็นส่วนหน้า (Presentation Layer) เชื่อมต่อกับ TaskManager
    """
    def __init__(self, task_manager):
        self.manager = task_manager

    def display_menu(self):
        """แสดงเมนูหลักของโปรแกรม"""
        print("\n" + "=" * 45)
        print("     Enhanced Task Manager (Week 11)")
        print("=" * 45)
        print("1. เพิ่มงานทั่วไป (Add Normal Task)")
        print("2. เพิ่มงานที่มีวันครบกำหนด (Add Due Date Task)")
        print("3. เพิ่มงานที่มีระดับความสำคัญ (Add Priority Task)")
        print("4. แสดงรายการงานทั้งหมด (List All Tasks)")
        print("5. เปลี่ยนสถานะงานเป็นเสร็จสิ้น (Complete Task)")
        print("6. ลบงาน (Delete Task)")
        print("7. ค้นหางาน (Search Tasks - Assignment)")
        print("8. กรองงาน (Filter Tasks - Assignment)")
        print("9. เรียงลำดับงาน (Sort Tasks - Assignment)")
        print("0. ออกจากโปรแกรม (Exit)")
        print("-" * 45)

    def get_user_choice(self):
        """รับค่าตัวเลือกจากผู้ใช้"""
        return input("เลือกเมนู (0-9): ").strip()

    def get_task_description(self):
        """รับรายละเอียดงาน พร้อมตรวจสอบไม่ให้เป็นค่าว่าง"""
        while True:
            description = input("กรอกรายละเอียดงาน (Description): ").strip()
            if description:
                return description
            print("ข้อผิดพลาด: รายละเอียดงานต้องไม่เป็นค่าว่าง กรุณาลองใหม่อีกครั้ง")

    def get_due_date_input(self):
        """รับและตรวจสอบรูปแบบวันกำหนดส่ง (YYYY-MM-DD)"""
        while True:
            due_date_str = input("กรอกวันครบกำหนด (YYYY-MM-DD เช่น 2024-12-31): ").strip()
            try:
                datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                return due_date_str
            except ValueError:
                print("รูปแบบวันที่ไม่ถูกต้อง! กรุณาใช้รูปแบบ YYYY-MM-DD (เช่น 2025-05-30)")

    def get_priority_input(self):
        """รับและตรวจสอบระดับความสำคัญ (High, Medium, Low)"""
        while True:
            priority = input("กรอกระดับความสำคัญ (High / Medium / Low): ").strip().capitalize()
            if priority in ["High", "Medium", "Low"]:
                return priority
            print("ระดับความสำคัญไม่ถูกต้อง! กรุณากรอก 'High', 'Medium', หรือ 'Low'")

    def get_tags_input(self):
        """รับป้ายกำกับ (Tags) โดยคั่นด้วยเครื่องหมายจุลภาค (Comma)"""
        tags_str = input("กรอกป้ายกำกับ (Tags คั่นด้วยจุลภาค เช่น work,urgent,home - หรือเว้นว่างได้): ").strip()
        if not tags_str:
            return []
        return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

    def run(self):
        """ลูปหลักในการทำงานของ CLI Application"""
        print("ยินดีต้อนรับสู่ระบบ Enhanced Task Manager!")
        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == '1':
                # เพิ่มงานทั่วไป
                description = self.get_task_description()
                tags = self.get_tags_input()
                new_task = self.manager.add_normal_task(description, tags=tags)
                print(f"[สำเร็จ]: เพิ่มงานทั่วไป ID {new_task.id} ('{new_task.description}') เรียบร้อยแล้ว")

            elif choice == '2':
                # เพิ่มงานที่มีวันครบกำหนด
                description = self.get_task_description()
                due_date_str = self.get_due_date_input()
                tags = self.get_tags_input()
                new_task = self.manager.add_due_date_task(description, due_date_str, tags=tags)
                print(f"[สำเร็จ]: เพิ่มงานครบกำหนด ID {new_task.id} (ครบกำหนด: {new_task.due_date}) เรียบร้อยแล้ว")

            elif choice == '3':
                # เพิ่มงานที่มีระดับความสำคัญ
                description = self.get_task_description()
                priority = self.get_priority_input()
                tags = self.get_tags_input()
                new_task = self.manager.add_priority_task(description, priority, tags=tags)
                print(f"[สำเร็จ]: เพิ่มงานความสำคัญ ID {new_task.id} (ระดับ: {new_task.priority}) เรียบร้อยแล้ว")

            elif choice == '4':
                # แสดงรายการงานทั้งหมด
                tasks = self.manager.get_all_tasks()
                if not tasks:
                    print("\n[แจ้งเตือน]: ยังไม่มีงานในระบบ")
                    continue
                print(f"\n--- รายการงานทั้งหมด ({len(tasks)} รายการ) ---")
                for task in tasks:
                    print(f"- {task}")
                print("-" * 35)

            elif choice == '5':
                # ทำเครื่องหมายเสร็จสิ้น
                try:
                    task_id = int(input("กรอก ID ของงานที่เสร็จสิ้น: ").strip())
                    success, message = self.manager.complete_task(task_id)
                    prefix = "[สำเร็จ]" if success else "[แจ้งเตือน]"
                    print(f"{prefix}: {message}")
                except ValueError:
                    print("ข้อผิดพลาด: ID ต้องเป็นตัวเลขจำนวนเต็มเท่านั้น")

            elif choice == '6':
                # ลบงาน
                try:
                    task_id = int(input("กรอก ID ของงานที่ต้องการลบ: ").strip())
                    success, message = self.manager.delete_task(task_id)
                    prefix = "[สำเร็จ]" if success else "[แจ้งเตือน]"
                    print(f"{prefix}: {message}")
                except ValueError:
                    print("ข้อผิดพลาด: ID ต้องเป็นตัวเลขจำนวนเต็มเท่านั้น")

            elif choice == '7':
                # ค้นหางาน (Search - สำหรับการบ้านนักศึกษา)
                keyword = input("กรอกคำค้นหา (Keyword): ").strip()
                if not keyword:
                    print("ข้อผิดพลาด: กรุณากรอกคำค้นหา")
                    continue
                found_tasks = self.manager.search_tasks(keyword)
                if found_tasks:
                    print(f"\n--- ผลการค้นหาสำหรับ '{keyword}' ({len(found_tasks)} รายการ) ---")
                    for task in found_tasks:
                        print(f"- {task}")
                    print("-" * 35)
                else:
                    print(f"ไม่พบงานที่ตรงกับคำค้น '{keyword}'")

            elif choice == '8':
                # กรองงาน (Filter - สำหรับการบ้านนักศึกษา)
                print("\nตัวเลือกการกรอง (สามารถเว้นว่างได้หากไม่ต้องการกรองเงื่อนไขนั้น):")
                status_in = input("กรองตามสถานะ (completed/pending/เว้นว่าง): ").strip().lower()
                status = True if status_in == "completed" else (False if status_in == "pending" else None)

                due_before = input("กรองงานครบกำหนดก่อนวันที่ (YYYY-MM-DD/เว้นว่าง): ").strip() or None
                if due_before:
                    try:
                        datetime.datetime.strptime(due_before, '%Y-%m-%d')
                    except ValueError:
                        print("รูปแบบวันที่ไม่ถูกต้อง! ไม่ใช้เงื่อนไขวันที่ในการกรองครั้งนี้")
                        due_before = None
                priority = input("กรองตามความสำคัญ (High/Medium/Low/เว้นว่าง): ").strip() or None
                tag = input("กรองตาม Tag (เว้นว่างได้): ").strip() or None

                filtered_tasks = self.manager.filter_tasks(
                    status=status,
                    due_date_before=due_before,
                    priority=priority,
                    tags=tag
                )
                if filtered_tasks:
                    print(f"\n--- ผลการกรองงาน ({len(filtered_tasks)} รายการ) ---")
                    for task in filtered_tasks:
                        print(f"- {task}")
                    print("-" * 35)
                else:
                    print("ไม่พบงานที่ตรงกับเงื่อนไขการกรอง")

            elif choice == '9':
                # จัดเรียงงาน (Sort - สำหรับการบ้านนักศึกษา)
                criterion = input("เรียงตาม (id / due_date / priority) [ค่าเริ่มต้น: id]: ").strip().lower() or "id"
                if criterion not in ("id", "due_date", "priority"):
                    print(f"ไม่รู้จักเกณฑ์ '{criterion}' — ใช้การเรียงตาม id แทน")
                    criterion = "id"
                reverse_in = input("เรียงจากมากไปน้อย (Descending? y/n) [ค่าเริ่มต้น: n]: ").strip().lower()
                reverse = (reverse_in in ['y', 'yes'])

                sorted_tasks = self.manager.sort_tasks(criterion=criterion, reverse=reverse)
                if sorted_tasks:
                    print(f"\n--- รายการงานที่จัดเรียงแล้ว (เกณฑ์: {criterion}) ---")
                    for task in sorted_tasks:
                        print(f"- {task}")
                    print("-" * 35)
                else:
                    print("ไม่มีรายการงานที่จะแสดงผล")

            elif choice == '0':
                print("\nขอบคุณที่ใช้งาน Enhanced Task Manager! ลาก่อน")
                break

            else:
                print("ตัวเลือกไม่ถูกต้อง! กรุณากรอกหมายเลขระหว่าง 0 ถึง 9")
