from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.auth.password import hash_password
from app.database.database import SessionLocal
from app.models.driver import Driver
from app.models.enums import DriverStatus, TripStatus, VehicleStatus
from app.models.expense import Expense
from app.models.fuel_log import FuelLog
from app.models.maintenance_log import MaintenanceLog
from app.models.role import Role
from app.models.trip import Trip
from app.models.user import User
from app.models.vehicle import Vehicle


ROLES = [
    ("Fleet Manager", "Manages fleet assets and vehicle operations."),
    ("Dispatcher", "Coordinates trip dispatch and driver assignment."),
    ("Safety Officer", "Oversees driver safety and compliance."),
    ("Financial Analyst", "Reviews fleet costs and financial reports."),
]

USERS = [
    ("Aarav Mehta", "fleet.manager@transitops.local", "Fleet Manager"),
    ("Neha Kapoor", "dispatcher@transitops.local", "Dispatcher"),
    ("Rohan Iyer", "safety.officer@transitops.local", "Safety Officer"),
    ("Priya Shah", "finance.analyst@transitops.local", "Financial Analyst"),
]

CITY_PAIRS = [
    ("Mumbai", "Pune"),
    ("Delhi", "Jaipur"),
    ("Bengaluru", "Mysuru"),
    ("Chennai", "Coimbatore"),
    ("Hyderabad", "Vijayawada"),
    ("Ahmedabad", "Surat"),
    ("Kolkata", "Durgapur"),
    ("Lucknow", "Kanpur"),
    ("Indore", "Bhopal"),
    ("Nagpur", "Raipur"),
]


def get_or_create_role(db: Session, name: str, description: str) -> Role:
    role = db.scalar(select(Role).where(Role.name == name))
    if role is not None:
        return role

    role = Role(name=name, description=description)
    db.add(role)
    db.flush()
    return role


def seed_roles(db: Session) -> dict[str, Role]:
    return {
        name: get_or_create_role(db, name, description)
        for name, description in ROLES
    }


def seed_users(db: Session, roles: dict[str, Role]) -> None:
    for full_name, email, role_name in USERS:
        if db.scalar(select(User).where(User.email == email)) is not None:
            continue
        db.add(
            User(
                full_name=full_name,
                email=email,
                hashed_password=hash_password("TransitOps@123"),
                role_id=roles[role_name].id,
                is_active=True,
            )
        )


def seed_vehicles(db: Session) -> list[Vehicle]:
    vehicles: list[Vehicle] = []
    vehicle_types = ["Container Truck", "Mini Truck", "Refrigerated Van", "Flatbed Truck"]
    statuses = [VehicleStatus.AVAILABLE] * 12 + [VehicleStatus.IN_SHOP] * 2 + [VehicleStatus.RETIRED]

    for index in range(15):
        registration_number = f"TO-{2026}-{index + 1:03d}"
        vehicle = db.scalar(
            select(Vehicle).where(Vehicle.registration_number == registration_number)
        )
        if vehicle is None:
            vehicle = Vehicle(
                registration_number=registration_number,
                vehicle_name=f"TransitOps Fleet {index + 1:02d}",
                vehicle_type=vehicle_types[index % len(vehicle_types)],
                max_load_capacity=3500 + (index * 250),
                odometer=18000 + (index * 3200),
                acquisition_cost=1800000 + (index * 125000),
                status=statuses[index],
            )
            db.add(vehicle)
            db.flush()
        vehicles.append(vehicle)
    return vehicles


def seed_drivers(db: Session) -> list[Driver]:
    drivers: list[Driver] = []
    names = [
        "Sanjay Patil",
        "Imran Khan",
        "Kiran Rao",
        "Vikram Singh",
        "Anil Kumar",
        "Mahesh Yadav",
        "Suresh Nair",
        "Nitin Joshi",
        "Farhan Ali",
        "Deepak Verma",
        "Arjun Reddy",
        "Manoj Das",
        "Harish Pillai",
        "Rahul Nambiar",
        "Prakash Sethi",
        "Dev Sharma",
        "Ajay Gupta",
        "Sameer Qureshi",
        "Rakesh Bhat",
        "Amit Chavan",
    ]
    statuses = [DriverStatus.AVAILABLE] * 16 + [DriverStatus.OFF_DUTY] * 3 + [DriverStatus.INACTIVE]

    for index, name in enumerate(names):
        license_number = f"TO-DL-{index + 1:05d}"
        driver = db.scalar(select(Driver).where(Driver.license_number == license_number))
        if driver is None:
            driver = Driver(
                name=name,
                license_number=license_number,
                license_category="HMV" if index % 3 else "LMV",
                license_expiry_date=date.today() + timedelta(days=365 + (index * 18)),
                contact_number=f"+9198000{index + 10000}",
                safety_score=78 + (index % 20),
                status=statuses[index],
            )
            db.add(driver)
            db.flush()
        drivers.append(driver)
    return drivers


