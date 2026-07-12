# TransitOps Database Schema

This document describes the planned PostgreSQL schema. It is not SQL and must not be treated as a migration.

## Database

Database name: `transitops`

## Tables

### roles

Columns:

- `id`: integer or UUID identifier
- `name`: role name
- `description`: optional role description
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys: None

Relationships:

- One role can belong to many users.

Unique Constraints:

- `name`

Recommended Indexes:

- `idx_roles_name`

### users

Columns:

- `id`: integer or UUID identifier
- `role_id`: reference to `roles.id`
- `first_name`: user first name
- `last_name`: user last name
- `email`: user email address
- `password_hash`: hashed password
- `is_active`: account active flag
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys:

- `role_id` references `roles.id`

Relationships:

- Many users belong to one role.

Unique Constraints:

- `email`

Recommended Indexes:

- `idx_users_email`
- `idx_users_role_id`
- `idx_users_is_active`

### vehicles

Columns:

- `id`: integer or UUID identifier
- `vehicle_number`: unique fleet or registration number
- `vehicle_type`: vehicle category or type
- `make`: manufacturer
- `model`: model name
- `year`: manufacturing year
- `status`: operational status
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys: None

Relationships:

- One vehicle can have many trips.
- One vehicle can have many maintenance logs.
- One vehicle can have many fuel logs.
- One vehicle can have many expenses.

Unique Constraints:

- `vehicle_number`

Recommended Indexes:

- `idx_vehicles_vehicle_number`
- `idx_vehicles_status`
- `idx_vehicles_vehicle_type`

### drivers

Columns:

- `id`: integer or UUID identifier
- `first_name`: driver first name
- `last_name`: driver last name
- `phone`: contact phone number
- `license_number`: driver license number
- `license_expiry_date`: license expiration date
- `status`: driver availability or employment status
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys: None

Relationships:

- One driver can have many trips.

Unique Constraints:

- `license_number`
- `phone`

Recommended Indexes:

- `idx_drivers_license_number`
- `idx_drivers_phone`
- `idx_drivers_status`

### trips

Columns:

- `id`: integer or UUID identifier
- `vehicle_id`: reference to `vehicles.id`
- `driver_id`: reference to `drivers.id`
- `origin`: trip origin
- `destination`: trip destination
- `scheduled_start_time`: planned start timestamp
- `scheduled_end_time`: planned end timestamp
- `actual_start_time`: actual start timestamp
- `actual_end_time`: actual end timestamp
- `status`: trip status
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys:

- `vehicle_id` references `vehicles.id`
- `driver_id` references `drivers.id`

Relationships:

- Many trips belong to one vehicle.
- Many trips belong to one driver.
- One trip can have many expenses.

Unique Constraints:

- None planned initially.

Recommended Indexes:

- `idx_trips_vehicle_id`
- `idx_trips_driver_id`
- `idx_trips_status`
- `idx_trips_scheduled_start_time`

### maintenance_logs

Columns:

- `id`: integer or UUID identifier
- `vehicle_id`: reference to `vehicles.id`
- `maintenance_type`: type of maintenance
- `description`: maintenance details
- `cost`: maintenance cost
- `status`: maintenance status
- `opened_at`: maintenance opened timestamp
- `closed_at`: maintenance closed timestamp
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys:

- `vehicle_id` references `vehicles.id`

Relationships:

- Many maintenance logs belong to one vehicle.

Unique Constraints:

- None planned initially.

Recommended Indexes:

- `idx_maintenance_logs_vehicle_id`
- `idx_maintenance_logs_status`
- `idx_maintenance_logs_opened_at`

### fuel_logs

Columns:

- `id`: integer or UUID identifier
- `vehicle_id`: reference to `vehicles.id`
- `driver_id`: optional reference to `drivers.id`
- `fuel_date`: fuel entry date
- `fuel_type`: fuel type
- `quantity`: fuel quantity
- `unit_price`: fuel price per unit
- `total_cost`: total fuel cost
- `odometer_reading`: vehicle odometer reading
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys:

- `vehicle_id` references `vehicles.id`
- `driver_id` references `drivers.id`

Relationships:

- Many fuel logs belong to one vehicle.
- Many fuel logs may belong to one driver.

Unique Constraints:

- None planned initially.

Recommended Indexes:

- `idx_fuel_logs_vehicle_id`
- `idx_fuel_logs_driver_id`
- `idx_fuel_logs_fuel_date`

### expenses

Columns:

- `id`: integer or UUID identifier
- `vehicle_id`: optional reference to `vehicles.id`
- `driver_id`: optional reference to `drivers.id`
- `trip_id`: optional reference to `trips.id`
- `expense_type`: expense category
- `amount`: expense amount
- `expense_date`: expense date
- `description`: optional expense details
- `created_at`: creation timestamp
- `updated_at`: update timestamp

Primary Key: `id`

Foreign Keys:

- `vehicle_id` references `vehicles.id`
- `driver_id` references `drivers.id`
- `trip_id` references `trips.id`

Relationships:

- Many expenses may belong to one vehicle.
- Many expenses may belong to one driver.
- Many expenses may belong to one trip.

Unique Constraints:

- None planned initially.

Recommended Indexes:

- `idx_expenses_vehicle_id`
- `idx_expenses_driver_id`
- `idx_expenses_trip_id`
- `idx_expenses_expense_date`
- `idx_expenses_expense_type`
