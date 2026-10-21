# src/google_sheets_utils.py
"""
Placeholder for future Google Sheets integration (conceptual, not used by main.py).

Local Excel (openpyxl)  vs  Google Sheets (gspread)
- openpyxl edits a .xlsx file on disk; gspread calls the Google Sheets API over the network.
- gspread needs credentials: a Service Account JSON key (for scripts/servers) or OAuth (acting as a user).
- API calls are rate-limited, so prefer range updates (ws.update("A1:C10", rows)) over cell-by-cell writes.
- Use Google Sheets when several people must see/edit live data; use local Excel for offline batch reports.

Example (requires `pip install gspread` and a service-account key shared on the target sheet):

    import gspread
    gc = gspread.service_account(filename="credentials.json")   # never commit this file
    ws = gc.open("Sales Report").worksheet("Summary")
    ws.update("A1", [["Product Name", "Total Revenue"], *rows])
"""


def upload_rows_to_google_sheet(spreadsheet_name, worksheet_name, rows, credentials_file="credentials.json"):
    """Write a 2D list to a Google Sheet. Not called by the prototype."""
    try:
        import gspread  # optional dependency
    except ImportError as e:
        raise ImportError("gspread is not installed. Run: pip install gspread") from e
    gc = gspread.service_account(filename=credentials_file)
    worksheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
    worksheet.clear()
    worksheet.update("A1", rows)
    return True
