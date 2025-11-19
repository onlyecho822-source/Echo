"""
Main FastAPI application for Echo Fact-Check.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import settings
from app.api.routes import audio, video, documents, factcheck, websocket

# Create FastAPI app
app = FastAPI(
    title="Echo Fact-Check",
    description="Real-time fact verification for audio, video, and documents",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(factcheck.router, prefix="/api/factcheck", tags=["Fact Check"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio Processing"])
app.include_router(video.router, prefix="/api/video", tags=["Video Processing"])
app.include_router(documents.router, prefix="/api/documents", tags=["Document Processing"])
app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """Serve the main frontend page."""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "app": "Echo Fact-Check",
        "version": "0.1.0",
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "has_ai_key": settings.has_ai_api_key(),
        "version": "0.1.0",
    }


@app.get("/api/config")
async def get_config():
    """Get public configuration."""
    return {
        "max_upload_size_mb": settings.max_upload_size_mb,
        "max_audio_duration_seconds": settings.max_audio_duration_seconds,
        "max_video_duration_seconds": settings.max_video_duration_seconds,
        "supported_audio_formats": ["mp3", "wav", "m4a", "ogg", "flac"],
        "supported_video_formats": ["mp4", "avi", "mov", "mkv", "webm"],
        "supported_document_formats": ["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    }


def run():
    """Run the application."""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
