from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.weather_service import WeatherService
from app.utils.risk_calculator import RiskCalculator

# Create router for risk endpoints
router = APIRouter()

@router.get("/risk")
async def get_risk(city: Optional[str] = Query("Wayanad", description="City name for weather data")):
    """
    Get climate risk assessment for a specified city.

    Fetches real-time weather data and calculates associated climate risks.

    Args:
        city (str): Name of the city to assess. Defaults to "Wayanad".

    Returns:
        Dict: Combined weather data and risk assessment results.

    Raises:
        HTTPException: If weather service or risk calculation fails.
    """
    try:
        # Initialize services
        weather_service = WeatherService()
        risk_calculator = RiskCalculator()

        # Fetch weather data
        weather_result = weather_service.get_weather(city)

        if weather_result["status"] != "success":
            raise HTTPException(
                status_code=503,
                detail=f"Weather service error: {weather_result.get('message', 'Unknown error')}"
            )

        weather_data = weather_result["data"]

        # Prepare weather data for risk calculation
        risk_input = {
            "temp": weather_data["temp"],
            "humidity": weather_data["humidity"],
            "rainfall": weather_data["rainfall"]
        }

        # Calculate risks
        risk_result = risk_calculator.calculate_risks(risk_input)

        if risk_result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail="Risk calculation failed"
            )

        # Combine weather and risk data
        combined_data = {
            "location": weather_data["city"],
            "weather": {
                "temperature": weather_data["temp"],
                "humidity": weather_data["humidity"],
                "rainfall": weather_data["rainfall"]
            },
            "risk_assessment": risk_result["data"]
        }

        return {
            "status": "success",
            "data": combined_data
        }

    except ValueError as e:
        # Weather service initialization error (missing API key)
        raise HTTPException(
            status_code=500,
            detail=f"Service configuration error: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )