"""
homework_main.py
การบ้าน (Assignment) — เมนู 1-7: Task 1 User Profile, Task 2 Post Comments, Task 3 Export JSON
สัปดาห์ที่ 10: Interacting with Web APIs: Fetching and Processing JSON Data
"""

import os
import sys
from typing import Optional

# ปรับปรุงการแสดงผลภาษาไทยและ Emoji บน Windows Console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# เพิ่มโฟลเดอร์ 'src' เข้าไปใน Python Path เพื่อให้สามารถ import โมดูลได้อย่างถูกต้อง
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from api_client import APIClient
from exporter import export_to_json_file


def display_menu() -> None:
    """แสดงเมนูตัวเลือกการทำงานของโปรแกรม"""
    print("\n" + "=" * 45)
    print("   🌐 Web API Data Fetcher CLI (Week 10)")
    print("=" * 45)
    print("  1. ดึงข้อมูลงานเดี่ยว (Fetch Single TODO)")
    print("  2. ดึงรายการโพสต์ทั้งหมด (Fetch All Posts)")
    print("  3. ดึงรายการ TODO ตามรหัสผู้ใช้ (Fetch User TODOs)")
    print("  4. [ใหม่] ดึงข้อมูลโปรไฟล์ผู้ใช้ (User Profile)")
    print("  5. [ใหม่] ดึงคอมเมนต์ของโพสต์ (Post Comments)")
    print("  6. [ใหม่] ดึงข้อมูลแล้วบันทึกเป็นไฟล์ JSON (Fetch & Export)")
    print("  7. ออกจากโปรแกรม (Exit)")
    print("=" * 45)


def ask_positive_int(prompt: str) -> Optional[int]:
    """
    รับตัวเลขจำนวนเต็มบวกจากผู้ใช้ (Input Validation)
    คืนค่า int หรือ None หากป้อนไม่ถูกต้อง (ไม่ทำให้โปรแกรมแครช)
    """
    raw = input(prompt).strip()
    try:
        value = int(raw)
    except ValueError:
        print(f"❌ ข้อผิดพลาด: '{raw}' ไม่ใช่ตัวเลขที่ถูกต้อง กรุณาป้อนเฉพาะตัวเลขจำนวนเต็ม")
        return None
    if value <= 0:
        print("❌ ข้อผิดพลาด: ต้องเป็นตัวเลขจำนวนเต็มบวกที่มากกว่า 0")
        return None
    return value


def handle_user_profile(client: APIClient) -> None:
    """Task 1: แสดงข้อมูลโปรไฟล์ผู้ใช้ รวมข้อมูลซ้อน (company.name, address.city)"""
    user_id = ask_positive_int("กรุณาป้อนรหัสผู้ใช้งาน User ID (เช่น 1, 2, 5): ")
    if user_id is None:
        return
    user = client.fetch_user_profile(user_id)
    if not user:
        print(f"⚠️ ไม่พบข้อมูลโปรไฟล์สำหรับ User ID {user_id}")
        return
    print("\n👤 --- ข้อมูลโปรไฟล์ผู้ใช้งาน ---")
    print(f"  • รหัสผู้ใช้ (ID)        : {user.get('id')}")
    print(f"  • ชื่อ-นามสกุล (Name)    : {user.get('name')}")
    print(f"  • ชื่อผู้ใช้ (Username)   : {user.get('username')}")
    print(f"  • อีเมล (Email)          : {user.get('email')}")
    print(f"  • เบอร์โทรศัพท์ (Phone)  : {user.get('phone')}")
    # Nested dictionary: ใช้ .get() ซ้อน พร้อมค่า default ป้องกัน KeyError
    print(f"  • บริษัท (Company)       : {user.get('company', {}).get('name', 'ไม่ระบุ')}")
    print(f"  • เมือง (City)           : {user.get('address', {}).get('city', 'ไม่ระบุ')}")
    print("-" * 45)


