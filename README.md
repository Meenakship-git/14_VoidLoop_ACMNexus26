# AlertWave Backend
# Production-ready FastAPI backend for AlertWave project

## Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- OpenWeatherMap API Key (sign up at https://openweathermap.org/api)
- MySQL Database

## Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set environment variables (see Environment Variables section)
6. Ensure MySQL server is running

## Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# OpenWeatherMap API
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key

# Database Configuration
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=alertwave_db
DB_PORT=3306
DB_POOL_SIZE=5
DB_CONNECT_TIMEOUT=10
```

## Running the Application
Run the application with: `uvicorn app.main:app --reload`

The API will be available at http://127.0.0.1:8000

## API Endpoints

### GET /health
Health check endpoint for monitoring application status.

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

### GET /risk
Climate risk assessment endpoint that fetches real-time weather data and calculates associated risks.

**Parameters:**
- `city` (optional): City name for weather data (default: "Wayanad")

**Example:** `GET /risk?city=London`

**Response:**
```json
{
  "status": "success",
  "data": {
    "location": "London",
    "weather": {
      "temperature": 15.5,
      "humidity": 72,
      "rainfall": 0.0
    },
    "risk_assessment": {
      "active_risks": [],
      "overall_risk_level": "Low",
      "risk_count": 0,
      "weather_summary": {
        "temperature": 15.5,
        "humidity": 72,
        "rainfall": 0.0
      }
    }
  }
}
```

### POST /simulate
Climate risk simulation endpoint that accepts weather parameters and returns simulated risk assessment.

**Request Body:**
```json
{
  "temperature": 35.5,
  "humidity": 85.0,
  "rainfall": 120.0
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "simulation_id": "sim_1234",
    "input_parameters": {
      "temperature": 35.5,
      "humidity": 85.0,
      "rainfall": 120.0
    },
    "risk_assessment": {
      "active_risks": [
        {
          "name": "Heatwave",
          "emoji": "🔥",
          "severity": "High",
          "description": "Extreme high temperatures pose health risks"
        },
        {
          "name": "Flood Risk",
          "emoji": "🌧",
          "severity": "High",
          "description": "Heavy rainfall may cause flooding"
        }
      ],
      "overall_risk_level": "High",
      "risk_count": 2,
      "weather_summary": {
        "temperature": 35.5,
        "humidity": 85.0,
        "rainfall": 120.0
      }
    },
    "simulation_type": "climate_risk_assessment"
  }
}
```

## Services and Utilities

### Weather Service
Fetches real-time weather data from OpenWeatherMap API.

### Risk Calculator
Climate monitoring risk calculation system that evaluates weather data against predefined risk rules.

### Database Connection
MySQL database connection manager with connection pooling for reliable database operations.

**Features:**
- Connection pooling for better performance
- Automatic transaction management
- Error handling and health checks
- Singleton pattern for global access

**Usage Example:**
```python
from app.utils.database import get_database

# Get database instance
db = get_database()

# Execute a query
results = db.execute_query("SELECT * FROM weather_data WHERE city = %s", ("London",))

# Use context manager for transactions
with db.get_cursor() as cursor:
    cursor.execute("INSERT INTO alerts (message, severity) VALUES (%s, %s)", 
                  ("High temperature alert", "high"))
```

**Health Check:**
```python
health = db.health_check()
print(health)  # {"status": "healthy", "message": "Database is responding correctly"}
```

## Project Structure
```
app/
├── main.py          # Main FastAPI application
├── routes/          # API route handlers
│   ├── __init__.py
│   ├── health.py
│   ├── risk.py
│   └── simulate.py
├── services/        # Business logic services
│   ├── __init__.py
│   └── weather_service.py
├── models/          # Data models
└── utils/           # Utility functions
    ├── __init__.py
    └── risk_calculator.py
```

## CORS
CORS is enabled for frontend connections from any origin.
