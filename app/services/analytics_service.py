"""
Analytics Service for RetailRec India.
Calculates dashboard KPIs, time-series monthly sales/profit trends,
category shares, state performance, and payment mode distributions from authentic sales data.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import PROCESSED_SALES_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self):
        self._df: Optional[pd.DataFrame] = None

    def _ensure_data(self):
        if self._df is None:
            if not os.path.exists(PROCESSED_SALES_FILE):
                raise FileNotFoundError(f"Sales file {PROCESSED_SALES_FILE} not found.")
            self._df = pd.read_csv(PROCESSED_SALES_FILE)
            self._df["order_date"] = pd.to_datetime(self._df["order_date"])

    def get_kpis(self) -> Dict[str, Any]:
        """Calculates authentic overall summary metrics."""
        self._ensure_data()
        df = self._df
        total_customers = int(df["customer_id"].nunique())
        total_orders = int(df["order_id"].nunique())
        total_sales = round(float(df["amount"].sum()), 2)
        total_qty = int(df["quantity"].sum())
        total_profit = round(float(df["profit"].sum()), 2)
        aov = round(total_sales / max(1, total_orders), 2)
        total_categories = int(df["category"].nunique())
        total_subcategories = int(df["sub_category"].nunique())
        min_date = df["order_date"].min().strftime("%Y-%m-%d")
        max_date = df["order_date"].max().strftime("%Y-%m-%d")

        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_sales": total_sales,
            "total_quantity": total_qty,
            "total_profit": total_profit,
            "average_order_value": aov,
            "total_categories": total_categories,
            "total_subcategories": total_subcategories,
            "min_order_date": min_date,
            "max_order_date": max_date,
        }

    def get_monthly_trends(self) -> List[Dict[str, Any]]:
        """Calculates monthly sales, profit, order count, and quantity."""
        self._ensure_data()
        df = self._df.copy()
        df["month"] = df["order_date"].dt.month
        df["month_name"] = df["order_date"].dt.strftime("%b")
        df["year"] = df["order_date"].dt.year
        df["month_year"] = df["order_date"].dt.strftime("%b %Y")

        monthly = df.groupby(["year", "month", "month_year", "month_name"]).agg(
            sales=("amount", "sum"),
            profit=("profit", "sum"),
            order_count=("order_id", "nunique"),
            quantity=("quantity", "sum")
        ).reset_index().sort_values(by=["year", "month"])

        monthly["sales"] = monthly["sales"].round(2)
        monthly["profit"] = monthly["profit"].round(2)

        return monthly.to_dict("records")

    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """Calculates sales and profit breakdown across product categories."""
        self._ensure_data()
        total_sales = float(self._df["amount"].sum())
        cat_group = self._df.groupby("category").agg(
            sales=("amount", "sum"),
            profit=("profit", "sum"),
            quantity=("quantity", "sum")
        ).reset_index()

        cat_group["sales"] = cat_group["sales"].round(2)
        cat_group["profit"] = cat_group["profit"].round(2)
        cat_group["percentage"] = (cat_group["sales"] / max(1, total_sales) * 100).round(2)
        cat_group = cat_group.sort_values(by="sales", ascending=False)

        return cat_group.to_dict("records")

    def get_state_distribution(self) -> List[Dict[str, Any]]:
        """Calculates sales distribution across Indian states."""
        self._ensure_data()
        state_group = self._df.groupby("state").agg(
            sales=("amount", "sum"),
            profit=("profit", "sum"),
            order_count=("order_id", "nunique"),
            customer_count=("customer_id", "nunique")
        ).reset_index()

        state_group["sales"] = state_group["sales"].round(2)
        state_group["profit"] = state_group["profit"].round(2)
        state_group = state_group.sort_values(by="sales", ascending=False)

        return state_group.to_dict("records")

    def get_payment_distribution(self) -> List[Dict[str, Any]]:
        """Calculates distribution of payment modes."""
        self._ensure_data()
        total_amount = float(self._df["amount"].sum())
        pay_group = self._df.groupby("payment_mode").agg(
            count=("order_id", "nunique"),
            total_amount=("amount", "sum")
        ).reset_index()

        pay_group["total_amount"] = pay_group["total_amount"].round(2)
        pay_group["percentage"] = (pay_group["total_amount"] / max(1, total_amount) * 100).round(2)
        pay_group = pay_group.sort_values(by="total_amount", ascending=False)

        return pay_group.to_dict("records")

    def get_top_subcategories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns top performing sub-categories by sales."""
        self._ensure_data()
        sub_group = self._df.groupby(["sub_category", "category"]).agg(
            total_sales=("amount", "sum"),
            total_quantity_sold=("quantity", "sum"),
            avg_price=("unit_price", "mean"),
            customer_count=("customer_id", "nunique"),
            order_count=("order_id", "nunique"),
        ).reset_index()

        sub_group["total_sales"] = sub_group["total_sales"].round(2)
        sub_group["avg_price"] = sub_group["avg_price"].round(2)
        sub_group["item_id"] = sub_group["sub_category"]
        sub_group = sub_group.sort_values(by="total_sales", ascending=False).head(limit)

        return sub_group.to_dict("records")

    def get_full_analytics(self) -> Dict[str, Any]:
        """Consolidates all analytics data for dashboard charts and metrics."""
        return {
            "kpi_summary": self.get_kpis(),
            "monthly_trends": self.get_monthly_trends(),
            "category_distribution": self.get_category_distribution(),
            "state_distribution": self.get_state_distribution(),
            "payment_distribution": self.get_payment_distribution(),
            "top_subcategories": self.get_top_subcategories(limit=10),
        }


analytics_service = AnalyticsService()
