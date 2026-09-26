"""
Data Preprocessing Pipeline for RetailRec India.
Cleans raw Orders.csv and Details.csv, integrates them on Order ID,
derives time and customer attributes, and generates a preprocessing report.
"""
import os
import sys
import json
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

from app.core.config import (
    RAW_ORDERS_FILE,
    RAW_DETAILS_FILE,
    PROCESSED_ORDERS_FILE,
    PROCESSED_DETAILS_FILE,
    PROCESSED_SALES_FILE,
    PREPROCESSING_REPORT_FILE,
    PROCESSED_DATA_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def clean_text_column(series: pd.Series) -> pd.Series:
    """Strips leading/trailing whitespace and standardizes text."""
    return series.astype(str).str.strip()


def run_preprocessing() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes the full preprocessing pipeline on the raw dataset.
    Returns the integrated cleaned DataFrame and the preprocessing report.
    """
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    if not os.path.exists(RAW_ORDERS_FILE) or not os.path.exists(RAW_DETAILS_FILE):
        raise FileNotFoundError(
            f"Raw dataset files not found. Ensure {RAW_ORDERS_FILE} and {RAW_DETAILS_FILE} exist."
        )

    logger.info("Loading raw Orders.csv and Details.csv...")
    raw_orders = pd.read_csv(RAW_ORDERS_FILE)
    raw_details = pd.read_csv(RAW_DETAILS_FILE)

    raw_orders_rows = len(raw_orders)
    raw_details_rows = len(raw_details)
    raw_missing_orders = int(raw_orders.isna().sum().sum())
    raw_missing_details = int(raw_details.isna().sum().sum())
    raw_duplicates_orders = int(raw_orders.duplicated().sum())
    raw_duplicates_details = int(raw_details.duplicated().sum())

    # Standardize column names
    orders = raw_orders.copy()
    orders.columns = [col.strip().lower().replace(" ", "_") for col in orders.columns]
    
    details = raw_details.copy()
    details.columns = [col.strip().lower().replace(" ", "_").replace("-", "_") for col in details.columns]

    # Clean text columns
    orders["order_id"] = clean_text_column(orders["order_id"])
    orders["customer_name"] = clean_text_column(orders["customername"] if "customername" in orders.columns else orders["customer_name"])
    if "customername" in orders.columns and "customer_name" not in orders.columns:
        orders = orders.rename(columns={"customername": "customer_name"})
    orders["state"] = clean_text_column(orders["state"])
    orders["city"] = clean_text_column(orders["city"])

    details["order_id"] = clean_text_column(details["order_id"])
    details["category"] = clean_text_column(details["category"])
    details["sub_category"] = clean_text_column(details["sub_category"])
    if "paymentmode" in details.columns:
        details["payment_mode"] = clean_text_column(details["paymentmode"])
        details = details.drop(columns=["paymentmode"])
    else:
        details["payment_mode"] = clean_text_column(details["payment_mode"])

    # Convert numeric fields
    details["amount"] = pd.to_numeric(details["amount"], errors="coerce").fillna(0.0)
    details["profit"] = pd.to_numeric(details["profit"], errors="coerce").fillna(0.0)
    details["quantity"] = pd.to_numeric(details["quantity"], errors="coerce").fillna(1).astype(int)

    # Validate amount >= 0 and quantity > 0
    valid_details_mask = (details["amount"] >= 0) & (details["quantity"] > 0)
    invalid_details_count = int((~valid_details_mask).sum())
    details = details[valid_details_mask].copy()

    # Convert dates (format: DD-MM-YYYY)
    orders["order_date"] = pd.to_datetime(orders["order_date"], format="%d-%m-%Y", errors="coerce")
    invalid_dates_count = int(orders["order_date"].isna().sum())
    orders = orders.dropna(subset=["order_date"]).copy()

    # Create deterministic customer ID mapping (CUST-001 ... CUST-336)
    unique_customer_names = sorted(orders["customer_name"].unique())
    customer_id_map = {name: f"CUST-{idx+1:03d}" for idx, name in enumerate(unique_customer_names)}
    orders["customer_id"] = orders["customer_name"].map(customer_id_map)

    # Merge Orders and Details on order_id
    merged = pd.merge(details, orders, on="order_id", how="inner")
    
    # Derived fields
    merged["transaction_value"] = merged["amount"]
    merged["unit_price"] = (merged["amount"] / merged["quantity"]).round(2)
    merged["order_year"] = merged["order_date"].dt.year
    merged["order_month"] = merged["order_date"].dt.month
    merged["order_quarter"] = merged["order_date"].dt.quarter
    merged["order_month_year"] = merged["order_date"].dt.strftime("%Y-%m")
    merged["item_id"] = merged["sub_category"]  # Sub-category is the authentic item identifier

    # Sort chronologically by order_date
    merged = merged.sort_values(by=["order_date", "order_id"]).reset_index(drop=True)

    # Calculate summary metrics for report
    total_sales = float(merged["amount"].sum())
    total_quantity = int(merged["quantity"].sum())
    total_profit = float(merged["profit"].sum())
    unique_customers = int(merged["customer_id"].nunique())
    unique_orders = int(merged["order_id"].nunique())
    unique_categories = int(merged["category"].nunique())
    unique_subcategories = int(merged["sub_category"].nunique())
    cleaned_rows = len(merged)

    # Generate preprocessing report
    report = {
        "dataset_name": "Madhav E-Commerce Sales Dataset",
        "raw_orders_row_count": raw_orders_rows,
        "raw_details_row_count": raw_details_rows,
        "raw_missing_values_orders": raw_missing_orders,
        "raw_missing_values_details": raw_missing_details,
        "raw_duplicates_orders": raw_duplicates_orders,
        "raw_duplicates_details": raw_duplicates_details,
        "cleaned_row_count": cleaned_rows,
        "missing_values_after_cleaning": int(merged.isna().sum().sum()),
        "invalid_details_removed": invalid_details_count,
        "invalid_dates_removed": invalid_dates_count,
        "number_of_customers": unique_customers,
        "number_of_orders": unique_orders,
        "number_of_categories": unique_categories,
        "number_of_subcategories": unique_subcategories,
        "total_sales_inr": round(total_sales, 2),
        "total_quantity": total_quantity,
        "total_profit_inr": round(total_profit, 2),
        "min_order_date": merged["order_date"].min().strftime("%Y-%m-%d"),
        "max_order_date": merged["order_date"].max().strftime("%Y-%m-%d"),
    }

    # Save processed files
    logger.info(f"Saving cleaned orders to {PROCESSED_ORDERS_FILE}...")
    orders.to_csv(PROCESSED_ORDERS_FILE, index=False)

    logger.info(f"Saving cleaned details to {PROCESSED_DETAILS_FILE}...")
    details.to_csv(PROCESSED_DETAILS_FILE, index=False)

    logger.info(f"Saving integrated sales transactions to {PROCESSED_SALES_FILE}...")
    merged.to_csv(PROCESSED_SALES_FILE, index=False)

    logger.info(f"Saving preprocessing report to {PREPROCESSING_REPORT_FILE}...")
    with open(PREPROCESSING_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Preprocessing completed successfully. Processed {cleaned_rows} transactions.")
    return merged, report


if __name__ == "__main__":
    merged_df, prep_report = run_preprocessing()
    print("Preprocessing Report:")
    print(json.dumps(prep_report, indent=2))
