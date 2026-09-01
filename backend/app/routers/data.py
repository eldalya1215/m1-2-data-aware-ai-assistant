import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_repository
from app.models import APIMessage, DataCreate, DataRecord, DataSummary, DataUpdate
from app.repositories.base import Repository
from app.services.summary import build_summary


router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", response_model=DataRecord, status_code=status.HTTP_201_CREATED)
def create_data(payload: DataCreate, repository: Repository = Depends(get_repository)):
    return repository.create_data(payload)


@router.get("", response_model=list[DataRecord])
def list_data(repository: Repository = Depends(get_repository)):
    return repository.list_data()


@router.get("/summary", response_model=DataSummary)
def get_summary(repository: Repository = Depends(get_repository)):
    return build_summary(repository.list_data())


@router.get("/export.csv", response_class=Response)
def export_csv(repository: Repository = Depends(get_repository)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "value", "memo"])
    for record in repository.list_data():
        writer.writerow([record.id, record.date.isoformat(), record.value, record.memo])
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data-export.csv"},
    )


@router.put("/{record_id}", response_model=DataRecord)
def update_data(record_id: str, payload: DataUpdate, repository: Repository = Depends(get_repository)):
    if not payload.model_fields_set:
        raise HTTPException(status_code=422, detail="수정할 필드를 하나 이상 입력하세요.")
    record = repository.update_data(record_id, payload)
    if record is None:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    return record


@router.delete("/{record_id}", response_model=APIMessage)
def delete_data(record_id: str, repository: Repository = Depends(get_repository)):
    if not repository.delete_data(record_id):
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    return APIMessage(message="데이터를 삭제했습니다.")
