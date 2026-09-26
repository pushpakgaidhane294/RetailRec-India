"""
Executable script to run NCF model training.
Usage: python scripts/train_model.py
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.train import train_ncf

if __name__ == "__main__":
    train_ncf()
