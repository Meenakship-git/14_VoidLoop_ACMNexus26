#!/usr/bin/env python3
"""
Test script for the new climate risk prediction model.
"""

from app.utils.risk_predictor import predict_climate_risk, ClimateRiskPredictor

def test_risk_predictor():
    """Test the risk predictor with various scenarios."""

    print("🧪 Testing Climate Risk Predictor")
    print("=" * 50)

    # Test cases with different weather conditions
    test_cases = [
        # (temperature, humidity, rainfall, expected_description)
        (20.0, 30.0, 0.0, "Low temperature, low humidity, no rain"),
        (25.0, 60.0, 2.0, "Moderate temperature, moderate humidity, light rain"),
        (35.0, 80.0, 15.0, "High temperature, high humidity, moderate rain"),
        (40.0, 90.0, 50.0, "Very high temperature, very high humidity, heavy rain"),
        (15.0, 95.0, 100.0, "Low temperature, extreme humidity, very heavy rain"),
    ]

    for temp, humidity, rainfall, description in test_cases:
        print(f"\n🌤️  Test Case: {description}")
        print(f"   Input: {temp}°C, {humidity}%, {rainfall}mm")

        try:
            risk_level, assessment = predict_climate_risk(temp, humidity, rainfall)

            print(f"   Risk Level: {risk_level.value}")
            print(f"   Risk Factors: {assessment['risk_factors']}")
            print(f"   Recommendations: {len(assessment['recommendations'])} items")

            # Show individual assessments
            for factor, details in assessment['individual_assessments'].items():
                print(f"   {factor.capitalize()}: {details['risk_level']} ({details['value']} {factor[:3]})")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    print("\n" + "=" * 50)
    print("✅ Risk predictor testing completed")

def test_threshold_updates():
    """Test updating thresholds."""

    print("\n🔧 Testing Threshold Updates")
    print("=" * 30)

    predictor = ClimateRiskPredictor()

    # Show original thresholds
    print("Original temperature thresholds:")
    print(f"  Low risk max: {predictor.temp_thresholds['low_risk_max']}°C")
    print(f"  Moderate risk max: {predictor.temp_thresholds['moderate_risk_max']}°C")

    # Update thresholds
    predictor.update_thresholds(temp_thresholds={
        'low_risk_max': 30.0,
        'moderate_risk_max': 40.0
    })

    print("Updated temperature thresholds:")
    print(f"  Low risk max: {predictor.temp_thresholds['low_risk_max']}°C")
    print(f"  Moderate risk max: {predictor.temp_thresholds['moderate_risk_max']}°C")

    # Test with updated thresholds
    risk_level, _ = predictor.predict_risk(35.0, 50.0, 5.0)
    print(f"Risk for 35°C with updated thresholds: {risk_level.value}")

    print("✅ Threshold update testing completed")

if __name__ == "__main__":
    test_risk_predictor()
    test_threshold_updates()