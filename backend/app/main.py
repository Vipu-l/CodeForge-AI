from fastapi import FastAPI
from app.routes.repository import router as repository_router
from fastapi.middleware.cors import CORSMiddleware
from app.routes.question import router as question_router


app = FastAPI(
    title="CodeForge AI",
    description="AI-powered codebase intelligence platform",
    version="1.0.0"
)

app.include_router(repository_router)
app.include_router(question_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to CodeForge AI"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeForge AI"
    }


@app.get("/api/info")
def project_info():
    return {
        "name": "CodeForge AI",
        "version": "1.0.0",
        "description": "AI-powered codebase analysis and developer assistant"
    }


@app.get("/api/status")
def project_status():
    return {
        "project": "CodeForge AI",
        "day": 1,
        "status": "development"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)