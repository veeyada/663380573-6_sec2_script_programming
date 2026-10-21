"""Creates the two sample attachments: data/reports/sales_report.pdf and data/reports/summary_data.xlsx."""
import os

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "data", "reports")
os.makedirs(OUT, exist_ok=True)

ROWS = [("Laptop", 2, 1200.50), ("Monitor", 3, 300.00), ("Projector", 1, 850.00),
        ("Webcam", 10, 45.00), ("Headset", 4, 99.99)]

pdf_path = os.path.join(OUT, "sales_report.pdf")
c = canvas.Canvas(pdf_path, pagesize=A4)
c.setFont("Helvetica-Bold", 18)
c.drawString(72, 780, "Daily Sales Report")
c.setFont("Helvetica", 12)
y = 740
for name, qty, price in ROWS:
    c.drawString(72, y, f"{name:<12} qty {qty:>3}   unit {price:>8.2f}   total {qty * price:>9.2f}")
    y -= 20
c.drawString(72, y - 10, f"Grand total: {sum(q * p for _, q, p in ROWS):,.2f}")
c.save()

wb = Workbook()
ws = wb.active
ws.title = "Summary"
ws.append(["Product", "Quantity", "Unit Price", "Total"])
for name, qty, price in ROWS:
    ws.append([name, qty, price, round(qty * price, 2)])
xlsx_path = os.path.join(OUT, "summary_data.xlsx")
wb.save(xlsx_path)
print(f"Created {pdf_path}\nCreated {xlsx_path}")
