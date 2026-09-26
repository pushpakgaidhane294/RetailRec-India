"""
Recommendation Service for RetailRec India.
Connects the API layer to the NCF inference engine.
"""
import logging
from typing import Dict, Any, Optional

from ml.predict import recommender_service

logger = logging.getLogger(__name__)


class RecommendationService:
    def get_recommendations(
        self,
        customer_id: str,
        top_k: int = 5,
        category: Optional[str] = None,
        exclude_purchased: bool = True,
    ) -> Dict[str, Any]:
        """Generates Top-K personalized recommendations using the trained NCF model."""
        return recommender_service.recommend(
            customer_query=customer_id,
            top_k=top_k,
            category_filter=category,
            exclude_already_purchased=exclude_purchased,
        )


recommendation_service = RecommendationService()
