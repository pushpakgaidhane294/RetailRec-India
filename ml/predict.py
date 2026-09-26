"""
Inference and Recommendation Prediction Engine for RetailRec India.
Uses trained NCF neural model to score candidate products and generate Top-K recommendations.
"""
import os
import sys
import json
import logging
import re
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import (
    MODEL_FILE,
    PROCESSED_SALES_FILE,
    CUSTOMER_ENCODER_FILE,
    ITEM_ENCODER_FILE,
)
from ml.model import RetailRecNCF
from ml.model_utils import load_encoders

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Production recommendation service maintaining preloaded model,
    encoders, and catalog statistics in memory for high-performance inference.
    """

    def __init__(self):
        self.model: Optional[RetailRecNCF] = None
        self.cust_to_idx: Dict[str, int] = {}
        self.idx_to_cust: Dict[int, str] = {}
        self.item_to_idx: Dict[str, int] = {}
        self.idx_to_item: Dict[int, str] = {}
        self.sales_df: Optional[pd.DataFrame] = None
        self.catalog_df: Optional[pd.DataFrame] = None
        self.customer_purchases: Dict[str, set] = {}
        self.customer_name_to_id: Dict[str, str] = {}
        self.customer_id_to_name: Dict[str, str] = {}
        self.popular_items: List[Dict[str, Any]] = []

    def load_artifacts(self) -> None:
        """Loads model, encoders, and catalog data into memory once."""
        if self.model is not None:
            return  # Already loaded

        logger.info("Loading recommendation engine artifacts...")
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(f"Trained model not found at {MODEL_FILE}. Run training first.")

        # Load encoders
        cust_enc, item_enc = load_encoders()
        self.cust_to_idx = cust_enc["to_index"]
        self.idx_to_cust = {int(k): v for k, v in cust_enc["to_label"].items()}
        self.item_to_idx = item_enc["to_index"]
        self.idx_to_item = {int(k): v for k, v in item_enc["to_label"].items()}

        # Load NCF model
        self.model = RetailRecNCF.load(MODEL_FILE)

        # Load transaction data
        if not os.path.exists(PROCESSED_SALES_FILE):
            raise FileNotFoundError(f"Sales file {PROCESSED_SALES_FILE} not found.")

        self.sales_df = pd.read_csv(PROCESSED_SALES_FILE)

        # Map customer names and IDs
        for _, row in self.sales_df[["customer_id", "customer_name"]].drop_duplicates().iterrows():
            self.customer_name_to_id[row["customer_name"].strip().lower()] = row["customer_id"]
            self.customer_id_to_name[row["customer_id"]] = row["customer_name"].strip()

        # Build customer purchase sets
        self.customer_purchases = (
            self.sales_df.groupby("customer_id")["sub_category"]
            .apply(lambda s: set(s))
            .to_dict()
        )

        # Build catalog summary (Sub-Category level)
        catalog = self.sales_df.groupby(["sub_category", "category"]).agg(
            total_quantity_sold=("quantity", "sum"),
            total_sales=("amount", "sum"),
            avg_price=("unit_price", "mean"),
            customer_count=("customer_id", "nunique"),
            order_count=("order_id", "nunique"),
        ).reset_index()
        catalog["avg_price"] = catalog["avg_price"].round(2)
        catalog["total_sales"] = catalog["total_sales"].round(2)
        catalog["item_id"] = catalog["sub_category"]
        self.catalog_df = catalog

        # Build explicit popularity fallback list (strictly labelled as fallback)
        pop = catalog.sort_values(by="total_quantity_sold", ascending=False).to_dict("records")
        self.popular_items = pop

        logger.info(
            f"Recommendation engine loaded successfully: {len(self.cust_to_idx)} customers, "
            f"{len(self.item_to_idx)} items, {len(self.catalog_df)} catalog entries."
        )

    def resolve_customer_id(self, query: str) -> Optional[str]:
        """Resolves input query which may be customer_id (e.g. CUST-001) or customer_name or display format."""
        if not query:
            return None
        q = str(query).strip()

        # 1. Check if ID pattern is present anywhere in query, e.g. "CUST-001" or "(CUST-001)"
        match = re.search(r"\b(CUST-\d{3,4})\b", q, re.IGNORECASE)
        if match:
            extracted_id = match.group(1).upper()
            if extracted_id in self.customer_id_to_name:
                return extracted_id

        # 2. Direct customer_id match (case-insensitive)
        upper_q = q.upper()
        if upper_q in self.customer_id_to_name:
            return upper_q

        # 3. Exact Name match (case-insensitive)
        lower_q = q.lower()
        if lower_q in self.customer_name_to_id:
            return self.customer_name_to_id[lower_q]

        # 4. Clean parentheses or extra tokens, e.g. "Aakanksha (CUST-001)"
        cleaned_name = re.sub(r"\(.*?\)", "", lower_q).strip()
        if cleaned_name and cleaned_name in self.customer_name_to_id:
            return self.customer_name_to_id[cleaned_name]

        # 5. Check if query is prefix or substring of customer name (with minimum length 3)
        if len(lower_q) >= 3:
            for name, cid in self.customer_name_to_id.items():
                if name.startswith(lower_q) or lower_q in name:
                    return cid

            # Word boundary match if customer name is contained as a distinct word in query
            for name, cid in self.customer_name_to_id.items():
                if len(name) >= 3 and re.search(rf"\b{re.escape(name)}\b", lower_q):
                    return cid

        return None

    def get_customer_summary(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Returns verified real customer profile metrics."""
        self.load_artifacts()
        resolved_id = self.resolve_customer_id(customer_id)
        if not resolved_id:
            return None

        cust_df = self.sales_df[self.sales_df["customer_id"] == resolved_id]
        if cust_df.empty:
            return None

        first_row = cust_df.iloc[0]
        total_orders = int(cust_df["order_id"].nunique())
        total_spending = round(float(cust_df["amount"].sum()), 2)
        total_qty = int(cust_df["quantity"].sum())
        unique_items = int(cust_df["sub_category"].nunique())
        aov = round(total_spending / max(1, total_orders), 2)
        first_date = str(cust_df["order_date"].min())[:10]
        last_date = str(cust_df["order_date"].max())[:10]

        return {
            "customer_id": resolved_id,
            "customer_name": first_row["customer_name"],
            "display_name": f"{first_row['customer_name']} ({resolved_id})",
            "state": first_row["state"],
            "city": first_row["city"],
            "total_orders": total_orders,
            "total_spending": total_spending,
            "total_quantity": total_qty,
            "unique_items": unique_items,
            "average_order_value": aov,
            "first_purchase_date": first_date,
            "last_purchase_date": last_date,
        }

    def recommend(
        self,
        customer_query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        exclude_already_purchased: bool = True,
    ) -> Dict[str, Any]:
        """
        Generates Top-K personalized recommendations for a customer using the trained NCF model.
        
        Steps:
        1. Resolve customer ID.
        2. Filter candidate items (by category and previous purchases).
        3. Score candidates with NCF deep learning embeddings.
        4. Sort and return Top-K with real product information and genuine model scores.
        """
        self.load_artifacts()
        resolved_id = self.resolve_customer_id(customer_query)

        # Cold start handling: customer not recognized in training dataset
        if not resolved_id:
            logger.warning(f"Unknown customer query: '{customer_query}'. Returning popularity fallback.")
            return self._build_popularity_fallback(
                query=customer_query,
                top_k=top_k,
                category_filter=category_filter,
                warning="Customer ID not found in historical dataset. Displaying popular items as fallback.",
            )

        customer_idx = self.cust_to_idx.get(resolved_id)
        if customer_idx is None:
            return self._build_popularity_fallback(
                query=customer_query,
                top_k=top_k,
                category_filter=category_filter,
                warning="Customer has no encoded embedding. Displaying popular items as fallback.",
            )

        customer_summary = self.get_customer_summary(resolved_id)
        purchased_items = self.customer_purchases.get(resolved_id, set())

        # Build candidate items
        all_catalog = self.catalog_df.copy()
        if category_filter and category_filter.lower() != "all":
            all_catalog = all_catalog[all_catalog["category"].str.lower() == category_filter.lower()]

        total_evaluated_pool = len(all_catalog)

        if exclude_already_purchased:
            candidate_df = all_catalog[~all_catalog["sub_category"].isin(purchased_items)].copy()
        else:
            candidate_df = all_catalog.copy()

        excluded_count = total_evaluated_pool - len(candidate_df)

        # If candidate pool is exhausted (e.g. customer bought all items in that category)
        if candidate_df.empty:
            logger.info("Candidate pool exhausted after exclusion. Re-evaluating with full catalog.")
            candidate_df = all_catalog.copy()
            excluded_count = 0

        # Model Inference
        candidate_items = candidate_df["sub_category"].tolist()
        candidate_indices = np.array([self.item_to_idx[item] for item in candidate_items], dtype=np.int32)
        customer_repeated = np.full(len(candidate_indices), customer_idx, dtype=np.int32)

        predicted_scores = self.model.predict_batch(customer_repeated, candidate_indices)
        candidate_df["model_score"] = [round(float(s), 4) for s in predicted_scores]

        # Rank descending by genuine model score
        ranked_df = candidate_df.sort_values(by="model_score", ascending=False).head(top_k)

        recommendations = []
        for rank, (_, row) in enumerate(ranked_df.iterrows(), start=1):
            recommendations.append({
                "rank": rank,
                "item_id": row["sub_category"],
                "sub_category": row["sub_category"],
                "category": row["category"],
                "avg_price": round(float(row["avg_price"]), 2),
                "model_score": float(row["model_score"]),
                "score_label": "Model Score",
                "is_fallback": False,
                "badge": "AI Recommended",
            })

        warning_msg = None
        if customer_summary and customer_summary["unique_items"] <= 1:
            warning_msg = "This customer has limited purchase history (1 item), so personalized recommendations may be less reliable."

        return {
            "customer_id": resolved_id,
            "customer_name": customer_summary["customer_name"] if customer_summary else resolved_id,
            "model_type": "Neural Collaborative Filtering (NCF)",
            "top_k": len(recommendations),
            "total_candidates_evaluated": total_evaluated_pool,
            "excluded_purchased_count": excluded_count,
            "recommendations": recommendations,
            "customer_summary": customer_summary,
            "explanation": "Recommendations are generated by a Neural Collaborative Filtering model trained on historical customer-item purchase interactions.",
            "fallback_used": False,
            "warning": warning_msg,
        }

    def _build_popularity_fallback(
        self,
        query: str,
        top_k: int,
        category_filter: Optional[str] = None,
        warning: str = "Fallback used",
    ) -> Dict[str, Any]:
        """Explicitly labelled fallback when customer is unknown."""
        pool = self.catalog_df.copy()
        if category_filter and category_filter.lower() != "all":
            pool = pool[pool["category"].str.lower() == category_filter.lower()]

        ranked = pool.sort_values(by="total_quantity_sold", ascending=False).head(top_k)
        max_qty = max(1, self.catalog_df["total_quantity_sold"].max())

        recs = []
        for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
            rel_score = round(float(row["total_quantity_sold"] / max_qty), 4)
            recs.append({
                "rank": rank,
                "item_id": row["sub_category"],
                "sub_category": row["sub_category"],
                "category": row["category"],
                "avg_price": round(float(row["avg_price"]), 2),
                "model_score": rel_score,
                "score_label": "Popularity Ratio",
                "is_fallback": True,
                "badge": "Popular Items Fallback",
            })

        return {
            "customer_id": query,
            "customer_name": f"Guest / Unknown ({query})",
            "model_type": "Popularity Fallback (Non-Personalized)",
            "top_k": len(recs),
            "total_candidates_evaluated": len(pool),
            "excluded_purchased_count": 0,
            "recommendations": recs,
            "customer_summary": None,
            "explanation": "Customer ID was not found in the historical training set. Displaying overall popular items as an explicitly labelled fallback.",
            "fallback_used": True,
            "warning": warning,
        }


# Global singleton instance for high performance and zero reload per request
recommender_service = RecommendationEngine()
