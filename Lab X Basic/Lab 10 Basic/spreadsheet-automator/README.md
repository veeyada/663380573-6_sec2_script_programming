# Week10_LabX-BASIC_-Automating
Week10_LabX BASIC_ Automating
This project demonstrates how to programmatically interact with Microsoft Excel `.xlsx` files using Python's `openpyxl` library. It includes functionalities to read data from an existing spreadsheet, perform calculations, and write formatted results to a new Excel file.

## Key Concepts Demonstrated

* **`openpyxl` Library**: Core library for reading, writing, and modifying Excel `.xlsx` files.
* **Workbook & Worksheet Management**: Loading, creating, and saving Excel workbooks; accessing and creating sheets.
* **Cell Manipulation**: Reading and writing cell values by coordinates or cell names.
* **Data Processing**: Iterating through rows, performing calculations (e.g., total sales).
* **Basic Formatting**: Applying fonts, fills, borders, and number formats to cells.
* **Column Width Adjustment**: Dynamically adjusting column widths for readability.

## Setup & How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/spreadsheet-automator.git](https://github.com/YOUR_USERNAME/spreadsheet-automator.git)
    cd spreadsheet-automator
    ```
2.  **Install Dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
    pip install openpyxl
    ```
3.  **Prepare Input Data:**
    * Create a folder named `data` in the root of your project: `mkdir data`.
    * Inside the `data` folder, create an Excel file named `input_sales.xlsx`.
    * Populate `input_sales.xlsx` with sample sales data. The script expects the first sheet to have headers "Product Name", "Quantity", and "Unit Price" in cells A1, B1, C1 respectively, and data starting from row 2.

    **Example `input_sales.xlsx` content:**

    | Product Name | Quantity | Unit Price |
    | :----------- | :------- | :--------- |
    | Laptop       | 2        | 1200.50    |
    | Mouse        | 5        | 25.00      |
    | Keyboard     | 3        | 75.99      |
    | Monitor      | 1        | 300.00     |
    | Printer      | 1        | 150.00     |

4.  **Run the script:**
    ```bash
    python main.py
    ```
    The script will:
    * Load `input_sales.xlsx`.
    * Calculate total prices per item and a grand total.
    * Create `output_sales_report.xlsx` in the `data` folder with the processed data and formatting.

## Project Structure



spreadsheet-automator/
├── src/
│ ├── init.py # Python package marker
│ └── excel_processor.py # Core logic for Excel file reading/writing/processing
├── data/
│ ├── input_sales.xlsx # Sample input Excel file (create this yourself)
│ └── output_sales_report.xlsx # Generated output Excel file
├── main.py # Application entry point
├── .gitignore # Files/folders to ignore in Git
└── README.md # This project overview



## Debugging Spreadsheet Automation

* **`FileNotFoundError`**: Ensure your `input_sales.xlsx` file is correctly placed in the `data` directory and its name matches exactly.
* **`InvalidFileException` (or similar `openpyxl` error)**: This often means the Excel file is corrupted, or it's not a valid `.xlsx` file (e.g., it's an old `.xls` format, which `openpyxl` doesn't support). Ensure you are saving as `.xlsx`.
* **`IndexError` or `TypeError`**: If your script expects a number but gets text (or vice versa), or if it tries to access a row/column that doesn't exist, these errors can occur. Add `try-except` blocks around data type conversions and checks for `None` values.
* **Data Mismatches**: The script assumes a specific column order (Product Name, Quantity, Unit Price). If your input file has a different order or missing columns, the calculations will be incorrect. Adjust the `excel_processor.py` logic to match your file's structure.
* **Formatting Issues**: If formatting doesn't appear, double-check the `openpyxl.styles` syntax. Ensure you are applying styles to the correct cell objects *before* saving.

## Extension Ideas (Future Work)

* **Google Sheets Integration**: Explore the Google Sheets API (`gspread` library) to read, write, and update data in cloud-based spreadsheets. This involves setting up API credentials.
* **Automated Data Validation**: Add logic to check for missing values, out-of-range numbers, or incorrect data types in the input spreadsheet.
* **Advanced Data Analysis**: Implement more complex calculations (e.g., average sales per product, sales trends, pivot table creation via data manipulation).
* **Chart Generation**: `openpyxl` supports creating charts directly within the Excel file based on your data.
* **Conditional Formatting**: Apply rules-based formatting (e.g., highlight low stock, high sales).
* **GUI for Spreadsheet Tasks**: Create a simple graphical user interface (GUI) using `Tkinter` or `PyQt` to allow users to select input/output files and trigger processing.
* **Integration with Databases**: Read data from Excel and insert it into a database, or query a database and export results to Excel.

---


แหล่งที่มา
1. https://github.com/GideonJagen/auto-budget
2. https://github.com/KijaziAbraham/Managing-Subscription-Payment
3. https://github.com/MikeyBeez/RAGAgent
4. https://automatetheboringstuff.com/2e/chapter13/
