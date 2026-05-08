from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Connect to MongoDB
    logger.info("🚀 Starting up application...")
    try:
        await connect_to_mongo()
        logger.info("✅ Application startup complete")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Close MongoDB connection
    logger.info("🛑 Shutting down application...")
    await close_mongo_connection()
    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Sentiment Analysis API",
    description="API for sentiment analysis using OpenAI LLM with S3 and MongoDB integration",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
from app.middleware.auth import verify_auth_token
app.middleware("http")(verify_auth_token)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Sentiment Analysis API",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.app_env
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.app_env
    }


# Import and include routers
from app.routes import transcript, analysis, auth

# Auth routes (no authentication required)
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Protected routes (authentication required)
app.include_router(
    transcript.router,
    prefix="/api/transcripts",
    tags=["Transcripts"]
)

app.include_router(
    analysis.router,
    prefix="/api/analyses",
    tags=["Analyses"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
