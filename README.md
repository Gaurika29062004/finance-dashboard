# Finance Dashboard API

A backend API for a role-based finance dashboard, built as part of an internship assignment.

Built with FastAPI and SQLite. No frontend — the API is the product.

---

## Stack

- **FastAPI** — Python web framework
- **SQLite** — file-based database, zero setup required
- **SQLAlchemy** — ORM for database access
- **JWT** — stateless authentication via python-jose
- **Pydantic v2** — request/response validation
- **passlib + bcrypt** — password hashing

---

## Project Structure
finance-dashboard/
├── app/
│   ├── main.py              # app entry point
│   ├── config.py            # settings and environment variables
│   ├── database.py          # database engine and session
│   ├── models/
│   │   └── models.py        # User and FinancialRecord table definitions
│   ├── schemas/
│   │   └── schemas.py       # pydantic schemas for validation
│   ├── middleware/
│   │   └── auth.py          # JWT logic, password hashing, role guards
│   └── routers/
│       ├── auth.py          # register and login
│       ├── users.py         # user management
│       ├── records.py       # financial records CRUD
│       └── dashboard.py     # summary and analytics
├── seed.py                  # creates 3 test users
├── requirements.txt
└── README.md
---

## Setup
```bash
git clone https://github.com/Gaurika29062004/finance-dashboard.git
cd finance-dashboard

python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt

python3 seed.py

uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to explore the API.

---

## Test Users

| Email | Password | Role |
|---|---|---|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

---

## Roles and Permissions

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| Login / Register | yes | yes | yes |
| View records | yes | yes | yes |
| Create / update records | no | yes | yes |
| Delete records | no | no | yes |
| Dashboard overview | yes | yes | yes |
| Dashboard full summary | no | yes | yes |
| Manage users | no | no | yes |

---

## API Overview

### Auth
- `POST /auth/register` — create a new user
- `POST /auth/login` — returns a JWT token

### Records
- `POST /records/` — create a record (analyst, admin)
- `GET /records/` — list records with filters and pagination
- `GET /records/{id}` — get a single record
- `PATCH /records/{id}` — update a record (analyst, admin)
- `DELETE /records/{id}` — soft delete (admin only)

Filters available on `GET /records/`: `type`, `category`, `date_from`, `date_to`, `page`, `page_size`

### Dashboard
- `GET /dashboard/overview` — totals for all authenticated users
- `GET /dashboard/summary` — full breakdown with category totals and monthly trends (analyst, admin)

### Users
- `GET /users/` — list all users (admin)
- `GET /users/me` — current user profile
- `PATCH /users/{id}` — update role or status (admin)
- `DELETE /users/{id}` — delete user (admin)

---

## Key Design Decisions

**Soft deletes** — records are never permanently removed, just marked as deleted. This preserves data history and allows recovery.

**Role guard factory** — access control uses a reusable `require_roles()` function that wraps FastAPI's dependency system. Keeps route definitions clean.

**SQLite** — chosen deliberately for zero-setup simplicity. The database file is created automatically on first run. Switching to PostgreSQL only requires changing `DATABASE_URL` in the config.

**Analyst permissions** — the assignment describes analysts as having read access and insight access. I extended this to include record creation and updates, since in a real finance dashboard the analyst role typically owns data entry.

---

## Error Responses

| Situation | Status |
|---|---|
| Missing or invalid fields | 422 |
| Wrong credentials | 401 |
| Insufficient role | 403 |
| Resource not found | 404 |
| Duplicate email | 400 |

---

## Optional Features Included

- JWT authentication
- Pagination on record listing
- Soft deletes
- Swagger UI at `/docs`
- Input validation via Pydantic
