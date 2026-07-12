
from app.schemas.common import ErrorResponse, PaginationResponse, SuccessResponse
from app.schemas.driver import DriverCreate, DriverResponse, DriverUpdate
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.schemas.fuel import FuelLogCreate, FuelLogResponse, FuelLogUpdate
from app.schemas.maintenance import (
    MaintenanceLogCreate,
    MaintenanceLogResponse,
    MaintenanceLogUpdate,
)
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate

__all__ = [
    "DriverCreate",
    "DriverResponse",
    "DriverUpdate",
    "ErrorResponse",
    "ExpenseCreate",
    "ExpenseResponse",
    "ExpenseUpdate",
    "FuelLogCreate",
    "FuelLogResponse",
    "FuelLogUpdate",
    "MaintenanceLogCreate",
    "MaintenanceLogResponse",
    "MaintenanceLogUpdate",
    "PaginationResponse",
    "RoleCreate",
    "RoleResponse",
    "RoleUpdate",
    "SuccessResponse",
    "TripCreate",
    "TripResponse",
    "TripUpdate",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "VehicleCreate",
    "VehicleResponse",
    "VehicleUpdate",
]
