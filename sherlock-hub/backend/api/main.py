"""
Sherlock Hub - Main FastAPI Application
Elite Intelligence Platform with Constitutional AI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.routes import entities, paths, qa, search, documents, nexus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sherlock Hub API",
    description="Elite Intelligence Platform with Graph Database and Constitutional AI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(entities.router, prefix="/api/entities", tags=["Entities"])
app.include_router(paths.router, prefix="/api/paths", tags=["Paths"])
app.include_router(qa.router, prefix="/api/qa", tags=["Q&A"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(nexus.router, prefix="/api/nexus", tags=["Nexus"])

@app.get("/")
async def root():
    return {"message": "Sherlock Hub API - Elite Intelligence Platform", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
