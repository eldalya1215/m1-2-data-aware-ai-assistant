from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_repository
from app.models import APIMessage, ConversationCreate, ConversationRecord
from app.repositories.base import Repository


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationRecord, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate, repository: Repository = Depends(get_repository)):
    return repository.create_conversation(payload)


@router.get("", response_model=list[ConversationRecord])
def list_conversations(repository: Repository = Depends(get_repository)):
    return repository.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationRecord)
def get_conversation(conversation_id: str, repository: Repository = Depends(get_repository)):
    conversation = repository.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return conversation


@router.delete("/{conversation_id}", response_model=APIMessage)
def delete_conversation(conversation_id: str, repository: Repository = Depends(get_repository)):
    if not repository.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return APIMessage(message="대화를 삭제했습니다.")
