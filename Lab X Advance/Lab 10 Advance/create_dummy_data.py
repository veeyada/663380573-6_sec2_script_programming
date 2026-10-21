# create_dummy_data.py
import os
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "SalesData"

ws.append(["Product Name", "Quantity", "Unit Price"])

data = [
    ["Laptop", 2, 1200.50], ["Mouse", 5, 25.00], ["Keyboard", 3, 75.99],
    ["Monitor", 1, 300.00], ["Projector", 1, 850.00], ["Webcam", 10, 45.00],
    ["Headset", 4, 99.99], ["SSD", 2, 180.00], ["Router", 1, 70.00]
]
for row in data:
    ws.append(row)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "input_data.xlsx")
os.makedirs(os.path.dirname(out), exist_ok=True)
wb.save(out)
print("✅ สร้างไฟล์ data/input_data.xlsx สำเร็จ!")
