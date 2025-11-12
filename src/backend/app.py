"""
Pet Battler - FastAPI Backend Main Application
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .routes import creature_router, game_router
from .middleware.rate_limit import RateLimitMiddleware

# Create FastAPI app
app = FastAPI(
    title="Pet Battler API",
    description="Tournament-style creature battle game API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Include routers
app.include_router(creature_router)
app.include_router(game_router)

# Mount static files and serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML."""
        return FileResponse(str(frontend_path / "index.html"))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pet-battler-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
