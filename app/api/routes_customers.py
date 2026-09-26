"""
Customer API Endpoints for RetailRec India.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import CustomerSummary, CustomerHistoryResponse
from app.services.customer_service import customer_service

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerSummary])
def list_customers(
    query: Optional[str] = Query(None, description="Search query matching customer name, ID, city, or state"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of customers to return"),
):
    """Retrieve list of customers with real aggregate metrics and profile information."""
    return customer_service.list_customers(query=query, limit=limit)


@router.get("/{customer_id}", response_model=CustomerSummary)
def get_customer(customer_id: str):
    """Retrieve detailed profile summary for a specific customer."""
    customer = customer_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer '{customer_id}' not found in historical sales records.",
        )
    return customer


@router.get("/{customer_id}/history", response_model=CustomerHistoryResponse)
def get_customer_history(
    customer_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by product category"),
    search: Optional[str] = Query(None, description="Search within item or order ID"),
):
    """Retrieve paginated purchase transaction history for a specific customer."""
    history = customer_service.get_customer_history(
        customer_query=customer_id,
        page=page,
        page_size=page_size,
        category=category,
        search=search,
    )
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No purchase history found for Customer '{customer_id}'.",
        )
    return history
