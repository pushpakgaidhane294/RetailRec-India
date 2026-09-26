"""
End-to-End API Integration Tests for RetailRec India.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "RetailRec India"
    assert data["model_loaded"] is True
    assert data["data_loaded"] is True


def test_stats_endpoint():
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_customers"] == 336
    assert data["total_orders"] == 500
    assert data["total_sales"] == 437771.0
    assert data["total_quantity"] == 5615
    assert data["total_profit"] == 36963.0


def test_list_customers():
    res = client.get("/api/customers?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 10
    first = data[0]
    assert "customer_id" in first
    assert "customer_name" in first
    assert "total_spending" in first


def test_get_customer_detail():
    res = client.get("/api/customers/CUST-001")
    assert res.status_code == 200
    data = res.json()
    assert data["customer_id"] == "CUST-001"
    assert data["total_orders"] >= 1


def test_customer_history():
    res = client.get("/api/customers/CUST-001/history")
    assert res.status_code == 200
    data = res.json()
    assert data["customer_id"] == "CUST-001"
    assert len(data["records"]) > 0
    record = data["records"][0]
    assert "order_id" in record
    assert "sub_category" in record
    assert "amount" in record


def test_customer_recommendations():
    res = client.get("/api/customers/CUST-001/recommendations?top_k=5")
    assert res.status_code == 200
    data = res.json()
    assert data["customer_id"] == "CUST-001"
    assert len(data["recommendations"]) == 5
    assert data["model_type"] == "Neural Collaborative Filtering (NCF)"
    first = data["recommendations"][0]
    assert first["score_label"] == "Model Score"
    assert 0.0 <= first["model_score"] <= 1.0


def test_products_list_and_search():
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 17

    res_search = client.get("/api/products/search?q=phone")
    assert res_search.status_code == 200
    results = res_search.json()
    assert len(results) >= 1
    assert "Phones" in results[0]["sub_category"]


def test_analytics_endpoint():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "monthly_trends" in data
    assert "category_distribution" in data
    assert "state_distribution" in data
    assert "payment_distribution" in data
    assert len(data["monthly_trends"]) == 12  # 12 months in 2018
    assert "month_name" in data["monthly_trends"][0]
    assert data["monthly_trends"][0]["month_name"] == "Jan"


def test_model_endpoints():
    res_info = client.get("/api/model/info")
    assert res_info.status_code == 200
    info = res_info.json()
    assert info["model_type"] == "Neural Collaborative Filtering (NCF)"
    assert info["n_customers"] == 336
    assert info["n_items"] == 17

    res_metrics = client.get("/api/model/metrics")
    assert res_metrics.status_code == 200
    metrics = res_metrics.json()
    assert "test_loss" in metrics
    assert "hit_rate_at_5" in metrics
    assert "hit_rate_at_10" in metrics
