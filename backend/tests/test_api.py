def test_health_and_swagger(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/docs").status_code == 200


def test_seed_data_and_summary(client):
    records = client.get("/api/data")
    assert records.status_code == 200
    assert len(records.json()) == 144

    summary = client.get("/api/data/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["count"] == 144
    assert payload["period"] == "1949-01 ~ 1960-12"
    assert payload["metrics"]["maximum"] == 622


def test_data_crud(client):
    created = client.post("/api/data", json={"date": "1961-01-01", "value": 450, "memo": "테스트"})
    assert created.status_code == 201
    record_id = created.json()["id"]

    updated = client.put(f"/api/data/{record_id}", json={"value": 475, "memo": "수정"})
    assert updated.status_code == 200
    assert updated.json()["value"] == 475

    deleted = client.delete(f"/api/data/{record_id}")
    assert deleted.status_code == 200
    assert client.delete(f"/api/data/{record_id}").status_code == 404


def test_conversation_and_context_chat(client):
    response = client.post("/api/chat", json={"message": "최근 추세가 어때?"})
    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["count"] == 144
    assert "144개" in body["answer"]

    conversation_id = body["conversation_id"]
    loaded = client.get(f"/api/conversations/{conversation_id}")
    assert loaded.status_code == 200
    assert len(loaded.json()["messages"]) == 2
    assert client.get("/api/conversations").json()[0]["id"] == conversation_id
    assert client.delete(f"/api/conversations/{conversation_id}").status_code == 200


def test_validation_and_export(client):
    invalid = client.post("/api/data", json={"date": "not-a-date", "value": -1, "memo": "x"})
    assert invalid.status_code == 422
    export = client.get("/api/data/export.csv")
    assert export.status_code == 200
    assert "text/csv" in export.headers["content-type"]
