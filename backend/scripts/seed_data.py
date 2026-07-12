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


DEFAULT_PASSWORD = "TransitOps@123"

ROLES = [
    ("Fleet Manager", "Manages fleet assets, capacity, and vehicle operations."),
    ("Dispatcher", "Coordinates vehicle assignment and trip dispatch."),
    ("Safety Officer", "Oversees driver compliance and operational safety."),
    ("Financial Analyst", "Reviews operational costs and fleet profitability."),
]

USERS = [
    ("Aarav Mehta", "fleet.manager@transitops.local", "Fleet Manager"),
    ("Neha Kapoor", "dispatcher@transitops.local", "Dispatcher"),
    ("Rohan Iyer", "safety.officer@transitops.local", "Safety Officer"),
    ("Priya Shah", "finance.analyst@transitops.local", "Financial Analyst"),
]

VEHICLES = [
    ("MH12TR1001", "Tata Prima 5530.S", "Container Truck", 28000, 142300, 5450000, VehicleStatus.AVAILABLE),
    ("DL01TR2240", "Ashok Leyland 4825", "Multi-Axle Truck", 32000, 118450, 6120000, VehicleStatus.ON_TRIP),
    ("KA05TR7781", "BharatBenz 3528C", "Tipper Truck", 26000, 96720, 4980000, VehicleStatus.AVAILABLE),
    ("TN09TR5542", "Eicher Pro 6048", "Long Haul Truck", 30000, 135880, 5720000, VehicleStatus.IN_SHOP),
    ("GJ18TR3321", "Mahindra Blazo X 49", "Flatbed Truck", 29000, 151200, 5360000, VehicleStatus.AVAILABLE),
    ("RJ14TR8832", "Tata Ultra T.16", "Box Truck", 9500, 84500, 2820000, VehicleStatus.AVAILABLE),
    ("TS08TR6720", "BharatBenz 1617R", "Refrigerated Truck", 10500, 76340, 3180000, VehicleStatus.ON_TRIP),
    ("WB19TR4511", "Ashok Leyland Ecomet", "Curtain Side Truck", 12000, 99210, 3040000, VehicleStatus.AVAILABLE),
    ("UP32TR0904", "Eicher Pro 3015", "Parcel Truck", 8500, 68800, 2460000, VehicleStatus.AVAILABLE),
    ("MP09TR7345", "Tata Signa 4018.S", "Trailer Truck", 34000, 166420, 6580000, VehicleStatus.ON_TRIP),
    ("KL07TR6209", "Mahindra Furio 16", "Rigid Truck", 11000, 73990, 2910000, VehicleStatus.AVAILABLE),
    ("HR55TR2188", "Volvo FM 420", "Heavy Hauler", 36000, 124650, 7850000, VehicleStatus.IN_SHOP),
    ("PB10TR8877", "Tata LPT 1918", "Cargo Truck", 14500, 110230, 3370000, VehicleStatus.AVAILABLE),
    ("OR02TR3456", "BharatBenz 2823R", "Open Body Truck", 21000, 92240, 4210000, VehicleStatus.AVAILABLE),
    ("AP31TR5190", "Ashok Leyland Partner", "Light Commercial Vehicle", 6500, 55780, 1980000, VehicleStatus.AVAILABLE),
]

DRIVERS = [
    ("Sanjay Patil", "TO-DL-00001", "HMV", 92, DriverStatus.AVAILABLE),
    ("Imran Khan", "TO-DL-00002", "HMV", 88, DriverStatus.ON_TRIP),
    ("Kiran Rao", "TO-DL-00003", "LMV", 81, DriverStatus.AVAILABLE),
    ("Vikram Singh", "TO-DL-00004", "HMV-TRAILER", 94, DriverStatus.OFF_DUTY),
    ("Anil Kumar", "TO-DL-00005", "HMV", 76, DriverStatus.AVAILABLE),
    ("Mahesh Yadav", "TO-DL-00006", "HAZMAT", 90, DriverStatus.ON_TRIP),
    ("Suresh Nair", "TO-DL-00007", "LMV", 84, DriverStatus.AVAILABLE),
    ("Nitin Joshi", "TO-DL-00008", "HMV", 79, DriverStatus.AVAILABLE),
    ("Farhan Ali", "TO-DL-00009", "HMV-TRAILER", 87, DriverStatus.INACTIVE),
    ("Deepak Verma", "TO-DL-00010", "HMV", 91, DriverStatus.AVAILABLE),
    ("Arjun Reddy", "TO-DL-00011", "REFRIGERATED", 86, DriverStatus.ON_TRIP),
    ("Manoj Das", "TO-DL-00012", "HMV", 74, DriverStatus.OFF_DUTY),
    ("Harish Pillai", "TO-DL-00013", "LMV", 82, DriverStatus.AVAILABLE),
    ("Rahul Nambiar", "TO-DL-00014", "HMV", 89, DriverStatus.AVAILABLE),
    ("Prakash Sethi", "TO-DL-00015", "HMV-TRAILER", 93, DriverStatus.AVAILABLE),
    ("Dev Sharma", "TO-DL-00016", "HAZMAT", 85, DriverStatus.AVAILABLE),
    ("Ajay Gupta", "TO-DL-00017", "HMV", 78, DriverStatus.OFF_DUTY),
    ("Sameer Qureshi", "TO-DL-00018", "REFRIGERATED", 96, DriverStatus.AVAILABLE),
    ("Rakesh Bhat", "TO-DL-00019", "HMV", 80, DriverStatus.AVAILABLE),
    ("Amit Chavan", "TO-DL-00020", "LMV", 83, DriverStatus.AVAILABLE),
]

