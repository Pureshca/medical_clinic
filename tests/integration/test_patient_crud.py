def test_patient_list(client):
    client.post("/login", json={"login": "admin", "password": "admin123"})
    res = client.get("/admin/patients")
    assert res.status_code == 200
    assert len(res.json) > 5
