def test_admin_only_access(client):
    # Логиним пациента
    client.post("/login", json={"login": "ivanov", "password": "password123"})

    res = client.get("/admin/doctors")
    assert res.status_code == 403
