# DATA PROCESSING AND ANALYSIS PIPELINE

## Overview

This project provides an automated pipeline for cleaning, analyzing, and reporting on e-commerce transaction data. It processes customer, product, and transaction datasets to generate insights on revenue trends, product performance, customer behavior, and key business metrics.

## Project Structure

```
data_raw/           - Raw CSV files (customers.csv, products.csv, transactions.csv)
data_clean/         - Cleaned CSV files after processing
reports/            - Generated CSV reports with analysis results
plots/              - Visualization charts saved as PNG files
data_cleaning.py    - Data cleaning and validation module
data_analysis.py    - Data analysis and reporting module
process_data.py     - Main automation pipeline script
requirements.txt    - Python package dependencies
README.md           - This file
```

## Installation

1. Ensure Python 3.7 or higher is installed on your system

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the required directory structure:
   - Create a `data_raw` folder
   - Place your raw CSV files in the data_raw folder:
     - `customers.csv`
     - `products.csv`
     - `transactions.csv`

## Usage

**Basic usage** (uses default directories):
```bash
python process_data.py
```

**Custom directories:**
```bash
python process_data.py --raw_data_dir input --clean_data_dir processed
```

**Filter by date range:**
```bash
python process_data.py --start_date 2024-01-01 --end_date 2024-12-31
```

**Run individual modules:**
```bash
python data_cleaning.py    # Run only data cleaning
python data_analysis.py    # Run only analysis (requires cleaned data)
```

## Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--raw_data_dir` | Directory containing raw CSV files | `data_raw` |
| `--clean_data_dir` | Directory for cleaned data output | `data_clean` |
| `--reports_dir` | Directory for report CSV files | `reports` |
| `--plots_dir` | Directory for plot PNG files | `plots` |
| `--start_date` | Filter transactions from date (YYYY-MM-DD) | None |
| `--end_date` | Filter transactions to date (YYYY-MM-DD) | None |

## Data Cleaning Features

- Comprehensive data profiling with null and unique value counts
- Date standardization (removes irregularities, converts to YYYY-MM-DD)
- Country name standardization (handles variations like US/USA/United States)
- Missing value imputation:
  - Transaction prices: filled with median price per product
  - Transaction status: filled with 'Unknown' (flag added)
  - Customer email: filled with 'unknown' (flag added)
- Duplicate removal in products dataset
- Creates flags for tracking imputed values

## Analysis Outputs

The pipeline generates the following reports (CSV files in `reports` folder):

1. `monthly_trends.csv` - Monthly revenue, cost, profit, and growth metrics
2. `product_metrics.csv` - Performance metrics by product
3. `category_metrics.csv` - Performance metrics by category
4. `monthly_aov.csv` - Average order value trends over time
5. `customer_behavior.csv` - Individual customer purchase patterns
6. `top_10_customers.csv` - Top 10 customers by revenue
7. `segment_summary.csv` - Customer segmentation by revenue
8. `active_customers_summary.csv` - Active customers across time windows
9. `repeat_customer_summary.csv` - Repeat purchase rates
10. `customer_country_summary.csv` - Customer distribution by country

## Visualizations

The following charts are generated (PNG files in `plots` folder):

1. `monthly_financial_trends.png` - Revenue, cost, profit, and growth trends
2. `product_performance_analysis.png` - Top 10 products by profit percentage
3. `category_performance_analysis.png` - Category-wise financial performance
4. `monthly_aov.png` - Average order value trend over time
5. `active_customers_summary.png` - Active customers across time periods
6. `Repeat Customers Summary.png` - Repeat customer rate trends
7. `customer_demographics.png` - Customer distribution by country

## Key Metrics Calculated

- Total Revenue, Cost, and Profit
- Profit Percentage
- Revenue Growth Rate
- Average Order Value (AOV)
- Customer Lifetime Value
- Customer Segmentation (Low/Medium/High value)
- Active Customer Counts
- Repeat Customer Rates
- Category and Product Performance

## Expected Input Data Format

**customers.csv:**
- `customer_id`, `name`, `email`, `signup_date`, `country`

**products.csv:**
- `product_id`, `product_name`, `category`, `cost_price`

**transactions.csv:**
- `transaction_id`, `customer_id`, `product_id`, `transaction_date`, `quantity`, `price`, `status`

## Troubleshooting

- If you get "file not found" errors, ensure raw CSV files are in `data_raw/`
- If plots don't generate, check that matplotlib backend is configured correctly
- For date parsing issues, verify dates are in recognizable formats
- Missing value warnings are normal and handled by imputation logic

## Notes

- The pipeline automatically creates output directories if they don't exist
- All monetary calculations assume consistent currency across datasets
- Date filters (if used) apply only to transaction dates
- Cleaned data preserves all original records with imputation flags