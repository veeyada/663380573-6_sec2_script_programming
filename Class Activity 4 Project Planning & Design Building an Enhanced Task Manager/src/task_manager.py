# src/task_manager.py
"""
โมดูล task_manager.py: Business Logic Layer ของระบบ Enhanced Task Manager
ทำหน้าที่จัดการ collection ของ Task objects, ควบคุมการทำงาน CRUD,
และเป็นพื้นที่ให้นักศึกษาพัฒนาตรรกะสำหรับการค้นหา (Search), การกรอง (Filter), และการจัดเรียง (Sort)
"""

import datetime
try:
    from .task import Task, DueDateTask, PriorityTask
    from .data_persistence import DataPersistence
except ImportError:
    from task import Task, DueDateTask, PriorityTask
    from data_persistence import DataPersistence



class TaskManager:
    """
    คลาสจัดการงาน (Task Manager)
    มุ่งเน้นที่ Business Logic ล้วนๆ ไม่มีการเข้าถึงไฟล์ I/O หรือ CLI Input/Output โดยตรง
    ตามหลักการ Separation of Concerns
    """
    def __init__(self, data_file='data/tasks.json'):
        self.persistence = DataPersistence(data_file)
        self.tasks = self.persistence.load_tasks()
        self.next_id = self._get_next_task_id()

    def _get_next_task_id(self):
        """คำนวณหา ID ลำดับถัดไปที่ไม่ซ้ำกันสำหรับงานใหม่"""
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def _save_changes(self):
        """บันทึกข้อมูลการเปลี่ยนแปลงไปยัง Data Persistence Layer"""
        self.persistence.save_tasks(self.tasks)

    # =========================================================================
    # การดำเนินการ CRUD พื้นฐาน (พร้อมใช้งาน)
    # =========================================================================

    def add_normal_task(self, description, tags=None):
        """เพิ่มงานทั่วไป (Normal Task)"""
        new_task = Task(self.next_id, description, tags=tags)
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_changes()
        return new_task

    def add_due_date_task(self, description, due_date_str, tags=None):
        """เพิ่มงานที่มีวันครบกำหนด (Due Date Task)"""
        new_task = DueDateTask(self.next_id, description, due_date_str, tags=tags)
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_changes()
        return new_task

    def add_priority_task(self, description, priority, tags=None):
        """เพิ่มงานที่มีระดับความสำคัญ (Priority Task)"""
        new_task = PriorityTask(self.next_id, description, priority, tags=tags)
        self.tasks.append(new_task)
        self.next_id += 1
        self._save_changes()
        return new_task

    def get_task_by_id(self, task_id):
        """ค้นหางานตาม ID"""
        return next((task for task in self.tasks if task.id == task_id), None)

    def complete_task(self, task_id):
        """ทำเครื่องหมายว่างานเสร็จสมบูรณ์แล้ว"""
        task = self.get_task_by_id(task_id)
        if task:
            if not task.completed:
                task.mark_complete()
                self._save_changes()
                return True, f"งาน ID {task_id} ถูกเปลี่ยนสถานะเป็น 'เสร็จสมบูรณ์ (Completed)' แล้ว"
            else:
                return False, f"งาน ID {task_id} มีสถานะเสร็จสมบูรณ์อยู่แล้ว"
        return False, f"ไม่พบงาน ID {task_id} ในระบบ"

    def delete_task(self, task_id):
        """ลบงานออกจากระบบตาม ID"""
        original_len = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.id != task_id]
        if len(self.tasks) < original_len:
            self._save_changes()
            return True, f"ลบงาน ID {task_id} เรียบร้อยแล้ว"
        return False, f"ไม่พบงาน ID {task_id} ในระบบ"

    def get_all_tasks(self):
        """ส่งคืนรายการงานทั้งหมด"""
        return list(self.tasks)

    # =========================================================================
    # ฟังก์ชันค้นหา / กรอง / จัดเรียง (Assignment — Implemented)
    # =========================================================================

    PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}

    def search_tasks(self, keyword):
        """
        ค้นหางานตามคำสำคัญ (keyword) แบบไม่สนตัวพิมพ์เล็ก/ใหญ่
        ตรงเมื่อ keyword อยู่ใน description หรืออยู่ใน tag ตัวใดตัวหนึ่ง

        :param keyword: คำค้น (str)
        :return: list ของ Task ที่ตรงเงื่อนไข (ว่างหาก keyword ว่าง)
        """
        keyword_lower = (keyword or "").strip().lower()
        if not keyword_lower:
            return []
        return [
            task for task in self.tasks
            if keyword_lower in task.description.lower()
            or any(keyword_lower in tag.lower() for tag in task.tags)
        ]

    def filter_tasks(self, status=None, due_date_before=None, priority=None, tags=None):
        """
        กรองงานตามเงื่อนไขที่กำหนด (ทุกเงื่อนไขที่ระบุต้องเป็นจริงพร้อมกัน — AND)

        :param status: True = เสร็จแล้ว, False = ยังไม่เสร็จ, None = ไม่กรอง
        :param due_date_before: str 'YYYY-MM-DD' หรือ datetime.date — เฉพาะ DueDateTask ที่ due_date <= วันที่นี้
        :param priority: 'High' / 'Medium' / 'Low' — เฉพาะ PriorityTask ระดับนั้น
        :param tags: str (คั่นด้วยจุลภาคได้) หรือ list — งานต้องมีทุก tag ที่ระบุ
        :return: list ของ Task ที่ผ่านทุกเงื่อนไข
        :raises ValueError: หาก due_date_before เป็นสตริงที่ไม่ใช่รูปแบบ YYYY-MM-DD
        """
        filtered = list(self.tasks)

        if status is not None:
            filtered = [t for t in filtered if t.completed == status]

        if due_date_before:
            if isinstance(due_date_before, str):
                due_date_before = datetime.datetime.strptime(due_date_before.strip(), "%Y-%m-%d").date()
            filtered = [t for t in filtered
                        if isinstance(t, DueDateTask) and t.due_date <= due_date_before]

        if priority:
            filtered = [t for t in filtered
                        if isinstance(t, PriorityTask) and t.priority.lower() == priority.strip().lower()]

        if tags:
            wanted = [x.strip().lower() for x in (tags.split(",") if isinstance(tags, str) else tags) if x.strip()]
            filtered = [t for t in filtered
                        if all(w in [tag.lower() for tag in t.tags] for w in wanted)]

        return filtered

    def sort_tasks(self, criterion="id", reverse=False):
        """
        จัดเรียงงาน (ไม่เปลี่ยนลำดับใน self.tasks — คืนลิสต์ใหม่)

        :param criterion: "id", "due_date" หรือ "priority" (ค่าอื่นจะใช้ "id")
        :param reverse: True = จากมากไปน้อย
        :return: list ของ Task ที่จัดเรียงแล้ว
        - due_date: งานที่ไม่มีวันครบกำหนดอยู่ท้ายสุดเสมอ
        - priority: High → Medium → Low, งานที่ไม่มี priority อยู่ท้ายสุดเสมอ
        """
        if criterion == "due_date":
            with_value = [t for t in self.tasks if isinstance(t, DueDateTask)]
            without = [t for t in self.tasks if not isinstance(t, DueDateTask)]
            with_value.sort(key=lambda t: (t.due_date, t.id), reverse=reverse)
            return with_value + sorted(without, key=lambda t: t.id)

        if criterion == "priority":
            with_value = [t for t in self.tasks if isinstance(t, PriorityTask)]
            without = [t for t in self.tasks if not isinstance(t, PriorityTask)]
            with_value.sort(key=lambda t: (self.PRIORITY_ORDER.get(t.priority, 99), t.id), reverse=reverse)
            return with_value + sorted(without, key=lambda t: t.id)

        return sorted(self.tasks, key=lambda t: t.id, reverse=reverse)
