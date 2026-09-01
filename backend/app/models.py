from __future__ import annotations

from datetime import date as DateType
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DataCreate(BaseModel):
    date: DateType
    value: float = Field(ge=0, le=1_000_000_000)
    memo: str = Field(default="", max_length=300)


class DataUpdate(BaseModel):
    date: DateType | None = None
    value: float | None = Field(default=None, ge=0, le=1_000_000_000)
    memo: str | None = Field(default=None, max_length=300)

    @field_validator("date", "value", "memo")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("수정 필드는 null일 수 없습니다.")
        return value


class DataRecord(DataCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class SummaryMetrics(BaseModel):
    total: float
    average: float
    maximum: float
    minimum: float
    latest: float


class DataSummary(BaseModel):
    period: str
    count: int
    metrics: SummaryMetrics
    trend: Literal["상승", "하락", "유지", "데이터 부족"]
    recent_change_pct: float | None
    latest_date: DateType | None
    unit: str = "천 명"


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)


class ConversationCreate(BaseModel):
    title: str = Field(default="새 대화", min_length=1, max_length=100)
    messages: list[Message] = Field(min_length=1, max_length=100)


class ConversationRecord(ConversationCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
    history: list[Message] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    summary: DataSummary


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class APIMessage(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    storage_backend: str
    ai_backend: str

    model_config = ConfigDict(json_schema_extra={"examples": [{"status": "ok", "storage_backend": "firestore", "ai_backend": "openai"}]})
