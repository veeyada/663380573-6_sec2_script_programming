"""
main.py
โปรแกรมหลัก Interactive CLI สำหรับทดสอบการเชื่อมต่อ Web API
สัปดาห์ที่ 10: Interacting with Web APIs: Fetching and Processing JSON Data
"""

import os
import sys

# แสดงผลภาษาไทยบน Windows Console ได้ถูกต้อง
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# เพิ่มโฟลเดอร์ 'src' เข้าไปใน Python Path เพื่อให้ import โมดูลได้
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from api_client import APIClient  # noqa: E402


def display_menu() -> None:
    """แสดงเมนูตัวเลือกการทำงานของโปรแกรม"""
    print("\n" + "=" * 45)
    print("   API Data Fetcher - JSONPlaceholder")
    print("=" * 45)
    print("  1. ดึงรายการ TODO ตามรหัส (Fetch a Single TODO)")
    print("  2. ดึงรายการโพสต์ทั้งหมด (Fetch All Posts)")
    print("  3. ดึงรายการ TODO ตามรหัสผู้ใช้ (Fetch User TODOs)")
    print("  4. ออกจากโปรแกรม (Exit)")
    print("=" * 45)


def ask_positive_int(prompt: str):
    """รับตัวเลขจำนวนเต็มบวก คืนค่า int หรือ None หากป้อนไม่ถูกต้อง"""
    raw = input(prompt).strip()
    try:
        value = int(raw)
    except ValueError:
        print(f"[ERROR] '{raw}' ไม่ใช่ตัวเลขที่ถูกต้อง กรุณาป้อนเฉพาะตัวเลขจำนวนเต็ม")
        return None
    if value <= 0:
        print("[ERROR] ต้องเป็นตัวเลขจำนวนเต็มบวกที่มากกว่า 0")
        return None
    return value


def handle_fetch_single_todo(client: APIClient) -> None:
    """ดึงและแสดงข้อมูล TODO รายการเดี่ยว"""
    todo_id = ask_positive_int("กรอกรหัส TODO (เช่น 1, 5, 10): ")
    if todo_id is None:
        return
    todo = client.fetch_single_todo(todo_id)
    if todo:
        status = "เสร็จแล้ว (Completed)" if todo.get("completed") else "ยังไม่เสร็จ (Pending)"
        print("\n--- รายละเอียด TODO ---")
        print(f"  รหัสงาน (ID)    : {todo.get('id')}")
        print(f"  รหัสผู้ใช้ (User ID): {todo.get('userId')}")
        print(f"  หัวข้อ (Title)   : {todo.get('title')}")
        print(f"  สถานะ (Status)  : {status}")
        print("-" * 45)
    else:
        print(f"ไม่พบข้อมูล TODO สำหรับรหัส {todo_id}")


def handle_fetch_all_posts(client: APIClient) -> None:
    """ดึงโพสต์ทั้งหมด แสดง 5 รายการแรก"""
    posts = client.fetch_all_posts()
    if not posts:
        print("ไม่สามารถดึงรายการโพสต์ได้ในขณะนี้")
        return
    total = len(posts)
    limit = 5
    print(f"\n--- แสดง {limit} รายการแรก (จากทั้งหมด {total} รายการ) ---")
    for index, post in enumerate(posts[:limit], start=1):
        print(f"\n[{index}] Post ID: {post.get('id')} | User ID: {post.get('userId')}")
        print(f"    หัวข้อ (Title): {post.get('title')}")
        body = post.get("body", "").replace("\n", " ")[:50]
        print(f"    เนื้อหา (Body) : {body}...")
    if total > limit:
        print(f"\n... และยังมีอีก {total - limit} โพสต์ที่ไม่ได้แสดงบนหน้าจอ")
    print("-" * 45)


def handle_fetch_user_todos(client: APIClient) -> None:
    """ดึงรายการ TODO ทั้งหมดของผู้ใช้"""
    user_id = ask_positive_int("กรอกรหัสผู้ใช้ (เช่น 1, 2, 3): ")
    if user_id is None:
        return
    todos = client.fetch_user_todos(user_id)
    if todos is None:
        print(f"เกิดข้อผิดพลาด ไม่สามารถดึงงานของ User ID {user_id} ได้")
        return
    if not todos:
        print(f"ไม่พบรายการ TODO ของ User ID {user_id}")
        return
    done = sum(1 for t in todos if t.get("completed"))
    print(f"\n--- รายการ TODO ของ User ID {user_id} (ทั้งหมด {len(todos)} รายการ) ---")
    for todo in todos:
        mark = "[x]" if todo.get("completed") else "[ ]"
        print(f"  {mark} {todo.get('id'):>3}. {todo.get('title')}")
    print("-" * 45)
    print(f"สรุป: เสร็จแล้ว {done}/{len(todos)} รายการ | ค้างอยู่ {len(todos) - done} รายการ")


def main() -> None:
    """ฟังก์ชันหลักควบคุมการทำงานของโปรแกรม"""
    client = APIClient()
    while True:
        display_menu()
        choice = input("กรุณาเลือกเมนู (1-4): ").strip()
        if choice == "1":
            handle_fetch_single_todo(client)
        elif choice == "2":
            handle_fetch_all_posts(client)
        elif choice == "3":
            handle_fetch_user_todos(client)
        elif choice == "4":
            print("\nขอบคุณที่ใช้งานโปรแกรม ลาก่อน!")
            break
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาป้อนตัวเลข 1 ถึง 4")


if __name__ == "__main__":
    main()
