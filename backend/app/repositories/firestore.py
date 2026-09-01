import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

from app.models import ConversationCreate, ConversationRecord, DataCreate, DataRecord, DataUpdate, utcnow
from app.repositories.base import Repository


class FirestoreRepository(Repository):
    def __init__(self, service_account_json: str | None, service_account_path: str | None) -> None:
        if not firebase_admin._apps:
            if service_account_json:
                credential = credentials.Certificate(json.loads(service_account_json))
            elif service_account_path:
                credential = credentials.Certificate(str(Path(service_account_path).expanduser()))
            else:
                raise RuntimeError("Firestore 사용 시 서비스 계정 환경 변수가 필요합니다.")
            firebase_admin.initialize_app(credential)
        self.db = firestore.client()

    @staticmethod
    def _data_record(document) -> DataRecord:
        return DataRecord(id=document.id, **document.to_dict())

    @staticmethod
    def _conversation_record(document) -> ConversationRecord:
        return ConversationRecord(id=document.id, **document.to_dict())

    def create_data(self, payload: DataCreate) -> DataRecord:
        now = utcnow()
        ref = self.db.collection("data").document()
        body = {**payload.model_dump(mode="json"), "created_at": now, "updated_at": now}
        ref.set(body)
        return DataRecord(id=ref.id, **body)

    def list_data(self) -> list[DataRecord]:
        documents = self.db.collection("data").order_by("date").stream()
        return [self._data_record(doc) for doc in documents]

    def update_data(self, record_id: str, payload: DataUpdate) -> DataRecord | None:
        ref = self.db.collection("data").document(record_id)
        snapshot = ref.get()
        if not snapshot.exists:
            return None
        changes = {**payload.model_dump(mode="json", exclude_unset=True), "updated_at": utcnow()}
        ref.update(changes)
        return self._data_record(ref.get())

    def delete_data(self, record_id: str) -> bool:
        ref = self.db.collection("data").document(record_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True

    def create_conversation(self, payload: ConversationCreate) -> ConversationRecord:
        now = utcnow()
        ref = self.db.collection("conversations").document()
        body = {**payload.model_dump(mode="json"), "created_at": now, "updated_at": now}
        ref.set(body)
        return ConversationRecord(id=ref.id, **body)

    def list_conversations(self) -> list[ConversationRecord]:
        documents = self.db.collection("conversations").order_by("updated_at", direction=firestore.Query.DESCENDING).stream()
        return [self._conversation_record(doc) for doc in documents]

    def get_conversation(self, conversation_id: str) -> ConversationRecord | None:
        snapshot = self.db.collection("conversations").document(conversation_id).get()
        return self._conversation_record(snapshot) if snapshot.exists else None

    def update_conversation(self, conversation_id: str, payload: ConversationCreate) -> ConversationRecord | None:
        ref = self.db.collection("conversations").document(conversation_id)
        if not ref.get().exists:
            return None
        ref.update({**payload.model_dump(mode="json"), "updated_at": utcnow()})
        return self._conversation_record(ref.get())

    def delete_conversation(self, conversation_id: str) -> bool:
        ref = self.db.collection("conversations").document(conversation_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True
