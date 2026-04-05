from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_roles
from app.models.models import User, UserRole
from app.schemas.schemas import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user's profile."""
    return current_user


@router.get(
    "/",
    response_model=list[UserOut],
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def list_users(db: Session = Depends(get_db)):
    """List all users. Admin only."""
    return db.query(User).all()


@router.get(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """Update a user's name, role, or active status. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Permanently delete a user. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
