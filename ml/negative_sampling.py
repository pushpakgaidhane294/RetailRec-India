"""
Negative Sampling for Neural Collaborative Filtering (NCF).
Constructs positive and negative interaction pairs with reproducible random sampling,
ensuring zero data leakage across training, validation, and test sets.
"""
import os
import sys
import logging
import numpy as np
import pandas as pd
from typing import Tuple, Set, Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def generate_negative_samples(
    interactions_subset: pd.DataFrame,
    all_interactions: pd.DataFrame,
    all_items: List[str],
    customer_encoder: Dict[str, int],
    item_encoder: Dict[str, int],
    negative_ratio: int = 2,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates training samples containing both positive (label=1) and
    negative (label=0) customer-item pairs.
    
    Zero Leakage Guarantee:
    Negative items for a customer are strictly chosen from items the customer NEVER
    purchased in the entire dataset history (neither in train, val, nor test).
    
    Returns:
        customer_indices: np.ndarray of shape (N,)
        item_indices: np.ndarray of shape (N,)
        labels: np.ndarray of shape (N,) with values 0 or 1
    """
    rng = np.random.RandomState(seed)

    # Precompute all items purchased by each customer across the entire dataset
    all_customer_items: Dict[str, Set[str]] = (
        all_interactions.groupby("customer_id")["sub_category"]
        .apply(lambda s: set(s))
        .to_dict()
    )

    all_items_set = set(all_items)

    customer_list = []
    item_list = []
    label_list = []

    for _, row in interactions_subset.iterrows():
        cid = row["customer_id"]
        iid = row["sub_category"]

        if cid not in customer_encoder or iid not in item_encoder:
            continue

        c_idx = customer_encoder[cid]
        i_idx = item_encoder[iid]

        # Positive sample
        customer_list.append(c_idx)
        item_list.append(i_idx)
        label_list.append(1.0)

        # Unpurchased items for this customer (leakage-free candidates)
        purchased_by_user = all_customer_items.get(cid, set())
        unpurchased_candidates = list(all_items_set - purchased_by_user)

        if not unpurchased_candidates:
            continue

        # Sample k negative items
        num_negatives = min(negative_ratio, len(unpurchased_candidates))
        chosen_negatives = rng.choice(unpurchased_candidates, size=num_negatives, replace=False)

        for neg_item in chosen_negatives:
            customer_list.append(c_idx)
            item_list.append(item_encoder[neg_item])
            label_list.append(0.0)

    # Convert to numpy arrays
    cust_arr = np.array(customer_list, dtype=np.int32)
    item_arr = np.array(item_list, dtype=np.int32)
    labels_arr = np.array(label_list, dtype=np.float32)

    # Shuffle synchronously
    shuffle_indices = rng.permutation(len(cust_arr))
    cust_arr = cust_arr[shuffle_indices]
    item_arr = item_arr[shuffle_indices]
    labels_arr = labels_arr[shuffle_indices]

    pos_count = int(np.sum(labels_arr == 1.0))
    neg_count = int(np.sum(labels_arr == 0.0))
    logger.info(
        f"Generated {len(labels_arr)} samples (Positives: {pos_count}, Negatives: {neg_count}, Ratio: {neg_count/max(1, pos_count):.2f}:1)"
    )

    return cust_arr, item_arr, labels_arr
