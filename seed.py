"""
Run this script once to create an initial admin user.
Usage: python seed.py
"""
from app.database import SessionLocal, Base, engine
from app.models.models import User, UserRole
from app.middleware.auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    existing = db.query(User).filter(User.email == "admin@finance.com").first()
    if existing:
        print("Admin user already exists. Skipping.")
        return

    admin = User(
        name="Super Admin",
        email="admin@finance.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
        is_active=True,
    )
    analyst = User(
        name="Test Analyst",
        email="analyst@finance.com",
        hashed_password=hash_password("analyst123"),
        role=UserRole.analyst,
        is_active=True,
    )
    viewer = User(
        name="Test Viewer",
        email="viewer@finance.com",
        hashed_password=hash_password("viewer123"),
        role=UserRole.viewer,
        is_active=True,
    )

    db.add_all([admin, analyst, viewer])
    db.commit()
    print("✅ Seeded users:")
    print("  Admin   → admin@finance.com   / admin123")
    print("  Analyst → analyst@finance.com / analyst123")
    print("  Viewer  → viewer@finance.com  / viewer123")

if __name__ == "__main__":
    seed()
    db.close()
