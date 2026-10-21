"""
src/exporter.py
ฟังก์ชันบันทึกข้อมูลที่ดึงจาก API ลงไฟล์ JSON (Assignment Task 3)
"""

import json
import os
from typing import Any

# โฟลเดอร์ปลายทางเริ่มต้น: my-api-fetcher/exports/
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")


def export_to_json_file(filename: str, data: Any) -> bool:
    """
    บันทึก data ลงไฟล์ JSON (utf-8, indent=4, ensure_ascii=False)

    - ถ้า filename ไม่มีโฟลเดอร์ จะบันทึกไว้ใน exports/
    - เติมนามสกุล .json ให้อัตโนมัติถ้าไม่มี

    :param filename: ชื่อไฟล์ เช่น 'user_1_profile.json'
    :param data: Dictionary หรือ List ที่ต้องการบันทึก
    :return: True หากบันทึกสำเร็จ, False หากล้มเหลว
    """
    if not filename.lower().endswith(".json"):
        filename += ".json"
    path = filename if os.path.dirname(filename) else os.path.join(EXPORT_DIR, filename)

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ บันทึกไฟล์สำเร็จ: {path}")
        return True
    except PermissionError:
        print(f"❌ ไม่มีสิทธิ์เขียนไฟล์: {path} (ไฟล์อาจเปิดค้างอยู่ในโปรแกรมอื่น)")
    except (IOError, OSError) as e:
        print(f"❌ เกิดข้อผิดพลาดในการเขียนไฟล์ '{path}': {e}")
    except TypeError as e:
        print(f"❌ ข้อมูลไม่สามารถแปลงเป็น JSON ได้: {e}")
    return False
