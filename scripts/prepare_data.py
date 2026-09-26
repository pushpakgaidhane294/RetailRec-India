"""
Dataset Preparation Script for RetailRec India.
Ensures raw dataset is downloaded, cleaned, integrated, and validated.
Usage: python scripts/prepare_data.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.download_dataset import download_all
from ml.preprocessing import run_preprocessing
from ml.interaction_builder import build_interactions

if __name__ == "__main__":
    print("Step 1: Downloading dataset if needed...")
    download_all()
    print("Step 2: Cleaning and integrating dataset...")
    run_preprocessing()
    print("Step 3: Building customer-item interactions and encoders...")
    build_interactions()
    print("Data preparation complete!")