def seed_trips(db: Session, vehicles: list[Vehicle], drivers: list[Driver]) -> list[Trip]:
    trips: list[Trip] = []
    statuses = [TripStatus.DRAFT] * 8 + [TripStatus.DISPATCHED] * 4 + [TripStatus.COMPLETED] * 6 + [TripStatus.CANCELLED] * 2

    for index in range(20):
        trip_code = f"TO-TRIP-{index + 1:04d}"
        trip = db.scalar(select(Trip).where(Trip.trip_code == trip_code))
        if trip is None:
            source, destination = CITY_PAIRS[index % len(CITY_PAIRS)]
            status = statuses[index]
            planned_distance = 145 + (index * 23)
            actual_distance = planned_distance + (index % 5) * 4 if status == TripStatus.COMPLETED else 0
            fuel_consumed = round(actual_distance / 4.8, 2) if actual_distance else 0
            revenue = planned_distance * 82 if status == TripStatus.COMPLETED else 0
            trip = Trip(
                trip_code=trip_code,
                source=source,
                destination=destination,
                cargo_weight=1200 + (index * 130),
                planned_distance=planned_distance,
                actual_distance=actual_distance,
                fuel_consumed=fuel_consumed,
                revenue=revenue,
                vehicle_id=vehicles[index % len(vehicles)].id,
                driver_id=drivers[index % len(drivers)].id,
                status=status,
            )
            db.add(trip)
            db.flush()
        trips.append(trip)
    return trips


def seed_maintenance(db: Session, vehicles: list[Vehicle]) -> None:
    maintenance_types = ["Preventive Service", "Brake Inspection", "Tyre Replacement", "Engine Tune"]
    for index in range(10):
        description = f"Seed maintenance record {index + 1:02d}"
        existing = db.scalar(
            select(MaintenanceLog).where(MaintenanceLog.description == description)
        )
        if existing is not None:
            continue
        start_date = date.today() - timedelta(days=45 - index)
        db.add(
            MaintenanceLog(
                vehicle_id=vehicles[index % len(vehicles)].id,
                maintenance_type=maintenance_types[index % len(maintenance_types)],
                description=description,
                cost=8500 + (index * 1350),
                start_date=start_date,
                end_date=start_date + timedelta(days=2 + (index % 3)),
                status="CLOSED" if index < 8 else "OPEN",
            )
        )


def seed_fuel_logs(db: Session, vehicles: list[Vehicle]) -> None:
    for index in range(25):
        fuel_date = date.today() - timedelta(days=index * 2)
        vehicle_id = vehicles[index % len(vehicles)].id
        existing = db.scalar(
            select(FuelLog).where(
                FuelLog.vehicle_id == vehicle_id,
                FuelLog.fuel_date == fuel_date,
            )
        )
        if existing is not None:
            continue
        liters = 55 + (index % 9) * 6
        db.add(
            FuelLog(
                vehicle_id=vehicle_id,
                liters=liters,
                cost=round(liters * 94.5, 2),
                fuel_date=fuel_date,
            )
        )


def seed_expenses(db: Session, vehicles: list[Vehicle]) -> None:
    expense_types = ["Toll", "Parking", "Permit", "Cleaning", "Loading Support"]
    for index in range(20):
        description = f"Seed expense record {index + 1:02d}"
        existing = db.scalar(select(Expense).where(Expense.description == description))
        if existing is not None:
            continue
        db.add(
            Expense(
                vehicle_id=vehicles[index % len(vehicles)].id,
                expense_type=expense_types[index % len(expense_types)],
                amount=450 + (index * 125),
                expense_date=date.today() - timedelta(days=index + 1),
                description=description,
            )
        )


def main() -> None:
    db = SessionLocal()
    try:
        roles = seed_roles(db)
        seed_users(db, roles)
        vehicles = seed_vehicles(db)
        drivers = seed_drivers(db)
        seed_trips(db, vehicles, drivers)
        seed_maintenance(db, vehicles)
        seed_fuel_logs(db, vehicles)
        seed_expenses(db, vehicles)
        db.commit()
        print("Seed data populated successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
