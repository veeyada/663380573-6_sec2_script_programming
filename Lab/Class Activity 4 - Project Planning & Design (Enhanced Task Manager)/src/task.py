# src/task.py
"""
โมดูล task.py: Data Models สำหรับจัดการงานในระบบ Task Manager
ประกอบด้วยคลาสพื้นฐาน Task และคลาสลูก DueDateTask และ PriorityTask
ตามหลักการ Object-Oriented Programming (Inheritance & Polymorphism)
"""

import datetime


class Task:
    """
    คลาสพื้นฐาน (Base Class) สำหรับงานทุกประเภทในระบบ Task Manager
    รองรับการกำหนด id, รายละเอียด (description), สถานะ (completed), และป้ายกำกับ (tags)
    """
    def __init__(self, id, description, completed=False, tags=None):
        self.id = id
        self.description = description
        self.completed = completed
        # กำหนด tags เป็นลิสต์ว่างหากไม่ได้ระบุ
        self.tags = list(tags) if tags is not None else []

    def mark_complete(self):
        """กำหนดสถานะงานเป็นเสร็จสมบูรณ์ (Completed)"""
        self.completed = True

    def add_tag(self, tag):
        """เพิ่ม tag ให้กับงาน (หลีกเลี่ยง tag ซ้ำ)"""
        cleaned_tag = tag.strip()
        if cleaned_tag and cleaned_tag not in self.tags:
            self.tags.append(cleaned_tag)

    def remove_tag(self, tag):
        """ลบ tag ออกจากงาน"""
        cleaned_tag = tag.strip()
        if cleaned_tag in self.tags:
            self.tags.remove(cleaned_tag)

    def to_dict(self):
        """
        แปลง Object ให้อยู่ในรูป Dictionary สำหรับการจัดเก็บแบบ JSON Serialization
        ระบุฟิลด์ '_type' เพื่อช่วยในการ Deserialize กลับมาเป็น Object
        """
        return {
            "id": self.id,
            "description": self.description,
            "completed": self.completed,
            "tags": self.tags,
            "_type": "Task"
        }

    def __str__(self):
        """แสดงผลข้อมูลงานในรูปแบบข้อความที่อ่านง่ายสำหรับผู้ใช้"""
        status = "Completed" if self.completed else "Pending"
        tags_str = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        return f"ID: {self.id} | Description: {self.description} | Status: {status}{tags_str}"

    def __repr__(self):
        return f"Task(id={self.id}, description='{self.description}', completed={self.completed}, tags={self.tags})"


class DueDateTask(Task):
    """
    คลาสงานที่มีวันกำหนดส่ง (Due Date) สืบทอดคุณสมบัติมาจากคลาส Task
    จัดเก็บวันกำหนดส่งในรูปแบบ datetime.date
    """
    def __init__(self, id, description, due_date, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        if isinstance(due_date, str):
            self.due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
        elif isinstance(due_date, datetime.date):
            self.due_date = due_date
        else:
            raise TypeError("due_date must be a string in YYYY-MM-DD format or a datetime.date object")

    def to_dict(self):
        """
        Override เมธอด to_dict เพื่อเพิ่มฟิลด์ due_date ในรูปแบบ 'YYYY-MM-DD'
        และระบุ '_type' เป็น 'DueDateTask'
        """
        base_dict = super().to_dict()
        base_dict["due_date"] = self.due_date.strftime('%Y-%m-%d')
        base_dict["_type"] = "DueDateTask"
        return base_dict

    def __str__(self):
        """Override เมธอด __str__ เพื่อแสดงผลวันกำหนดส่ง (Due Date)"""
        base_str = super().__str__()
        base_str_without_tags = base_str.split(' | Tags:')[0] if ' | Tags:' in base_str else base_str
        tags_part = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        return f"{base_str_without_tags} | Due: {self.due_date.strftime('%Y-%m-%d')}{tags_part}"

    def __repr__(self):
        return f"DueDateTask(id={self.id}, description='{self.description}', due_date='{self.due_date.strftime('%Y-%m-%d')}', completed={self.completed}, tags={self.tags})"


class PriorityTask(Task):
    """
    คลาสงานที่มีการระบุระดับความสำคัญ (Priority Level) สืบทอดคุณสมบัติมาจากคลาส Task
    ระดับความสำคัญ เช่น High, Medium, Low
    """
    def __init__(self, id, description, priority, completed=False, tags=None):
        super().__init__(id, description, completed, tags)
        self.priority = priority.capitalize() if isinstance(priority, str) else str(priority)

    def to_dict(self):
        """
        Override เมธอด to_dict เพื่อเพิ่มฟิลด์ priority
        และระบุ '_type' เป็น 'PriorityTask'
        """
        base_dict = super().to_dict()
        base_dict["priority"] = self.priority
        base_dict["_type"] = "PriorityTask"
        return base_dict

    def __str__(self):
        """Override เมธอด __str__ เพื่อแสดงระดับความสำคัญ (Priority)"""
        base_str = super().__str__()
        base_str_without_tags = base_str.split(' | Tags:')[0] if ' | Tags:' in base_str else base_str
        tags_part = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        return f"{base_str_without_tags} | Priority: {self.priority}{tags_part}"

    def __repr__(self):
        return f"PriorityTask(id={self.id}, description='{self.description}', priority='{self.priority}', completed={self.completed}, tags={self.tags})"
