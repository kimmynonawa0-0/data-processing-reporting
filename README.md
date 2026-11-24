# Data Analytics Automation

A small Python project that turns source data files into clean, useful summaries, charts, and reports — automatically.

## Problem

People often receive data files and need to clean them, understand a few key trends, and share the results. This project automates those steps: it reads CSV and Excel files, cleans them, and produces summaries, charts, and reports.

## Current status

The program has two workflows, both available from the command line and a local upload screen.

The sales workflow processes sales CSV files. It validates each file, calculates revenue and unit metrics, and exports Excel and PDF reports.

The generic cleaning workflow reads any CSV or Excel file, detects the type of each column, removes duplicate rows, trims text, fills missing values, and generates charts automatically. Every cleaning action is recorded in an audit. Both workflows support files and folders, scan folders recursively, allow a custom output directory, and record each result in a processing log. Automated tests cover the reading, profiling, cleaning, charting, validation, analysis, reporting, logging, and command-line behavior.

## Development steps

The project grew one understandable feature at a time:

1. Create the project structure and sample sales data.
2. Read one CSV file and show a basic summary.
3. Check required columns and report data quality issues.
4. Calculate a few sales metrics, such as monthly sales and sales by category.
5. Export the cleaned data and summaries to an Excel workbook.
6. Create a short PDF report from the same analysis.
7. Automate processing multiple CSV files and record what happened.
8. Optionally add a simple file-upload screen after the analysis pipeline works.
9. Add a generic cleaning mode that profiles and cleans any CSV or Excel file, audits every change, and generates charts automatically.

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

To process every CSV file inside a folder, including its subfolders:

```powershell
python -m data_processing_reporting path\to\csv_folder
```

To write the reports and processing log into a different folder instead of `outputs`:

```powershell
python -m data_processing_reporting path\to\csv_folder --output-directory path\to\reports
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
Total units: 13
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

Done: 1 succeeded, 0 failed.
Processing log: outputs\processing_log.csv
```

The required columns are `order_date`, `product`, `category`, `quantity`, and `unit_price`. The validation checks for a missing header row, missing columns, an empty dataset, blank required values, exact duplicate rows, dates outside the `YYYY-MM-DD` format, quantities that are not positive whole numbers, and prices that are not nonnegative numbers.

Revenue is calculated as `quantity * unit_price`. All rows are assumed to use the same currency because the current CSV format does not include a currency column. Analysis is skipped when validation finds an issue.

The generated Excel workbook contains a `Cleaned Data` sheet with converted dates, numbers, revenue, and month values. Its `Summary` sheet contains the total revenue, total units, average order value, unique product count, date range, top products by revenue, and the category and monthly revenue totals. Generated workbooks are stored in `outputs/` and are not committed to Git.

The generated one-page PDF contains the headline KPIs (total revenue, units, rows, average order value, unique products, and order date range), a category revenue chart, a monthly revenue chart, the top five products, and the single-currency assumption. Generated PDFs are also stored in `outputs/` and kept out of Git.

Every attempted file adds one row to `outputs/processing_log.csv`. The log records the UTC processing time, source file, status, row count, validation or processing issues, and generated report paths. A failed file does not stop the remaining files in the folder. Folders are scanned recursively, including nested subfolders. After a run, the command line prints a short summary of how many files succeeded and failed.

## Generic cleaning mode

Add `--generic` to clean any CSV or Excel file instead of running the sales workflow:

```powershell
python -m data_processing_reporting data\sample_messy.csv --generic
```

Run it without a path to clean the included messy sample automatically:

Example output:

```text
Files found: 1

Processing: data\sample_messy.csv
File: data\sample_messy.csv
Columns: order_date, product, category, quantity, unit_price
Rows before cleaning: 12
Rows after cleaning: 10
Duplicate rows dropped: 2
Nulls filled:
- category: 1 filled using mode (Electronics)
- quantity: 2 filled using median (2.0)
- unit_price: 3 filled using median (10.0)
Charts generated: 6
Cleaned CSV: outputs\sample_messy_cleaned.csv
Cleaned Excel: outputs\sample_messy_cleaned.xlsx
PDF report: outputs\sample_messy_report.pdf

Done: 1 succeeded, 0 failed.
Processing log: outputs\processing_log.csv
```

The generic workflow profiles each file to detect `numeric`, `datetime`, and `categorical` columns, then:

- removes exact duplicate rows,
- trims outer spaces from text columns,
- fills missing values by column type: the median for numeric columns, the most common value for categorical columns, and the nearest date for datetime columns.

Every change is recorded in a cleaning audit, which appears in the command-line output, the Excel `Cleaning Audit` sheet, and the PDF report. Nulls that could not be filled are reported instead of silently dropped.

Charts are chosen by column type: histograms and box plots for numeric columns, a monthly line for datetime columns, top-category bars for categorical columns with few unique values, a scatter plot of the first two numeric columns, and a correlation heatmap when at least two numeric columns exist. At most six charts are generated to keep reports compact.

The workflow exports three files next to the source: `*_cleaned.csv`, `*_cleaned.xlsx`, and `*_report.pdf`.

## Upload interface

Start the local Streamlit interface:

```powershell
python -m streamlit run app.py
```

Upload one sales CSV in the `Sales Reports` tab to view its validation result, a KPI row with total revenue, total units, average order value, and unique products, the order date range, styled category and monthly revenue charts, a top products table, the revenue share per category, the cleaned data, and the report download buttons.

Upload any CSV or Excel file in the `Data Cleaner` tab to view its cleaning summary, a data quality card with the row and column counts, missing cell share, duplicate rows, and column type mix, a cleaning audit, the generated charts in a two-column grid, and download buttons for the cleaned CSV, cleaned Excel, and PDF report. The cleaned data sits in an expandable section. Reports are generated locally in `outputs/`. The upload interface does not currently process folders. Every upload, valid or not, adds one row to the same processing log used by the command line.

## Tests

Install the runtime and development dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

Run the automated tests:

```powershell
python -m pytest
```

The current version loads each file into memory and expects a readable file with a header row.

## Learning topics

Python modules and command-line entry points, CSV and file handling, data validation, pandas, column type inference, data cleaning audits, automatic chart selection, summary metrics, Excel and PDF output, logging, and basic testing will be introduced as the project grows.
