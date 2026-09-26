"""
Configuration management for RetailRec India.
Uses relative paths based on repository root so the project is portable across Windows, Linux, and Render.
"""
import os
from pydantic import BaseModel

# Base directory (root of the project)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Artifact directories
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MODEL_DIR = os.path.join(ARTIFACTS_DIR, "model")
ENCODERS_DIR = os.path.join(ARTIFACTS_DIR, "encoders")

# Frontend directory
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# File paths
RAW_ORDERS_FILE = os.path.join(RAW_DATA_DIR, "Orders.csv")
RAW_DETAILS_FILE = os.path.join(RAW_DATA_DIR, "Details.csv")

PROCESSED_ORDERS_FILE = os.path.join(PROCESSED_DATA_DIR, "cleaned_orders.csv")
PROCESSED_DETAILS_FILE = os.path.join(PROCESSED_DATA_DIR, "cleaned_details.csv")
PROCESSED_SALES_FILE = os.path.join(PROCESSED_DATA_DIR, "sales_transactions.csv")
INTERACTIONS_FILE = os.path.join(PROCESSED_DATA_DIR, "customer_item_interactions.csv")
PREPROCESSING_REPORT_FILE = os.path.join(PROCESSED_DATA_DIR, "preprocessing_report.json")

MODEL_FILE = os.path.join(MODEL_DIR, "retailrec_model.keras")
MODEL_METADATA_FILE = os.path.join(MODEL_DIR, "model_metadata.json")
TRAINING_HISTORY_FILE = os.path.join(MODEL_DIR, "training_history.json")
EVALUATION_METRICS_FILE = os.path.join(MODEL_DIR, "evaluation_metrics.json")

CUSTOMER_ENCODER_FILE = os.path.join(ENCODERS_DIR, "customer_encoder.json")
ITEM_ENCODER_FILE = os.path.join(ENCODERS_DIR, "item_encoder.json")


class Settings(BaseModel):
    APP_NAME: str = "RetailRec India"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Deep Learning-Based Personalized Product Recommendation System Using Neural Collaborative Filtering"
    
    # Server configuration (supporting Render's dynamically assigned $PORT)
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ML Hyperparameters
    RANDOM_SEED: int = 42
    EMBEDDING_DIM: int = 32
    DENSE_UNITS_1: int = 64
    DENSE_UNITS_2: int = 32
    DROPOUT_RATE: float = 0.20
    BATCH_SIZE: int = 32
    MAX_EPOCHS: int = 35
    NEGATIVE_RATIO: int = 2  # 2 negative samples for each positive interaction


settings = Settings()
