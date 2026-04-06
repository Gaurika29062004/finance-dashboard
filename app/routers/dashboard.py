from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_roles
from app.models.models import FinancialRecord, RecordType, User, UserRole
from app.schemas.schemas import (
    CategorySummary,
    DashboardSummary,
    MonthlyTrend,
    RecordOut,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin, UserRole.analyst)),
):
    """Full dashboard summary. Analyst and Admin only."""
    records = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.is_deleted == False)
        .order_by(FinancialRecord.date.desc())
        .all()
    )

    total_income = sum(r.amount for r in records if r.type == RecordType.income)
    total_expenses = sum(r.amount for r in records if r.type == RecordType.expense)
    net_balance = total_income - total_expenses

    category_map = defaultdict(float)
    for r in records:
        category_map[r.category] += r.amount

    category_wise = [
        CategorySummary(category=cat, total=round(total, 2))
        for cat, total in sorted(category_map.items(), key=lambda x: -x[1])
    ]

    monthly_map = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for r in records:
        month_key = r.date.strftime("%Y-%m")
        if r.type == RecordType.income:
            monthly_map[month_key]["income"] += r.amount
        else:
            monthly_map[month_key]["expense"] += r.amount

    monthly_trends = [
        MonthlyTrend(
            month=month,
            income=round(data["income"], 2),
            expense=round(data["expense"], 2),
        )
        for month, data in sorted(monthly_map.items())
    ]

    recent_records = records[:5]

    return DashboardSummary(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_balance=round(net_balance, 2),
        total_records=len(records),
        category_wise=category_wise,
        monthly_trends=monthly_trends,
        recent_records=[RecordOut.model_validate(r) for r in recent_records],
    )


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Basic totals. All authenticated users."""
    records = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.is_deleted == False)
        .all()
    )
    total_income = round(sum(r.amount for r in records if r.type == RecordType.income), 2)
    total_expenses = round(sum(r.amount for r in records if r.type == RecordType.expense), 2)

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": round(total_income - total_expenses, 2),
        "total_records": len(records),
    }