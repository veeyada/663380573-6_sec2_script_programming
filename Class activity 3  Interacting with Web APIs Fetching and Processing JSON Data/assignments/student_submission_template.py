"""
assignments/student_submission_template.py
=============================================================================
แม่แบบโค้ดส่งการบ้าน (Student Submission Template)
สัปดาห์ที่ 10: Interacting with Web APIs: Fetching and Processing JSON Data
=============================================================================

คำแนะนำสำหรับนักศึกษา:
1. เติมเต็มโค้ดในตำแหน่งที่มีเครื่องหมาย `# TODO` ให้สมบูรณ์ตามข้อกำหนดใน assignment_guide.md
2. ทดสอบการรันโปรแกรมให้ครบทุกเมนู
3. สามารถเปลี่ยนชื่อไฟล์เป็น `student_submission_<รหัสนักศึกษา>.py` ก่อนส่งงาน
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional
import requests

# ปรับปรุงการแสดงผลภาษาไทยและ Emoji บน Windows Console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class ExtendedAPIClient:
    """
    คลาสขยายสำหรับการทำงานกับ JSONPlaceholder API
    ประกอบด้วยฟังก์ชันพื้นฐาน และฟังก์ชันที่นักศึกษาต้องพัฒนาเพิ่มเติม
    """

    BASE_URL: str = "https://jsonplaceholder.typicode.com"

    def _make_request(self, endpoint: str, timeout: int = 10) -> Optional[Any]:
        """
        ฟังก์ชันส่วนกลางสำหรับส่งคำขอ HTTP GET พร้อม Error Handling
        """
        url = f"{self.BASE_URL}{endpoint}"
        print(f"[INFO] กำลังส่งคำขอ (GET) ไปที่: {url}")
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print(f"[ERROR] HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"[ERROR] Connection Error: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"[ERROR] Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"[ERROR] Request Error: {err}")
        except json.JSONDecodeError:
            print("[ERROR] ไม่สามารถแปลงข้อมูลที่ได้รับเป็น JSON ได้")
        return None

    # --- เมธอดพื้นฐานเดิมจากห้องเรียน ---
    def fetch_single_todo(self, todo_id: int) -> Optional[Dict[str, Any]]:
        return self._make_request(f"/todos/{todo_id}")

    def fetch_all_posts(self) -> Optional[List[Dict[str, Any]]]:
        return self._make_request("/posts")

    def fetch_user_todos(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        return self._make_request(f"/todos?userId={user_id}")

    # =========================================================================
    # 🎯 TODO: TASK 1 - ดึงข้อมูลโปรไฟล์ผู้ใช้งาน (User Profile)
    # =========================================================================
    def fetch_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูลโปรไฟล์ของผู้ใช้จาก Endpoint: /users/{user_id}
        
        คำแนะนำ:
        - เรียกใช้งาน self._make_request(...) ด้วย endpoint ที่ถูกต้อง
        - ส่งคืน Dictionary ของผู้ใช้ หรือ None หากเกิดข้อผิดพลาด
        """
        # TODO: เขียนโค้ดของนักศึกษาที่นี่
        endpoint = f"/users/{user_id}"
        return self._make_request(endpoint)

    # =========================================================================
    # 🎯 TODO: TASK 2 - ดึงคอมเมนต์ของโพสต์ (Post Comments)
    # =========================================================================
    def fetch_post_comments(self, post_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        ดึงรายการคอมเมนต์ทั้งหมดใต้โพสต์จาก Endpoint: /posts/{post_id}/comments
        
        คำแนะนำ:
        - เรียกใช้งาน self._make_request(...) ด้วย endpoint ที่ถูกต้อง
        - ส่งคืน List ของคอมเมนต์ หรือ None หากเกิดข้อผิดพลาด
        """
        # TODO: เขียนโค้ดของนักศึกษาที่นี่
        endpoint = f"/posts/{post_id}/comments"
        return self._make_request(endpoint)


# =============================================================================
# 🎯 TODO: TASK 3 - ฟังก์ชันสำหรับส่งออกข้อมูลเป็นไฟล์ JSON (Export to JSON)
# =============================================================================
def export_to_json_file(filename: str, data: Any) -> bool:
    """
    บันทึกข้อมูล data ลงในไฟล์ JSON ตามชื่อที่ระบุ

    ข้อกำหนด:
    1. ใช้ open(..., 'w', encoding='utf-8')
    2. ใช้ json.dump(...) โดยกำหนด indent=4 และ ensure_ascii=False
    3. มี try-except ดักจับข้อผิดพลาด เช่น IOError หรือ OSError
    4. คืนค่า True หากบันทึกสำเร็จ หรือ False หากเกิดข้อผิดพลาด

    :param filename: ชื่อไฟล์ที่ต้องการบันทึก เช่น 'output.json'
    :param data: ข้อมูลที่ต้องการบันทึก (Dictionary หรือ List)
    :return: True หากสำเร็จ, False หากล้มเหลว
    """
    # TODO: เขียนโค้ดของนักศึกษาที่นี่
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ บันทึกไฟล์สำเร็จเรียบร้อยแล้ว: {filename}")
        return True
    except PermissionError:
        print(f"❌ ไม่มีสิทธิ์เขียนไฟล์: {filename} (ไฟล์อาจเปิดค้างอยู่ในโปรแกรมอื่น)")
        return False
    except (IOError, OSError) as e:
        print(f"❌ เกิดข้อผิดพลาดในการเขียนไฟล์: {e}")
        return False
    except TypeError as e:
        print(f"❌ ข้อมูลไม่สามารถแปลงเป็น JSON ได้: {e}")
        return False


# =============================================================================
# ส่วนจัดการหน้าจอ CLI และการแสดงผล
# =============================================================================

def display_menu() -> None:
    """แสดงเมนูตัวเลือกทั้งหมด รวมทั้งตัวเลือกใหม่ของการบ้าน"""
    print("\n" + "=" * 55)
    print("   🚀 Extended Web API Fetcher & Exporter (Assignment)")
    print("=" * 55)
    print("  1. ดึงข้อมูลงานเดี่ยว (Fetch Single TODO)")
    print("  2. ดึงรายการโพสต์ทั้งหมด (Fetch All Posts)")
    print("  3. ดึงรายการ TODO ตาม User ID")
    print("  4. [Task 1] ดึงข้อมูลโปรไฟล์ผู้ใช้ (Fetch User Profile)")
    print("  5. [Task 2] ดึงคอมเมนต์ใต้โพสต์ (Fetch Post Comments)")
    print("  6. [Task 3] ดึงข้อมูลและบันทึกลงไฟล์ JSON (Fetch & Export)")
    print("  7. ออกจากโปรแกรม (Exit)")
    print("=" * 55)


def handle_user_profile(client: ExtendedAPIClient) -> None:
    """จัดการการแสดงผลข้อมูลโปรไฟล์ผู้ใช้ (Task 1)"""
    raw_input = input("กรุณาป้อนรหัสผู้ใช้งาน User ID (เช่น 1, 2, 5): ").strip()
    try:
        user_id = int(raw_input)
        if user_id <= 0:
            print("❌ User ID ต้องเป็นตัวเลขจำนวนเต็มบวก")
            return

        user_data = client.fetch_user_profile(user_id)
        if user_data:
            print("\n👤 --- ข้อมูลโปรไฟล์ผู้ใช้งาน ---")
            print(f"  • รหัสผู้ใช้ (ID)    : {user_data.get('id')}")
            print(f"  • ชื่อ-นามสกุล (Name) : {user_data.get('name')}")
            print(f"  • ชื่อผู้ใช้ (Username): {user_data.get('username')}")
            print(f"  • อีเมล (Email)       : {user_data.get('email')}")
            print(f"  • เบอร์โทรศัพท์ (Phone) : {user_data.get('phone')}")
            
            # การเข้าถึงข้อมูลแบบซ้อน (Nested Dictionary)
            company_name = user_data.get("company", {}).get("name", "ไม่ระบุ")
            city = user_data.get("address", {}).get("city", "ไม่ระบุ")
            print(f"  • บริษัท (Company)   : {company_name}")
            print(f"  • เมืองที่อยู่ (City)   : {city}")
            print("-" * 40)
        else:
            print(f"⚠️ ไม่พบข้อมูลโปรไฟล์สำหรับ User ID {user_id}")
    except ValueError:
        print("❌ กรุณาป้อนเฉพาะตัวเลขจำนวนเต็มเท่านั้น")


def handle_post_comments(client: ExtendedAPIClient) -> None:
    """จัดการการแสดงผลคอมเมนต์ของโพสต์ (Task 2)"""
    raw_input = input("กรุณาป้อนรหัสโพสต์ Post ID (เช่น 1, 2, 3): ").strip()
    try:
        post_id = int(raw_input)
        if post_id <= 0:
            print("❌ Post ID ต้องเป็นตัวเลขจำนวนเต็มบวก")
            return

        comments = client.fetch_post_comments(post_id)
        if comments is not None:
            if len(comments) == 0:
                print(f"ℹ️ ไม่พบคอมเมนต์สำหรับ Post ID {post_id}")
            else:
                print(f"\n💬 --- พบคอมเมนต์ทั้งหมด {len(comments)} รายการสำหรับ Post ID {post_id} ---")
                display_limit = 3
                for i, comment in enumerate(comments[:display_limit], start=1):
                    print(f"\n  [{i}] ผู้เขียน: {comment.get('name')}")
                    print(f"      อีเมล : {comment.get('email')}")
                    comment_snippet = comment.get('body', '').replace('\n', ' ')[:70]
                    print(f"      ข้อความ: {comment_snippet}...")
                
                if len(comments) > display_limit:
                    print(f"\n  ... และอีก {len(comments) - display_limit} คอมเมนต์ที่เหลือ")
                print("-" * 50)
        else:
            print(f"⚠️ เกิดข้อผิดพลาดในการดึงคอมเมนต์ของ Post ID {post_id}")
    except ValueError:
        print("❌ กรุณาป้อนเฉพาะตัวเลขจำนวนเต็มเท่านั้น")


def handle_export_workflow(client: ExtendedAPIClient) -> None:
    """จัดการกระบวนการดึงข้อมูลแล้วบันทึกลงไฟล์ JSON (Task 3)"""
    print("\n📦 เลือกประเภทข้อมูลที่ต้องการดึงและบันทึก:")
    print("  A. บันทึกข้อมูลงานเดี่ยว (Single TODO)")
    print("  B. บันทึกข้อมูลโปรไฟล์ผู้ใช้ (User Profile)")
    print("  C. บันทึกคอมเมนต์ใต้โพสต์ (Post Comments)")
    sub_choice = input("กรุณาเลือก (A/B/C): ").strip().upper()

    data_to_export = None
    default_filename = "exported_data.json"

    if sub_choice == "A":
        todo_id_str = input("ป้อน TODO ID ที่ต้องการ: ").strip()
        if todo_id_str.isdigit() and int(todo_id_str) > 0:
            data_to_export = client.fetch_single_todo(int(todo_id_str))
            default_filename = f"todo_{todo_id_str}.json"
    elif sub_choice == "B":
        user_id_str = input("ป้อน User ID ที่ต้องการ: ").strip()
        if user_id_str.isdigit() and int(user_id_str) > 0:
            data_to_export = client.fetch_user_profile(int(user_id_str))
            default_filename = f"user_{user_id_str}_profile.json"
    elif sub_choice == "C":
        post_id_str = input("ป้อน Post ID ที่ต้องการ: ").strip()
        if post_id_str.isdigit() and int(post_id_str) > 0:
            data_to_export = client.fetch_post_comments(int(post_id_str))
            default_filename = f"post_{post_id_str}_comments.json"
    else:
        print("⚠️ ตัวเลือกไม่ถูกต้อง ยกเลิกการส่งออกข้อมูล")
        return

    if data_to_export:
        filename_input = input(f"ระบุชื่อไฟล์ที่ต้องการบันทึก (กด Enter เพื่อใช้ '{default_filename}'): ").strip()
        final_filename = filename_input if filename_input else default_filename
        export_to_json_file(final_filename, data_to_export)
    else:
        print("⚠️ ไม่พบข้อมูลที่จะนำไปบันทึกลงไฟล์")


def main() -> None:
    """ฟังก์ชันหลักควบคุมการทำงานของแอปพลิเคชัน"""
    client = ExtendedAPIClient()

    while True:
        display_menu()
        choice = input("กรุณาเลือกตัวเลือก (1-7): ").strip()

        if choice == "1":
            raw_id = input("ป้อน TODO ID (เช่น 1): ").strip()
            if raw_id.isdigit() and int(raw_id) > 0:
                item = client.fetch_single_todo(int(raw_id))
                print(f"ผลลัพธ์: {item}")
            else:
                print("❌ รหัสไม่ถูกต้อง")
        elif choice == "2":
            posts = client.fetch_all_posts()
            print(f"ดึงข้อมูลโพสต์ได้ทั้งหมด: {len(posts) if posts else 0} รายการ")
        elif choice == "3":
            raw_uid = input("ป้อน User ID: ").strip()
            if raw_uid.isdigit() and int(raw_uid) > 0:
                todos = client.fetch_user_todos(int(raw_uid))
                print(f"พบ {len(todos) if todos else 0} งานสำหรับ User นี้")
            else:
                print("❌ รหัสไม่ถูกต้อง")
        elif choice == "4":
            handle_user_profile(client)
        elif choice == "5":
            handle_post_comments(client)
        elif choice == "6":
            handle_export_workflow(client)
        elif choice == "7":
            print("\n👋 ขอบคุณที่ร่วมทำการบ้านและใช้งานโปรแกรม! ปิดโปรแกรมเรียบร้อย")
            break
        else:
            print("⚠️ ตัวเลือกไม่ถูกต้อง กรุณาป้อน 1-7")


if __name__ == "__main__":
    main()
