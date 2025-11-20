def test_login_success(client):
    res = client.post("/login", json={"login": "admin", "password": "admin123"})
    assert res.status_code == 200

def test_login_fail(client):
    res = client.post("/login", json={"login": "admin", "password": "wrong"})
    assert res.status_code == 401

