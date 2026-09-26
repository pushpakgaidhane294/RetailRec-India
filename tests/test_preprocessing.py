"""
Tests for Data Preprocessing and Validation.
"""
import os
import sys
import pytest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import (
    PROCESSED_ORDERS_FILE,
    PROCESSED_DETAILS_FILE,
    PROCESSED_SALES_FILE,
    PREPROCESSING_REPORT_FILE,
)


def test_processed_files_exist():
    assert os.path.exists(PROCESSED_ORDERS_FILE), "Cleaned orders file missing"
    assert os.path.exists(PROCESSED_DETAILS_FILE), "Cleaned details file missing"
    assert os.path.exists(PROCESSED_SALES_FILE), "Sales transactions file missing"
    assert os.path.exists(PREPROCESSING_REPORT_FILE), "Preprocessing report missing"


def test_sales_dataset_integrity():
    df = pd.read_csv(PROCESSED_SALES_FILE)
    assert len(df) == 1500, f"Expected 1500 records, got {len(df)}"
    assert df["customer_id"].nunique() == 336, f"Expected 336 customers, got {df['customer_id'].nunique()}"
    assert df["sub_category"].nunique() == 17, f"Expected 17 sub-categories, got {df['sub_category'].nunique()}"
    assert (df["amount"] < 0).sum() == 0, "Found negative amounts"
    assert (df["quantity"] <= 0).sum() == 0, "Found non-positive quantities"
    assert "order_year" in df.columns
    assert "order_month" in df.columns
    assert "transaction_value" in df.columns
