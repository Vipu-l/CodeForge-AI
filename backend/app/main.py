from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.repository import router as repository_router
from app.routes.question import router as question_router


app = FastAPI(
    title="CodeForge AI",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://code-forge-ai-gold.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(
    repository_router
)

app.include_router(
    question_router
)


# --------------------------------------------------
# Basic Routes
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "CodeForge AI backend is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/api/project")
def project_info():
    return {
        "name": "CodeForge AI",
        "description": (
            "AI-powered repository analysis "
            "and RAG-based code assistant."
        ),
    }


@app.get("/api/project/status")
def project_status():
    return {
        "status": "running",
        "service": "CodeForge AI",
    }