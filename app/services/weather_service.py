import os
import requests
from typing import Dict, Any, Optional

class WeatherService:
    """
    Service for fetching real-time weather data from OpenWeatherMap API.

    This service provides methods to retrieve current weather conditions
    including temperature, humidity, and rainfall data for a given city.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        """Initialize the weather service with API key from environment."""
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHERMAP_API_KEY environment variable is required")

    def get_weather(self, city: str = "Wayanad") -> Dict[str, Any]:
        """
        Fetch current weather data for a specified city.

        Args:
            city (str): Name of the city to fetch weather for. Defaults to "Wayanad".

        Returns:
            Dict[str, Any]: Structured weather data containing temperature,
                           humidity, and rainfall information.

        Raises:
            requests.RequestException: If there's an error with the API request.
            ValueError: If the API response is invalid or city is not found.
        """
        try:
            # Prepare API request parameters
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Use Celsius for temperature
            }

            # Make API request
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes

            # Parse JSON response
            data = response.json()

            # Extract required weather information
            weather_info = {
                "city": data.get("name", city),
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "rainfall": self._extract_rainfall(data)
            }

            return {
                "status": "success",
                "data": weather_info
            }

        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"API request failed: {str(e)}"
            }
        except KeyError as e:
            return {
                "status": "error",
                "message": f"Invalid API response format: missing key {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }

    def _extract_rainfall(self, data: Dict[str, Any]) -> float:
        """
        Extract rainfall data from the API response.

        Args:
            data (Dict[str, Any]): The full API response data.

        Returns:
            float: Rainfall amount in mm for the last hour, or 0.0 if no rain.
        """
        # OpenWeatherMap provides rain data in "rain" object with "1h" key
        rain_data = data.get("rain", {})
        return rain_data.get("1h", 0.0)