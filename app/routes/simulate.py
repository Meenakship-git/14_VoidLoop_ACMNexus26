from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.weather_risk_data_service import WeatherRiskDataService
from app.utils.simulation_engine import (
    ClimateSimulationEngine,
    SimulationScenario,
    simulate_climate_scenario,
    simulate_predefined_scenario,
    PREDEFINED_SCENARIOS
)

# Create router for simulation endpoints
router = APIRouter()

class ClimateSimulationRequest(BaseModel):
    """Request model for climate risk simulation."""
    temperature: float = Field(..., description="Temperature in Celsius", ge=-50, le=60)
    humidity: float = Field(..., description="Humidity percentage", ge=0, le=100)
    rainfall: float = Field(..., description="Rainfall in mm", ge=0)
    city: str = Field("Simulation", description="City name for simulation (optional)")
    scenario_name: str = Field("custom", description="Name for this simulation scenario")

    class Config:
        schema_extra = {
            "example": {
                "temperature": 35.5,
                "humidity": 85.0,
                "rainfall": 120.0,
                "city": "Wayanad",
                "scenario_name": "heatwave_simulation"
            }
        }

class BatchSimulationRequest(BaseModel):
    """Request model for batch climate risk simulation."""
    scenarios: List[Dict[str, Any]] = Field(..., description="List of simulation scenarios")
    city: str = Field("BatchSimulation", description="City name for batch simulation")

    class Config:
        schema_extra = {
            "example": {
                "scenarios": [
                    {"temperature": 25.0, "humidity": 50.0, "rainfall": 0.0, "name": "normal"},
                    {"temperature": 35.0, "humidity": 80.0, "rainfall": 10.0, "name": "hot_humid"},
                    {"temperature": 20.0, "humidity": 90.0, "rainfall": 50.0, "name": "rainy"}
                ],
                "city": "TestCity"
            }
        }

