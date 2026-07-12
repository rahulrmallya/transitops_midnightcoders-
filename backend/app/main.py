from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, drivers, expenses, fuel, maintenance, reports, trips, vehicles


app = FastAPI(
    title="TransitOps API",
    version="1.0.0",
    description="Enterprise Transport Operations Platform Backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health")
def health_check() -> dict:
    return {
        "success": True,
        "message": "Backend running successfully",
        "data": {
            "status": "healthy",
            "version": "1.0.0",
        },
    }


api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(fuel.router, prefix="/fuel", tags=["Fuel"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

app.include_router(api_router)