def handle_post_comments(client: APIClient) -> None:
    """Task 2: แสดงจำนวนคอมเมนต์ทั้งหมด และ 5 รายการแรก"""
    post_id = ask_positive_int("กรุณาป้อนรหัสโพสต์ Post ID (เช่น 1, 2, 3): ")
    if post_id is None:
        return
    comments = client.fetch_post_comments(post_id)
    if comments is None:
        print(f"⚠️ เกิดข้อผิดพลาดในการดึงคอมเมนต์ของ Post ID {post_id}")
        return
    if not comments:
        print(f"ℹ️ ไม่พบคอมเมนต์สำหรับ Post ID {post_id}")
        return
    display_limit = 5
    print(f"\n💬 --- พบคอมเมนต์ทั้งหมด {len(comments)} รายการสำหรับ Post ID {post_id} ---")
    for i, comment in enumerate(comments[:display_limit], start=1):
        print(f"\n  [{i}] ผู้เขียน : {comment.get('name')}")
        print(f"      อีเมล   : {comment.get('email')}")
        print(f"      ข้อความ : {comment.get('body', '').replace(chr(10), ' ')[:80]}...")
    if len(comments) > display_limit:
        print(f"\n  ... และอีก {len(comments) - display_limit} คอมเมนต์")
    print("-" * 45)


def handle_export(client: APIClient) -> None:
    """Task 3: ดึงข้อมูลตามประเภทที่เลือก แล้วบันทึกเป็นไฟล์ JSON ในโฟลเดอร์ exports/"""
    print("\n📦 เลือกประเภทข้อมูลที่ต้องการดึงและบันทึก:")
    print("  A. งานเดี่ยว (Single TODO)")
    print("  B. โปรไฟล์ผู้ใช้ (User Profile)")
    print("  C. คอมเมนต์ใต้โพสต์ (Post Comments)")
    print("  D. TODO ทั้งหมดของผู้ใช้ (User TODOs)")
    sub = input("กรุณาเลือก (A/B/C/D): ").strip().upper()

    options = {
        "A": ("TODO ID", client.fetch_single_todo, "todo_{}.json"),
        "B": ("User ID", client.fetch_user_profile, "user_{}_profile.json"),
        "C": ("Post ID", client.fetch_post_comments, "post_{}_comments.json"),
        "D": ("User ID", client.fetch_user_todos, "user_{}_todos.json"),
    }
    if sub not in options:
        print("⚠️ ตัวเลือกไม่ถูกต้อง ยกเลิกการส่งออกข้อมูล")
        return
    label, fetch, name_pattern = options[sub]
    item_id = ask_positive_int(f"ป้อน {label} ที่ต้องการ: ")
    if item_id is None:
        return
    data = fetch(item_id)
    if not data:
        print("⚠️ ไม่พบข้อมูลที่จะนำไปบันทึกลงไฟล์")
        return
    default_name = name_pattern.format(item_id)
    filename = input(f"ระบุชื่อไฟล์ (กด Enter เพื่อใช้ '{default_name}'): ").strip() or default_name
    export_to_json_file(filename, data)


def handle_fetch_single_todo(client: APIClient) -> None:
    """ฟังก์ชันจัดการการดึงข้อมูล TODO รายการเดี่ยว"""
    raw_input = input("กรุณาป้อนรหัส TODO ID ที่ต้องการค้นหา (เช่น 1, 5, 10): ").strip()
    try:
        todo_id = int(raw_input)
        if todo_id <= 0:
            print("❌ ข้อผิดพลาด: รหัส TODO ID ต้องเป็นตัวเลขจำนวนเต็มบวกที่มากกว่า 0")
            return

        todo_item = client.fetch_single_todo(todo_id)
        if todo_item:
            print("\n📋 --- ข้อมูลงาน TODO รายการเดี่ยว ---")
            print(f"  • รหัสงาน (ID)       : {todo_item.get('id')}")
            print(f"  • รหัสผู้รับผิดชอบ (User ID): {todo_item.get('userId')}")
            print(f"  • หัวข้องาน (Title)  : {todo_item.get('title')}")
            status_text = "เสร็จสิ้น (Completed) ✅" if todo_item.get("completed") else "รอดำเนินการ (Pending) ⏳"
            print(f"  • สถานะงาน (Status)  : {status_text}")
            print("----------------------------------------")
        else:
            print(f"⚠️ ไม่พบข้อมูล TODO สำหรับ ID: {todo_id}")

    except ValueError:
        print(f"❌ ข้อผิดพลาด: '{raw_input}' ไม่ใช่ตัวเลขที่ถูกต้อง กรุณาป้อนเฉพาะตัวเลขจำนวนเต็ม")


