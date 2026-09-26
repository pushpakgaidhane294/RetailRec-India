"""
Tests for NCF Model Architecture and Saved Weights.
"""
import os
import sys
import pytest
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.config import MODEL_FILE, MODEL_METADATA_FILE, EVALUATION_METRICS_FILE
from ml.model import RetailRecNCF


def test_model_artifact_exists():
    assert os.path.exists(MODEL_FILE), "Trained model file missing"
    assert os.path.exists(MODEL_METADATA_FILE), "Model metadata missing"
    assert os.path.exists(EVALUATION_METRICS_FILE), "Evaluation metrics missing"


def test_model_loading_and_inference():
    model = RetailRecNCF.load(MODEL_FILE)
    assert model.num_customers == 336
    assert model.num_items == 17

    # Test single prediction
    score = model.predict_score(0, 0)
    assert 0.0 <= score <= 1.0, f"Score {score} out of bounds"

    # Test batch prediction
    c_indices = np.array([0, 1, 2], dtype=np.int32)
    i_indices = np.array([5, 10, 15], dtype=np.int32)
    batch_scores = model.predict_batch(c_indices, i_indices)
    assert len(batch_scores) == 3
    for s in batch_scores:
        assert 0.0 <= s <= 1.0
