from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.weather_service import WeatherService
from app.services.weather_risk_data_service import WeatherRiskDataService
from app.utils.risk_predictor import predict_climate_risk

# Create router for risk endpoints
router = APIRouter()

@router.get("/risk")
async def get_risk(city: Optional[str] = Query("Wayanad", description="City name for weather data")):
    """
    Get climate risk assessment for a specified city.

    Fetches real-time weather data, predicts risk level, and stores data.

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
        data_service = WeatherRiskDataService()

        # Fetch weather data
        weather_result = weather_service.get_weather(city)

        if weather_result["status"] != "success":
            raise HTTPException(
                status_code=503,
                detail=f"Weather service error: {weather_result.get('message', 'Unknown error')}"
            )

        weather_data = weather_result["data"]

        # Predict risk using the new predictor
        risk_level, risk_assessment = predict_climate_risk(
            temperature=weather_data["temp"],
            humidity=weather_data["humidity"],
            rainfall=weather_data["rainfall"]
        )

        # Store data in database
        storage_result = data_service.insert_weather_risk_data(
            city=city,
            temperature=weather_data["temp"],
            humidity=weather_data["humidity"],
            rainfall=weather_data["rainfall"],
            risk_level=risk_level.value,
            risk_details=risk_assessment
        )

        # Log storage result (but don't fail the request if storage fails)
        if storage_result["status"] != "success":
            print(f"Warning: Failed to store data: {storage_result.get('message')}")

        # Combine weather and risk data
        combined_data = {
            "location": weather_data["city"],
            "weather": {
                "temperature": weather_data["temp"],
                "humidity": weather_data["humidity"],
                "rainfall": weather_data["rainfall"]
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
            }
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

@router.get("/risk/history")
async def get_risk_history(city: Optional[str] = Query(None, description="Filter by city name"),
                          limit: int = Query(50, description="Maximum number of records to return", ge=1, le=1000)):
    """
    Get historical weather and risk data.

    Args:
        city (str, optional): Filter by city name. If not provided, returns all cities.
        limit (int): Maximum number of records to return (1-1000).

    Returns:
        Dict: Historical weather and risk data.

    Raises:
        HTTPException: If database query fails.
    """
    try:
        data_service = WeatherRiskDataService()
        result = data_service.get_weather_risk_history(city=city, limit=limit)

        if result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Database query failed: {result.get('message', 'Unknown error')}"
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/risk/statistics")
async def get_risk_statistics(city: Optional[str] = Query(None, description="Filter by city name"),
                             days: int = Query(7, description="Number of days to look back", ge=1, le=365)):
    """
    Get risk level statistics for the specified period.

    Args:
        city (str, optional): Filter by city name. If not provided, returns global statistics.
        days (int): Number of days to look back (1-365).

    Returns:
        Dict: Risk statistics for the period.

    Raises:
        HTTPException: If database query fails.
    """
    try:
        data_service = WeatherRiskDataService()
        result = data_service.get_risk_statistics(city=city, days=days)

        if result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Database query failed: {result.get('message', 'Unknown error')}"
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )