# TransitOps Backend

Enterprise Transport Operations Platform Backend built with FastAPI, SQLAlchemy, PostgreSQL, JWT authentication, and Pydantic.

## Installation

Run commands from the `backend` directory.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Database

TransitOps expects PostgreSQL and the `transitops` database.

Create the database locally before running the API:

```sql
CREATE DATABASE transitops;
```

Configure the connection in `.env`:

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/transitops
```

Run migrations or create tables using the project migration workflow before seeding data.

## Run Commands

Start the development server:

```bash
uvicorn app.main:app --reload
```

Health check:

```text
GET /api/v1/health
```

Compile check:

```bash
python -m compileall app
```

## Seed Command

Populate development data:

```bash
python scripts/seed_data.py
```

The seed script creates roles, users, 15 vehicles, 20 drivers, 20 trips, 10 maintenance records, 25 fuel logs, and 20 expenses. It uses stable identifiers so repeated runs do not create duplicate seed records.

Default seeded user password:

```text
TransitOps@123
```

## API Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

All API routes are prefixed with:

```text
/api/v1
```

All endpoints return the standard `SuccessResponse` or `ErrorResponse` format.

## Environment Variables

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/transitops
SECRET_KEY=replace-with-a-secure-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Do not commit real secrets.
