from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.services.weather_risk_data_service import WeatherRiskDataService
from app.utils.risk_predictor import predict_climate_risk

# Create router for simulation endpoints
router = APIRouter()

class ClimateSimulationRequest(BaseModel):
    """Request model for climate risk simulation."""
    temperature: float = Field(..., description="Temperature in Celsius", ge=-50, le=60)
    humidity: float = Field(..., description="Humidity percentage", ge=0, le=100)
    rainfall: float = Field(..., description="Rainfall in mm", ge=0)
    city: str = Field("Simulation", description="City name for simulation (optional)")

    class Config:
        schema_extra = {
            "example": {
                "temperature": 35.5,
                "humidity": 85.0,
                "rainfall": 120.0,
                "city": "Wayanad"
            }
        }

@router.post("/simulate")
async def simulate_climate_risk(request: ClimateSimulationRequest):
    """
    Simulate climate risk assessment based on provided weather conditions.

    Accepts temperature, humidity, and rainfall values to simulate
    potential climate risks and stores the simulation data.

    Args:
        request (ClimateSimulationRequest): Weather parameters for simulation.

    Returns:
        Dict: Simulated risk assessment results.

    Raises:
        HTTPException: If risk calculation fails.
    """
    try:
        # Initialize services
        data_service = WeatherRiskDataService()

        # Predict risk using the new predictor
        risk_level, risk_assessment = predict_climate_risk(
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall
        )

        # Store simulation data in database
        storage_result = data_service.insert_weather_risk_data(
            city=request.city,
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall,
            risk_level=risk_level.value,
            risk_details={
                **risk_assessment,
                "simulation": True,
                "simulation_id": f"sim_{hash(str(request.dict())) % 10000:04d}"
            }
        )

        # Log storage result (but don't fail the request if storage fails)
        if storage_result["status"] != "success":
            print(f"Warning: Failed to store simulation data: {storage_result.get('message')}")

        # Prepare simulation response
        simulation_response = {
            "simulation_id": f"sim_{hash(str(request.dict())) % 10000:04d}",
            "input_parameters": {
                "temperature": request.temperature,
                "humidity": request.humidity,
                "rainfall": request.rainfall,
                "city": request.city
            },
            "risk_assessment": {
                "risk_level": risk_level.value,
                "individual_assessments": risk_assessment["individual_assessments"],
                "risk_factors": risk_assessment["risk_factors"],
                "recommendations": risk_assessment["recommendations"]
            },
            "data_storage": {
                "stored": storage_result["status"] == "success",
                "message": storage_result.get("message", "Storage status unknown")
            },
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