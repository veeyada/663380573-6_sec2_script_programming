# src/spreadsheet_agent.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Color, Alignment
from openpyxl.chart import BarChart, LineChart, PieChart, Reference, Series
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, IconSetRule, Rule
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.utils import get_column_letter, range_boundaries, column_index_from_string
from openpyxl.worksheet.datavalidation import DataValidation
from collections import OrderedDict
import logging
import datetime
import json

from utils import setup_logging

logger = setup_logging(__name__)

class SpreadsheetAgent:
    def __init__(self, config):
        self.config = config
        self.workbook = None
        self.audit_log = []
        self.start_time = datetime.datetime.now()
        logger.info("Spreadsheet Agent initialized.")

    def _log_audit(self, status, message, task_type="N/A", details=None):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "status": status,
            "task_type": task_type,
            "message": message,
            "details": details if details else {}
        }
        self.audit_log.append(log_entry)
        if status in ["ERROR", "CRITICAL"]:
            logger.error(f"AUDIT LOG - {status}: {message} | Task: {task_type}")
        else:
            logger.info(f"AUDIT LOG - {status}: {message} | Task: {task_type}")

    def _load_workbook(self):
        input_file = self.config["input_file"]
        try:
            self.workbook = openpyxl.load_workbook(input_file)
            self._log_audit("SUCCESS", f"Workbook '{input_file}' loaded.", "load_workbook")
            return True
        except FileNotFoundError:
            self._log_audit("ERROR", f"Input file not found: {input_file}", "load_workbook")
            return False
        except Exception as e:
            self._log_audit("ERROR", f"Failed to load workbook: {e}", "load_workbook")
            return False

    def _get_sheet(self, sheet_name):
        if sheet_name in self.workbook.sheetnames:
            return self.workbook[sheet_name]
        else:
            logger.warning(f"Sheet '{sheet_name}' not found. Creating new sheet.")
            return self.workbook.create_sheet(sheet_name)

    @staticmethod
    def _last_data_row(sheet, column="A", start_row=2):
        """Last row of the contiguous block of values in `column` starting at `start_row`."""
        row = start_row
        while sheet[f"{column}{row}"].value not in (None, ""):
            row += 1
        return row - 1

    def _expand_range(self, sheet, cell_range):
        """Replace '{last_row}' in a range like 'B1:B{last_row}' with the sheet's last data row."""
        if cell_range and "{last_row}" in cell_range:
            return cell_range.replace("{last_row}", str(self._last_data_row(sheet)))
        return cell_range

    def _process_copy_data_task(self, task):
        src_sheet_name = task.get("source_sheet")
        dest_sheet_name = task.get("dest_sheet")
        if not src_sheet_name or not dest_sheet_name:
            self._log_audit("ERROR", "Missing source/dest sheet", "copy_data", task)
            return
        src_sheet = self._get_sheet(src_sheet_name)
        dest_sheet = self._get_sheet(dest_sheet_name)
        for row in src_sheet.iter_rows():
            for cell in row:
                dest_sheet[cell.coordinate].value = cell.value
        for cell in dest_sheet[1]:
            cell.font = Font(bold=True)
        for col in range(1, dest_sheet.max_column + 3):  # +2 leaves room for calculated columns
            dest_sheet.column_dimensions[get_column_letter(col)].width = 16
        self._log_audit("SUCCESS", f"Copied '{src_sheet_name}' to '{dest_sheet_name}'", "copy_data")

    def _process_calculate_column_task(self, task):
        sheet_name = task.get("sheet")
        target_col = task.get("target_column")
        start_row = task.get("start_row", 2)
        formula = task.get("formula")
        if not all([sheet_name, target_col, formula]):
            self._log_audit("ERROR", "Missing fields for calculate_column", "calculate_column", task)
            return
        sheet = self._get_sheet(sheet_name)
        header_name = task.get("header", "Calculated Column")
        sheet[f"{target_col}1"].value = header_name
        sheet[f"{target_col}1"].font = Font(bold=True)
        last_row = self._last_data_row(sheet, "A", start_row)
        for row_num in range(start_row, last_row + 1):
            cell_coord = f"{target_col}{row_num}"
            try:
                sheet[cell_coord] = formula.replace("{row}", str(row_num))
                if task.get("number_format"):
                    sheet[cell_coord].number_format = task["number_format"]
            except Exception as e:
                self._log_audit("ERROR", f"Failed formula at {cell_coord}: {e}", "calculate_column")
        self._log_audit("SUCCESS", f"Column '{target_col}' calculated in '{sheet_name}'", "calculate_column")

    def _process_conditional_format_task(self, task):
        sheet_name = task.get("sheet")
        data_range = task.get("range")
        rule_type = task.get("rule_type")
        if not all([sheet_name, data_range, rule_type]):
            self._log_audit("ERROR", "Missing fields for conditional_format", "conditional_format", task)
            return
        sheet = self._get_sheet(sheet_name)
        try:
            if rule_type == "color_scale":
                min_color = Color(task.get("min_color", "FF0000"))
                mid_color = Color(task.get("mid_color", "FFFF00"))
                max_color = Color(task.get("max_color", "00FF00"))
                rule = ColorScaleRule(start_type='min', start_color=min_color,
                                     mid_type='percentile', mid_value=50, mid_color=mid_color,
                                     end_type='max', end_color=max_color)
                sheet.conditional_formatting.add(data_range, rule)
            elif rule_type == "expression":
                formula = task.get("formula")
                fill_color = task.get("fill_color", "FFC7CE")
                font_color = task.get("font_color", "9C0006")
                dxf = DifferentialStyle(
                    font=Font(color=font_color),
                    fill=PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                )
                rule = Rule(type='expression', formula=[formula], dxf=dxf)
                sheet.conditional_formatting.add(data_range, rule)
            self._log_audit("SUCCESS", f"Applied '{rule_type}' to '{data_range}'", "conditional_format")
        except Exception as e:
            self._log_audit("ERROR", f"Failed conditional format: {e}", "conditional_format", task)

    def _process_chart_task(self, task):
        sheet_name = task.get("sheet")
        chart_type = task.get("chart_type")
        data_range = task.get("data_range")
        category_range = task.get("category_range")
        title = task.get("title", "Chart")
        top_left_cell = task.get("top_left_cell", "G2")
        if not all([sheet_name, chart_type, data_range]):
            self._log_audit("ERROR", "Missing fields for chart", "chart", task)
            return
        sheet = self._get_sheet(sheet_name)
        try:
            if chart_type == "bar":
                chart = BarChart()
            elif chart_type == "line":
                chart = LineChart()
            elif chart_type == "pie":
                chart = PieChart()
            else:
                self._log_audit("ERROR", f"Unsupported chart: {chart_type}", "chart", task)
                return
            data_range = self._expand_range(sheet, data_range)
            category_range = self._expand_range(sheet, category_range)
            min_col, min_row, max_col, max_row = range_boundaries(data_range)
            data = Reference(sheet, min_col=min_col, min_row=min_row, max_col=max_col, max_row=max_row)
            series = Series(data, title_from_data=True)
            chart.series.append(series)
            if category_range:
                mc, mr, xc, xr = range_boundaries(category_range)
                cats = Reference(sheet, min_col=mc, min_row=mr, max_col=xc, max_row=xr)
                chart.set_categories(cats)
            chart.title = title
            if chart_type != "pie":
                chart.x_axis.title = task.get("x_axis_title")
                chart.y_axis.title = task.get("y_axis_title")
                chart.legend = None  # single series: the title already says what it is
            chart.width = task.get("width", 18)
            chart.height = task.get("height", 9)
            sheet.add_chart(chart, top_left_cell)
            self._log_audit("SUCCESS", f"Chart '{title}' added", "chart")
        except Exception as e:
            self._log_audit("ERROR", f"Failed chart: {e}", "chart", task)

    def _process_summary_task(self, task):
        """
        Aggregate rows of `source_sheet` by `group_by_column` into `dest_sheet`.
        The value of each row is the product of `value_columns` (e.g. Quantity x Unit Price),
        computed in Python so the Summary (and charts built on it) never depend on Excel recalculation.
        """
        src_name, dest_name = task.get("source_sheet"), task.get("dest_sheet", "Summary")
        group_col = task.get("group_by_column", "A")
        value_cols = task.get("value_columns", [])
        if not src_name or not value_cols:
            self._log_audit("ERROR", "Missing source_sheet/value_columns for summary", "summary", task)
            return
        src = self._get_sheet(src_name)
        totals = OrderedDict()
        skipped = 0
        for row in range(2, self._last_data_row(src, group_col) + 1):
            key = src[f"{group_col}{row}"].value
            try:
                value = 1.0
                for col in value_cols:
                    value *= float(src[f"{col}{row}"].value)
            except (TypeError, ValueError):
                skipped += 1
                logger.warning(f"Summary: skipping row {row} (non-numeric value)")
                continue
            totals[key] = totals.get(key, 0.0) + value

        items = list(totals.items())
        if task.get("sort") in ("desc", "asc"):
            items.sort(key=lambda kv: kv[1], reverse=task["sort"] == "desc")

        if dest_name in self.workbook.sheetnames:
            del self.workbook[dest_name]
        dest = self.workbook.create_sheet(dest_name)
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        dest.append([task.get("group_header", "Product Name"), task.get("value_header", "Total Revenue")])
        for cell in dest[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
        for key, value in items:
            dest.append([key, round(value, 2)])
        last = len(items) + 1
        number_format = task.get("number_format", "#,##0.00")
        for row in range(2, last + 1):
            dest[f"B{row}"].number_format = number_format
        if task.get("add_totals", True) and items:
            dest[f"A{last + 2}"] = "Grand Total"
            dest[f"B{last + 2}"] = f"=SUM(B2:B{last})"
            dest[f"A{last + 3}"] = "Average"
            dest[f"B{last + 3}"] = f"=AVERAGE(B2:B{last})"
            for row in (last + 2, last + 3):
                dest[f"A{row}"].font = Font(bold=True)
                dest[f"B{row}"].font = Font(bold=True)
                dest[f"B{row}"].number_format = number_format
        dest.column_dimensions["A"].width = 22
        dest.column_dimensions["B"].width = 18
        msg = f"Summary '{dest_name}' created with {len(items)} groups"
        if skipped:
            msg += f" ({skipped} invalid rows skipped)"
        self._log_audit("SUCCESS", msg, "summary")

    def _process_data_validation_task(self, task):
        """Add a dropdown list or a whole-number/decimal rule to a range."""
        sheet = self._get_sheet(task.get("sheet"))
        cell_range = self._expand_range(sheet, task.get("range"))
        vtype = task.get("validation_type")
        try:
            if vtype == "list":
                options = ",".join(task.get("options", []))
                dv = DataValidation(type="list", formula1=f'"{options}"', allow_blank=True)
            elif vtype in ("whole", "decimal"):
                dv = DataValidation(type=vtype, operator=task.get("operator", "between"),
                                    formula1=str(task.get("min", 0)), formula2=str(task.get("max", 1000000)))
            else:
                self._log_audit("ERROR", f"Unsupported validation_type: {vtype}", "data_validation", task)
                return
            dv.error = task.get("error_message", "Invalid value")
            dv.errorTitle = "Invalid input"
            dv.prompt = task.get("prompt", "")
            dv.showErrorMessage = True
            dv.showInputMessage = bool(dv.prompt)
            sheet.add_data_validation(dv)
            dv.add(cell_range)
            if task.get("header_cell"):
                sheet[task["header_cell"]] = task.get("header", "")
                sheet[task["header_cell"]].font = Font(bold=True)
            if task.get("default_value") is not None:
                min_col, min_row, max_col, max_row = range_boundaries(cell_range)
                for r in range(min_row, max_row + 1):
                    for c in range(min_col, max_col + 1):
                        if sheet.cell(row=r, column=c).value is None:
                            sheet.cell(row=r, column=c, value=task["default_value"])
            self._log_audit("SUCCESS", f"Data validation '{vtype}' added to '{cell_range}'", "data_validation")
        except Exception as e:
            self._log_audit("ERROR", f"Failed data validation: {e}", "data_validation", task)

    def _process_protect_sheet_task(self, task):
        """Protect a sheet so its values/formulas cannot be edited by accident."""
        sheet = self._get_sheet(task.get("sheet"))
        try:
            sheet.protection.sheet = True
            if task.get("password"):
                sheet.protection.password = task["password"]
            self._log_audit("SUCCESS", f"Sheet '{sheet.title}' protected", "protect_sheet")
        except Exception as e:
            self._log_audit("ERROR", f"Failed to protect sheet: {e}", "protect_sheet", task)

    def _add_audit_log_sheet(self):
        if not self.audit_log:
            return
        audit_sheet = self.workbook.create_sheet("Audit Log", 0)
        audit_sheet.append(["Timestamp", "Status", "Task Type", "Message", "Details"])
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="333333", end_color="333333", fill_type="solid")
        for col_num in range(1, 6):
            cell = audit_sheet.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
        for entry in self.audit_log:
            audit_sheet.append([
                entry["timestamp"], entry["status"], entry["task_type"],
                entry["message"], json.dumps(entry["details"])
            ])
        for col_num in range(1, 6):
            max_length = 0
            column_letter = get_column_letter(col_num)
            for cell in audit_sheet[column_letter]:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            if max_length > 0:
                audit_sheet.column_dimensions[column_letter].width = min(max_length + 2, 80)
        logger.info("Audit log sheet created.")

    def run(self):
        if not self._load_workbook():
            self._log_audit("CRITICAL", "Agent could not start", "run")
            return
        try:
            for i, task in enumerate(self.config["tasks"]):
                task_type = task.get("type")
                logger.info(f"Executing Task {i+1}: Type='{task_type}'")
                if task_type == "copy_data":
                    self._process_copy_data_task(task)
                elif task_type == "calculate_column":
                    self._process_calculate_column_task(task)
                elif task_type == "conditional_format":
                    self._process_conditional_format_task(task)
                elif task_type == "chart":
                    self._process_chart_task(task)
                elif task_type == "summary":
                    self._process_summary_task(task)
                elif task_type == "data_validation":
                    self._process_data_validation_task(task)
                elif task_type == "protect_sheet":
                    self._process_protect_sheet_task(task)
                else:
                    self._log_audit("WARNING", f"Unsupported task: {task_type}", "task_execution")
            ok = sum(1 for e in self.audit_log if e["status"] == "SUCCESS")
            bad = sum(1 for e in self.audit_log if e["status"] in ("ERROR", "CRITICAL"))
            self._log_audit("INFO", f"Summary: {ok} step(s) succeeded, {bad} failed", "run_summary")
            output_file = self.config["output_file"]
            self._log_audit("SUCCESS", f"Workbook saved to '{output_file}'", "save_workbook")
            self._add_audit_log_sheet()
            self.workbook.save(output_file)
            logger.info(f"✅ Final workbook saved to: {output_file}")
        except Exception as e:
            self._log_audit("CRITICAL", f"Unhandled error: {e}", "run")
            logger.critical(f"Error: {e}", exc_info=True)
        finally:
            duration = (datetime.datetime.now() - self.start_time).total_seconds()
            logger.info(f"⏱️  Agent finished in {duration:.2f} seconds.")
