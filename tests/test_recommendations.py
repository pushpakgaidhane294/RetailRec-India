"""
Tests for Recommendation Engine and Business Logic.
"""
import sys
import os
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict import recommender_service


def test_recommendation_real_customer():
    # Test with CUST-001 (Aaditya)
    result = recommender_service.recommend("CUST-001", top_k=5)
    assert result["customer_id"] == "CUST-001"
    assert result["model_type"] == "Neural Collaborative Filtering (NCF)"
    assert len(result["recommendations"]) <= 5
    assert result["fallback_used"] is False

    recs = result["recommendations"]
    assert len(recs) > 0
    first = recs[0]
    assert "rank" in first
    assert "sub_category" in first
    assert "model_score" in first
    assert 0.0 <= first["model_score"] <= 1.0
    assert first["score_label"] == "Model Score"
    assert first["badge"] == "AI Recommended"


def test_recommendation_by_customer_name():
    # Test query using name instead of ID
    result = recommender_service.recommend("Harivansh", top_k=3)
    assert result["customer_name"] == "Harivansh"
    assert len(result["recommendations"]) == 3
    assert result["fallback_used"] is False


def test_cold_start_unknown_customer():
    # Test with non-existent customer
    result = recommender_service.recommend("UNKNOWN_CUSTOMER_9999", top_k=5)
    assert result["fallback_used"] is True
    assert "Fallback" in result["model_type"]
    assert len(result["recommendations"]) == 5
    first = result["recommendations"][0]
    assert first["is_fallback"] is True
    assert first["badge"] == "Popular Items Fallback"
