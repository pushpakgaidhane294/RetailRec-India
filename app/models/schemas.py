"""
Pydantic schemas for RetailRec India API requests and responses.
Ensures strong typing, data integrity, and OpenAPI documentation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    app_name: str
    version: str
    model_loaded: bool
    data_loaded: bool


class DashboardStats(BaseModel):
    total_customers: int
    total_orders: int
    total_sales: float
    total_quantity: int
    total_profit: float
    average_order_value: float
    total_categories: int
    total_subcategories: int
    min_order_date: str
    max_order_date: str


class CustomerSummary(BaseModel):
    customer_id: str
    customer_name: str
    display_name: str
    state: str
    city: str
    total_orders: int
    total_spending: float
    total_quantity: int
    unique_items: int
    average_order_value: float
    first_purchase_date: str
    last_purchase_date: str


class CustomerHistoryItem(BaseModel):
    order_id: str
    order_date: str
    category: str
    sub_category: str
    quantity: int
    amount: float
    profit: float
    payment_mode: str
    state: str
    city: str


class CustomerHistoryResponse(BaseModel):
    customer_id: str
    customer_name: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    records: List[CustomerHistoryItem]


class RecommendationItem(BaseModel):
    rank: int
    item_id: str
    sub_category: str
    category: str
    avg_price: float
    model_score: float
    score_label: str = "Model Score"
    is_fallback: bool = False
    badge: str = "AI Recommended"


class RecommendationResponse(BaseModel):
    customer_id: str
    customer_name: str
    model_type: str = "Neural Collaborative Filtering (NCF)"
    top_k: int
    total_candidates_evaluated: int
    excluded_purchased_count: int
    recommendations: List[RecommendationItem]
    customer_summary: Optional[CustomerSummary] = None
    explanation: str
    fallback_used: bool = False
    warning: Optional[str] = None


class ProductItem(BaseModel):
    item_id: str
    sub_category: str
    category: str
    total_quantity_sold: int
    total_sales: float
    avg_price: float
    customer_count: int
    order_count: int


class MonthlySalesPoint(BaseModel):
    month_year: str
    year: int
    month: int
    month_name: Optional[str] = None
    sales: float
    profit: float
    order_count: int
    quantity: int


class CategorySalesPoint(BaseModel):
    category: str
    sales: float
    profit: float
    quantity: int
    percentage: float


class StateSalesPoint(BaseModel):
    state: str
    sales: float
    profit: float
    order_count: int
    customer_count: int


class PaymentModePoint(BaseModel):
    payment_mode: str
    count: int
    total_amount: float
    percentage: float


class AnalyticsResponse(BaseModel):
    monthly_trends: List[MonthlySalesPoint]
    category_distribution: List[CategorySalesPoint]
    state_distribution: List[StateSalesPoint]
    payment_distribution: List[PaymentModePoint]
    top_subcategories: List[ProductItem]
    kpi_summary: DashboardStats


class ModelMetadataResponse(BaseModel):
    model_type: str
    architecture: str
    embedding_dim: int
    dense_layers: List[int]
    dropout_rate: float
    optimizer: str
    loss_function: str
    epochs_trained: int
    batch_size: int
    random_seed: int
    n_customers: int
    n_items: int
    n_training_samples: int
    n_validation_samples: int
    n_test_samples: int
    negative_sample_ratio: str
    training_timestamp: str


class EvaluationMetricsResponse(BaseModel):
    model_metadata: ModelMetadataResponse
    loss: float
    val_loss: float
    binary_accuracy: float
    val_binary_accuracy: float
    precision_at_5: Optional[float] = None
    recall_at_5: Optional[float] = None
    hit_rate_at_5: Optional[float] = None
    precision_at_10: Optional[float] = None
    recall_at_10: Optional[float] = None
    hit_rate_at_10: Optional[float] = None
    training_history: Dict[str, List[float]]
    evaluation_limitations: str
