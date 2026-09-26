"""
Product and Catalog Service for RetailRec India.
Provides catalog queries, product metrics, and category filtering.
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import PROCESSED_SALES_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._products_cache: Optional[List[Dict[str, Any]]] = None

    def _ensure_data(self):
        if self._df is None:
            if not os.path.exists(PROCESSED_SALES_FILE):
                raise FileNotFoundError(f"Sales file {PROCESSED_SALES_FILE} not found.")
            self._df = pd.read_csv(PROCESSED_SALES_FILE)
            
            catalog = self._df.groupby(["sub_category", "category"]).agg(
                total_quantity_sold=("quantity", "sum"),
                total_sales=("amount", "sum"),
                avg_price=("unit_price", "mean"),
                customer_count=("customer_id", "nunique"),
                order_count=("order_id", "nunique"),
            ).reset_index()

            catalog["avg_price"] = catalog["avg_price"].round(2)
            catalog["total_sales"] = catalog["total_sales"].round(2)
            catalog["item_id"] = catalog["sub_category"]
            
            catalog = catalog.sort_values(by="total_sales", ascending=False).reset_index(drop=True)
            self._products_cache = catalog.to_dict("records")

    def list_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        sort_by: str = "total_sales",
        ascending: bool = False,
    ) -> List[Dict[str, Any]]:
        """Returns catalog items matching optional text query and category filter."""
        self._ensure_data()
        items = list(self._products_cache)

        if category and category.lower() != "all":
            items = [item for item in items if item["category"].lower() == category.lower()]

        if query:
            q = query.strip().lower()
            items = [
                item for item in items
                if q in item["sub_category"].lower() or q in item["category"].lower()
            ]

        if sort_by in ["total_sales", "total_quantity_sold", "avg_price", "customer_count", "order_count"]:
            items.sort(key=lambda x: x[sort_by], reverse=not ascending)

        return items

    def list_categories(self) -> List[str]:
        """Returns unique categories available in the authentic dataset."""
        self._ensure_data()
        return sorted(list(set(item["category"] for item in self._products_cache)))


product_service = ProductService()
