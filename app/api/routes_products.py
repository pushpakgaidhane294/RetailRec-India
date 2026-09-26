"""
Product and Catalog API Endpoints for RetailRec India.
"""
from typing import List, Optional
from fastapi import APIRouter, Query

from app.models.schemas import ProductItem
from app.services.product_service import product_service

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[ProductItem])
def list_products(
    category: Optional[str] = Query(None, description="Filter by product category"),
    sort_by: str = Query("total_sales", description="Field to sort by (total_sales, total_quantity_sold, avg_price)"),
    ascending: bool = Query(False, description="Sort ascending order"),
):
    """List all authentic catalog sub-categories with sales, order count, and customer metrics."""
    return product_service.list_products(category=category, sort_by=sort_by, ascending=ascending)


@router.get("/search", response_model=List[ProductItem])
def search_products(
    q: Optional[str] = Query(None, description="Search query across sub-category or category name"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """Search catalog items by keyword and category."""
    return product_service.list_products(query=q, category=category)


@router.get("/categories", response_model=List[str])
def list_categories():
    """List all authentic categories present in the dataset."""
    return product_service.list_categories()
