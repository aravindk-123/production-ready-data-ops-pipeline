"""
Data Processing Pipeline Automation

Usage:
    python automation.py
    python automation.py --raw_data_dir input --clean_data_dir processed
    python automation.py --start_date 2024-01-01 --end_date 2024-12-31
"""

import argparse
import sys
import logging
from pathlib import Path

import data_cleaning
import data_analysis


def setup_logging():
    """Configure simple logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="End-to-end data operations pipeline")

    parser.add_argument("--raw_data_dir", default="data_raw", help="Directory with raw CSV files")
    parser.add_argument("--clean_data_dir", default="data_clean", help="Directory for cleaned data")
    parser.add_argument("--reports_dir", default="reports", help="Directory for reports")
    parser.add_argument("--plots_dir", default="plots", help="Directory for plots")
    parser.add_argument("--start_date", help="Filter from date (YYYY-MM-DD)")
    parser.add_argument("--end_date", help="Filter to date (YYYY-MM-DD)")

    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging()

    # Create directories
    Path(args.raw_data_dir).mkdir(exist_ok=True)
    Path(args.clean_data_dir).mkdir(exist_ok=True)
    Path(args.reports_dir).mkdir(exist_ok=True)
    Path(args.plots_dir).mkdir(exist_ok=True)

    try:
        # Task 1: Data Cleaning
        logging.info("Running Task-1: Data Cleaning & Validation")
        data_cleaning.main(raw_dir=args.raw_data_dir, clean_dir=args.clean_data_dir, start_date=args.start_date, end_date=args.end_date)
        logging.info("Task-1 completed successfully\n")

        # Task 2: Data Analysis
        logging.info("Running Task-2: Data Analysis & Reporting")
        data_analysis.main(clean_dir=args.clean_data_dir, reports_dir=args.reports_dir, plots_dir=args.plots_dir, start_date=args.start_date, end_date=args.end_date)
        logging.info("Task-2 completed successfully\n")

        logging.info("Pipeline execution completed")

    except Exception as e:
        logging.error(f"✗ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
