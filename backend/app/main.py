from fastapi import FastAPI

app = FastAPI(
    title="CodeForge AI",
    description="AI-powered codebase intelligence platform",
    version="1.0.0"
)


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