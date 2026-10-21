# main.py
"""
จุดเริ่มต้นการทำงานของแอปพลิเคชัน (Application Entry Point)
ทำหน้าที่ประสานงาน (Orchestrator) เชื่อมต่อโมดูล TaskManager เข้ากับ CLIInterface
แล้วเริ่มต้นการทำงานของโปรแกรม
"""

import sys
import os

# ตั้งค่าการเข้ารหัสของ Input/Output ให้รองรับ UTF-8 (ภาษาไทย) บน Windows Console
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

# เพิ่มไดเรกทอรีหลักของโปรเจกต์และโฟลเดอร์ src เข้าสู่ sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from src.task_manager import TaskManager
    from src.cli_interface import CLIInterface
except ImportError:
    from task_manager import TaskManager
    from cli_interface import CLIInterface




def main():
    """ฟังก์ชันหลักสำหรับเริ่มต้นแอปพลิเคชัน Enhanced Task Manager"""
    manager = TaskManager()
    cli = CLIInterface(manager)
    cli.run()


if __name__ == "__main__":
    main()
