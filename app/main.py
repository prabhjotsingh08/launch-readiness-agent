from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug: Print environment variables (without sensitive values)
logger.info("Environment variables loaded:")
logger.info(f"LINEAR_API_KEY set: {'Yes' if os.getenv('LINEAR_API_KEY') else 'No'}")
logger.info(f"LINEAR_API_URL set: {'Yes' if os.getenv('LINEAR_API_URL') else 'No'}")
logger.info(f"GITHUB_WEBHOOK_SECRET set: {'Yes' if os.getenv('GITHUB_WEBHOOK_SECRET') else 'No'}")

app = FastAPI(
    title="Launch Readiness Agent",
    description="API for synchronizing GitHub events with Linear projects",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Import and include routers
from app.routers import github, linear

app.include_router(github.router, prefix="/api/github", tags=["github"])
app.include_router(linear.router, prefix="/api/linear", tags=["linear"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 