class RangeSimulationRequest(BaseModel):
    """Request model for range-based climate risk simulation."""
    temperature_range: List[float] = Field(..., description="Min/max temperature range", min_items=2, max_items=2)
    humidity_range: List[float] = Field(..., description="Min/max humidity range", min_items=2, max_items=2)
    rainfall_range: List[float] = Field(..., description="Min/max rainfall range", min_items=2, max_items=2)
    steps: int = Field(3, description="Number of steps for each parameter", ge=2, le=10)
    city: str = Field("RangeSimulation", description="City name for range simulation")

    class Config:
        schema_extra = {
            "example": {
                "temperature_range": [20.0, 40.0],
                "humidity_range": [30.0, 90.0],
                "rainfall_range": [0.0, 25.0],
                "steps": 3,
                "city": "ClimateStudy"
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
        # Create simulation scenario
        scenario = SimulationScenario(
            name=request.scenario_name,
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall,
            description=f"Custom simulation: {request.temperature}°C, {request.humidity}%, {request.rainfall}mm"
        )

        # Run simulation using the engine
        simulation_result = simulate_climate_scenario(
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall,
            scenario_name=request.scenario_name
        )

        # Store simulation data in database
        data_service = WeatherRiskDataService()
        storage_result = data_service.insert_weather_risk_data(
            city=request.city,
            temperature=request.temperature,
            humidity=request.humidity,
            rainfall=request.rainfall,
            risk_level=simulation_result.risk_level.value,
            risk_details={
                **simulation_result.risk_assessment,
                "simulation": True,
                "simulation_id": simulation_result.simulation_id,
                "processing_time_ms": simulation_result.processing_time_ms
            }
        )

        # Log storage result (but don't fail the request if storage fails)
        if storage_result["status"] != "success":
            print(f"Warning: Failed to store simulation data: {storage_result.get('message')}")

        # Prepare simulation response
        simulation_response = {
            "simulation_id": simulation_result.simulation_id,
            "scenario": {
                "name": scenario.name,
                "temperature": scenario.temperature,
                "humidity": scenario.humidity,
                "rainfall": scenario.rainfall,
                "description": scenario.description
            },
            "input_parameters": {
                "temperature": request.temperature,
                "humidity": request.humidity,
                "rainfall": request.rainfall,
                "city": request.city,
                "scenario_name": request.scenario_name
            },
            "risk_assessment": {
                "risk_level": simulation_result.risk_level.value,
                "individual_assessments": simulation_result.risk_assessment["individual_assessments"],
                "risk_factors": simulation_result.risk_assessment["risk_factors"],
                "recommendations": simulation_result.risk_assessment["recommendations"]
            },
            "performance": {
                "processing_time_ms": simulation_result.processing_time_ms,
                "timestamp": simulation_result.timestamp.isoformat()
            },
            "data_storage": {
                "stored": storage_result["status"] == "success",
                "message": storage_result.get("message", "Storage status unknown")
            },
            "simulation_type": "single_scenario"
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

@router.post("/simulate/batch")
async def simulate_batch_climate_risk(request: BatchSimulationRequest):
    """
    Simulate multiple climate risk scenarios in batch.

    Accepts a list of weather scenarios and simulates risk for each.

    Args:
        request (BatchSimulationRequest): Batch simulation parameters.

    Returns:
        Dict: Batch simulation results with individual and summary data.

    Raises:
        HTTPException: If batch simulation fails.
    """
    try:
        # Initialize services
        data_service = WeatherRiskDataService()
        simulation_engine = ClimateSimulationEngine()

        # Convert request scenarios to SimulationScenario objects
        scenarios = []
        for scenario_data in request.scenarios:
            scenario = SimulationScenario(
                name=scenario_data.get("name", f"scenario_{len(scenarios)}"),
                temperature=scenario_data["temperature"],
                humidity=scenario_data["humidity"],
                rainfall=scenario_data["rainfall"],
                description=scenario_data.get("description", "Batch scenario")
            )
            scenarios.append(scenario)

        # Run batch simulation
        batch_results = simulation_engine.simulate_batch_scenarios(scenarios)

        # Store batch results in database
        stored_count = 0
        for result in batch_results:
            storage_result = data_service.insert_weather_risk_data(
                city=request.city,
                temperature=result.scenario.temperature,
                humidity=result.scenario.humidity,
                rainfall=result.scenario.rainfall,
                risk_level=result.risk_level.value,
                risk_details={
                    **result.risk_assessment,
                    "simulation": True,
                    "simulation_id": result.simulation_id,
                    "batch_simulation": True,
                    "processing_time_ms": result.processing_time_ms
                }
            )
            if storage_result["status"] == "success":
                stored_count += 1

        # Get risk distribution analysis
        risk_distribution = simulation_engine.get_risk_distribution(batch_results)

        # Prepare batch response
        batch_response = {
            "batch_id": f"batch_{datetime.now().strftime('%H%M%S')}",
            "total_scenarios": len(scenarios),
            "successful_simulations": len(batch_results),
            "scenarios": [
                {
                    "simulation_id": result.simulation_id,
                    "scenario": {
                        "name": result.scenario.name,
                        "temperature": result.scenario.temperature,
                        "humidity": result.scenario.humidity,
                        "rainfall": result.scenario.rainfall,
                        "description": result.scenario.description
                    },
                    "risk_level": result.risk_level.value,
                    "processing_time_ms": result.processing_time_ms
                }
                for result in batch_results
            ],
            "risk_distribution": risk_distribution,
            "data_storage": {
                "stored_count": stored_count,
                "total_count": len(batch_results),
                "success_rate": round((stored_count / len(batch_results)) * 100, 2) if batch_results else 0
            },
            "simulation_type": "batch_scenarios"
        }

        return {
            "status": "success",
            "data": batch_response
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch simulation error: {str(e)}"
        )

@router.post("/simulate/range")
async def simulate_range_climate_risk(request: RangeSimulationRequest):
    """
    Simulate climate risk across a range of weather conditions.

    Creates a grid of scenarios covering specified ranges and simulates risk.

    Args:
        request (RangeSimulationRequest): Range simulation parameters.

    Returns:
        Dict: Range simulation results with grid analysis.

    Raises:
        HTTPException: If range simulation fails.
    """
    try:
        # Initialize services
        data_service = WeatherRiskDataService()
        simulation_engine = ClimateSimulationEngine()

        # Run range simulation
        range_results = simulation_engine.simulate_weather_range(
            temp_range=tuple(request.temperature_range),
            humidity_range=tuple(request.humidity_range),
            rainfall_range=tuple(request.rainfall_range),
            steps=request.steps
        )

        # Store range results in database (sample only, not all to avoid overload)
        stored_count = 0
        max_storage = min(50, len(range_results))  # Limit storage to prevent database overload

        for i, result in enumerate(range_results):
            if i >= max_storage:
                break
            storage_result = data_service.insert_weather_risk_data(
                city=request.city,
                temperature=result.scenario.temperature,
                humidity=result.scenario.humidity,
                rainfall=result.scenario.rainfall,
                risk_level=result.risk_level.value,
                risk_details={
                    **result.risk_assessment,
                    "simulation": True,
                    "simulation_id": result.simulation_id,
                    "range_simulation": True,
                    "processing_time_ms": result.processing_time_ms
                }
            )
            if storage_result["status"] == "success":
                stored_count += 1

        # Get risk distribution analysis
        risk_distribution = simulation_engine.get_risk_distribution(range_results)

        # Calculate average processing time
        avg_processing_time = sum(r.processing_time_ms for r in range_results) / len(range_results)

        # Prepare range response
        range_response = {
            "range_id": f"range_{datetime.now().strftime('%H%M%S')}",
            "parameter_ranges": {
                "temperature": request.temperature_range,
                "humidity": request.humidity_range,
                "rainfall": request.rainfall_range
            },
            "steps": request.steps,
            "total_scenarios": len(range_results),
            "risk_distribution": risk_distribution,
            "performance": {
                "average_processing_time_ms": round(avg_processing_time, 2),
                "total_processing_time_ms": round(sum(r.processing_time_ms for r in range_results), 2)
            },
            "data_storage": {
                "stored_count": stored_count,
                "sampled_from": len(range_results),
                "storage_limited": len(range_results) > max_storage
            },
            "simulation_type": "range_analysis"
        }

        return {
            "status": "success",
            "data": range_response
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Range simulation error: {str(e)}"
        )

@router.get("/simulate/scenarios")
async def get_predefined_scenarios():
    """
    Get list of predefined simulation scenarios.

    Returns:
        Dict: Available predefined scenarios for quick testing.
    """
    try:
        scenarios_info = []
        for key, scenario in PREDEFINED_SCENARIOS.items():
            scenarios_info.append({
                "key": key,
                "name": scenario.name,
                "description": scenario.description,
                "parameters": {
                    "temperature": scenario.temperature,
                    "humidity": scenario.humidity,
                    "rainfall": scenario.rainfall
                }
            })

        return {
            "status": "success",
            "data": {
                "scenarios": scenarios_info,
                "count": len(scenarios_info)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving scenarios: {str(e)}"
        )

@router.get("/simulate/scenarios/{scenario_key}")
async def simulate_predefined_scenario_endpoint(scenario_key: str):
    """
    Simulate a predefined climate risk scenario.

    Args:
        scenario_key (str): Key of the predefined scenario.

    Returns:
        Dict: Simulation result for the predefined scenario.

    Raises:
        HTTPException: If scenario key is invalid or simulation fails.
    """
    try:
        # Run predefined scenario simulation
        simulation_result = simulate_predefined_scenario(scenario_key)

        # Prepare response
        scenario_response = {
            "simulation_id": simulation_result.simulation_id,
            "scenario": {
                "key": scenario_key,
                "name": simulation_result.scenario.name,
                "description": simulation_result.scenario.description,
                "parameters": {
                    "temperature": simulation_result.scenario.temperature,
                    "humidity": simulation_result.scenario.humidity,
                    "rainfall": simulation_result.scenario.rainfall
                }
            },
            "risk_assessment": {
                "risk_level": simulation_result.risk_level.value,
                "individual_assessments": simulation_result.risk_assessment["individual_assessments"],
                "risk_factors": simulation_result.risk_assessment["risk_factors"],
                "recommendations": simulation_result.risk_assessment["recommendations"]
            },
            "performance": {
                "processing_time_ms": simulation_result.processing_time_ms,
                "timestamp": simulation_result.timestamp.isoformat()
            },
            "simulation_type": "predefined_scenario"
        }

        return {
            "status": "success",
            "data": scenario_response
        }

    except KeyError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Predefined scenario simulation error: {str(e)}"
        )