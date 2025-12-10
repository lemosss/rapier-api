from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.auth.routes import router as auth_router
from apps.companies.routes import router as companies_router
from core.config import settings

app = FastAPI(
    title="Rapier Auth API",
    description="API com sistema de autenticação e múltiplos apps",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(companies_router, prefix="/api/v1", tags=["companies"])


@app.get("/")
async def root():
    return {"message": "Rapier Auth API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

