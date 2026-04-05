from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.models import RecordType, UserRole


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.viewer


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# ─── Financial Record Schemas ─────────────────────────────────────────────────

class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Must be greater than 0")
    type: RecordType
    category: str = Field(..., min_length=1, max_length=100)
    date: datetime
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Category cannot be blank")
        return v.strip()


class RecordUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[RecordType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class RecordOut(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: str
    date: datetime
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Pagination Schema ────────────────────────────────────────────────────────

class PaginatedRecords(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: list[RecordOut]


# ─── Dashboard Schemas ────────────────────────────────────────────────────────

class CategorySummary(BaseModel):
    category: str
    total: float


class MonthlyTrend(BaseModel):
    month: str  # e.g. "2024-03"
    income: float
    expense: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_records: int
    category_wise: list[CategorySummary]
    monthly_trends: list[MonthlyTrend]
    recent_records: list[RecordOut]
