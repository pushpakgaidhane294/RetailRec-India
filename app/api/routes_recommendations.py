"""
Recommendation API Endpoints for RetailRec India.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import RecommendationResponse
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/customers", tags=["Recommendations"])


@router.get("/{customer_id}/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    customer_id: str,
    top_k: int = Query(5, ge=1, le=17, description="Number of recommendations to return"),
    category: Optional[str] = Query(None, description="Optional category filter (e.g. Electronics, Clothing, Furniture)"),
    exclude_purchased: bool = Query(True, description="Whether to exclude items previously purchased by this customer"),
):
    """
    Generate Top-K personalized product recommendations using the trained Neural Collaborative Filtering model.
    Scores candidate items via customer-item embeddings, ranks them, and returns genuine Model Scores.
    """
    try:
        results = recommendation_service.get_recommendations(
            customer_id=customer_id,
            top_k=top_k,
            category=category,
            exclude_purchased=exclude_purchased,
        )
        return results
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(exc)}",
        )
