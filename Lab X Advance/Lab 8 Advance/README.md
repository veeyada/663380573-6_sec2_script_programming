# Week 8 LabX ADV: Agentic Data Processing (Advanced CSV & JSON Workflows)

A configuration-driven **Data Agent** that runs a multi-step data pipeline over CSV and JSON files.
The pipeline is described entirely in `configs/data_pipeline_config.json`; the agent reads it, dispatches each
task to the right handler, passes results between tasks through an internal `data_store`, and writes a JSON
audit report of everything it did.

Only the Python standard library is used (`csv`, `json`, `logging`, `collections`, `datetime`), so there is nothing to install.

## How it works

```
data_pipeline_config.json ──► ConfigParser (validate) ──► DataAgent.run()
                                                            │  for each task:
                                                            │    1. read input from data_store[input_data_key]
                                                            │    2. dispatch by "type" → CSVTasks / JSONTasks / ConversionTasks
                                                            │    3. write result to data_store[output_data_key]
                                                            │    4. append an entry to the audit log
                                                            ▼
                                             data/*.csv, data/*.json, reports/audit_report_*.json
```

| Module | Responsibility |
| :-- | :-- |
| `src/data_agent.py` | `DataAgent`: task dispatcher, `data_store` (state between tasks), audit report |
| `src/csv_tasks.py` | load / save CSV, aggregate (`sum`, `count`, `average`), filter (`>`, `<`, `>=`, `<=`, `==`, `!=`) |
| `src/json_tasks.py` | load / save JSON, update nested data (`set`, `add_to_list`, `remove_from_list`), query by dot-path |
| `src/conversion_tasks.py` | CSV → JSON (with type conversion), JSON → CSV (flattens nested keys like `details.brand`) |
| `src/config_parser.py` | loads and validates the pipeline config |
| `src/utils.py` | logging, directory helper, audit log entries |

## Task types (config schema)

| `type` | Required fields | Optional |
| :-- | :-- | :-- |
| `load_csv` / `load_json` | `file_path`, `output_data_key` | |
| `save_csv` | `file_path`, `input_data_key` | `fieldnames` (else inferred) |
| `save_json` | `file_path`, `input_data_key` | `indent` |
| `transform_csv_aggregate` | `input_data_key`, `output_data_key`, `group_by_field`, `aggregate_field` | `aggregate_type`: `sum` (default) / `count` / `average` |
| `filter_csv` | `input_data_key`, `output_data_key`, `filter_field`, `operator`, `value` | |
| `update_json_data` | `input_data_key`, `output_data_key`, `updates` (list of `{path, value, operation}`) | |
| `query_json_data` | `input_data_key`, `output_data_key`, `path` (e.g. `0.details.brand`) | |
| `csv_to_json_conversion` | `input_data_key`, `output_data_key` | |
| `json_to_csv_conversion` | `input_data_key`, `output_data_key` | `fieldnames` (dot-paths for nested keys) |

Paths in `update_json_data` / `query_json_data` use dots, with numbers for list indexes: `1.details.layout` = item 1 → `details` → `layout`. An empty path `""` with `add_to_list` appends to the root list.

## The pipeline in this repo

Prototype goals 1–9 from the lab sheet, plus extra tasks for the remaining lecture topics (filtering, average aggregation, JSON → CSV flattening):

| # | Task | Output |
| :-: | :-- | :-- |
| 1 | Load `input_sales.csv` | `raw_sales_data` (10 rows) |
| 2 | Aggregate sales by `Customer` (sum of `Amount`) | `customer_sales_summary` |
| 3 | Save aggregated CSV | `data/processed_sales_by_customer.csv` |
| 4–5 | Convert raw sales to JSON (numbers become numbers) and save | `data/sales_data.json` |
| 6 | Load `input_inventory.json` | `raw_inventory_data` |
| 7 | Update stock, layout, dpi, colour, and add product `PROD004` | `updated_inventory_data` |
| 8 | Query `0.details.brand` | `TechCorp` |
| 9 | Save updated inventory | `data/updated_inventory.json` |
| + | Filter orders with `Amount > 100` | `data/high_value_orders.csv` |
| + | Average order amount per customer | `data/average_order_by_customer.csv` |
| + | Flatten updated inventory to CSV | `data/inventory_flat.csv` |
| — | Audit report (automatic) | `reports/audit_report_<timestamp>.json` |

## How to run

```bash
cd agentic-data-processor
python main.py
```
(On Windows, if `python` is not recognised: `py main.py`, or the full path to `python.exe`.)

Expected end of the console output:
```text
... - src.data_agent - INFO - Summary: 15 task(s) succeeded, 0 failed. Data store keys: [...]
... - src.data_agent - INFO - Audit report saved to: .../reports/audit_report_YYYYMMDD_HHMMSS.json
... - __main__ - INFO - Data automation process completed.
```

Expected `data/processed_sales_by_customer.csv`:
```text
Customer,Total_Amount
Alice,1425.75
Bob,130.75
Charlie,500.0
David,90.0
Eve,15.5
```

## Error handling

* Missing input files are reported **before** the pipeline starts.
* Invalid config (missing `type`, `file_path`, `input_data_key`, …) stops with a clear message.
* A task whose input key is missing, or whose data is bad (e.g. non-numeric `Amount`), is logged as `ERROR` in the audit report and the agent continues with the next task.
* Bad rows during aggregation/filtering are skipped with a warning instead of crashing.

## Project structure

```text
agentic-data-processor/
├── src/
│   ├── __init__.py
│   ├── data_agent.py
│   ├── csv_tasks.py
│   ├── json_tasks.py
│   ├── conversion_tasks.py
│   ├── config_parser.py
│   └── utils.py
├── configs/
│   └── data_pipeline_config.json
├── data/
│   ├── input_sales.csv                 # input
│   ├── input_inventory.json            # input
│   ├── processed_sales_by_customer.csv # output
│   ├── sales_data.json                 # output
│   ├── updated_inventory.json          # output
│   ├── high_value_orders.csv           # output (extra)
│   ├── average_order_by_customer.csv   # output (extra)
│   └── inventory_flat.csv              # output (extra)
├── reports/                            # audit reports
├── main.py
├── .gitignore
└── README.md
```

## Extension ideas

* CSV join task (merge two CSVs on a common key).
* JSON schema validation with `jsonschema` before processing.
* Conditional tasks (`run_if`) so the agent can choose its next step based on earlier results.
