def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200

def test_health_db(client):
    res = client.get("/health/db")
    assert res.status_code == 200
