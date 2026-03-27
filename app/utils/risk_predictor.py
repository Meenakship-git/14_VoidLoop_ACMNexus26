from typing import Dict, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Enumeration of possible risk levels."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

class ClimateRiskPredictor:
    """
    Simple rule-based climate risk prediction model.

    This predictor uses configurable thresholds to assess climate risk
    based on temperature, humidity, and rainfall inputs. Designed to be
    easily upgradeable to machine learning models in the future.

    Risk Assessment Rules:
    - Temperature: High temperatures increase risk
    - Humidity: High humidity combined with temperature increases risk
    - Rainfall: Heavy rainfall increases risk
    - Combined factors: Multiple high-risk conditions escalate overall risk
    """

    def __init__(self):
        """
        Initialize the risk predictor with default thresholds.

        Thresholds can be adjusted based on domain knowledge or
        calibrated against historical data.
        """
        # Temperature thresholds (°C)
        self.temp_thresholds = {
            'low_risk_max': 25.0,      # Below this: low risk
            'moderate_risk_max': 35.0, # Between low_risk_max and this: moderate risk
            # Above moderate_risk_max: high risk
        }

        # Humidity thresholds (%)
        self.humidity_thresholds = {
            'low_risk_max': 60.0,      # Below this: low risk
            'moderate_risk_max': 80.0, # Between low_risk_max and this: moderate risk
            # Above moderate_risk_max: high risk
        }

        # Rainfall thresholds (mm)
        self.rainfall_thresholds = {
            'low_risk_max': 5.0,       # Below this: low risk
            'moderate_risk_max': 25.0, # Between low_risk_max and this: moderate risk
            # Above moderate_risk_max: high risk
        }

        # Risk escalation rules (number of high-risk conditions)
        self.risk_escalation = {
            'high_conditions_for_moderate': 1,  # 1+ high conditions = at least moderate
            'high_conditions_for_high': 2,      # 2+ high conditions = high risk
        }

    def predict_risk(self, temperature: float, humidity: float,
                    rainfall: float) -> Tuple[RiskLevel, Dict[str, Any]]:
        """
        Predict climate risk level based on weather conditions.

        Args:
            temperature (float): Temperature in Celsius
            humidity (float): Humidity percentage (0-100)
            rainfall (float): Rainfall in millimeters

        Returns:
            Tuple[RiskLevel, Dict[str, Any]]: Risk level and detailed assessment

        Raises:
            ValueError: If input values are outside reasonable ranges
        """
        # Input validation
        self._validate_inputs(temperature, humidity, rainfall)

        # Assess individual risk factors
        temp_risk = self._assess_temperature_risk(temperature)
        humidity_risk = self._assess_humidity_risk(humidity)
        rainfall_risk = self._assess_rainfall_risk(rainfall)

        # Combine assessments using escalation rules
        overall_risk = self._combine_risk_assessments(temp_risk, humidity_risk, rainfall_risk)

        # Prepare detailed assessment
        assessment = {
            'risk_level': overall_risk.value,
            'individual_assessments': {
                'temperature': {
                    'value': temperature,
                    'risk_level': temp_risk.value,
                    'threshold_used': self._get_temp_threshold(temp_risk)
                },
                'humidity': {
                    'value': humidity,
                    'risk_level': humidity_risk.value,
                    'threshold_used': self._get_humidity_threshold(humidity_risk)
                },
                'rainfall': {
                    'value': rainfall,
                    'risk_level': rainfall_risk.value,
                    'threshold_used': self._get_rainfall_threshold(rainfall_risk)
                }
            },
            'risk_factors': self._count_risk_factors(temp_risk, humidity_risk, rainfall_risk),
            'recommendations': self._generate_recommendations(overall_risk)
        }

        logger.info(f"Risk prediction: {temperature}°C, {humidity}%, {rainfall}mm -> {overall_risk.value}")

        return overall_risk, assessment

    def _validate_inputs(self, temperature: float, humidity: float, rainfall: float) -> None:
        """Validate input parameters."""
        if not isinstance(temperature, (int, float)) or temperature < -50 or temperature > 60:
            raise ValueError(f"Temperature must be between -50°C and 60°C, got {temperature}")

        if not isinstance(humidity, (int, float)) or humidity < 0 or humidity > 100:
            raise ValueError(f"Humidity must be between 0% and 100%, got {humidity}")

        if not isinstance(rainfall, (int, float)) or rainfall < 0:
            raise ValueError(f"Rainfall must be non-negative, got {rainfall}")

    def _assess_temperature_risk(self, temperature: float) -> RiskLevel:
        """Assess risk based on temperature."""
        if temperature <= self.temp_thresholds['low_risk_max']:
            return RiskLevel.LOW
        elif temperature <= self.temp_thresholds['moderate_risk_max']:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.HIGH

    def _assess_humidity_risk(self, humidity: float) -> RiskLevel:
        """Assess risk based on humidity."""
        if humidity <= self.humidity_thresholds['low_risk_max']:
            return RiskLevel.LOW
        elif humidity <= self.humidity_thresholds['moderate_risk_max']:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.HIGH

    def _assess_rainfall_risk(self, rainfall: float) -> RiskLevel:
        """Assess risk based on rainfall."""
        if rainfall <= self.rainfall_thresholds['low_risk_max']:
            return RiskLevel.LOW
        elif rainfall <= self.rainfall_thresholds['moderate_risk_max']:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.HIGH

    def _combine_risk_assessments(self, temp_risk: RiskLevel,
                                humidity_risk: RiskLevel,
                                rainfall_risk: RiskLevel) -> RiskLevel:
        """
        Combine individual risk assessments using escalation rules.

        Logic:
        - If any factor is HIGH, risk is at least MODERATE
        - If 2+ factors are HIGH, risk is HIGH
        - Otherwise, use the highest individual risk level
        """
        risk_levels = [temp_risk, humidity_risk, rainfall_risk]
        high_count = sum(1 for risk in risk_levels if risk == RiskLevel.HIGH)

        if high_count >= self.risk_escalation['high_conditions_for_high']:
            return RiskLevel.HIGH
        elif high_count >= self.risk_escalation['high_conditions_for_moderate']:
            return RiskLevel.MODERATE
        else:
            # Return the highest individual risk
            if RiskLevel.HIGH in risk_levels:
                return RiskLevel.HIGH
            elif RiskLevel.MODERATE in risk_levels:
                return RiskLevel.MODERATE
            else:
                return RiskLevel.LOW

    def _count_risk_factors(self, temp_risk: RiskLevel,
                          humidity_risk: RiskLevel,
                          rainfall_risk: RiskLevel) -> Dict[str, int]:
        """Count the number of factors at each risk level."""
        return {
            'high': sum(1 for risk in [temp_risk, humidity_risk, rainfall_risk]
                       if risk == RiskLevel.HIGH),
            'moderate': sum(1 for risk in [temp_risk, humidity_risk, rainfall_risk]
                           if risk == RiskLevel.MODERATE),
            'low': sum(1 for risk in [temp_risk, humidity_risk, rainfall_risk]
                      if risk == RiskLevel.LOW)
        }

    def _generate_recommendations(self, overall_risk: RiskLevel) -> list:
        """Generate recommendations based on overall risk level."""
        recommendations = []

        if overall_risk == RiskLevel.HIGH:
            recommendations.extend([
                "⚠️  High risk conditions detected - take immediate precautions",
                "Avoid outdoor activities during peak heat/humidity",
                "Stay hydrated and monitor weather updates",
                "Prepare emergency supplies for potential severe weather"
            ])
        elif overall_risk == RiskLevel.MODERATE:
            recommendations.extend([
                "⚡ Moderate risk - stay alert to changing conditions",
                "Limit prolonged outdoor exposure",
                "Keep emergency kit ready",
                "Monitor local weather forecasts"
            ])
        else:  # LOW
            recommendations.extend([
                "✅ Low risk conditions - normal activities can continue",
                "Stay aware of any sudden weather changes",
                "Enjoy outdoor activities with standard precautions"
            ])

        return recommendations

    def _get_temp_threshold(self, risk_level: RiskLevel) -> str:
        """Get the temperature threshold description for a risk level."""
        if risk_level == RiskLevel.LOW:
            return f"≤{self.temp_thresholds['low_risk_max']}°C"
        elif risk_level == RiskLevel.MODERATE:
            return f"{self.temp_thresholds['low_risk_max']+0.1:.1f}°C - {self.temp_thresholds['moderate_risk_max']}°C"
        else:
            return f">{self.temp_thresholds['moderate_risk_max']}°C"

    def _get_humidity_threshold(self, risk_level: RiskLevel) -> str:
        """Get the humidity threshold description for a risk level."""
        if risk_level == RiskLevel.LOW:
            return f"≤{self.humidity_thresholds['low_risk_max']}%"
        elif risk_level == RiskLevel.MODERATE:
            return f"{self.humidity_thresholds['low_risk_max']+0.1:.1f}% - {self.humidity_thresholds['moderate_risk_max']}%"
        else:
            return f">{self.humidity_thresholds['moderate_risk_max']}%"

    def _get_rainfall_threshold(self, risk_level: RiskLevel) -> str:
        """Get the rainfall threshold description for a risk level."""
        if risk_level == RiskLevel.LOW:
            return f"≤{self.rainfall_thresholds['low_risk_max']}mm"
        elif risk_level == RiskLevel.MODERATE:
            return f"{self.rainfall_thresholds['low_risk_max']+0.1:.1f}mm - {self.rainfall_thresholds['moderate_risk_max']}mm"
        else:
            return f">{self.rainfall_thresholds['moderate_risk_max']}mm"

    def update_thresholds(self, temp_thresholds: Dict[str, float] = None,
                         humidity_thresholds: Dict[str, float] = None,
                         rainfall_thresholds: Dict[str, float] = None) -> None:
        """
        Update risk assessment thresholds.

        This method allows for dynamic threshold updates, which could be
        useful for calibration or seasonal adjustments.

        Args:
            temp_thresholds: New temperature thresholds
            humidity_thresholds: New humidity thresholds
            rainfall_thresholds: New rainfall thresholds
        """
        if temp_thresholds:
            self.temp_thresholds.update(temp_thresholds)
        if humidity_thresholds:
            self.humidity_thresholds.update(humidity_thresholds)
        if rainfall_thresholds:
            self.rainfall_thresholds.update(rainfall_thresholds)

        logger.info("Risk prediction thresholds updated")

# Global instance for easy access
default_predictor = ClimateRiskPredictor()

def predict_climate_risk(temperature: float, humidity: float,
                        rainfall: float) -> Tuple[RiskLevel, Dict[str, Any]]:
    """
    Convenience function to predict climate risk using default predictor.

    Args:
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage (0-100)
        rainfall (float): Rainfall in millimeters

    Returns:
        Tuple[RiskLevel, Dict[str, Any]]: Risk level and detailed assessment
    """
    return default_predictor.predict_risk(temperature, humidity, rainfall)