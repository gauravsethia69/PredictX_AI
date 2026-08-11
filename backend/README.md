# PredictX Backend V3 — Fixed

This backend is aligned with the PredictX Frontend V2 and the ESP32 contract.

ESP32 remains the authority for:
- health
- machine_status
- failure_probability
- diagnosis
- recommendation
- failure_stage
- remaining_life_hours
- prediction_explanation

The backend stores those values and calculates only historical trends and alerts.

## Start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger:
http://127.0.0.1:8000/docs

## Important

If you are replacing the previous V2 backend and its SQLite database was created with the broken schema, stop Uvicorn and delete `predictx.db` once before starting V3. V3 recreates the table automatically.

## ESP32 JSON

The preferred payload is:

{
  "machine_id": "MACHINE-001",
  "temperature": 29,
  "vibration": 0,
  "current": 0.317,
  "sound": 613,
  "motor_running": true,
  "source": "esp32",
  "health": 88,
  "machine_status": "GOOD",
  "failure_probability": 6,
  "diagnosis": "Healthy Machine",
  "recommendation": "Normal Operation",
  "failure_stage": "Minor Deviation",
  "remaining_life_hours": 200,
  "prediction_explanation": "All sensors within learned baseline."
}

The API also accepts the Arduino camelCase equivalents:
machineStatus, failureProbability, aiReport, failureStage, remainingOperatingHours, predictionExplanation.
