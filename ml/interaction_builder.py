"""
Interaction Builder and Dataset Validation for RetailRec India.
Transforms sales transactions into customer-product interaction pairs,
validates interaction matrix density and statistics, creates encoders,
and performs chronological train/validation/test splitting.
"""
import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import (
    PROCESSED_SALES_FILE,
    INTERACTIONS_FILE,
    CUSTOMER_ENCODER_FILE,
    ITEM_ENCODER_FILE,
    ENCODERS_DIR,
    PROCESSED_DATA_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_interactions() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Builds aggregated customer-item interaction matrix, calculates validation metrics,
    creates customer/item encoders, and splits chronologically into train, val, and test sets.
    """
    os.makedirs(ENCODERS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    if not os.path.exists(PROCESSED_SALES_FILE):
        raise FileNotFoundError(f"Processed sales file {PROCESSED_SALES_FILE} not found. Run preprocessing first.")

    logger.info("Loading sales transactions...")
    sales_df = pd.read_csv(PROCESSED_SALES_FILE)
    sales_df["order_date"] = pd.to_datetime(sales_df["order_date"])

    # Aggregate by customer and item (Sub-Category)
    interactions = sales_df.groupby(["customer_id", "customer_name", "sub_category", "category"]).agg(
        interaction=("amount", lambda x: 1),
        quantity=("quantity", "sum"),
        amount=("amount", "sum"),
        purchase_count=("order_id", "count"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max")
    ).reset_index()

    interactions["item_id"] = interactions["sub_category"]
    interactions.to_csv(INTERACTIONS_FILE, index=False)
    logger.info(f"Saved {len(interactions)} customer-item interaction records to {INTERACTIONS_FILE}")

    # Calculate validation metrics
    total_customers = int(sales_df["customer_id"].nunique())
    total_items = int(sales_df["sub_category"].nunique())
    total_interactions = len(interactions)
    possible_pairs = total_customers * total_items
    density = round(total_interactions / possible_pairs, 6)

    # Customer level interaction distribution
    cust_counts = interactions.groupby("customer_id")["sub_category"].count()
    min_interactions_cust = int(cust_counts.min())
    max_interactions_cust = int(cust_counts.max())
    mean_interactions_cust = round(float(cust_counts.mean()), 2)

    # Item level interaction distribution
    item_counts = interactions.groupby("sub_category")["customer_id"].count()
    min_interactions_item = int(item_counts.min())
    max_interactions_item = int(item_counts.max())
    mean_interactions_item = round(float(item_counts.mean()), 2)

    # Repeat customers (multiple orders)
    orders_per_cust = sales_df.groupby("customer_id")["order_id"].nunique()
    repeat_customers_count = int((orders_per_cust > 1).sum())
    
    # Repeat purchases of same item
    repeat_pairs_count = int((interactions["purchase_count"] > 1).sum())

    validation_stats = {
        "unique_customers": total_customers,
        "unique_items": total_items,
        "total_positive_interactions": total_interactions,
        "possible_customer_item_pairs": possible_pairs,
        "interaction_density": density,
        "interaction_density_percent": f"{density * 100:.2f}%",
        "repeat_customers_orders_gt_1": repeat_customers_count,
        "repeat_customer_item_pairs": repeat_pairs_count,
        "min_interactions_per_customer": min_interactions_cust,
        "max_interactions_per_customer": max_interactions_cust,
        "mean_interactions_per_customer": mean_interactions_cust,
        "min_interactions_per_item": min_interactions_item,
        "max_interactions_per_item": max_interactions_item,
        "mean_interactions_per_item": mean_interactions_item,
    }

    logger.info("=== DATASET VALIDATION METRICS ===")
    for k, v in validation_stats.items():
        logger.info(f"  {k}: {v}")

    # Build Encoders
    unique_customer_ids = sorted(sales_df["customer_id"].unique())
    customer_to_idx = {cid: idx for idx, cid in enumerate(unique_customer_ids)}
    idx_to_customer = {idx: cid for cid, idx in customer_to_idx.items()}

    unique_item_ids = sorted(sales_df["sub_category"].unique())
    item_to_idx = {iid: idx for idx, iid in enumerate(unique_item_ids)}
    idx_to_item = {idx: iid for iid, idx in item_to_idx.items()}

    # Save Encoders
    with open(CUSTOMER_ENCODER_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "to_index": customer_to_idx,
            "to_label": idx_to_customer,
            "n_classes": len(customer_to_idx)
        }, f, indent=2)

    with open(ITEM_ENCODER_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "to_index": item_to_idx,
            "to_label": idx_to_item,
            "n_classes": len(item_to_idx)
        }, f, indent=2)

    logger.info(f"Saved encoders to {CUSTOMER_ENCODER_FILE} and {ITEM_ENCODER_FILE}")

    # Chronological Split (Leave-One-Out / Multi-Holdout by Timestamp)
    # Sort interactions strictly by customer and first_order_date
    sorted_interactions = interactions.sort_values(by=["customer_id", "first_order_date"]).reset_index(drop=True)
    
    train_rows, val_rows, test_rows = [], [], []

    for cid, group in sorted_interactions.groupby("customer_id"):
        n = len(group)
        if n >= 3:
            # Earliest to train, second-to-latest to val, latest to test
            train_rows.append(group.iloc[:-2])
            val_rows.append(group.iloc[[-2]])
            test_rows.append(group.iloc[[-1]])
        elif n == 2:
            # Earlier to train, latest to test
            train_rows.append(group.iloc[[0]])
            test_rows.append(group.iloc[[1]])
        else:
            # Customers with 1 interaction go to train so their embedding learns their interaction
            train_rows.append(group.iloc[[0]])

    train_df = pd.concat(train_rows).reset_index(drop=True)
    val_df = pd.concat(val_rows).reset_index(drop=True) if val_rows else pd.DataFrame(columns=interactions.columns)
    test_df = pd.concat(test_rows).reset_index(drop=True) if test_rows else pd.DataFrame(columns=interactions.columns)

    logger.info(f"Chronological split complete:")
    logger.info(f"  Train positive interactions: {len(train_df)}")
    logger.info(f"  Validation positive interactions: {len(val_df)}")
    logger.info(f"  Test positive interactions: {len(test_df)}")

    return interactions, train_df, val_df, test_df, validation_stats


if __name__ == "__main__":
    build_interactions()
