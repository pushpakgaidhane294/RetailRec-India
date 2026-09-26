"""
Analytics and Statistics API Endpoints for RetailRec India.
"""
from fastapi import APIRouter
from app.models.schemas import DashboardStats, AnalyticsResponse
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/api", tags=["Analytics & Statistics"])


@router.get("/stats", response_model=DashboardStats)
def get_stats():
    """Retrieve top-level authentic KPIs and overview numbers."""
    return analytics_service.get_kpis()


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    """Retrieve comprehensive analytics data for charts, distributions, and trends."""
    return analytics_service.get_full_analytics()
