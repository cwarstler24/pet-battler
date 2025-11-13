"""
Pet Battler - Main Entry Point
Run the FastAPI server for the Pet Battler game.
"""

import uvicorn

if __name__ == "__main__":
    print("🎮 Starting Pet Battler Server...")
    print("📍 Frontend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")

    uvicorn.run(
        "src.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
