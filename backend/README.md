# TransitOps Backend

Enterprise Transport Operations Platform Backend.

## Project Setup

Create a virtual environment from the `backend` directory:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

## Install

```bash
pip install -r requirements.txt
```

## Database Configuration

Copy `.env.example` to `.env` and provide the PostgreSQL connection string and secrets:

```text
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/transitops
SECRET_KEY=replace-with-a-secure-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Do not commit real secrets.

## Run

```bash
uvicorn app.main:app --reload
```

Health check:

```text
GET /api/v1/health
```

Swagger UI:

```text
/docs
```
