# Data-Processing-Reporting

A small Python project for turning source data into clear, useful summaries and reports.

## Problem

People often receive data and need to check it, understand a few key trends, and share the results. This project will automate those steps, starting with a simple, known CSV format.

## Current status

The program can read one local CSV file and display its columns, row count, and first five records. Data validation and analysis will be added in later steps. Other input formats can be considered after the basic CSV workflow is clear and useful.

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
```

## Run

Use Python 3 to read the included sample CSV:

```powershell
python -m data_processing_reporting
```

You can also provide another CSV file:

```powershell
python -m data_processing_reporting path\to\your_file.csv
```

Example output:

```text
File: data\sample_sales.csv
Columns: order_date, product, category, quantity, unit_price
Number of rows: 5

Preview:
2026-01-05 | Notebook | Stationery | 3 | 4.50
2026-01-08 | Pen Set | Stationery | 2 | 6.00
```

The current version loads the whole CSV into memory and expects a readable file with a header row. More detailed validation will be added in the next development step.

## Learning topics

Python modules and command-line entry points, CSV and file handling, data validation, pandas, summary metrics, Excel and PDF output, logging, and basic testing will be introduced as the project grows.
