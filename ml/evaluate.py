"""
Model Evaluation Module for RetailRec India.
Loads the trained NCF model and assesses loss, accuracy, and recommendation ranking metrics.
"""
import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import (
    MODEL_FILE,
    INTERACTIONS_FILE,
    EVALUATION_METRICS_FILE,
    settings,
)
from ml.model import RetailRecNCF
from ml.model_utils import load_encoders, compute_ranking_metrics_at_k
from ml.negative_sampling import generate_negative_samples
from ml.interaction_builder import build_interactions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_trained_model() -> Dict[str, Any]:
    """
    Evaluates the currently saved NCF model against the test set and ranking tasks.
    """
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"Model file {MODEL_FILE} not found. Please train model first.")

    logger.info(f"Loading trained NCF model from {MODEL_FILE}...")
    model = RetailRecNCF.load(MODEL_FILE)

    interactions, train_df, val_df, test_df, _ = build_interactions()
    cust_enc, item_enc = load_encoders()
    cust_to_idx = cust_enc["to_index"]
    item_to_idx = item_enc["to_index"]
    all_items = sorted(list(item_to_idx.keys()))

    # Negative sampling for test set
    test_c, test_i, test_y = generate_negative_samples(
        interactions_subset=test_df,
        all_interactions=interactions,
        all_items=all_items,
        customer_encoder=cust_to_idx,
        item_encoder=item_to_idx,
        negative_ratio=settings.NEGATIVE_RATIO,
        seed=settings.RANDOM_SEED + 2,
    )

    eval_loss_acc = model.evaluate(test_c, test_i, test_y)
    ranking_metrics = compute_ranking_metrics_at_k(
        model=model,
        test_interactions_df=test_df,
        train_interactions_df=train_df,
        customer_encoder=cust_to_idx,
        item_encoder=item_to_idx,
        all_items=all_items,
        k_list=[5, 10],
    )

    results = {
        "test_loss": round(eval_loss_acc["loss"], 4),
        "test_binary_accuracy": round(eval_loss_acc["binary_accuracy"], 4),
        "hit_rate_at_5": ranking_metrics.get("hit_rate_at_5"),
        "recall_at_5": ranking_metrics.get("recall_at_5"),
        "precision_at_5": ranking_metrics.get("precision_at_5"),
        "hit_rate_at_10": ranking_metrics.get("hit_rate_at_10"),
        "recall_at_10": ranking_metrics.get("recall_at_10"),
        "precision_at_10": ranking_metrics.get("precision_at_10"),
        "evaluated_customers": ranking_metrics.get("evaluated_customers_count"),
    }

    logger.info("Evaluation Results:")
    for k, v in results.items():
        logger.info(f"  {k}: {v}")

    return results


if __name__ == "__main__":
    evaluate_trained_model()
