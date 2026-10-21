"""
src/api_client.py
โมดูลสำหรับติดต่อสื่อสารกับ Web API (JSONPlaceholder)
จัดทำขึ้นสำหรับการเรียนรู้ของนักศึกษาชั้นปีที่ 2
"""

import json
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


class APIClient:
    """
    คลาส APIClient ทำหน้าที่เป็นตัวกลางในการส่ง HTTP Request ไปยัง REST API
    และแปลงผลลัพธ์จาก JSON เป็น Python Data Structure (Dictionary/List)
    พร้อมการจัดการข้อผิดพลาด (Error Handling) ที่ครอบคลุม
    """

    BASE_URL: str = "https://jsonplaceholder.typicode.com"

    def __init__(self, base_url: Optional[str] = None) -> None:
        """
        กำหนดค่าเริ่มต้นของ APIClient
        :param base_url: URL ฐานของ API (หากไม่ระบุจะใช้ค่าเริ่มต้นของ JSONPlaceholder)
        """
        if base_url:
            self.BASE_URL = base_url.rstrip("/")

    def _make_request(
        self, endpoint: str, timeout: int = 10
    ) -> Optional[Any]:
        """
        ฟังก์ชันผู้ช่วยภายใน (Internal Helper) สำหรับส่ง HTTP GET Request ไปยัง Endpoint ที่ระบุ
        
        ขั้นตอนการทำงาน:
        1. ประกอบ Full URL จาก BASE_URL และ endpoint
        2. ส่ง GET Request พร้อมกำหนด Timeout ป้องกันโปรแกรมค้าง
        3. ตรวจสอบสถานะการตอบกลับด้วย response.raise_for_status()
        4. ถอดรหัสข้อมูล JSON ด้วย response.json() และคืนค่า
        5. ดักจับและแสดงข้อผิดพลาดทางเครือข่ายและ HTTP Status ต่างๆ

        :param endpoint: พาธปลายทาง เช่น '/todos/1' หรือ '/posts'
        :param timeout: เวลาสูงสุดในการรอการตอบกลับจากเซิร์ฟเวอร์ (วินาที)
        :return: ข้อมูลที่แปลงจาก JSON (List หรือ Dict) หรือ None หากเกิดข้อผิดพลาด
        """
        url = f"{self.BASE_URL}{endpoint}"
        print(f"[INFO] กำลังส่งคำขอ (GET) ไปที่: {url}")

        try:
            # ส่งคำขอ HTTP GET
            response = requests.get(url, timeout=timeout)

            # ตรวจสอบ HTTP Status Code:
            # หาก status code เป็น 4xx (Client Error) หรือ 5xx (Server Error) จะโยน HTTPError ออกมา
            response.raise_for_status()

            # แปลง JSON string ใน response.text เป็น Python dictionary หรือ list
            return response.json()

        except requests.exceptions.HTTPError as errh:
            # เกิดเมื่อ Server ตอบกลับ Status Code ที่ผิดพลาด เช่น 404 Not Found หรือ 500 Internal Server Error
            print(f"[ERROR] HTTP Error ({response.status_code}): {errh}")
        except requests.exceptions.ConnectionError as errc:
            # เกิดปัญหาการเชื่อมต่อเครือข่าย เช่น เน็ตหลุด หรือ Domain ผิด
            print(f"[ERROR] Connection Error (ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้): {errc}")
        except requests.exceptions.Timeout as errt:
            # เซิร์ฟเวอร์ใช้เวลาตอบกลับนานเกินกว่าค่า timeout ที่กำหนด
            print(f"[ERROR] Timeout Error (หมดเวลาการเชื่อมต่อ {timeout} วินาที): {errt}")
        except requests.exceptions.RequestException as err:
            # ข้อผิดพลาดอื่นๆ ที่เกี่ยวข้องกับ requests
            print(f"[ERROR] Request Exception (เกิดข้อผิดพลาดในการส่งคำขอ): {err}")
        except json.JSONDecodeError:
            # กรณีข้อมูลที่ตอบกลับมาไม่ใช่ฟอร์แมต JSON ที่ถูกต้อง (เช่น ได้รับหน้าเว็บ HTML แสดงข้อผิดพลาด)
            preview = response.text[:100] if "response" in locals() else "N/A"
            print(f"[ERROR] JSON Decode Error (ไม่สามารถแปลงข้อมูลเป็น JSON ได้): {preview}...")

        return None

    def fetch_single_todo(self, todo_id: int) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูลงาน TODO รายการเดี่ยวตาม ID
        Endpoint: GET /todos/{todo_id}

        :param todo_id: รหัสของ TODO (จำนวนเต็มบวก)
        :return: Dictionary ข้อมูล TODO หรือ None หากไม่พบ
        """
        return self._make_request(f"/todos/{todo_id}")

    def fetch_all_posts(self) -> Optional[List[Dict[str, Any]]]:
        """
        ดึงรายการโพสต์ทั้งหมดจากระบบ
        Endpoint: GET /posts

        :return: List ของ Dictionary โพสต์ หรือ None หากเกิดข้อผิดพลาด
        """
        return self._make_request("/posts")

    def fetch_user_todos(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        ดึงรายการ TODO ทั้งหมดของผู้ใช้งานคนใดคนหนึ่งโดยใช้ Query Parameter
        Endpoint: GET /todos?userId={user_id}

        :param user_id: รหัสของผู้ใช้ (จำนวนเต็มบวก)
        :return: List ของ Dictionary งาน TODO ของผู้ใช้นั้น
        """
        return self._make_request(f"/todos?userId={user_id}")

    # ------------------------------------------------------------------
    # Assignment Task 1 & 2
    # ------------------------------------------------------------------
    def fetch_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        ดึงข้อมูลโปรไฟล์ผู้ใช้ (Task 1)
        Endpoint: GET /users/{user_id}

        :param user_id: รหัสผู้ใช้ (จำนวนเต็มบวก)
        :return: Dictionary ข้อมูลผู้ใช้ หรือ None หากไม่พบ (เช่น ID 999 -> 404)
        """
        data = self._make_request(f"/users/{user_id}")
        # บาง API ตอบ {} แทน 404 เมื่อไม่พบข้อมูล -> ถือว่าไม่พบ
        return data if data else None

    def fetch_post_comments(self, post_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        ดึงคอมเมนต์ทั้งหมดใต้โพสต์ (Task 2)
        Endpoint: GET /posts/{post_id}/comments

        :param post_id: รหัสโพสต์ (จำนวนเต็มบวก)
        :return: List ของคอมเมนต์ (อาจเป็น [] หากไม่มีคอมเมนต์) หรือ None หากเกิดข้อผิดพลาด
        """
        return self._make_request(f"/posts/{post_id}/comments")
