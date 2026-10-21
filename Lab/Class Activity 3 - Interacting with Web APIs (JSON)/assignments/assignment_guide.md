# 📘 คู่มือการส่งการบ้าน (Assignment Guide)
## สัปดาห์ที่ 10: Interacting with Web APIs: Fetching and Processing JSON Data
### สำหรับ: นักศึกษาชั้นปีที่ 2 สาขาวิชาวิทยาการคอมพิวเตอร์ / เทคโนโลยีสารสนเทศ

---

## 🎯 1. วัตถุประสงค์ของการบ้าน (Objectives)
1. สามารถเขียนโค้ดภาษา Python เพื่อเชื่อมต่อกับ REST API ภายนอกด้วยไลบรารี `requests` ได้อย่างถูกต้อง
2. สามารถจัดการข้อผิดพลาด (Exception Handling) ที่เกิดจาก Network หรือ HTTP Status Code ได้อย่างมีประสิทธิภาพ
3. สามารถนำข้อมูลที่ได้รับในรูปแบบ JSON มาแกะ (Parse) โครงสร้างข้อมูลแบบ Dictionary ซ้อนกัน (Nested Dictionary/List) และนำมาแสดงผลหรือประมวลผลต่อได้
4. สามารถจัดเก็บข้อมูลที่ดึงมาจาก API ลงในไฟล์ถาวร (JSON File Export) บนเครื่องคอมพิวเตอร์ได้
5. ฝึกฝนการออกแบบโครงสร้างโปรแกรมแบบโมดูลาร์ (Modular Code) และการสร้าง Interactive CLI

---

## 📋 2. รายละเอียดภารกิจที่ต้องทำ (Tasks Specification)

ให้นักศึกษาพัฒนาต่อยอดจากโค้ดตัวอย่างในโปรเจกต์ หรือนำไฟล์ `assignments/student_submission_template.py` ไปเติมเต็มโค้ดในจุดที่มีเครื่องหมาย `# TODO` ให้สมบูรณ์ โดยมีทั้งหมด 4 ภารกิจย่อยดังนี้:

---

### 🔹 ภารกิจที่ 1: ดึงข้อมูลโปรไฟล์ผู้ใช้งาน (Task 1: Fetch User Profile)
- **คะแนนเต็ม**: 25 คะแนน
- **สิ่งที่ต้องทำ**:
  - เพิ่ม Method ในคลาส `ExtendedAPIClient` ชื่อ:
    ```python
    def fetch_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
    ```
  - ทำการส่งคำขอแบบ HTTP GET ไปยัง Endpoint:
    `https://jsonplaceholder.typicode.com/users/{user_id}`
  - จัดการกรณีที่ผู้ใช้ป้อน ID ที่ไม่มีอยู่จริง (เช่น ID 999) ให้คืนค่า `None` หรือแสดงข้อความแจ้งเตือนที่เข้าใจง่าย ไม่ให้โปรแกรมแครช (Crash)
  - นำข้อมูลที่ได้มาแสดงผลในรูปแบบที่อ่านง่าย โดยต้องดึงฟิลด์ต่อไปนี้ออกมาแสดงอย่างน้อย:
    - **ชื่อ-นามสกุล** (`name`)
    - **ชื่อผู้ใช้** (`username`)
    - **อีเมล** (`email`)
    - **เบอร์โทรศัพท์** (`phone`)
    - **ชื่อบริษัท** (`company` -> `name`)
    - **ที่อยู่ (เมือง)** (`address` -> `city`)

---

### 🔹 ภารกิจที่ 2: ดึงรายการคอมเมนต์ใต้โพสต์ (Task 2: Fetch Post Comments)
- **คะแนนเต็ม**: 25 คะแนน
- **สิ่งที่ต้องทำ**:
  - เพิ่ม Method ในคลาส `ExtendedAPIClient` ชื่อ:
    ```python
    def fetch_post_comments(self, post_id: int) -> Optional[List[Dict[str, Any]]]:
    ```
  - ทำการส่งคำขอแบบ HTTP GET ไปยัง Endpoint:
    `https://jsonplaceholder.typicode.com/posts/{post_id}/comments`
  - นำรายการคอมเมนต์ที่ได้มาแสดงผล โดยแสดง:
    - จำนวนคอมเมนต์ทั้งหมดที่พบ
    - รายการคอมเมนต์ (แสดงอย่างน้อย 3-5 รายการแรก): ชื่อผู้คอมเมนต์ (`name`), อีเมล (`email`), และข้อความคอมเมนต์ (`body`)

---

### 🔹 ภารกิจที่ 3: ฟังก์ชันบันทึกข้อมูลเป็นไฟล์ JSON (Task 3: Export Data to JSON)
- **คะแนนเต็ม**: 25 คะแนน
- **สิ่งที่ต้องทำ**:
  - สร้างฟังก์ชันสำหรับ Export ข้อมูลที่ดึงได้ลงเป็นไฟล์ `.json` เช่น:
    ```python
    def export_to_json_file(filename: str, data: Any) -> bool:
    ```
  - ตรวจสอบให้แน่ใจว่าไฟล์ที่บันทึกใช้การเข้ารหัส `utf-8` และฟอร์แมต JSON ที่สวยงามอ่านง่าย (`indent=4`, `ensure_ascii=False`)
  - ใส่ `try-except` สำหรับดักจับกรณีเกิดข้อผิดพลาดในการเขียนไฟล์ (เช่น `IOError`, `PermissionError`)

