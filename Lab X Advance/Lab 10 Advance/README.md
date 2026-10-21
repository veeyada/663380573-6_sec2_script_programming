# Week 10 LabX ADV: Advanced Spreadsheet Automation & Agentic Workflows

Video : https://drive.google.com/file/d/1fRBgMPkE9jJM11FgxvwrTIl1-yzr4xce/view?usp=sharing

ในการส่งงานให้แนบรูปหน้า Raw Data, SalesData และ Audit Log ของไฟล์ excel มาด้วย

---

## Overview

A **config-driven Spreadsheet Agent** ("Agentic Sales Reporter"). The agent reads a plan from
`configs/example_spreadsheet_config.json`, loads `data/input_data.xlsx`, runs each task in order
(formulas, conditional formatting, data validation, summary, charts, sheet protection), writes an
**Audit Log** sheet, and saves `data/output_report.xlsx`.

| Goal from the lab sheet | How it is done |
| :-- | :-- |
| Load `input_data.xlsx` from config | `input_file` in the config |
| Copy data to a "Raw Data" sheet | task `copy_data` |
| Calculate a "Total Revenue" column | task `calculate_column` with formula `=B{row}*C{row}` |
| Highlight high/low revenue | task `conditional_format` (`color_scale`, and `expression` for "High Value") |
| Create a "Summary" sheet with aggregated data | task `summary`: revenue per product, sorted, with `=SUM` / `=AVERAGE` totals |
| Bar chart of product-wise revenue | task `chart` (`bar`) on the Summary sheet, plus a `pie` chart of revenue share |
| Audit Log sheet | created automatically as the first sheet of the output |
| Save `output_report.xlsx` | `output_file` in the config |

Extra lecture topics also covered: **data validation** (whole-number Quantity, "Review" dropdown
Approved/Pending/Rejected) and **sheet protection** (Summary sheet, password `lab10`).

## Output workbook

| Sheet | Contents |
| :-- | :-- |
| Audit Log | timestamp, status, task type and message for every step |
| SalesData | original input data |
| Raw Data | copied data + Total Revenue (formula), Status (`IF` formula), Review dropdown, colour scale, bar chart |
| Summary | revenue per product (highest first), Grand Total 5,183.93, Average 575.99, bar + pie charts, protected |

## How to run

```bash
pip install -r requirements.txt
python create_dummy_data.py   # only if data/input_data.xlsx is missing
python main.py
```
(On Windows, if `python` is not recognised use `py main.py` or the full path to `python.exe`.)

Expected end of the console output:
```text
... AUDIT LOG - INFO: Summary: 13 step(s) succeeded, 0 failed | Task: run_summary
... ✅ Final workbook saved to: .../data/output_report.xlsx
```
Open `data/output_report.xlsx` in Excel. Formula cells (Total Revenue, Status, Grand Total) are calculated when Excel opens the file.

## Task types (config schema)

| `type` | Fields |
| :-- | :-- |
| `copy_data` | `source_sheet`, `dest_sheet` |
| `calculate_column` | `sheet`, `target_column`, `header`, `formula` (use `{row}`), optional `start_row`, `number_format` |
| `conditional_format` | `sheet`, `range`, `rule_type`: `color_scale` (`min_color`, `mid_color`, `max_color`) or `expression` (`formula`, `fill_color`, `font_color`) |
| `data_validation` | `sheet`, `range`, `validation_type`: `list` (`options`) or `whole`/`decimal` (`operator`, `min`, `max`); optional `header_cell`, `header`, `default_value`, `prompt`, `error_message` |
| `summary` | `source_sheet`, `dest_sheet`, `group_by_column`, `value_columns` (multiplied per row), optional `sort` (`desc`/`asc`), `add_totals` |
| `chart` | `sheet`, `chart_type` (`bar`/`line`/`pie`), `data_range`, `category_range`, `title`, `x_axis_title`, `y_axis_title`, `top_left_cell` |
| `protect_sheet` | `sheet`, optional `password` |

Ranges may use `{last_row}` (e.g. `B1:B{last_row}`), which the agent replaces with the last row of data,
so the same config works when rows are added.

## Error handling & logging

* Each task runs in its own `try/except`; a failing task is recorded as `ERROR` in the Audit Log and the agent continues.
* Missing input file or invalid config (missing `type`, `sheet`, …) stops the run with a clear message.
* Non-numeric rows are skipped (with a warning) when building the summary.

## Integration concepts

* **CSV / SQLite / Web API:** load rows with `csv.DictReader`, `sqlite3` (`cursor.fetchall()`), or `requests.get(...).json()`, then `sheet.append(row)` for each row — the rest of the pipeline is unchanged.
* **Google Sheets:** see `src/google_sheets_utils.py` (placeholder). `gspread` uses a service-account or OAuth credential, works with ranges over the network and is rate-limited; choose it for live collaboration, and openpyxl for offline batch reports.

## Project structure

```text
├── src/
│   ├── __init__.py
│   ├── spreadsheet_agent.py     # agent: task dispatcher + task handlers + audit log
│   ├── config_parser.py         # loads/validates the config
│   ├── utils.py                 # logging helpers
│   └── google_sheets_utils.py   # placeholder for Google Sheets integration
├── configs/
│   └── example_spreadsheet_config.json
├── data/
│   ├── input_data.xlsx
│   └── output_report.xlsx
├── create_dummy_data.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```
