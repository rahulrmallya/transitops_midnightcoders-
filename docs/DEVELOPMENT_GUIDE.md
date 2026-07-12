# TransitOps Development Guide

This guide defines development expectations for the TransitOps backend.

## Folder Structure

Keep the existing backend structure unchanged:

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

Do not rename folders, move files, or introduce a new architecture.

## Architecture

Request flow:

```text
Frontend
REST API
Router
Service
Database
```

Rules:

- Routers receive requests and return standard API responses.
- Services contain business logic.
- Database access should use SQLAlchemy ORM.
- Dependency injection should be used for shared resources such as database sessions and authenticated users.

## Coding Standards

- Use Python 3.12.
- Use FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, JWT authentication, bcrypt, and python-dotenv.
- Use `snake_case` for Python variables, functions, modules, and database field names.
- Use clear, small functions.
- Keep routers thin.
- Keep services independent.
- Avoid duplicate code.
- Follow SOLID principles where practical.
- Do not add business rules until explicitly requested.

## API Standards

All endpoints must be prefixed with:

```text
/api/v1
```

All responses must follow:

```json
{
  "success": true,
  "message": "",
  "data": {}
}
```

or:

```json
{
  "success": false,
  "message": "",
  "errors": {}
}
```

Never return custom response formats.

## Frontend API Consumption

- The frontend must communicate only through REST APIs.
- The frontend should use the contract in `docs/API_CONTRACT.md`.
- The frontend should expect all responses to include `success`, `message`, and either `data` or `errors`.
- JSON response fields may use `camelCase` where appropriate for frontend mapping.
- Backend internals should remain `snake_case`.

## Naming Conventions

- Python files, functions, variables, and ORM attributes: `snake_case`
- Database tables and columns: `snake_case`
- JSON fields exposed for frontend mapping: `camelCase` where appropriate
- Classes and Pydantic schemas: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

## Environment Variables

Expected variables should be defined in `.env` and loaded with `python-dotenv`.

Recommended environment variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ENVIRONMENT`

Do not commit real secrets.

## Branch Strategy

- Keep branches small and focused.
- Use descriptive branch names.
- Avoid rewriting published history.
- Do not force push, rebase, amend, or squash commits already pushed to the connected branch.
- Keep the branch in a working state so Lovable sync remains reliable.

## Commit Message Convention

Use concise, descriptive commit messages.

Recommended format:

```text
type: short description
```

Common types:

- `docs`
- `feat`
- `fix`
- `refactor`
- `test`
- `chore`

Examples:

```text
docs: add API contract
feat: add vehicle service
fix: handle missing driver lookup
```

## Development Rules

- Read `PROJECT_CONTEXT.md` before generating code.
- Do not modify `PROJECT_CONTEXT.md` unless explicitly instructed.
- Do not modify unrelated files.
- Do not change API formats without approval.
- Extend the existing architecture instead of replacing it.
