# Finance Dashboard API

I built this as a backend assignment — a REST API for a role-based finance dashboard where different users interact with financial data based on their access level.

A few decisions I made deliberately:

- Used SQLite instead of PostgreSQL. The assignment is about backend logic, not infrastructure. SQLite means anyone can clone this and run it in under a minute with no external setup.
- Built the role guard as a reusable factory function (`require_roles()`). Adding a new role or changing permissions on any route is a one-line change, not a refactor.
- Analysts can create and update records, not just read them. In a real finance dashboard, analysts own the data entry — restricting them to read-only didn't make sense.
- Soft deletes on records. Data shouldn't disappear permanently in a finance system. Deleted records stay in the DB marked as `is_deleted=True`.

The API is fully explorable via Swagger at `/docs` — no separate client needed.

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

```
finance-dashboard/
├── app/
│   ├── main.py              # entry point, registers all routers
│   ├── config.py            # JWT secret, token expiry, DB URL
│   ├── database.py          # SQLAlchemy engine and session
│   ├── models/
│   │   └── models.py        # User and FinancialRecord table definitions
│   ├── schemas/
│   │   └── schemas.py       # Pydantic schemas for input validation
│   ├── middleware/
│   │   └── auth.py          # JWT creation, role-based access guards
│   └── routers/
│       ├── auth.py          # POST /auth/register, POST /auth/login
│       ├── users.py         # user management (admin only)
│       ├── records.py       # CRUD + filters + pagination
│       └── dashboard.py     # summary analytics endpoints
├── seed.py                  # creates admin, analyst, viewer test users
├── requirements.txt
└── README.md
```

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

## Error Responses

| Situation | Status |
|---|---|
| Missing or invalid fields | 422 |
| Wrong credentials | 401 |
| Insufficient role | 403 |
| Resource not found | 404 |
| Duplicate email | 400 |