def handle_fetch_all_posts(client: APIClient) -> None:
    """ฟังก์ชันจัดการการดึงและแสดงรายการโพสต์"""
    posts = client.fetch_all_posts()
    if posts:
        total_posts = len(posts)
        display_limit = 5  # แสดงเฉพาะ 5 รายการแรกเพื่อความกระชับในเทอร์มินัล
        print(f"\n📝 --- แสดง {display_limit} รายการแรก (จากทั้งหมด {total_posts} รายการ) ---")
        
        for index, post in enumerate(posts[:display_limit], start=1):
            print(f"\n[{index}] Post ID: {post.get('id')} | User ID: {post.get('userId')}")
            print(f"    หัวข้อ (Title): {post.get('title')}")
            body_snippet = post.get('body', '').replace('\n', ' ')[:60]
            print(f"    เนื้อหา (Body) : {body_snippet}...")

        if total_posts > display_limit:
            print(f"\n... และยังมีอีก {total_posts - display_limit} โพสต์ที่ไม่ได้แสดงบนหน้าจอ")
        print("-" * 45)
    else:
        print("⚠️ ไม่สามารถดึงรายการโพสต์ได้ในขณะนี้")


def handle_fetch_user_todos(client: APIClient) -> None:
    """ฟังก์ชันจัดการการดึงงาน TODO ของผู้ใช้ตามรหัสผู้ใช้"""
    raw_input = input("กรุณาป้อนรหัสผู้ใช้งาน User ID (เช่น 1, 2, 3): ").strip()
    try:
        user_id = int(raw_input)
        if user_id <= 0:
            print("❌ ข้อผิดพลาด: User ID ต้องเป็นตัวเลขจำนวนเต็มบวกที่มากกว่า 0")
            return

        user_todos = client.fetch_user_todos(user_id)
        if user_todos is not None:
            if len(user_todos) == 0:
                print(f"ℹ️ ไม่พบรายการงาน TODO ของ User ID {user_id}")
            else:
                print(f"\n📋 --- รายการงาน TODO ทั้งหมดของ User ID {user_id} (รวม {len(user_todos)} รายการ) ---")
                completed_count = 0
                for todo in user_todos:
                    is_done = todo.get("completed", False)
                    if is_done:
                        completed_count += 1
                    status_icon = "✅" if is_done else "⏳"
                    print(f"  [{todo.get('id'):03d}] {status_icon} {todo.get('title')}")

                print("-" * 45)
                print(f"สรุป: เสร็จแล้ว {completed_count}/{len(user_todos)} งาน | รอดำเนินการ {len(user_todos) - completed_count} งาน")
        else:
            print(f"⚠️ เกิดข้อผิดพลาด ไม่สามารถดึงงานของ User ID {user_id} ได้")

    except ValueError:
        print(f"❌ ข้อผิดพลาด: '{raw_input}' ไม่ใช่ตัวเลขที่ถูกต้อง กรุณาป้อนเฉพาะตัวเลขจำนวนเต็ม")


def main() -> None:
    """ฟังก์ชันหลักในการควบคุม Flow การทำงานของโปรแกรม"""
    client = APIClient()

    while True:
        display_menu()
        choice = input("กรุณาเลือกเมนู (1-7): ").strip()

        if choice == "1":
            handle_fetch_single_todo(client)
        elif choice == "2":
            handle_fetch_all_posts(client)
        elif choice == "3":
            handle_fetch_user_todos(client)
        elif choice == "4":
            handle_user_profile(client)
        elif choice == "5":
            handle_post_comments(client)
        elif choice == "6":
            handle_export(client)
        elif choice == "7":
            print("\n👋 ขอบคุณที่ใช้งานโปรแกรม ขอยุติการทำงาน!")
            break
        else:
            print("⚠️ ตัวเลือกไม่ถูกต้อง กรุณาป้อนตัวเลขระหว่าง 1 ถึง 7 เท่านั้น")


if __name__ == "__main__":
    main()