---

### 🔹 ภารกิจที่ 4: อัปเดตเมนู Interactive CLI และการตรวจสอบข้อมูล (Task 4: Interactive CLI Integration)
- **คะแนนเต็ม**: 25 คะแนน
- **สิ่งที่ต้องทำ**:
  - เพิ่มตัวเลือกในฟังก์ชันแสดงเมนู CLI ดังนี้:
    1. ดึงข้อมูลงานเดี่ยว (Single TODO)
    2. ดึงรายการโพสต์ทั้งหมด (All Posts)
    3. ดึงรายการ TODO ตาม User ID
    4. **[ใหม่]** ดึงข้อมูลโปรไฟล์ผู้ใช้ (User Profile)
    5. **[ใหม่]** ดึงคอมเมนต์ของโพสต์ (Post Comments)
    6. **[ใหม่]** ดึงข้อมูลแล้วบันทึกเป็นไฟล์ JSON (Fetch & Export to JSON)
    7. ออกจากโปรแกรม (Exit)
  - มีการตรวจสอบความถูกต้องของข้อมูลที่ผู้ใช้ป้อน (Input Validation) เสมอ เช่น ตรวจสอบว่าเป็นตัวเลขจำนวนเต็มบวก ป้องกันโปรแกรมหยุดทำงานเมื่อผู้ใช้พิมพ์ตัวอักษรแทนตัวเลข

---

## 📊 3. เกณฑ์การให้คะแนน (Grading Rubric - รวม 100 คะแนน)

| ลำดับ | รายการประเมิน | คะแนนเต็ม | เกณฑ์การพิจารณา |
|:---:|:---|:---:|:---|
| 1 | **Task 1: User Profile** | 25 | ดึงข้อมูลได้ถูกต้องตาม endpoint, เข้าถึงข้อมูล nested dictionary ได้ครบถ้วน, ดักจับกรณีไม่พบ ID ได้อย่างถูกต้อง |
| 2 | **Task 2: Post Comments** | 25 | ดึงข้อมูลคอมเมนต์สำเร็จ, วนลูปแสดงผลสวยงาม, ระบุจำนวนคอมเมนต์ทั้งหมด |
| 3 | **Task 3: Export to JSON** | 25 | บันทึกไฟล์สำเร็จ, รองรับภาษาไทย (`ensure_ascii=False`, `utf-8`), จัดการ exception ได้ดี |
| 4 | **Task 4: CLI & Validation** | 15 | เมนูใช้งานได้จริง, มีการป้องกันข้อผิดพลาดจากการป้อนข้อมูลของผู้ใช้ (Input Validation) ไม่ให้เกิด Unhandled Exception |
| 5 | **Code Quality & Git** | 10 | เขียนโค้ดสะอาด มีการตั้งชื่อตัวแปรที่สื่อความหมาย มี Comment/Docstring และมี Commit Message ที่ชัดเจน |

---

## 📦 4. สิ่งที่ต้องส่ง (Deliverables)

1. **Source Code**:
   - ไฟล์โค้ดที่ทำเสร็จสมบูรณ์ (เช่น `student_submission.py` หรือโฟลเดอร์โปรเจกต์ที่อัปเดตแล้ว)
2. **ภาพหลักฐานการทดสอบ (Screenshots/Log)**:
   - ภาพการทดสอบรันโปรแกรมในเทอร์มินัล แสดงการทำงานของแต่ละฟังก์ชัน (ข้อ 1-6)
   - ภาพไฟล์ JSON ที่ถูกบันทึกออกมาจริง
3. **Repository Link**:
   - ลิงก์ GitHub Repository ของตนเอง (ตั้งค่าเป็น Public หรือแชร์สิทธิ์ให้ผู้สอน)
   - มีข้อความ Commit History แสดงความคืบหน้าของการเขียนโค้ดอย่างน้อย 3 Commits

---

## 💡 5. เคล็ดลับและข้อแนะนำ (Tips & Troubleshooting)

> [!TIP]
> **การเข้าถึง Nested Dictionary ใน Python**:
> หากข้อมูล JSON มีลักษณะดังนี้:
> ```json
> {
>   "name": "Leanne Graham",
>   "company": {
>     "name": "Romaguera-Crona"
>   }
> }
> ```
> การเข้าถึงชื่อบริษัทใน Python ให้ใช้คำสั่ง:
> ```python
> company_name = user_data.get("company", {}).get("name", "ไม่ระบุ")
> ```
> การใช้ `.get()` ซ้อนกันพร้อมใส่ default value เป็น `{}` จะช่วยป้องกันข้อผิดพลาด `AttributeError` หรือ `KeyError` ในกรณีที่คีย์ดังกล่าวไม่มีอยู่จริง!

> [!WARNING]
> **ปัญหาภาษาไทยบน Windows**:
> หากรันบน Windows Terminal แล้วพบปัญหาตัวอักษรหรือ Emoji ไม่แสดงผล ให้เพิ่มคำสั่งนี้ไว้บนสุดของโปรแกรม:
> ```python
> import sys
> if sys.platform == "win32":
>     sys.stdout.reconfigure(encoding="utf-8", errors="replace")
> ```
