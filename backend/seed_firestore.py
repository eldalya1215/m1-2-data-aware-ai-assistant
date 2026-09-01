"""AirPassengers 144개 레코드를 빈 Firestore data 컬렉션에 적재한다."""

import csv
from pathlib import Path

from app.config import get_settings
from app.models import DataCreate
from app.repositories.firestore import FirestoreRepository


def main() -> None:
    settings = get_settings()
    repository = FirestoreRepository(
        service_account_json=settings.firebase_service_account_json,
        service_account_path=settings.firebase_service_account_path,
    )
    existing = repository.list_data()
    if existing:
        raise SystemExit(f"data 컬렉션에 이미 {len(existing)}개가 있어 중복 적재를 중단합니다.")

    csv_path = Path(settings.seed_csv_path)
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        repository.create_data(
            DataCreate(
                date=row["date"],
                value=float(row["passengers_thousands"]),
                memo="AirPassengers 원본 데이터",
            )
        )
    print(f"Firestore data 컬렉션에 {len(rows)}개 레코드를 적재했습니다.")


if __name__ == "__main__":
    main()
