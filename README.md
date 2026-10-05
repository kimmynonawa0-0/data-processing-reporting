# Data-Processing-Reporting

A small Python project for turning source data into clear, useful summaries and reports.

## Problem

People often receive data and need to check it, understand a few key trends, and share the results. This project will automate those steps, starting with a simple, known CSV format.

## Current status

The program can process sales CSV files through a command-line workflow or a local upload screen. It validates each file, calculates revenue metrics, and exports Excel and PDF reports. The command-line workflow also supports folders and records each result in a processing log. Automated tests cover the main validation and calculation rules.

## Planned development

Each step will add one understandable feature:

1. Create the project structure and sample sales data.
2. Read one CSV file and show a basic summary.
3. Check required columns and report data quality issues.
4. Calculate a few sales metrics, such as monthly sales and sales by category.
5. Export the cleaned data and summaries to an Excel workbook.
6. Create a short PDF report from the same analysis.
7. Automate processing multiple CSV files and record what happened.
8. Optionally add a simple file-upload screen after the analysis pipeline works.

The first version will run locally and use sample sales data. It will not need a database or cloud service.

## Project structure

```text
data_processing_reporting/  Python application
data/                       Small sample input data
outputs/                    Generated reports (kept out of Git)
app.py                      Local file-upload interface
tests/                      Automated tests
```

## Run

Install the project dependency:

```powershell
python -m pip install -r requirements.txt
```

Use Python 3 to analyze the included sample CSV:

```powershell
python -m data_processing_reporting
```

You can also provide another CSV file:

```powershell
python -m data_processing_reporting path\to\your_file.csv
```

To process every CSV file directly inside a folder:

```powershell
python -m data_processing_reporting path\to\csv_folder
```

Example output:

```text
CSV files found: 1

Processing: data\sample_sales.csv
File: data\sample_sales.csv
Columns: order_date, product, category, quantity, unit_price
Number of rows: 5

Validation:
Passed: all required fields contain valid values.

Sales analysis:
Total revenue: 110.49
Revenue by category:
- Electronics: 62.49
- Stationery: 48.00
Revenue by month:
- 2026-01: 50.49
- 2026-02: 60.00
Excel report: outputs\sample_sales_report.xlsx
PDF report: outputs\sample_sales_report.pdf

Preview:
2026-01-05 | Notebook | Stationery | 3 | 4.50
2026-01-08 | Pen Set | Stationery | 2 | 6.00

Processing log: outputs\processing_log.csv
```

The required columns are `order_date`, `product`, `category`, `quantity`, and `unit_price`. The validation checks for missing columns, an empty dataset, blank required values, exact duplicate rows, dates outside the `YYYY-MM-DD` format, quantities that are not positive whole numbers, and prices that are not nonnegative numbers.

Revenue is calculated as `quantity * unit_price`. All rows are assumed to use the same currency because the current CSV format does not include a currency column. Analysis is skipped when validation finds an issue.

The generated Excel workbook contains a `Cleaned Data` sheet with converted dates, numbers, revenue, and month values. Its `Summary` sheet contains the overall, category, and monthly revenue totals. Generated workbooks are stored in `outputs/` and are not committed to Git.

The generated one-page PDF contains total revenue, a category revenue chart, a monthly revenue chart, and the single-currency assumption. Generated PDFs are also stored in `outputs/` and kept out of Git.

Every attempted file adds one row to `outputs/processing_log.csv`. The log records the UTC processing time, source file, status, row count, validation or processing issues, and generated report paths. A failed file does not stop the remaining files in the folder. Folder processing is currently nonrecursive.

## Upload interface

Start the local Streamlit interface:

```powershell
python -m streamlit run app.py
```

Upload one CSV to view its validation result, total revenue, grouped charts, cleaned data, and report download buttons. Reports are generated locally in `outputs/`. The upload interface does not currently process folders or add entries to the command-line processing log.

## Tests

Install the runtime and development dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

Run the validation and analysis tests:

```powershell
python -m pytest
```

The current version loads the whole CSV into memory and expects a readable file with a header row.

## Learning topics

Python modules and command-line entry points, CSV and file handling, data validation, pandas, summary metrics, Excel and PDF output, logging, and basic testing will be introduced as the project grows.
