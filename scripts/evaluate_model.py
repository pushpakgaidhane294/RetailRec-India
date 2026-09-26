"""
Script to evaluate saved NCF model.
Usage: python scripts/evaluate_model.py
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.evaluate import evaluate_trained_model

if __name__ == "__main__":
    evaluate_trained_model()
