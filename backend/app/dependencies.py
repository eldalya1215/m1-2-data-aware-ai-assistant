from functools import lru_cache

from app.config import get_settings
from app.repositories.base import Repository
from app.repositories.firestore import FirestoreRepository
from app.repositories.memory import MemoryRepository


@lru_cache
def get_repository() -> Repository:
    settings = get_settings()
    if settings.storage_backend.lower() == "firestore":
        return FirestoreRepository(
            service_account_json=settings.firebase_service_account_json,
            service_account_path=settings.firebase_service_account_path,
        )
    return MemoryRepository(settings.seed_csv_path)
