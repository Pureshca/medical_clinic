def test_doctor_add_visit(client):
    client.post("/login", json={"login": "belov", "password": "doctor123"})

    res = client.post("/doctor/visit", json={
        "patient_id": 1,
        "date": "2025-01-01 10:00",
        "symptoms": "cough"
    })

    assert res.status_code == 201


def test_visit_json(client):
    client.post("/login", json={"login": "belov", "password": "doctor123"})
    res = client.get("/doctor/visit/1")
    assert res.status_code == 200
    assert "patient" in res.json
