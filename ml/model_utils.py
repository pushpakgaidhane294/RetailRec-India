"""
Utility helpers for RetailRec India ML workflows.
Includes encoder loading, ID translation, ranking metric computations (Hit Rate@K, Recall@K, Precision@K).
"""
import os
import sys
import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import CUSTOMER_ENCODER_FILE, ITEM_ENCODER_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_encoders() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Loads customer and item encoders from artifacts/encoders/."""
    if not os.path.exists(CUSTOMER_ENCODER_FILE) or not os.path.exists(ITEM_ENCODER_FILE):
        raise FileNotFoundError("Encoder files not found. Run interaction builder first.")

    with open(CUSTOMER_ENCODER_FILE, "r", encoding="utf-8") as f:
        cust_enc = json.load(f)

    with open(ITEM_ENCODER_FILE, "r", encoding="utf-8") as f:
        item_enc = json.load(f)

    return cust_enc, item_enc


def compute_ranking_metrics_at_k(
    model,
    test_interactions_df,
    train_interactions_df,
    customer_encoder: Dict[str, int],
    item_encoder: Dict[str, int],
    all_items: List[str],
    k_list: List[int] = [5, 10],
) -> Dict[str, float]:
    """
    Computes authentic ranking metrics (Hit Rate@K, Recall@K, Precision@K) on the holdout test set.
    
    Standard Recommendation Evaluation Protocol (He et al.):
    For each test customer who has a holdout purchase in the test set:
    1. Score all candidate items (excluding items already purchased in the training set).
    2. Rank candidates descending by NCF model prediction score.
    3. Check if the ground-truth test holdout item appears in the Top-K.
    4. Compute Hit Rate, Recall, and Precision strictly from model predictions.
    """
    all_item_indices = np.array([item_encoder[item] for item in all_items], dtype=np.int32)
    inv_item_encoder = {idx: item for item, idx in item_encoder.items()}

    # Items each customer purchased in training
    train_history: Dict[str, set] = (
        train_interactions_df.groupby("customer_id")["sub_category"]
        .apply(lambda s: set(s))
        .to_dict()
    )

    # Test holdout items per customer
    test_ground_truth: Dict[str, set] = (
        test_interactions_df.groupby("customer_id")["sub_category"]
        .apply(lambda s: set(s))
        .to_dict()
    )

    hits_at_k = {k: 0 for k in k_list}
    precision_at_k = {k: 0.0 for k in k_list}
    recall_at_k = {k: 0.0 for k in k_list}
    evaluated_customers = 0

    for cid, true_items in test_ground_truth.items():
        if cid not in customer_encoder:
            continue

        c_idx = customer_encoder[cid]
        already_purchased_in_train = train_history.get(cid, set())

        # Candidate items: all items minus what was seen during training
        candidate_items = [item for item in all_items if item not in already_purchased_in_train]
        if not candidate_items:
            continue

        candidate_indices = np.array([item_encoder[item] for item in candidate_items], dtype=np.int32)
        customer_repeated = np.full(len(candidate_indices), c_idx, dtype=np.int32)

        # Predict scores using the NCF model
        predicted_scores = model.predict_batch(customer_repeated, candidate_indices)

        # Sort candidate items by predicted score descending
        sorted_indices = np.argsort(predicted_scores)[::-1]
        ranked_items = [candidate_items[idx] for idx in sorted_indices]

        evaluated_customers += 1

        for k in k_list:
            top_k_items = set(ranked_items[:k])
            relevant_retrieved = top_k_items.intersection(true_items)
            num_retrieved_relevant = len(relevant_retrieved)

            # Hit Rate@K: 1 if at least one ground-truth test item is in Top-K
            if num_retrieved_relevant > 0:
                hits_at_k[k] += 1

            # Precision@K: relevant retrieved / K
            precision_at_k[k] += num_retrieved_relevant / k

            # Recall@K: relevant retrieved / total relevant test items for this user
            recall_at_k[k] += num_retrieved_relevant / max(1, len(true_items))

    metrics = {}
    if evaluated_customers > 0:
        for k in k_list:
            metrics[f"hit_rate_at_{k}"] = round(hits_at_k[k] / evaluated_customers, 4)
            metrics[f"precision_at_{k}"] = round(precision_at_k[k] / evaluated_customers, 4)
            metrics[f"recall_at_{k}"] = round(recall_at_k[k] / evaluated_customers, 4)
    else:
        for k in k_list:
            metrics[f"hit_rate_at_{k}"] = 0.0
            metrics[f"precision_at_{k}"] = 0.0
            metrics[f"recall_at_{k}"] = 0.0

    metrics["evaluated_customers_count"] = evaluated_customers
    return metrics
