import csv
from pathlib import Path
from threading import RLock
from uuid import uuid4

from app.models import ConversationCreate, ConversationRecord, DataCreate, DataRecord, DataUpdate, utcnow
from app.repositories.base import Repository


class MemoryRepository(Repository):
    """로컬 개발과 자동 테스트용 저장소. 운영 환경에서는 Firestore를 사용한다."""

    def __init__(self, seed_csv_path: str | None = None) -> None:
        self._data: dict[str, DataRecord] = {}
        self._conversations: dict[str, ConversationRecord] = {}
        self._lock = RLock()
        if seed_csv_path:
            self._seed(seed_csv_path)

    def _seed(self, seed_csv_path: str) -> None:
        path = Path(seed_csv_path)
        if not path.exists():
            return
        with path.open(encoding="utf-8-sig", newline="") as file:
            for index, row in enumerate(csv.DictReader(file), start=1):
                payload = DataCreate(
                    date=row["date"],
                    value=float(row["passengers_thousands"]),
                    memo="AirPassengers 원본 데이터",
                )
                now = utcnow()
                record_id = f"seed-{index:03d}"
                self._data[record_id] = DataRecord(id=record_id, created_at=now, updated_at=now, **payload.model_dump())

    def create_data(self, payload: DataCreate) -> DataRecord:
        with self._lock:
            now = utcnow()
            record = DataRecord(id=uuid4().hex, created_at=now, updated_at=now, **payload.model_dump())
            self._data[record.id] = record
            return record

    def list_data(self) -> list[DataRecord]:
        with self._lock:
            return sorted(self._data.values(), key=lambda item: (item.date, item.id))

    def update_data(self, record_id: str, payload: DataUpdate) -> DataRecord | None:
        with self._lock:
            current = self._data.get(record_id)
            if current is None:
                return None
            updated = current.model_copy(update={**payload.model_dump(exclude_unset=True), "updated_at": utcnow()})
            self._data[record_id] = updated
            return updated

    def delete_data(self, record_id: str) -> bool:
        with self._lock:
            return self._data.pop(record_id, None) is not None

    def create_conversation(self, payload: ConversationCreate) -> ConversationRecord:
        with self._lock:
            now = utcnow()
            record = ConversationRecord(id=uuid4().hex, created_at=now, updated_at=now, **payload.model_dump())
            self._conversations[record.id] = record
            return record

    def list_conversations(self) -> list[ConversationRecord]:
        with self._lock:
            return sorted(self._conversations.values(), key=lambda item: item.updated_at, reverse=True)

    def get_conversation(self, conversation_id: str) -> ConversationRecord | None:
        with self._lock:
            return self._conversations.get(conversation_id)

    def update_conversation(self, conversation_id: str, payload: ConversationCreate) -> ConversationRecord | None:
        with self._lock:
            current = self._conversations.get(conversation_id)
            if current is None:
                return None
            updated = current.model_copy(update={**payload.model_dump(), "updated_at": utcnow()})
            self._conversations[conversation_id] = updated
            return updated

    def delete_conversation(self, conversation_id: str) -> bool:
        with self._lock:
            return self._conversations.pop(conversation_id, None) is not None
