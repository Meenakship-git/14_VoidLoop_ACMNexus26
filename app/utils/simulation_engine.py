from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from app.utils.risk_predictor import predict_climate_risk, RiskLevel

logger = logging.getLogger(__name__)

@dataclass
class SimulationScenario:
    """
    Represents a single climate simulation scenario.

    Attributes:
        name (str): Scenario identifier/name
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage (0-100)
        rainfall (float): Rainfall in millimeters
        description (str, optional): Human-readable description
    """
    name: str
    temperature: float
    humidity: float
    rainfall: float
    description: Optional[str] = None

@dataclass
class SimulationResult:
    """
    Result of a climate risk simulation.

    Attributes:
        scenario (SimulationScenario): The input scenario
        risk_level (RiskLevel): Predicted risk level
        risk_assessment (Dict[str, Any]): Detailed risk assessment
        simulation_id (str): Unique simulation identifier
        timestamp (datetime): When simulation was run
        processing_time_ms (float): Time taken to process (milliseconds)
    """
    scenario: SimulationScenario
    risk_level: RiskLevel
    risk_assessment: Dict[str, Any]
    simulation_id: str
    timestamp: datetime
    processing_time_ms: float

class ClimateSimulationEngine:
    """
    Lightweight simulation engine for climate risk assessment.

    This engine provides fast, efficient simulation of climate risk scenarios
    using the underlying risk prediction model. Designed for both single
    scenario simulation and batch processing.
    """

    def __init__(self):
        """Initialize the simulation engine."""
        self.simulation_counter = 0

    def simulate_single_scenario(self, scenario: SimulationScenario) -> SimulationResult:
        """
        Simulate a single climate risk scenario.

        Args:
            scenario (SimulationScenario): The scenario to simulate

        Returns:
            SimulationResult: Complete simulation result

        Raises:
            ValueError: If scenario parameters are invalid
        """
        start_time = datetime.now()

        # Validate scenario
        self._validate_scenario(scenario)

        # Generate simulation ID
        simulation_id = self._generate_simulation_id()

        try:
            # Run risk prediction
            risk_level, risk_assessment = predict_climate_risk(
                temperature=scenario.temperature,
                humidity=scenario.humidity,
                rainfall=scenario.rainfall
            )

            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000

            # Create result
            result = SimulationResult(
                scenario=scenario,
                risk_level=risk_level,
                risk_assessment=risk_assessment,
                simulation_id=simulation_id,
                timestamp=end_time,
                processing_time_ms=round(processing_time, 2)
            )

            logger.info(f"Simulation {simulation_id} completed: {scenario.name} -> {risk_level.value} "
                       ".2f")

            return result

        except Exception as e:
            logger.error(f"Simulation failed for scenario {scenario.name}: {str(e)}")
            raise

    def simulate_batch_scenarios(self, scenarios: List[SimulationScenario]) -> List[SimulationResult]:
        """
        Simulate multiple climate risk scenarios in batch.

        Args:
            scenarios (List[SimulationScenario]): List of scenarios to simulate

        Returns:
            List[SimulationResult]: List of simulation results

        Raises:
            ValueError: If any scenario is invalid
        """
        if not scenarios:
            return []

        # Validate all scenarios first
        for scenario in scenarios:
            self._validate_scenario(scenario)

        results = []
        batch_start_time = datetime.now()

        for scenario in scenarios:
            try:
                result = self.simulate_single_scenario(scenario)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch simulation failed for scenario {scenario.name}: {str(e)}")
                # Continue with other scenarios but log the error
                continue

        batch_end_time = datetime.now()
        batch_time = (batch_end_time - batch_start_time).total_seconds() * 1000

        logger.info(f"Batch simulation completed: {len(results)}/{len(scenarios)} scenarios "
                   ".2f")

        return results

    def simulate_weather_range(self, temp_range: Tuple[float, float],
                             humidity_range: Tuple[float, float],
                             rainfall_range: Tuple[float, float],
                             steps: int = 5) -> List[SimulationResult]:
        """
        Simulate risk across a range of weather conditions.

        Creates a grid of scenarios covering the specified ranges and
        simulates risk for each combination.

        Args:
            temp_range (Tuple[float, float]): Min/max temperature
            humidity_range (Tuple[float, float]): Min/max humidity
            rainfall_range (Tuple[float, float]): Min/max rainfall
            steps (int): Number of steps for each parameter (default: 5)

        Returns:
            List[SimulationResult]: Simulation results for all combinations
        """
        # Generate parameter values using built-in range
        temp_values = [temp_range[0] + i * (temp_range[1] - temp_range[0]) / (steps - 1)
                      for i in range(steps)]
        humidity_values = [humidity_range[0] + i * (humidity_range[1] - humidity_range[0]) / (steps - 1)
                          for i in range(steps)]
        rainfall_values = [rainfall_range[0] + i * (rainfall_range[1] - rainfall_range[0]) / (steps - 1)
                          for i in range(steps)]

        scenarios = []
        scenario_count = 0

        # Create scenarios for all combinations
        for temp in temp_values:
            for humidity in humidity_values:
                for rainfall in rainfall_values:
                    scenario_count += 1
                    scenario = SimulationScenario(
                        name=f"range_sim_{scenario_count:03d}",
                        temperature=round(temp, 1),
                        humidity=round(humidity, 1),
                        rainfall=round(rainfall, 1),
                        description=f"T:{temp:.1f}°C, H:{humidity:.1f}%, R:{rainfall:.1f}mm"
                    )
                    scenarios.append(scenario)

        logger.info(f"Generated {len(scenarios)} scenarios for weather range simulation")
        return self.simulate_batch_scenarios(scenarios)

    def get_risk_distribution(self, results: List[SimulationResult]) -> Dict[str, Any]:
        """
        Analyze risk distribution from simulation results.

        Args:
            results (List[SimulationResult]): Simulation results to analyze

        Returns:
            Dict[str, Any]: Risk distribution statistics
        """
        if not results:
            return {"error": "No results to analyze"}

        risk_counts = {"Low": 0, "Moderate": 0, "High": 0}
        total_scenarios = len(results)

        for result in results:
            risk_counts[result.risk_level.value] += 1

        # Calculate percentages
        distribution = {}
        for risk_level, count in risk_counts.items():
            percentage = (count / total_scenarios) * 100
            distribution[risk_level.lower()] = {
                "count": count,
                "percentage": round(percentage, 2)
            }

        # Find most common risk level
        most_common = max(risk_counts.items(), key=lambda x: x[1])

        return {
            "total_scenarios": total_scenarios,
            "distribution": distribution,
            "most_common_risk": most_common[0],
            "risk_range": {
                "min": min(r.risk_level.value for r in results),
                "max": max(r.risk_level.value for r in results)
            }
        }

    def _validate_scenario(self, scenario: SimulationScenario) -> None:
        """Validate a simulation scenario."""
        if not isinstance(scenario.temperature, (int, float)) or not (-50 <= scenario.temperature <= 60):
            raise ValueError(f"Temperature must be between -50°C and 60°C, got {scenario.temperature}")

        if not isinstance(scenario.humidity, (int, float)) or not (0 <= scenario.humidity <= 100):
            raise ValueError(f"Humidity must be between 0% and 100%, got {scenario.humidity}")

        if not isinstance(scenario.rainfall, (int, float)) or scenario.rainfall < 0:
            raise ValueError(f"Rainfall must be non-negative, got {scenario.rainfall}")

    def _generate_simulation_id(self) -> str:
        """Generate a unique simulation ID."""
        self.simulation_counter += 1
        timestamp = datetime.now().strftime("%H%M%S")
        return f"sim_{timestamp}_{self.simulation_counter:04d}"

