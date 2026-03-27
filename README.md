# AlertWave Backend
# Production-ready FastAPI backend for AlertWave project

## Requirements
- Python 3.8+
- FastAPI
- Uvicorn

## Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Running the Application
Run the application with: `uvicorn app.main:app --reload`

The API will be available at http://127.0.0.1:8000

## API Endpoints
- GET /health - Health check endpoint
- GET /risk - Get risk information
- POST /simulate - Simulate an action

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
├── models/          # Data models
└── utils/           # Utility functions
```

## CORS
CORS is enabled for frontend connections from any origin.