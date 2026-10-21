# src/data_persistence.py
"""
โมดูล data_persistence.py: จัดการการบันทึกและโหลดข้อมูลงานจากไฟล์ JSON (Data Layer)
รวมศูนย์การทำงานกับ File I/O และการแปลงข้อมูล (Serialization/Deserialization)
เพื่อสนับสนุนหลักการ Separation of Concerns
"""

import json
import os
try:
    from .task import Task, DueDateTask, PriorityTask
except ImportError:
    from task import Task, DueDateTask, PriorityTask



class DataPersistence:
    """
    คลาสสำหรับจัดการการจัดเก็บข้อมูลงาน (Data Persistence)
    ทำหน้าที่โหลดและบันทึก Task objects ลงในไฟล์ JSON
    """
    def __init__(self, data_file='data/tasks.json'):
        self.data_file = data_file
        # กำหนด Path ให้สัมพันธ์กับตำแหน่งของโปรเจกต์ (ย้อนขึ้น 1 ระดับจากโฟลเดอร์ src/)
        self._data_file_path = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', self.data_file)
        )

    def get_file_path(self):
        """ส่งคืนที่อยู่เต็ม (Absolute Path) ของไฟล์ข้อมูล"""
        return self._data_file_path

    def load_tasks(self):
        """
        โหลดรายการงานจากไฟล์ JSON และแปลงกลับเป็นอ็อบเจกต์ของ Task หรือคลาสลูก
        ตามค่าที่ระบุในฟิลด์ '_type'
        """
        if not os.path.exists(self._data_file_path):
            dir_path = os.path.dirname(self._data_file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            return []

        try:
            with open(self._data_file_path, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)
                loaded_tasks = []
                for t_dict in raw_tasks:
                    # ดึง _type ออกมาเพื่อกำหนดคลาสในการ Instantiate
                    task_type = t_dict.pop('_type', 'Task')
                    # ให้แน่ใจว่าฟิลด์ tags มีค่าเป็นลิสต์
                    t_dict.setdefault('tags', [])

                    if task_type == "Task":
                        loaded_tasks.append(Task(**t_dict))
                    elif task_type == "DueDateTask":
                        loaded_tasks.append(DueDateTask(**t_dict))
                    elif task_type == "PriorityTask":
                        loaded_tasks.append(PriorityTask(**t_dict))
                    else:
                        print(f"Warning: ไม่รู้จัก task type '{task_type}' (Task ID: {t_dict.get('id', 'N/A')}) ข้ามรายการนี้")
                return loaded_tasks
        except json.JSONDecodeError:
            print("Warning: ไฟล์ tasks.json ว่างเปล่าหรือรูปแบบไม่ถูกต้อง กำลังเริ่มด้วยรายการงานว่าง")
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดงาน: {e} กำลังเริ่มด้วยรายการงานว่าง")
            return []

    def save_tasks(self, tasks):
        """
        บันทึกรายการ Task objects ทั้งหมดลงในไฟล์ JSON
        โดยเรียกใช้เมธอด to_dict() ของแต่ละ Task ตามหลัก Polymorphism
        """
        tasks_as_dicts = [task.to_dict() for task in tasks]
        dir_path = os.path.dirname(self._data_file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(self._data_file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks_as_dicts, f, indent=4, ensure_ascii=False)
