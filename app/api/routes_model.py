"""
Model Performance and Metadata API Endpoints for RetailRec India.
"""
import os
import json
from fastapi import APIRouter, HTTPException

from app.core.config import (
    MODEL_METADATA_FILE,
    TRAINING_HISTORY_FILE,
    EVALUATION_METRICS_FILE,
)

router = APIRouter(prefix="/api/model", tags=["Model"])


@router.get("/info")
def get_model_info():
    """Retrieve architecture, hyperparameters, and dataset specs of the trained NCF model."""
    if not os.path.exists(MODEL_METADATA_FILE):
        raise HTTPException(status_code=404, detail="Model metadata not found. Train the model first.")
    with open(MODEL_METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/metrics")
def get_model_metrics():
    """Retrieve genuine evaluation metrics including Loss, Binary Accuracy, Hit Rate@K, Recall@K, Precision@K."""
    if not os.path.exists(EVALUATION_METRICS_FILE):
        raise HTTPException(status_code=404, detail="Evaluation metrics not found. Train and evaluate the model first.")
    with open(EVALUATION_METRICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/history")
def get_training_history():
    """Retrieve epoch-by-epoch loss and accuracy history during training."""
    if not os.path.exists(TRAINING_HISTORY_FILE):
        raise HTTPException(status_code=404, detail="Training history not found.")
    with open(TRAINING_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
