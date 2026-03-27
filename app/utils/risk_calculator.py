from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """Enumeration for risk severity levels."""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

@dataclass
class RiskRule:
    """
    Represents a single risk assessment rule.

    Attributes:
        name (str): Name of the risk (e.g., "Heatwave")
        condition (Callable): Function that takes weather data and returns bool
        emoji (str): Emoji representation of the risk
        severity (RiskLevel): Severity level of the risk
        description (str): Human-readable description of the risk
    """
    name: str
    condition: Callable[[Dict[str, float]], bool]
    emoji: str
    severity: RiskLevel
    description: str

class RiskCalculator:
    """
    Climate monitoring risk calculation system.

    This class evaluates weather data against predefined risk rules
    to determine potential climate-related risks and overall risk level.
    """

    def __init__(self):
        """Initialize the risk calculator with default risk rules."""
        self.risk_rules = self._initialize_risk_rules()

    def _initialize_risk_rules(self) -> List[RiskRule]:
        """
        Initialize the default set of risk assessment rules.

        Returns:
            List[RiskRule]: List of predefined risk rules
        """
        return [
            RiskRule(
                name="Heatwave",
                condition=lambda data: data.get("temp", 0) > 35,
                emoji="🔥",
                severity=RiskLevel.HIGH,
                description="Extreme high temperatures pose health risks"
            ),
            RiskRule(
                name="Flood Risk",
                condition=lambda data: data.get("rainfall", 0) > 100,
                emoji="🌧",
                severity=RiskLevel.HIGH,
                description="Heavy rainfall may cause flooding"
            ),
            RiskRule(
                name="Landslide Risk",
                condition=lambda data: data.get("humidity", 0) > 90,
                emoji="🏔",
                severity=RiskLevel.MODERATE,
                description="High humidity increases landslide probability"
            ),
            # Additional rules can be easily added here
        ]

    def add_risk_rule(self, rule: RiskRule) -> None:
        """
        Add a new risk rule to the calculator.

        Args:
            rule (RiskRule): The risk rule to add
        """
        self.risk_rules.append(rule)

    def calculate_risks(self, weather_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate risks based on weather data.

        Args:
            weather_data (Dict[str, float]): Weather data containing
                                           temp, humidity, and rainfall

        Returns:
            Dict[str, Any]: Risk assessment results with individual risks
                          and overall risk level
        """
        active_risks = []
        max_severity = RiskLevel.LOW

        # Evaluate each risk rule
        for rule in self.risk_rules:
            if rule.condition(weather_data):
                active_risks.append({
                    "name": rule.name,
                    "emoji": rule.emoji,
                    "severity": rule.severity.value,
                    "description": rule.description
                })

                # Update maximum severity level
                if rule.severity == RiskLevel.HIGH:
                    max_severity = RiskLevel.HIGH
                elif rule.severity == RiskLevel.MODERATE and max_severity != RiskLevel.HIGH:
                    max_severity = RiskLevel.MODERATE

        # Determine overall risk level based on active risks
        overall_risk = self._calculate_overall_risk(active_risks)

        return {
            "status": "success",
            "data": {
                "active_risks": active_risks,
                "overall_risk_level": overall_risk.value,
                "risk_count": len(active_risks),
                "weather_summary": {
                    "temperature": weather_data.get("temp", 0),
                    "humidity": weather_data.get("humidity", 0),
                    "rainfall": weather_data.get("rainfall", 0)
                }
            }
        }

    def _calculate_overall_risk(self, active_risks: List[Dict[str, Any]]) -> RiskLevel:
        """
        Calculate the overall risk level based on active risks.

        Args:
            active_risks (List[Dict[str, Any]]): List of active risk dictionaries

        Returns:
            RiskLevel: Overall risk level
        """
        if not active_risks:
            return RiskLevel.LOW

        # Count risks by severity
        high_risks = sum(1 for risk in active_risks if risk["severity"] == "High")
        moderate_risks = sum(1 for risk in active_risks if risk["severity"] == "Moderate")

        # Determine overall risk
        if high_risks > 0:
            return RiskLevel.HIGH
        elif moderate_risks > 1:  # Multiple moderate risks
            return RiskLevel.HIGH
        elif moderate_risks > 0:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def get_available_risks(self) -> List[Dict[str, Any]]:
        """
        Get information about all available risk rules.

        Returns:
            List[Dict[str, Any]]: List of all risk rules with their details
        """
        return [
            {
                "name": rule.name,
                "emoji": rule.emoji,
                "severity": rule.severity.value,
                "description": rule.description
            }
            for rule in self.risk_rules
        ]