from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from app.config import settings
from app.database import Base, engine
from app.routers import auth, dashboard, records, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=settings.APP_NAME, version="1.0.0", routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema["paths"].values():
        for op in path.values():
            op["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Unexpected error"})

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Welcome to Finance Dashboard API"}
