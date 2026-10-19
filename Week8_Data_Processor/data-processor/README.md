# Week 8: Automating with CSV and JSON Data

This project focuses on programmatic interaction with two fundamental structured plaintext data formats: CSV (Comma Separated Values) and JSON (JavaScript Object Notation). It reads, writes, and manipulates data in these files using Python's built-in `csv` and `json` modules.

## Key Concepts Demonstrated

* **CSV Reading (DictReader)**: Reading CSV files where the first row acts as a header, so each row is a dictionary.
* **CSV Writing (DictWriter)**: Writing Python lists of dictionaries back into CSV files with proper headers.
* **CSV Data Processing**: Basic aggregation (sum, average) and filtering records based on conditions.
* **JSON Reading (`json.load`)**: Parsing JSON files into Python dictionaries and lists.
* **JSON Writing (`json.dump`)**: Serializing Python objects into JSON files, pretty-printed.
* **JSON Data Manipulation**: Accessing nested data, updating existing entries, and adding new data.
* **Modular Design**: CSV and JSON logic live in separate modules (`csv_handler.py`, `json_handler.py`).
* **Robustness**: Basic error handling for file operations and data parsing.

## Setup & How to Run

1. **Clone the repository** and go to this folder:
   ```bash
   cd week8/data-processor
   ```
2. **(Optional) Create a virtual environment.** `csv` and `json` are built-in, so nothing needs to be installed:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. **Input data files** are already provided in `data/`:
   * `data/input_sales.csv`: sample sales data (first row is the header).
   * `data/input_inventory.json`: sample product inventory with nested `details`.
4. **Run the script:**
   ```bash
   python main.py
   ```
   The script will:
   * Read `data/input_sales.csv`.
   * Filter records where `Amount` >= 100 and calculate total sales and average price.
   * Write the filtered rows plus a summary row to `data/output_filtered_sales.csv`.
   * Read `data/input_inventory.json`.
   * Update stock levels for `PROD001` (to 60) and `PROD003` (to 75).
   * Add a new product (`PROD004`, Gaming Headset).
   * Write the updated inventory to `data/output_updated_inventory.json`.

## Expected Output

`data/output_filtered_sales.csv`:

```
OrderID,Product,Amount,Price,Customer
101,Laptop,1200.50,1200.50,Alice
104,Monitor,300.00,300.00,Charlie
107,Headphones,150.00,150.00,Alice
SUMMARY,Total/Avg,1902.00,237.75,Count: 3
```

Total Sales and Average Item Price are computed over all 8 sales; the count is the number of filtered rows.

## Project Structure

```
data-processor/
├── src/
│   ├── __init__.py          # Python package marker
│   ├── csv_handler.py       # Encapsulates CSV operations
│   ├── json_handler.py      # Encapsulates JSON operations
│   └── utils.py             # Logging and directory creation
├── data/
│   ├── input_sales.csv                 # Sample input CSV
│   ├── output_filtered_sales.csv       # Output: filtered CSV with summary
│   ├── input_inventory.json            # Sample input JSON
│   └── output_updated_inventory.json   # Output: updated JSON
├── main.py                  # Application entry point
├── .gitignore
└── README.md
```

## Debugging CSV and JSON Automation

* **`FileNotFoundError`**: Make sure `input_sales.csv` and `input_inventory.json` are in the `data` directory.
* **`KeyError` in CSV processing**: Header names in `input_sales.csv` must exactly match the keys used (`Amount`, `Price`). Watch for typos or extra spaces. The `fieldnames` passed to `DictWriter` must match the dictionary keys.
* **`ImportError` / `ModuleNotFoundError`**: `main.py` adds `src/` to `sys.path`, so the modules import each other with `from utils import ...`, not the relative `from .utils import ...`.
* **`json.JSONDecodeError`**: Invalid JSON syntax in `input_inventory.json` (missing commas, unquoted keys, wrong brackets). Save the file as UTF-8.
* **`ValueError: could not convert string to float`**: A numeric CSV field contains non-numeric text (for example `$`, thousands separators, or an empty string). Such rows are logged and skipped.
* **Data not updating in JSON**: Check that the `product_id` exists and that the inventory is a list of dictionaries.
* **Encoding issues**: Both reading and writing use `encoding='utf-8'`.

## Extension Ideas

* CSV to JSON / JSON to CSV converter (flattening nested JSON).
* Stronger data validation (required fields, numeric checks).
* Large-file processing (chunked reads, `pandas`, `ijson`).
* Working with JSON from web APIs.
* Using CSV/JSON as an import/export layer for SQLite.
* JSON-based application configuration.
* Automated HTML or text reports.
