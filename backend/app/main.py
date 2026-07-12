from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import auth, drivers, expenses, fuel, maintenance, reports, trips, vehicles
from app.schemas.common import ErrorResponse


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


@app.exception_handler(HTTPException)
def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=message, errors={}).model_dump(),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(ErrorResponse(
            message="Validation error",
            errors={"details": exc.errors()},
        )),
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
