from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config.logging import configure_logging
from app.database.database import engine
from app.middleware.exception_handlers import register_exception_handlers
from app.routers import auth, drivers, expenses, fuel, maintenance, reports, trips, vehicles
from app.schemas.common import SuccessResponse


configure_logging()

app = FastAPI(
    title="TransitOps API",
    version="1.0.0",
    description=(
        "TransitOps is an enterprise transport operations API for managing fleet "
        "assets, drivers, trips, maintenance, fuel usage, expenses, and executive "
        "reporting. All endpoints use the standard SuccessResponse/ErrorResponse "
        "contract and are protected by JWT authentication where required."
    ),
    openapi_tags=[
        {"name": "System", "description": "API health and platform status endpoints."},
        {
            "name": "Authentication",
            "description": (
                "JWT login, registration, and authenticated profile endpoints."
            ),
        },
        {
            "name": "Vehicles",
            "description": (
                "Vehicle inventory, lifecycle state, capacity, and odometer "
                "endpoints."
            ),
        },
        {
            "name": "Drivers",
            "description": (
                "Driver profiles, licensing, safety score, and availability "
                "endpoints."
            ),
        },
        {
            "name": "Trips",
            "description": (
                "Core dispatch workflow for draft, dispatched, completed, and "
                "cancelled trips."
            ),
        },
        {
            "name": "Maintenance",
            "description": (
                "Vehicle maintenance intake, tracking, and closure endpoints."
            ),
        },
        {
            "name": "Fuel",
            "description": "Fuel purchase and consumption tracking endpoints.",
        },
        {
            "name": "Expenses",
            "description": "Operational expense capture and management endpoints.",
        },
        {
            "name": "Reports",
            "description": (
                "Dashboard, fleet utilization, and cost reporting endpoints."
            ),
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)

api_router = APIRouter(prefix="/api/v1")


@api_router.get(
    "/health",
    tags=["System"],
    response_model=SuccessResponse[dict],
    summary="Check API health",
    description="Returns API status, database connectivity, version, and current server time.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "API health details returned."},
    },
)
def health_check() -> SuccessResponse[dict]:
    database_status = "connected"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    return SuccessResponse(
        message="Backend running successfully",
        data={
            "api_status": "healthy",
            "database_status": database_status,
            "version": "1.0.0",
            "current_time": datetime.now(timezone.utc).isoformat(),
        },
    )


api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(fuel.router, prefix="/fuel", tags=["Fuel"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

app.include_router(api_router)
