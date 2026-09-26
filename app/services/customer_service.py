"""
Customer Data Service for RetailRec India.
Provides customer lookups, autocomplete search, profile summaries, and paginated transaction history.
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import PROCESSED_SALES_FILE
from ml.predict import recommender_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class CustomerService:
    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._customers_cache: Optional[List[Dict[str, Any]]] = None

    def _ensure_data(self):
        if self._df is None:
            recommender_service.load_artifacts()
            if not os.path.exists(PROCESSED_SALES_FILE):
                raise FileNotFoundError(f"Sales file {PROCESSED_SALES_FILE} not found.")
            self._df = pd.read_csv(PROCESSED_SALES_FILE)
            self._df["order_date"] = pd.to_datetime(self._df["order_date"])
            
            # Build customer summary table
            grouped = self._df.groupby(["customer_id", "customer_name", "state", "city"]).agg(
                total_orders=("order_id", "nunique"),
                total_spending=("amount", "sum"),
                total_quantity=("quantity", "sum"),
                unique_items=("sub_category", "nunique"),
                first_purchase_date=("order_date", "min"),
                last_purchase_date=("order_date", "max"),
            ).reset_index()

            grouped["total_spending"] = grouped["total_spending"].round(2)
            grouped["average_order_value"] = (grouped["total_spending"] / grouped["total_orders"]).round(2)
            grouped["first_purchase_date"] = grouped["first_purchase_date"].dt.strftime("%Y-%m-%d")
            grouped["last_purchase_date"] = grouped["last_purchase_date"].dt.strftime("%Y-%m-%d")
            grouped["display_name"] = grouped["customer_name"] + " (" + grouped["customer_id"] + ")"

            # Sort by total spending descending
            grouped = grouped.sort_values(by="total_spending", ascending=False).reset_index(drop=True)
            self._customers_cache = grouped.to_dict("records")

    def list_customers(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Searchable customer listing for autocomplete and selectors."""
        self._ensure_data()
        customers = self._customers_cache or []
        if not query:
            return customers[:limit]

        q = query.strip().lower()
        filtered = [
            c for c in customers
            if q in c["customer_name"].lower() or q in c["customer_id"].lower() or q in c["city"].lower() or q in c["state"].lower()
        ]
        return filtered[:limit]

    def get_customer(self, customer_query: str) -> Optional[Dict[str, Any]]:
        """Resolves customer by ID or name and returns verified profile summary."""
        self._ensure_data()
        resolved_id = recommender_service.resolve_customer_id(customer_query)
        if not resolved_id:
            return None

        for c in self._customers_cache:
            if c["customer_id"] == resolved_id:
                return c
        return None

    def get_customer_history(
        self,
        customer_query: str,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Returns paginated actual purchase records for a given customer."""
        self._ensure_data()
        resolved_id = recommender_service.resolve_customer_id(customer_query)
        if not resolved_id:
            return None

        cust_records = self._df[self._df["customer_id"] == resolved_id].copy()
        if cust_records.empty:
            return None

        # Extract customer name before applying any optional filters
        customer_name = cust_records.iloc[0]["customer_name"]

        # Optional filters
        if category and category.lower() != "all":
            cust_records = cust_records[cust_records["category"].str.lower() == category.lower()]

        if search:
            s = search.strip().lower()
            cust_records = cust_records[
                cust_records["sub_category"].str.lower().str.contains(s, na=False, regex=False)
                | cust_records["order_id"].str.lower().str.contains(s, na=False, regex=False)
                | cust_records["payment_mode"].str.lower().str.contains(s, na=False, regex=False)
            ]

        # Sort chronologically descending (latest first)
        cust_records = cust_records.sort_values(by="order_date", ascending=False)
        total_records = len(cust_records)
        total_pages = max(1, (total_records + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))

        if total_records == 0:
            return {
                "customer_id": resolved_id,
                "customer_name": customer_name,
                "total_records": 0,
                "page": 1,
                "page_size": page_size,
                "total_pages": 1,
                "records": [],
            }

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_slice = cust_records.iloc[start_idx:end_idx]

        records = []
        for _, row in page_slice.iterrows():
            records.append({
                "order_id": row["order_id"],
                "order_date": row["order_date"].strftime("%Y-%m-%d"),
                "category": row["category"],
                "sub_category": row["sub_category"],
                "quantity": int(row["quantity"]),
                "amount": round(float(row["amount"]), 2),
                "profit": round(float(row["profit"]), 2),
                "payment_mode": row["payment_mode"],
                "state": row["state"],
                "city": row["city"],
            })

        return {
            "customer_id": resolved_id,
            "customer_name": customer_name,
            "total_records": total_records,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "records": records,
        }


customer_service = CustomerService()
