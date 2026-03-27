from fastapi import APIRouter

# Create router for health endpoints
router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the application.
    Used for monitoring and load balancer health checks.
    """
    return {
        "status": "success",
        "data": {
            "status": "healthy",
            "timestamp": "2023-01-01T00:00:00Z"  # In production, use actual timestamp
        }
    }