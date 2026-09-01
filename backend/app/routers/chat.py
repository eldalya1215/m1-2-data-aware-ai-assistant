from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.dependencies import get_repository
from app.models import ChatRequest, ChatResponse, ConversationCreate, Message
from app.repositories.base import Repository
from app.services.chat import generate_answer
from app.services.summary import build_summary


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    repository: Repository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
):
    summary = build_summary(repository.list_data())
    try:
        answer = generate_answer(payload.message, payload.history, summary, settings)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 응답을 생성하지 못했습니다: {error}",
        ) from error

    messages = [*payload.history, Message(role="user", content=payload.message), Message(role="assistant", content=answer)]
    title = payload.message[:40]
    conversation_payload = ConversationCreate(title=title, messages=messages)
    conversation = None
    if payload.conversation_id:
        conversation = repository.update_conversation(payload.conversation_id, conversation_payload)
    if conversation is None:
        conversation = repository.create_conversation(conversation_payload)
    return ChatResponse(answer=answer, conversation_id=conversation.id, summary=summary)
