from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.utils.risk_calculator import RiskCalculator

# Create router for simulation endpoints
router = APIRouter()

class ClimateSimulationRequest(BaseModel):
    """Request model for climate risk simulation."""
    temperature: float = Field(..., description="Temperature in Celsius", ge=-50, le=60)
    humidity: float = Field(..., description="Humidity percentage", ge=0, le=100)
    rainfall: float = Field(..., description="Rainfall in mm", ge=0)

    class Config:
        schema_extra = {
            "example": {
                "temperature": 35.5,
                "humidity": 85.0,
                "rainfall": 120.0
            }
        }

@router.post("/simulate")
async def simulate_climate_risk(request: ClimateSimulationRequest):
    """
    Simulate climate risk assessment based on provided weather conditions.

    Accepts temperature, humidity, and rainfall values to simulate
    potential climate risks without fetching real weather data.

    Args:
        request (ClimateSimulationRequest): Weather parameters for simulation.

    Returns:
        Dict: Simulated risk assessment results.

    Raises:
        HTTPException: If risk calculation fails.
    """
    try:
        # Initialize risk calculator
        risk_calculator = RiskCalculator()

        # Prepare simulation data
        simulation_data = {
            "temp": request.temperature,
            "humidity": request.humidity,
            "rainfall": request.rainfall
        }

        # Calculate risks based on simulated weather data
        risk_result = risk_calculator.calculate_risks(simulation_data)

        if risk_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail="Risk calculation simulation failed"
            )

        # Prepare simulation response
        simulation_response = {
            "simulation_id": f"sim_{hash(str(simulation_data)) % 10000:04d}",
            "input_parameters": {
                "temperature": request.temperature,
                "humidity": request.humidity,
                "rainfall": request.rainfall
            },
            "risk_assessment": risk_result["data"],
            "simulation_type": "climate_risk_assessment"
        }

        return {
            "status": "success",
            "data": simulation_response
        }

    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Simulation error: {str(e)}"
        )