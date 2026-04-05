from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_roles
from app.models.models import FinancialRecord, RecordType, User, UserRole
from app.schemas.schemas import PaginatedRecords, RecordCreate, RecordOut, RecordUpdate

router = APIRouter(prefix="/records", tags=["Financial Records"])


def get_record_or_404(record_id: int, db: Session) -> FinancialRecord:
    record = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.id == record_id, FinancialRecord.is_deleted == False)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ─── Create ───────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=RecordOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.admin, UserRole.analyst))],
)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new financial record. Admin and Analyst only."""
    record = FinancialRecord(**payload.model_dump(), created_by=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ─── List with Filters + Pagination ──────────────────────────────────────────

@router.get("/", response_model=PaginatedRecords)
def list_records(
    type: Optional[RecordType] = Query(None, description="Filter by income or expense"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    date_from: Optional[datetime] = Query(None, description="Filter records from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter records up to this date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # any authenticated user can view
):
    """
    List all financial records with optional filters and pagination.
    Accessible to all authenticated users (Viewer, Analyst, Admin).
    """
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if date_from:
        query = query.filter(FinancialRecord.date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.date <= date_to)

    total = query.count()
    total_pages = max(1, -(-total // page_size))  # ceiling division
    records = (
        query.order_by(FinancialRecord.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "data": records,
    }


# ─── Get Single ───────────────────────────────────────────────────────────────

@router.get("/{record_id}", response_model=RecordOut)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a single record by ID. All authenticated users."""
    return get_record_or_404(record_id, db)


# ─── Update ───────────────────────────────────────────────────────────────────

@router.patch(
    "/{record_id}",
    response_model=RecordOut,
    dependencies=[Depends(require_roles(UserRole.admin, UserRole.analyst))],
)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
):
    """Update a record. Admin and Analyst only."""
    record = get_record_or_404(record_id, db)
    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


# ─── Soft Delete ──────────────────────────────────────────────────────────────

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Soft delete a record (marks as deleted, not permanently removed). Admin only."""
    record = get_record_or_404(record_id, db)
    record.is_deleted = True
    db.commit()
