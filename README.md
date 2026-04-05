# Finance Dashboard API

A role-based finance management backend built with **FastAPI** and **SQLite**.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | FastAPI | Fast, modern, built-in Swagger UI |
| Database | SQLite | Zero setup, file-based, perfect for assessments |
| ORM | SQLAlchemy | Clean Pythonic DB access |
| Auth | JWT (python-jose) | Stateless, industry standard |
| Validation | Pydantic v2 | Automatic input validation with clear errors |
| Password Hashing | passlib + bcrypt | Secure, one-way hashing |

---

## Project Structure

```
finance-dashboard/
├── app/
│   ├── main.py              # App entry point, router registration
│   ├── config.py            # Settings (secret key, DB URL, token expiry)
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models/
│   │   └── models.py        # User and FinancialRecord DB models
│   ├── schemas/
│   │   └── schemas.py       # Pydantic schemas for request/response validation
│   ├── middleware/
│   │   └── auth.py          # JWT logic, password hashing, role guard factory
│   └── routers/
│       ├── auth.py          # POST /auth/register, POST /auth/login
│       ├── users.py         # User management (Admin only)
│       ├── records.py       # Financial record CRUD with filters + pagination
│       └── dashboard.py     # Summary analytics endpoints
├── seed.py                  # Creates 3 test users (admin/analyst/viewer)
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd finance-dashboard
pip install -r requirements.txt
```

### 2. Seed the database with test users

```bash
python seed.py
```

This creates:
| Email | Password | Role |
|---|---|---|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

### 4. Open Swagger UI

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

To authenticate in Swagger:
1. Call `POST /auth/login` with your credentials
2. Copy the `access_token` from the response
3. Click the **Authorize** button (top right of Swagger UI)
4. Paste the token and click Authorize

---

## Role-Based Access Control

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| `POST /auth/register` | ✅ | ✅ | ✅ |
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `GET /users/me` | ✅ | ✅ | ✅ |
| `GET /users/` | ❌ | ❌ | ✅ |
| `PATCH /users/{id}` | ❌ | ❌ | ✅ |
| `DELETE /users/{id}` | ❌ | ❌ | ✅ |
| `GET /records/` | ✅ | ✅ | ✅ |
| `GET /records/{id}` | ✅ | ✅ | ✅ |
| `POST /records/` | ❌ | ✅ | ✅ |
| `PATCH /records/{id}` | ❌ | ✅ | ✅ |
| `DELETE /records/{id}` | ❌ | ❌ | ✅ |
| `GET /dashboard/overview` | ✅ | ✅ | ✅ |
| `GET /dashboard/summary` | ❌ | ✅ | ✅ |

---

## API Reference

### Auth

#### `POST /auth/register`
Register a new user.
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secret123",
  "role": "viewer"
}
```

#### `POST /auth/login`
Login and receive a JWT token.
```json
{
  "email": "admin@finance.com",
  "password": "admin123"
}
```
Response:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

### Financial Records

#### `POST /records/`
Create a new record. (Analyst, Admin)
```json
{
  "amount": 5000,
  "type": "income",
  "category": "Salary",
  "date": "2024-03-01T00:00:00",
  "notes": "Monthly salary"
}
```

#### `GET /records/`
List records with optional filters and pagination. (All roles)

Query params:
- `type` — `income` or `expense`
- `category` — partial match (case-insensitive)
- `date_from` — ISO datetime
- `date_to` — ISO datetime
- `page` — default `1`
- `page_size` — default `10`, max `100`

Example:
```
GET /records/?type=expense&category=food&page=1&page_size=5
```

Response:
```json
{
  "total": 3,
  "page": 1,
  "page_size": 5,
  "total_pages": 1,
  "data": [...]
}
```

#### `PATCH /records/{id}`
Update a record partially. (Analyst, Admin)

#### `DELETE /records/{id}`
Soft delete a record — marks `is_deleted=true`, not permanently removed. (Admin)

---

### Dashboard

#### `GET /dashboard/overview`
Basic totals for all authenticated users.
```json
{
  "total_income": 13000.0,
  "total_expenses": 1500.0,
  "net_balance": 11500.0,
  "total_records": 4
}
```

#### `GET /dashboard/summary`
Full analytics for Analyst and Admin:
- Total income, expenses, net balance
- Category-wise totals (sorted by highest)
- Monthly income vs expense trends
- 5 most recent records

---

## Key Design Decisions & Assumptions

### 1. Soft Deletes
Records are never permanently deleted. They are marked with `is_deleted=True`. This preserves data integrity and allows recovery if needed. Only Admins can delete.

### 2. Role Guard Factory
Access control uses a reusable `require_roles(*roles)` factory function that returns a FastAPI dependency. This keeps route definitions clean:
```python
dependencies=[Depends(require_roles(UserRole.admin, UserRole.analyst))]
```

### 3. Analyst Can Create/Update Records
The assignment says Analysts can "view records and access insights". I extended this to allow record creation and updates as well, since Analysts are the primary data entry users in a finance dashboard. This is documented as an assumption.

### 4. Pagination
Implemented on `GET /records/` with `page` and `page_size` query params. Response includes `total`, `total_pages`, and `data` array.

### 5. SQLite
Used for zero-setup simplicity. The database file (`finance.db`) is auto-created on first run. To switch to PostgreSQL, simply change `DATABASE_URL` in `.env`.

### 6. JWT Expiry
Tokens expire after 24 hours by default. Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`.

---

## Environment Variables (optional)

Create a `.env` file to override defaults:

```env
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./finance.db
```

---

## Error Handling

| Scenario | Status Code |
|---|---|
| Invalid input / missing fields | `422 Unprocessable Entity` |
| Wrong email or password | `401 Unauthorized` |
| Insufficient role | `403 Forbidden` |
| Resource not found | `404 Not Found` |
| Duplicate email on register | `400 Bad Request` |
| Unexpected server error | `500 Internal Server Error` |

---

## What's Included (Optional Features)

- ✅ JWT Authentication
- ✅ Pagination
- ✅ Soft Deletes
- ✅ Swagger / OpenAPI docs (auto-generated at `/docs`)
- ✅ Input validation via Pydantic
- ✅ Role-based access control middleware
