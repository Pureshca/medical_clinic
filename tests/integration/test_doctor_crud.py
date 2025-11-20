def test_doctor_create(client):
    client.post("/login", json={"login": "admin", "password": "admin123"})

    res = client.post("/admin/doctors", json={
        "first_name": "Test",
        "last_name": "Doctor",
        "position": "Test",
        "login": "test_doc",
        "password": "123"
    })
    assert res.status_code == 201
