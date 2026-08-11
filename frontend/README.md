# PredictX Frontend V2 — Reference UI Redesign

This build keeps the existing PredictX backend/API integration and Arduino data contract while redesigning the entire frontend UI around the supplied dark PredictX reference style.

## What is preserved

- Existing FastAPI API integration in `src/api.js`
- Existing Arduino/ESP32 payload fields and backend response fields
- Machine selection
- Latest sensor readings
- Historical trends
- Alerts
- Arduino prediction values
- Maintenance and settings pages

## UI changes

- Dark industrial dashboard theme
- Orange / red / gold / purple accent system
- Reference-style left navigation
- KPI cards with animated data bars
- Separate parameter charts
- Machine visual-twin panel
- Recent alerts / AI diagnosis / health history panels
- Responsive desktop/tablet/mobile layout
- Hover, glow, chart-draw and refresh animations
- Automatic latest-data refresh every 3 seconds

## Run

```bash
npm install
npm run dev
```

Open the Vite URL shown by the terminal, normally `http://localhost:5173`.

## Backend

The frontend expects the existing API base URL from `.env` / `VITE_API_URL`.

Default:

```text
http://localhost:8000/api
```

The frontend reads the current backend through:

- `GET /api/machines`
- `GET /api/readings/latest/{machine_id}`
- `GET /api/trends/{machine_id}?limit=200`
- `GET /api/alerts/{machine_id}?limit=50`

The frontend does **not** replace or recalculate the Arduino prediction values.
