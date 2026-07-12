# TransitOps Project Context

This document is the permanent architecture reference for TransitOps.

Every future implementation must follow this document unless explicitly instructed otherwise.

## Project

Name: TransitOps

Description:

TransitOps is an enterprise Transport Operations Management Platform built for a hackathon.

The project manages:

- Vehicles
- Drivers
- Trips
- Maintenance
- Fuel Logs
- Expenses
- Reports
- Authentication
- Role Based Access

## Important Collaboration Rules

This project is being developed simultaneously by multiple developers on different laptops.

Consistency is more important than speed.

Rules:

- Never rename folders.
- Never move files.
- Never change API formats.
- Never introduce new architectures.
- Always extend the existing architecture.

## Tech Stack

Backend:

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Pydantic v2
- Alembic
- JWT Authentication
- bcrypt
- python-dotenv

Frontend:

- The frontend already exists.
- The frontend communicates only through REST APIs.
- Never generate frontend code.

## API Prefix

All API routes must use:

```text
/api/v1
```

## Response Format

Every endpoint must return the standard response format.

Success:

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

Failure:

```json
{
  "success": false,
  "message": "",
  "errors": {}
}
```

Never return custom response formats.

## Database

Database engine:

- PostgreSQL

Database name:

```text
transitops
```

Required tables:

- users
- roles
- vehicles
- drivers
- trips
- maintenance_logs
- fuel_logs
- expenses

## Project Structure

The backend project structure must remain:

```text
backend/
app/
auth/
config/
database/
middleware/
models/
routers/
schemas/
services/
utils/
main.py
requirements.txt
.env
README.md
```

Never change this structure.

## Architecture

Request flow:

```text
Frontend
↓
REST API
↓
Router
↓
Service
↓
Database
```

Rules:

- Business logic must never exist inside routers.
- Routers only receive requests and return responses.
- Services contain all business logic.

## Business Rules

Business rules will be implemented later.

Do not implement business rules until explicitly requested.

## Coding Standards

Standards:

- Use snake_case for Python.
- Use SQLAlchemy ORM.
- Use dependency injection.
- Keep routers thin.
- Keep services independent.
- Avoid duplicate code.
- Follow SOLID principles where practical.

## Git Rules

Rules:

- Never modify unrelated files.
- Keep commits focused.
- Prefer small incremental changes.
- Do not rewrite published git history.
- Do not force push, rebase, amend, or squash commits that are already pushed.

## Future Rule

Every future prompt must first read `PROJECT_CONTEXT.md` before generating code.

If a future prompt conflicts with `PROJECT_CONTEXT.md`, ask for clarification instead of changing the architecture.