TRIP_LANES = [
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
    ("Kochi", "Kozhikode"),
    ("Chandigarh", "Ludhiana"),
    ("Visakhapatnam", "Vijayawada"),
    ("Bhubaneswar", "Cuttack"),
    ("Patna", "Ranchi"),
]


def get_or_create_role(db: Session, name: str, description: str) -> Role:
    role = db.scalar(select(Role).where(Role.name == name))
    if role is not None:
        role.description = description
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
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(
                full_name=full_name,
                email=email,
                hashed_password=hash_password(DEFAULT_PASSWORD),
                role_id=roles[role_name].id,
                is_active=True,
            )
            db.add(user)
            continue

        user.full_name = full_name
        user.role_id = roles[role_name].id
        user.is_active = True


def seed_vehicles(db: Session) -> list[Vehicle]:
    vehicles: list[Vehicle] = []
    for record in VEHICLES:
        (
            registration_number,
            vehicle_name,
            vehicle_type,
            max_load_capacity,
            odometer,
            acquisition_cost,
            status,
        ) = record
        vehicle = db.scalar(
            select(Vehicle).where(Vehicle.registration_number == registration_number)
        )
        if vehicle is None:
            vehicle = Vehicle(
                registration_number=registration_number,
                vehicle_name=vehicle_name,
                vehicle_type=vehicle_type,
                max_load_capacity=max_load_capacity,
                odometer=odometer,
                acquisition_cost=acquisition_cost,
                status=status,
            )
            db.add(vehicle)
            db.flush()
        vehicles.append(vehicle)
    return vehicles


def seed_drivers(db: Session) -> list[Driver]:
    drivers: list[Driver] = []
    for index, (name, license_number, category, safety_score, status) in enumerate(DRIVERS):
        driver = db.scalar(select(Driver).where(Driver.license_number == license_number))
        if driver is None:
            driver = Driver(
                name=name,
                license_number=license_number,
                license_category=category,
                license_expiry_date=date.today() + timedelta(days=420 + (index * 21)),
                contact_number=f"+9198700{index + 11000}",
                safety_score=safety_score,
                status=status,
            )
            db.add(driver)
            db.flush()
        drivers.append(driver)
    return drivers


def seed_trips(db: Session, vehicles: list[Vehicle], drivers: list[Driver]) -> list[Trip]:
    trips: list[Trip] = []
    statuses = (
        [TripStatus.DRAFT] * 7
        + [TripStatus.DISPATCHED] * 6
        + [TripStatus.COMPLETED] * 9
        + [TripStatus.CANCELLED] * 3
    )

    for index in range(25):
        trip_code = f"TO-TRIP-{index + 1:04d}"
        trip = db.scalar(select(Trip).where(Trip.trip_code == trip_code))
        if trip is None:
            source, destination = TRIP_LANES[index % len(TRIP_LANES)]
            status = statuses[index]
            planned_distance = 120 + (index * 19)
            actual_distance = (
                planned_distance + ((index % 6) * 5)
                if status == TripStatus.COMPLETED
                else 0
            )
            fuel_consumed = round(actual_distance / 4.6, 2) if actual_distance else 0
            revenue = round(planned_distance * (78 + (index % 7) * 4), 2)
            cargo_weight = 1800 + (index * 410)
            trip = Trip(
                trip_code=trip_code,
                source=source,
                destination=destination,
                cargo_weight=cargo_weight,
                planned_distance=planned_distance,
                actual_distance=actual_distance,
                fuel_consumed=fuel_consumed,
                revenue=revenue if status == TripStatus.COMPLETED else 0,
                vehicle_id=vehicles[index % len(vehicles)].id,
                driver_id=drivers[index % len(drivers)].id,
                status=status,
            )
            db.add(trip)
            db.flush()
        trips.append(trip)
    return trips


def seed_maintenance(db: Session, vehicles: list[Vehicle]) -> None:
    maintenance_types = [
        "Preventive Service",
        "Brake Inspection",
        "Tyre Replacement",
        "Engine Tune",
        "Refrigeration Unit Check",
    ]
    statuses = ["CLOSED"] * 7 + ["OPEN"] * 3

    for index in range(10):
        description = f"Seed maintenance record {index + 1:02d}"
        existing = db.scalar(
            select(MaintenanceLog).where(MaintenanceLog.description == description)
        )
        if existing is not None:
            continue

        start_date = date.today() - timedelta(days=55 - (index * 4))
        db.add(
            MaintenanceLog(
                vehicle_id=vehicles[(index * 2) % len(vehicles)].id,
                maintenance_type=maintenance_types[index % len(maintenance_types)],
                description=description,
                cost=7200 + (index * 1650),
                start_date=start_date,
                end_date=start_date + timedelta(days=1 + (index % 4)),
                status=statuses[index],
            )
        )


def seed_fuel_logs(db: Session, vehicles: list[Vehicle]) -> None:
    for index in range(30):
        fuel_date = date.today() - timedelta(days=index + (index // 3))
        vehicle_id = vehicles[index % len(vehicles)].id
        existing = db.scalar(
            select(FuelLog).where(
                FuelLog.vehicle_id == vehicle_id,
                FuelLog.fuel_date == fuel_date,
            )
        )
        if existing is not None:
            continue

        liters = 48 + ((index * 7) % 55)
        db.add(
            FuelLog(
                vehicle_id=vehicle_id,
                liters=liters,
                cost=round(liters * (92.5 + (index % 5)), 2),
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
                vehicle_id=vehicles[(index * 3) % len(vehicles)].id,
                expense_type=expense_types[index % len(expense_types)],
                amount=350 + (index * 145),
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
        print(f"Default seeded user password: {DEFAULT_PASSWORD}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
