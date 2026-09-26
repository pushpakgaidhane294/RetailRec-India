"""
Main FastAPI Application for RetailRec India.
Serves both backend REST APIs and frontend UI with preloaded ML artifacts.
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings, FRONTEND_DIR, MODEL_FILE, PROCESSED_SALES_FILE
from app.models.schemas import HealthResponse
from app.api import (
    routes_customers,
    routes_recommendations,
    routes_products,
    routes_analytics,
    routes_model,
)
from ml.predict import recommender_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager: loads ML artifacts once during startup."""
    logger.info("Initializing RetailRec India application...")
    try:
        recommender_service.load_artifacts()
        logger.info("All ML artifacts successfully initialized.")
    except Exception as e:
        logger.warning(f"Could not preload ML artifacts on startup: {e}. Inference will attempt on demand.")
    yield
    logger.info("Shutting down RetailRec India application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(routes_customers.router)
app.include_router(routes_recommendations.router)
app.include_router(routes_products.router)
app.include_router(routes_analytics.router)
app.include_router(routes_model.router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint for Render and monitoring."""
    if recommender_service.model is None and os.path.exists(MODEL_FILE):
        try:
            recommender_service.load_artifacts()
        except Exception:
            pass
    model_exists = os.path.exists(MODEL_FILE) and recommender_service.model is not None
    data_exists = os.path.exists(PROCESSED_SALES_FILE)
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model_loaded": model_exists,
        "data_loaded": data_exists,
    }


# Frontend HTML Page Routes
@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/recommendations", include_in_schema=False)
@app.get("/recommendations.html", include_in_schema=False)
def serve_recommendations():
    return FileResponse(os.path.join(FRONTEND_DIR, "recommendations.html"))


@app.get("/history", include_in_schema=False)
@app.get("/history.html", include_in_schema=False)
def serve_history():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))


@app.get("/products", include_in_schema=False)
@app.get("/products.html", include_in_schema=False)
def serve_products():
    return FileResponse(os.path.join(FRONTEND_DIR, "products.html"))


@app.get("/analytics", include_in_schema=False)
@app.get("/analytics.html", include_in_schema=False)
def serve_analytics():
    return FileResponse(os.path.join(FRONTEND_DIR, "analytics.html"))


@app.get("/model", include_in_schema=False)
@app.get("/model.html", include_in_schema=False)
def serve_model():
    return FileResponse(os.path.join(FRONTEND_DIR, "model.html"))


@app.get("/about", include_in_schema=False)
@app.get("/about.html", include_in_schema=False)
def serve_about():
    return FileResponse(os.path.join(FRONTEND_DIR, "about.html"))


# Mount static assets (css, js, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
# Also mount at root for relative subfolder asset paths (/css, /js)
if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
