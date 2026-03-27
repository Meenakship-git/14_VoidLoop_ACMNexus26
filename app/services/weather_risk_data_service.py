import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherRiskDataService:
    """
    Database service for storing and retrieving weather and risk data.

    This service provides methods to insert weather readings with associated
    risk assessments into the MySQL database with proper error handling
    and transaction management.
    """

    def __init__(self):
        """Initialize the data service with database connection."""
        self.db = get_database()

    def insert_weather_risk_data(self, city: str, temperature: float,
                               humidity: float, rainfall: float,
                               risk_level: str, risk_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Insert weather and risk data into the database.

        Args:
            city (str): City name for the weather reading
            temperature (float): Temperature in Celsius
            humidity (float): Humidity percentage (0-100)
            rainfall (float): Rainfall in mm
            risk_level (str): Risk level (Low, Moderate, High)
            risk_details (Dict[str, Any], optional): Additional risk assessment details

        Returns:
            Dict[str, Any]: Result of the insertion operation

        Raises:
            Exception: If database operation fails
        """
        try:
            # Prepare the data for insertion
            timestamp = datetime.now()

            # Convert risk_details to JSON string if provided
            risk_details_json = None
            if risk_details:
                import json
                risk_details_json = json.dumps(risk_details)

            # Prepare the SQL query with parameters
            insert_query = """
            INSERT INTO weather_risk_data
            (city, temperature, humidity, rainfall, risk_level, risk_details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            params = (city, temperature, humidity, rainfall,
                     risk_level, risk_details_json, timestamp)

            # Execute the insert query
            result = self.db.execute_query(insert_query, params, fetch=False)

            logger.info(f"Successfully inserted weather risk data for {city}: "
                       f"temp={temperature}°C, risk={risk_level}")

            return {
                "status": "success",
                "message": f"Weather risk data inserted successfully for {city}",
                "data": {
                    "city": city,
                    "temperature": temperature,
                    "humidity": humidity,
                    "rainfall": rainfall,
                    "risk_level": risk_level,
                    "timestamp": timestamp.isoformat()
                }
            }

        except Exception as e:
            error_msg = f"Failed to insert weather risk data for {city}: {str(e)}"
            logger.error(error_msg)

            return {
                "status": "error",
                "message": error_msg,
                "error_details": str(e)
            }

    def get_weather_risk_history(self, city: Optional[str] = None,
                               limit: int = 50) -> Dict[str, Any]:
        """
        Retrieve weather and risk data history from the database.

        Args:
            city (str, optional): Filter by city name. If None, returns all cities.
            limit (int): Maximum number of records to return (default: 50)

        Returns:
            Dict[str, Any]: Query results with weather risk data history
        """
        try:
            # Build the query based on parameters
            if city:
                query = """
                SELECT id, city, temperature, humidity, rainfall,
                       risk_level, risk_details, timestamp
                FROM weather_risk_data
                WHERE city = %s
                ORDER BY timestamp DESC
                LIMIT %s
                """
                params = (city, limit)
            else:
                query = """
                SELECT id, city, temperature, humidity, rainfall,
                       risk_level, risk_details, timestamp
                FROM weather_risk_data
                ORDER BY timestamp DESC
                LIMIT %s
                """
                params = (limit,)

            # Execute the query
            results = self.db.execute_query(query, params)

            # Process the results
            processed_results = []
            if results:
                for row in results:
                    # Parse risk_details JSON if present
                    risk_details = None
                    if row.get('risk_details'):
                        import json
                        try:
                            risk_details = json.loads(row['risk_details'])
                        except json.JSONDecodeError:
                            risk_details = None

                    processed_results.append({
                        "id": row.get("id"),
                        "city": row.get("city"),
                        "temperature": row.get("temperature"),
                        "humidity": row.get("humidity"),
                        "rainfall": row.get("rainfall"),
                        "risk_level": row.get("risk_level"),
                        "risk_details": risk_details,
                        "timestamp": row.get("timestamp").isoformat() if row.get("timestamp") else None
                    })

            logger.info(f"Retrieved {len(processed_results)} weather risk records"
                       f"{' for ' + city if city else ''}")

            return {
                "status": "success",
                "message": f"Retrieved {len(processed_results)} weather risk records",
                "data": processed_results
            }

        except Exception as e:
            error_msg = f"Failed to retrieve weather risk history: {str(e)}"
            logger.error(error_msg)

            return {
                "status": "error",
                "message": error_msg,
                "error_details": str(e)
            }

    def get_risk_statistics(self, city: Optional[str] = None,
                          days: int = 7) -> Dict[str, Any]:
        """
        Get risk level statistics for the specified period.

        Args:
            city (str, optional): Filter by city name
            days (int): Number of days to look back (default: 7)

        Returns:
            Dict[str, Any]: Risk statistics for the period
        """
        try:
            # Build the query for statistics
            if city:
                query = """
                SELECT
                    COUNT(*) as total_records,
                    AVG(temperature) as avg_temperature,
                    AVG(humidity) as avg_humidity,
                    AVG(rainfall) as avg_rainfall,
                    SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk_count,
                    SUM(CASE WHEN risk_level = 'Moderate' THEN 1 ELSE 0 END) as moderate_risk_count,
                    SUM(CASE WHEN risk_level = 'Low' THEN 1 ELSE 0 END) as low_risk_count
                FROM weather_risk_data
                WHERE city = %s AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """
                params = (city, days)
            else:
                query = """
                SELECT
                    COUNT(*) as total_records,
                    AVG(temperature) as avg_temperature,
                    AVG(humidity) as avg_humidity,
                    AVG(rainfall) as avg_rainfall,
                    SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk_count,
                    SUM(CASE WHEN risk_level = 'Moderate' THEN 1 ELSE 0 END) as moderate_risk_count,
                    SUM(CASE WHEN risk_level = 'Low' THEN 1 ELSE 0 END) as low_risk_count
                FROM weather_risk_data
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """
                params = (days,)

            # Execute the query
            results = self.db.execute_query(query, params)

            if results and len(results) > 0:
                stats = results[0]

                return {
                    "status": "success",
                    "message": f"Risk statistics for last {days} days{' in ' + city if city else ''}",
                    "data": {
                        "period_days": days,
                        "city": city,
                        "total_records": stats.get("total_records", 0),
                        "average_conditions": {
                            "temperature": round(stats.get("avg_temperature", 0), 2),
                            "humidity": round(stats.get("avg_humidity", 0), 2),
                            "rainfall": round(stats.get("avg_rainfall", 0), 2)
                        },
                        "risk_distribution": {
                            "high": stats.get("high_risk_count", 0),
                            "moderate": stats.get("moderate_risk_count", 0),
                            "low": stats.get("low_risk_count", 0)
                        }
                    }
                }
            else:
                return {
                    "status": "success",
                    "message": "No data found for the specified period",
                    "data": None
                }

        except Exception as e:
            error_msg = f"Failed to get risk statistics: {str(e)}"
            logger.error(error_msg)

            return {
                "status": "error",
                "message": error_msg,
                "error_details": str(e)
            }