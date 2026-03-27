#!/usr/bin/env python3
"""
Test script for the climate simulation engine.
"""

from app.utils.simulation_engine import (
    ClimateSimulationEngine,
    SimulationScenario,
    simulate_climate_scenario,
    simulate_predefined_scenario,
    PREDEFINED_SCENARIOS
)

def test_single_simulation():
    """Test single scenario simulation."""
    print("🧪 Testing Single Scenario Simulation")
    print("=" * 40)

    # Test custom scenario
    scenario = SimulationScenario(
        name="test_scenario",
        temperature=32.0,
        humidity=75.0,
        rainfall=12.0,
        description="Test hot and humid conditions"
    )

    engine = ClimateSimulationEngine()
    result = engine.simulate_single_scenario(scenario)

    print(f"Scenario: {result.scenario.name}")
    print(f"Input: {result.scenario.temperature}°C, {result.scenario.humidity}%, {result.scenario.rainfall}mm")
    print(f"Risk Level: {result.risk_level.value}")
    print(f"Processing Time: {result.processing_time_ms:.2f}ms")
    print(f"Simulation ID: {result.simulation_id}")

    # Test convenience function
    result2 = simulate_climate_scenario(25.0, 50.0, 0.0, "convenience_test")
    print(f"\nConvenience Function Test: {result2.risk_level.value}")

    print("✅ Single simulation test completed\n")

def test_batch_simulation():
    """Test batch scenario simulation."""
    print("🔄 Testing Batch Scenario Simulation")
    print("=" * 40)

    scenarios = [
        SimulationScenario("cool_dry", 18.0, 30.0, 0.0, "Cool and dry day"),
        SimulationScenario("warm_humid", 28.0, 70.0, 5.0, "Warm and humid"),
        SimulationScenario("hot_wet", 38.0, 85.0, 30.0, "Hot and wet conditions"),
        SimulationScenario("extreme", 45.0, 95.0, 80.0, "Extreme weather")
    ]

    engine = ClimateSimulationEngine()
    results = engine.simulate_batch_scenarios(scenarios)

    print(f"Processed {len(results)} scenarios:")
    for result in results:
        print(f"  {result.scenario.name}: {result.risk_level.value} "
              f"({result.processing_time_ms:.2f}ms)")

    # Test risk distribution
    distribution = engine.get_risk_distribution(results)
    print(f"\nRisk Distribution: {distribution['distribution']}")
    print(f"Most Common Risk: {distribution['most_common_risk']}")

    print("✅ Batch simulation test completed\n")

def test_range_simulation():
    """Test range-based simulation."""
    print("📊 Testing Range-Based Simulation")
    print("=" * 40)

    engine = ClimateSimulationEngine()
    results = engine.simulate_weather_range(
        temp_range=(20.0, 40.0),
        humidity_range=(40.0, 80.0),
        rainfall_range=(0.0, 20.0),
        steps=3
    )

    print(f"Generated {len(results)} scenarios from ranges")
    print("Sample results:")
    for i, result in enumerate(results[:5]):  # Show first 5
        print(f"  {i+1}. {result.scenario.temperature}°C, {result.scenario.humidity}%, "
              f"{result.scenario.rainfall}mm -> {result.risk_level.value}")

    distribution = engine.get_risk_distribution(results)
    print(f"\nOverall Risk Distribution: {distribution['distribution']}")

    print("✅ Range simulation test completed\n")

def test_predefined_scenarios():
    """Test predefined scenarios."""
    print("🎯 Testing Predefined Scenarios")
    print("=" * 40)

    print(f"Available predefined scenarios: {list(PREDEFINED_SCENARIOS.keys())}")

    for key in PREDEFINED_SCENARIOS.keys():
        try:
            result = simulate_predefined_scenario(key)
            print(f"  {key}: {result.scenario.description} -> {result.risk_level.value}")
        except Exception as e:
            print(f"  {key}: Error - {str(e)}")

    print("✅ Predefined scenarios test completed\n")

def test_performance():
    """Test simulation performance."""
    print("⚡ Testing Simulation Performance")
    print("=" * 40)

    import time

    # Test single simulation performance
    scenario = SimulationScenario("perf_test", 30.0, 60.0, 10.0)

    engine = ClimateSimulationEngine()

    # Warm up
    engine.simulate_single_scenario(scenario)

    # Time multiple runs
    runs = 10
    start_time = time.time()
    for _ in range(runs):
        engine.simulate_single_scenario(scenario)
    end_time = time.time()

    avg_time = ((end_time - start_time) / runs) * 1000
    print(f"Average single simulation time: {avg_time:.2f}ms")

    # Test batch performance
    scenarios = [SimulationScenario(f"batch_{i}", 25.0 + i, 50.0 + i, i)
                for i in range(20)]

    start_time = time.time()
    results = engine.simulate_batch_scenarios(scenarios)
    end_time = time.time()

    batch_time = (end_time - start_time) * 1000
    avg_batch_time = batch_time / len(scenarios)

    print(f"Batch of {len(scenarios)} simulations: {batch_time:.2f}ms total")
    print(f"Average per scenario: {avg_batch_time:.2f}ms")

    print("✅ Performance test completed\n")

if __name__ == "__main__":
    print("🚀 Climate Simulation Engine Test Suite")
    print("=" * 50)

    test_single_simulation()
    test_batch_simulation()
    test_range_simulation()
    test_predefined_scenarios()
    test_performance()

    print("🎉 All simulation engine tests completed!")