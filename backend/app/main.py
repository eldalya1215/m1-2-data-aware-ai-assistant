from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, conversations, data
from app.models import HealthResponse


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="시계열 데이터 CRUD, 요약, 대화 저장, GPT 컨텍스트 주입 API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/", tags=["system"])
def root():
    return {"message": settings.app_name, "docs": "/docs"}


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health():
    return HealthResponse(status="ok", storage_backend=settings.storage_backend, ai_backend=settings.ai_backend)
