# 🌐 สัปดาห์ที่ 10: Interacting with Web APIs: Fetching and Processing JSON Data
### เอกสารการเรียนรู้และคู่มือปฏิบัติการ สำหรับนักศึกษาชั้นปีที่ 2

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Requests](https://img.shields.io/badge/Library-Requests_2.32.3-orange.svg)](https://requests.readthedocs.io/)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Week10__Interacting__with__Web__APIs-blue?logo=github)](https://github.com/tankeiei/Week10_Interacting_with_Web_APIs)

---

## 📖 สารบัญ (Table of Contents)
1. [ภาพรวมและวัตถุประสงค์การเรียนรู้ (Overview & Learning Outcomes)](#1-ภาพรวมและวัตถุประสงค์การเรียนรู้)
2. [ทฤษฎีพื้นฐานที่ต้องรู้ (Core Concepts)](#2-ทฤษฎีพื้นฐานที่ต้องรู้)
3. [โครงสร้างของโปรเจกต์ (Project Structure)](#3-โครงสร้างของโปรเจกต์)
4. [การติดตั้งและเตรียมสภาพแวดล้อม (Setup & Installation)](#4-การติดตั้งและเตรียมสภาพแวดล้อม)
5. [วิธีการเปิดใช้งานและรันโปรแกรม (How to Run)](#5-วิธีการเปิดใช้งานและรันโปรแกรม)
6. [คู่มือการดีบักบน Visual Studio Code (VS Code Debugging)](#6-คู่มือการดีบักบน-visual-studio-code)
7. [การใช้งานบน Google Colab (Colab Workflow)](#7-การใช้งานบน-google-colab)
8. [รายละเอียดการบ้านและสิ่งที่ต้องทำส่ง (Assignment Deliverables)](#8-รายละเอียดการบ้านและสิ่งที่ต้องทำส่ง)
9. [ปัญหาที่พบบ่อยและแนวทางแก้ไข (Troubleshooting & FAQ)](#9-ปัญหาที่พบบ่อยและแนวทางแก้ไข)
10. [แหล่งข้อมูลศึกษาเพิ่มเติม (References)](#10-แหล่งข้อมูลศึกษาเพิ่มเติม)

---

## 🎯 1. ภาพรวมและวัตถุประสงค์การเรียนรู้

ในยุคของการพัฒนาซอฟต์แวร์สมัยใหม่ โปรแกรมส่วนใหญ่ไม่ได้ทำงานแบบตัดขาดจากโลกภายนอก (Standalone) แต่จะต้องมีการแลกเปลี่ยนข้อมูลกับระบบภายนอกผ่านเครือข่ายอินเทอร์เน็ต เช่น การดึงสภาพอากาศ, อัตราแลกเปลี่ยนเงิน, การยืนยันตัวตน, หรือระบบชำระเงิน บทเรียนสัปดาห์นี้จะพานักศึกษาไปเรียนรู้วิธีการเขียนภาษา Python เพื่อเชื่อมต่อกับ Web API ดึงข้อมูลฟอร์แมต JSON และประมวลผลข้อมูลอย่างถูกต้อง

### ผลลัพธ์การเรียนรู้ (Learning Outcomes):
* เข้าใจความหมายและบทบาทของ **API (Application Programming Interface)**
* รู้วิธีการติดตั้งและจัดการแพ็กเกจภายนอกด้วยคำสั่ง `pip` และการใช้ไฟล์ `requirements.txt`
* เข้าใจรูปแบบคำขอ **HTTP GET Request** และความหมายของ **HTTP Status Codes**
* สามารถแปลงข้อมูล **JSON** เป็นโครงสร้างข้อมูลในภาษา Python (Dictionary, List) และเข้าถึงข้อมูลที่ซ้อนกันได้
* สามารถเขียนโค้ดดักจับข้อผิดพลาด (**Error/Exception Handling**) เพื่อป้องกันไม่ให้โปรแกรมหยุดทำงาน (Crash)

---

## 💡 2. ทฤษฎีพื้นฐานที่ต้องรู้

### 2.1 API คืออะไร? (Analogy: เมนูและพนักงานเสิร์ฟในร้านอาหาร)
ลองจินตนาการว่าคุณไปนั่งรับประทานอาหารที่ร้าน:
* **คุณ (Client / ผู้ใช้)**: ต้องการสั่งอาหาร
* **ห้องครัว (Server / ฐานข้อมูล)**: เป็นที่ปรุงอาหารและเก็บวัตถุดิบทั้งหมด
* **พนักงานเสิร์ฟ + เล่มเมนู (API)**: คุณไม่สามารถเดินเข้าไปหยิบของในห้องครัวเองได้ คุณต้องเปิดดู "เมนู" (API Documentation / Endpoint) แล้วสั่งกับ "พนักงานเสิร์ฟ" พนักงานเสิร์ฟจะนำคำสั่งไปบอกห้องครัว และนำอาหาร (Data / Response) กลับมาเสิร์ฟให้คุณ

```
+----------------+          HTTP GET (สั่งอาหาร)          +--------------------+
|  Python Client |  ----------------------------------->  |  API Web Server    |
|   (โปรแกรมเรา)  |  <-----------------------------------  |  (JSONPlaceholder) |
+----------------+         JSON Data (ได้รับข้อมูล)        +--------------------+
```

### 2.2 HTTP Methods และ Status Codes
ในการติดต่อกับ Web API จะมีกริยา (Methods) หลักๆ ดังนี้:
* `GET`: ใช้สำหรับ **ร้องขอ / ดึงข้อมูล** (เป็นเนื้อหาหลักของสัปดาห์นี้)
* `POST`: ใช้สำหรับสร้างข้อมูลใหม่
* `PUT` / `PATCH`: ใช้สำหรับแก้ไขข้อมูล
* `DELETE`: ใช้สำหรับลบข้อมูล

#### รหัสสถานะ HTTP ที่พบบ่อย (HTTP Status Codes):
* `200 OK`: สำเร็จ คำขอถูกต้องและได้รับข้อมูล
* `400 Bad Request`: คำขอไม่ถูกต้อง เช่น รูปแบบข้อมูลผิด
* `404 Not Found`: ไม่พบหน้าที่ร้องขอ หรือไม่พบรหัส Resource ที่ระบุ
* `500 Internal Server Error`: เซิร์ฟเวอร์ปลายทางเกิดข้อผิดพลาดภายใน

### 2.3 JSON (JavaScript Object Notation) เทียบกับ Python
JSON เป็นรูปแบบข้อความมาตรฐานที่ระบบต่างๆ นิยมใช้แลกเปลี่ยนข้อมูล:

| โครงสร้างใน JSON | โครงสร้างใน Python | ตัวอย่าง |
|:---|:---|:---|
| **Object** `{ ... }` | **Dictionary** `{ ... }` | `{"name": "Somchai", "age": 20}` |
| **Array** `[ ... ]` | **List** `[ ... ]` | `[1, 2, 3, "Apple"]` |
| **string** | **str** | `"hello"` |
| **number** | **int** หรือ **float** | `100`, `3.14` |
| **boolean** (`true`, `false`) | **bool** (`True`, `False`) | `True`, `False` |
| **null** | **None** | `None` |

---

## 📁 3. โครงสร้างของโปรเจกต์

```text
Week10_ Interacting with Web APIs/
│
├── .gitignore                          # กำหนดไฟล์/โฟลเดอร์ที่ไม่ต้องอัปโหลดขึ้น Git
├── requirements.txt                    # กำหนดชื่อและเวอร์ชันของไลบรารีที่จำเป็น
├── README.md                           # คู่มือการเรียนรู้ภาษาไทยฉบับสมบูรณ์ (ไฟล์นี้)
├── main.py                             # สคริปต์หลักสำหรับรันเมนู Interactive CLI
│
├── src/                                # ซอร์สโค้ดของแพ็กเกจ
│   ├── __init__.py                     # ระบุว่าโฟลเดอร์ src เป็น Python Package
│   └── api_client.py                   # คลาส APIClient ห่อหุ้มตรรกะการเรียกใช้ Web API
│
├── assignments/                        # ส่วนสำหรับการบ้านที่นักศึกษาต้องทำส่ง
│   ├── assignment_guide.md             # โจทย์ ข้อกำหนด และเกณฑ์การให้คะแนนอย่างละเอียด
│   └── student_submission_template.py  # โค้ดแม่แบบตั้งต้น (มีจุด TODO ให้นักศึกษาเติม)
│
└── colab/                              # ส่วนสำหรับผู้ใช้งาน Google Colab
    └── Week10_Web_APIs_Colab.ipynb     # สมุดงาน Jupyter Notebook สำหรับ Colab
```

---

## ⚙️ 4. การติดตั้งและเตรียมสภาพแวดล้อม

### ขั้นตอนที่ 1: ตรวจสอบ Python บนเครื่อง
เปิด Terminal (macOS/Linux) หรือ PowerShell (Windows) แล้วพิมพ์:
```bash
python --version
```
*(ควรเป็น Python 3.8 ขึ้นไป)*

### ขั้นตอนที่ 2: โคลนหรือดาวน์โหลด Repository
```bash
git clone https://github.com/tankeiei/Week10_Interacting_with_Web_APIs.git
cd Week10_Interacting_with_Web_APIs
```

### ขั้นตอนที่ 3: สร้างและเปิดใช้งาน Virtual Environment
การใช้ Virtual Environment ช่วยป้องกันไม่ให้เวอร์ชันของไลบรารีตีกันกับโปรเจกต์อื่น:

* **บน Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(หากติดข้อผิดพลาด Execution Policy ให้รัน `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` ก่อน)*

* **บน macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### ขั้นตอนที่ 4: ติดตั้ง Library จาก `requirements.txt`
```bash
pip install -r requirements.txt
```

---

## 🚀 5. วิธีการเปิดใช้งานและรันโปรแกรม

### 5.1 รันโปรแกรมหลัก (Demo CLI)
เมื่ออยู่ในโฟลเดอร์โปรเจกต์ ให้รันคำสั่ง:
```bash
python main.py
```
จะปรากฏเมนูดังภาพ:
```text
=============================================
   🌐 Web API Data Fetcher CLI (Week 10)
=============================================
  1. ดึงข้อมูลงานเดี่ยว (Fetch Single TODO)
  2. ดึงรายการโพสต์ทั้งหมด (Fetch All Posts)
  3. ดึงรายการ TODO ตามรหัสผู้ใช้ (Fetch User TODOs)
  4. ออกจากโปรแกรม (Exit)
=============================================
กรุณาเลือกเมนู (1-4):
```

### 5.2 ทดสอบการทำงานแต่ละเมนู:
* **เมนู 1**: ป้อนรหัส TODO เช่น `1` เพื่อดูรายละเอียดงานเดี่ยว หรือทดลองป้อน `99999` เพื่อทดสอบกรณีไม่พบข้อมูล (404)
* **เมนู 2**: ดึงโพสต์บล็อกทั้งหมด (โปรแกรมจะสรุป 5 รายการแรกมาแสดง)
* **เมนู 3**: ป้อน User ID เช่น `1` หรือ `2` เพื่อดูงานทั้งหมดของผู้ใช้คนนั้น พร้อมสรุปจำนวนงานที่ทำเสร็จแล้ว

---

## 🐞 6. คู่มือการดีบักบน Visual Studio Code

การตั้ง Breakpoint และสังเกตการทำงานทีละบรรทัด (Step Over) เป็นทักษะสำคัญมากในการเข้าใจกระบวนการทำงานของ API:

### ขั้นตอนการตั้งค่าและดีบัก:
1. **เปิดโฟลเดอร์โปรเจกต์ใน VS Code**: ไปที่ `File > Open Folder...`
2. **ตั้งจุด Breakpoint (จุดสีแดง)**:
   * เปิดไฟล์ `src/api_client.py` แล้วคลิกที่หน้าเลขบรรทัดในฟังก์ชัน `_make_request` ตรงบรรทัด:
     ```python
     response = requests.get(url, timeout=timeout)
     ```
3. **เริ่มการดีบัก (Start Debugging)**:
   * เปิดไฟล์ `main.py`
   * กดปุ่ม `F5` หรือคลิกแท็บ **Run and Debug** ทางซ้ายมือ แล้วเลือก **Python File**
4. **สังเกตตัวแปรในหน้าต่าง Variables**:
   * เมื่อโปรแกรมหยุดที่ Breakpoint ให้กดปุ่ม `F10` (Step Over) 1 ครั้ง
   * สังเกตตัวแปร `response` ในแท็บตัวแปรทางซ้าย:
     * `response.status_code`: ดูว่าเป็นเลข `200` หรือไม่
     * `response.ok`: ดูว่าเป็น `True` หรือไม่
     * `response.text`: ดูข้อความดิบ (Raw String) ที่เซิร์ฟเวอร์ส่งกลับมา
     * `response.json()`: สังเกตการแปลงข้อความเป็น Python Dictionary
5. **ทดลองจำลอง Error (Error Simulation)**:
   * ลองตัดอินเทอร์เน็ต แล้วรันโปรแกรมดูว่าโค้ดวิ่งเข้าบล็อก `requests.exceptions.ConnectionError` หรือไม่
   * ลองเปลี่ยน `BASE_URL` เป็น URL ปลอม เช่น `https://this-is-fake-domain-12345.com`

---

## ☁️ 7. การใช้งานบน Google Colab

สำหรับนักศึกษาที่ไม่สะดวกติดตั้งโปรแกรมบนคอมพิวเตอร์ หรือใช้งานผ่านแท็บเล็ต:
1. เข้าไปที่โฟลเดอร์ `colab/`
2. อัปโหลดไฟล์ [Week10_Web_APIs_Colab.ipynb](file:///c:/Users/tanku/Documents/งานโฟ/Week10_%20Interacting%20with%20Web%20APIs/colab/Week10_Web_APIs_Colab.ipynb) ขึ้นบน [Google Colab](https://colab.research.google.com/)
3. สั่งรันเซลล์ตามลำดับจากบนลงล่าง โดยแต่ละเซลล์จะมีคำอธิบายและตัวอย่างพร้อมใช้งานทันที

---

## 📝 8. รายละเอียดการบ้านและสิ่งที่ต้องทำส่ง

> [!IMPORTANT]
> **นักศึกษาทุกคนจะต้องพัฒนาส่วนต่อขยายและส่งงานตามข้อกำหนดดังต่อไปนี้**
> ดูรายละเอียดและโจทย์ฉบับเต็มได้ที่เอกสาร [assignments/assignment_guide.md](file:///c:/Users/tanku/Documents/งานโฟ/Week10_%20Interacting%20with%20Web%20APIs/assignments/assignment_guide.md)

### 8.1 สรุปภารกิจ 4 Tasks:
1. **Task 1: User Profile (`fetch_user_profile(user_id)`) [25 คะแนน]**
   * ดึงข้อมูลผู้ใช้จาก `/users/{user_id}` และเข้าถึงข้อมูลแบบซ้อน เช่น ชื่อบริษัท และเมืองที่อยู่
2. **Task 2: Post Comments (`fetch_post_comments(post_id)`) [25 คะแนน]**
   * ดึงรายการคอมเมนต์ใต้โพสต์จาก `/posts/{post_id}/comments` พร้อมแสดงจำนวนคอมเมนต์ทั้งหมด
3. **Task 3: Export to JSON (`export_to_json_file(filename, data)`) [25 คะแนน]**
   * ฟังก์ชันบันทึกข้อมูลที่ดึงได้ลงเป็นไฟล์ `.json` โดยใช้ `encoding='utf-8'` และ `indent=4`
4. **Task 4: CLI Integration & Validation [25 คะแนน]**
   * เชื่อมต่อฟังก์ชันเข้ากับเมนู Interactive CLI และตรวจสอบ Input ป้องกันข้อผิดพลาดจากการกรอกข้อมูล

### 8.2 การเริ่มต้นทำการบ้าน:
เราได้เตรียมแม่แบบไฟล์ไว้ให้เรียบร้อยแล้วที่:
👉 [assignments/student_submission_template.py](file:///c:/Users/tanku/Documents/งานโฟ/Week10_%20Interacting%20with%20Web%20APIs/assignments/student_submission_template.py)

นักศึกษาสามารถเปิดไฟล์ดังกล่าว ค้นหาคอมเมนต์ `# TODO` และเขียนโค้ดเพิ่มเติมได้ทันที

### 8.3 เกณฑ์การให้คะแนน (Grading Rubric):
* **ความถูกต้องตามโจทย์ (Correctness)**: 75% (Task 1-3 ข้อละ 25%)
* **การจัดการข้อผิดพลาดและ CLI (Robustness & CLI)**: 15%
* **คุณภาพของโค้ดและการใช้งาน Git (Code Quality & Git)**: 10%

---

## ❓ 9. ปัญหาที่พบบ่อยและแนวทางแก้ไข

### 1. ภาษาไทยหรือ Emoji ไม่แสดงผลบน Windows
* **สาเหตุ**: คอนโซลของ Windows ในโหมดเริ่มต้นอาจใช้รหัสหน้าภาษา cp1252 หรือ cp874
* **วิธีแก้**: โค้ดในโปรเจกต์นี้ได้รับการเพิ่มคำสั่งตั้งค่ามาตรฐานเรียบร้อยแล้ว:
  ```python
  import sys
  if sys.platform == "win32":
      sys.stdout.reconfigure(encoding="utf-8", errors="replace")
  ```

### 2. เกิดข้อผิดพลาด `ModuleNotFoundError: No module named 'requests'`
* **สาเหตุ**: ยังไม่ได้เปิดใช้งาน Virtual Environment หรือยังไม่ได้สั่งติดตั้งไลบรารี
* **วิธีแก้**: ตรวจสอบว่ามี `(venv)` ขึ้นหน้ารหัสคำสั่งในเทอร์มินัลหรือไม่ และสั่ง `pip install -r requirements.txt` อีกครั้ง

### 3. รัน `Activate.ps1` บน Windows แล้วแจ้งเตือน Execution Policy Error
* **วิธีแก้**: เปิด PowerShell แล้วรันคำสั่ง:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

---

## 📚 10. แหล่งข้อมูลศึกษาเพิ่มเติม

1. [Requests: HTTP for Humans (Official Documentation)](https://requests.readthedocs.io/)
2. [JSONPlaceholder - Free Fake REST API](https://jsonplaceholder.typicode.com/)
3. [Python JSON Documentation](https://docs.python.org/3/library/json.html)
4. [MDN Web Docs: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)

---
*จัดทำขึ้นสำหรับการเรียนการสอนวิชาการเขียนโปรแกรมและการเชื่อมต่อ Web APIs ชั้นปีที่ 2*

---

## ✅ การบ้าน (Assignment) — ทำครบทั้ง 4 ภารกิจในโปรเจกต์หลัก

| ภารกิจ | ไฟล์ / ฟังก์ชัน | เมนู |
| :-- | :-- | :-: |
| Task 1: User Profile (`/users/{id}`) แสดง name, username, email, phone, company.name, address.city และจัดการ ID ที่ไม่มีอยู่ (เช่น 999) | `src/api_client.py` → `fetch_user_profile()` | 4 |
| Task 2: Post Comments (`/posts/{id}/comments`) แสดงจำนวนทั้งหมด + 5 รายการแรก (name, email, body) | `src/api_client.py` → `fetch_post_comments()` | 5 |
| Task 3: Export to JSON (utf-8, `indent=4`, `ensure_ascii=False`, ดักจับ `PermissionError`/`IOError`/`OSError`) บันทึกลงโฟลเดอร์ `exports/` | `src/exporter.py` → `export_to_json_file()` | 6 |
| Task 4: เมนู 1–7 และ Input Validation (ตัวอักษร, 0, ค่าติดลบ ไม่ทำให้โปรแกรมแครช) | `homework_main.py` → `ask_positive_int()` | ทั้งหมด |

ไฟล์ `assignments/student_submission_template.py` ก็เติม TODO ครบแล้วเช่นกัน (ไฟล์เดียวรันได้ด้วย `python assignments/student_submission_template.py`)

### วิธีรัน
```bash
pip install -r requirements.txt
python main.py           # กิจกรรมในห้อง: เมนู 1-4 (Single TODO, All Posts, User TODOs, Exit)
python homework_main.py  # การบ้าน: เมนู 1-7 (+ User Profile, Post Comments, Export JSON)
```

### ทดสอบอัตโนมัติ (ไม่ต้องใช้อินเทอร์เน็ต — จำลอง requests.get)
```bash
python -m unittest discover tests
```
ผลที่ควรได้: `Ran 8 tests ... OK`

### หลักฐานสำหรับส่งงาน
1. `python homework_main.py` รันเมนู 1–6 แล้วแคปหน้าจอเทอร์มินัล
2. เมนู 6 → B → 1 → Enter จะได้ไฟล์ `exports/user_1_profile.json` เปิดแล้วแคปหน้าจอ

## 👨‍💻 ผู้จัดทำ
* **ชื่อ-นามสกุล**: ศุภกร กงชา
* **รหัสนักศึกษา**: 633021103-2
* **กลุ่มเรียน**: Sec. 2
