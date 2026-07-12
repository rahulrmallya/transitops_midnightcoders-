from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.database import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.services.expense_service import (
    ExpenseNotFoundError,
    ExpenseService,
    ExpenseValidationError,
)
from app.services.vehicle_service import VehicleNotFoundError

router = APIRouter()

EXPENSE_ROLES = ("Fleet Manager", "Financial Analyst")
EXPENSE_RESPONSES = {
    status.HTTP_200_OK: {"description": "Expense operation completed."},
    status.HTTP_201_CREATED: {"description": "Expense created."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid expense request."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Expense or vehicle not found."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error."},
}


def _handle_expense_service_error(exc: Exception) -> None:
    if isinstance(exc, (ExpenseNotFoundError, VehicleNotFoundError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, ExpenseValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    summary="List expenses",
    description=(
        "Returns paginated operating expenses with vehicle and category filters "
        "for cost review."
    ),
    responses=EXPENSE_RESPONSES,
)
def get_expenses(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*EXPENSE_ROLES))],
    vehicle_id: Annotated[
        int | None,
        Query(gt=0, description="Filter expenses for a specific vehicle."),
    ] = None,
    expense_type: Annotated[
        str | None,
        Query(
            description="Filter by expense category such as Toll, Permit, or Parking.",
        ),
    ] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort field supported by the expense service."),
    ] = "created_at",
    sort_order: Annotated[
        str,
        Query(description="Sort direction: asc or desc."),
    ] = "desc",
    page: Annotated[int, Query(ge=1, description="One-based page number.")] = 1,
    limit: Annotated[
        int,
        Query(ge=1, description="Maximum records to return per page."),
    ] = 10,
) -> SuccessResponse[dict[str, Any]]:
    service = ExpenseService(db)
    try:
        expenses = service.get_all_expenses(
            vehicle_id=vehicle_id,
            expense_type=expense_type,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )
    except Exception as exc:
        _handle_expense_service_error(exc)

    return SuccessResponse(message="Expenses retrieved", data=expenses)


@router.get(
    "/{expense_id}",
    response_model=SuccessResponse[ExpenseResponse],
    summary="Get expense",
    description=(
        "Returns a single expense record with category, amount, date, and "
        "vehicle reference."
    ),
    responses=EXPENSE_RESPONSES,
)
def get_expense(
    expense_id: Annotated[int, Path(gt=0, description="Unique expense identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*EXPENSE_ROLES))],
) -> SuccessResponse[ExpenseResponse]:
    service = ExpenseService(db)
    try:
        expense = service.get_expense_by_id(expense_id)
    except Exception as exc:
        _handle_expense_service_error(exc)

    return SuccessResponse(
        message="Expense retrieved",
        data=ExpenseResponse.model_validate(expense),
    )


@router.post(
    "",
    response_model=SuccessResponse[ExpenseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create expense",
    description="Creates an operating expense for an existing vehicle.",
    responses=EXPENSE_RESPONSES,
)
def create_expense(
    payload: ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*EXPENSE_ROLES))],
) -> SuccessResponse[ExpenseResponse]:
    service = ExpenseService(db)
    try:
        expense = service.create_expense(payload)
    except Exception as exc:
        _handle_expense_service_error(exc)

    return SuccessResponse(
        message="Expense created",
        data=ExpenseResponse.model_validate(expense),
    )


@router.put(
    "/{expense_id}",
    response_model=SuccessResponse[ExpenseResponse],
    summary="Update expense",
    description="Updates an existing operating expense record.",
    responses=EXPENSE_RESPONSES,
)
def update_expense(
    expense_id: Annotated[int, Path(gt=0, description="Unique expense identifier.")],
    payload: ExpenseUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*EXPENSE_ROLES))],
) -> SuccessResponse[ExpenseResponse]:
    service = ExpenseService(db)
    try:
        expense = service.update_expense(expense_id, payload)
    except Exception as exc:
        _handle_expense_service_error(exc)

    return SuccessResponse(
        message="Expense updated",
        data=ExpenseResponse.model_validate(expense),
    )


@router.delete(
    "/{expense_id}",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Delete expense",
    description="Deletes an expense record when no longer needed for cost tracking.",
    responses=EXPENSE_RESPONSES,
)
def delete_expense(
    expense_id: Annotated[int, Path(gt=0, description="Unique expense identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*EXPENSE_ROLES))],
) -> SuccessResponse[dict[str, Any]]:
    service = ExpenseService(db)
    try:
        service.delete_expense(expense_id)
    except Exception as exc:
        _handle_expense_service_error(exc)

    return SuccessResponse(message="Expense deleted", data={})
