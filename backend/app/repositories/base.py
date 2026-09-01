from abc import ABC, abstractmethod

from app.models import ConversationCreate, ConversationRecord, DataCreate, DataRecord, DataUpdate


class Repository(ABC):
    @abstractmethod
    def create_data(self, payload: DataCreate) -> DataRecord: ...

    @abstractmethod
    def list_data(self) -> list[DataRecord]: ...

    @abstractmethod
    def update_data(self, record_id: str, payload: DataUpdate) -> DataRecord | None: ...

    @abstractmethod
    def delete_data(self, record_id: str) -> bool: ...

    @abstractmethod
    def create_conversation(self, payload: ConversationCreate) -> ConversationRecord: ...

    @abstractmethod
    def list_conversations(self) -> list[ConversationRecord]: ...

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> ConversationRecord | None: ...

    @abstractmethod
    def update_conversation(self, conversation_id: str, payload: ConversationCreate) -> ConversationRecord | None: ...

    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> bool: ...
