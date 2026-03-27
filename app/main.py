from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes import health, risk, simulate

# Create FastAPI application instance
app = FastAPI(
    title="AlertWave API",
    description="Production-ready FastAPI backend for AlertWave",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(risk.router)
app.include_router(simulate.router)

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "status": "success",
        "data": {
            "message": "Welcome to AlertWave API",
            "version": "1.0.0"
        }
    }