from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api import documents, users, payments, admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Translation System API",
    description="API for translation management System with premium features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Enhanced CORS Configuration
origins = [
    "https://6j2q5nl3-8000.uks1.devtunnels.ms",
    "http://localhost:3000",
    "http://192.168.30.1:3000",  # Added port
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Important for dev tunnels
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Only add HTTPS redirect if not using dev tunnels
if not settings.DEBUG and "devtunnels.ms" not in str(settings.ALLOWED_HOSTS):
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    https_only=not settings.DEBUG,  # Only force HTTPS in production
    same_site="lax"  # Changed from "none" for better security
)

# Routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(admin.router, prefix="/api/admins", tags=["admins"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])


@app.options("/{path:path}")
async def options_handler():
    return {"message": "OK"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}