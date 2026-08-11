from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine

from app.routes.sensor import (
    router as sensor_router,
)
from app.routes.dashboard import (
    router as dashboard_router,
)
from app.routes.machines import (
    router as machines_router,
)
from app.routes.alerts import (
    router as alerts_router,
)
from app.routes.trends import (
    router as trends_router,
)


# Make sure SQLAlchemy knows about the model
# before creating tables.
from app.db.models import SensorReading  # noqa: F401


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="PredictX AI Backend",
    version="3.0.0",
    description=(
        "ESP32-driven industrial "
        "predictive maintenance backend."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    sensor_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    machines_router
)

app.include_router(
    alerts_router
)

app.include_router(
    trends_router
)


@app.get("/")
def root():
    return {
        "project": "PredictX AI",
        "status": "Backend running",
        "version": "3.0.0",
        "architecture": (
            "ESP32 -> FastAPI -> "
            "SQLite -> React"
        ),
    }


@app.get("/health")
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "PredictX AI Backend",
    }