# Predefined common scenarios for quick testing
PREDEFINED_SCENARIOS = {
    "normal_day": SimulationScenario(
        name="normal_day",
        temperature=25.0,
        humidity=50.0,
        rainfall=0.0,
        description="Typical normal weather day"
    ),
    "hot_humid": SimulationScenario(
        name="hot_humid",
        temperature=35.0,
        humidity=80.0,
        rainfall=5.0,
        description="Hot and humid conditions"
    ),
    "heavy_rain": SimulationScenario(
        name="heavy_rain",
        temperature=22.0,
        humidity=90.0,
        rainfall=50.0,
        description="Heavy rainfall event"
    ),
    "extreme_heat": SimulationScenario(
        name="extreme_heat",
        temperature=45.0,
        humidity=20.0,
        rainfall=0.0,
        description="Extreme heat wave"
    ),
    "monsoon": SimulationScenario(
        name="monsoon",
        temperature=28.0,
        humidity=85.0,
        rainfall=25.0,
        description="Monsoon-like conditions"
    )
}

# Global simulation engine instance
simulation_engine = ClimateSimulationEngine()

def simulate_climate_scenario(temperature: float, humidity: float, rainfall: float,
                            scenario_name: str = "custom") -> SimulationResult:
    """
    Convenience function to simulate a single climate scenario.

    Args:
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage (0-100)
        rainfall (float): Rainfall in millimeters
        scenario_name (str): Name for the scenario

    Returns:
        SimulationResult: Simulation result
    """
    scenario = SimulationScenario(
        name=scenario_name,
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall
    )
    return simulation_engine.simulate_single_scenario(scenario)

def simulate_predefined_scenario(scenario_key: str) -> SimulationResult:
    """
    Simulate a predefined scenario.

    Args:
        scenario_key (str): Key from PREDEFINED_SCENARIOS

    Returns:
        SimulationResult: Simulation result

    Raises:
        KeyError: If scenario key doesn't exist
    """
    if scenario_key not in PREDEFINED_SCENARIOS:
        available = list(PREDEFINED_SCENARIOS.keys())
        raise KeyError(f"Scenario '{scenario_key}' not found. Available: {available}")

    return simulation_engine.simulate_single_scenario(PREDEFINED_SCENARIOS[scenario_key])