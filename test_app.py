import os
import pytest
from unittest.mock import patch

# Перед импортом подменяем БД на SQLite in-memory
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db  # noqa


# ============================================================
# FIXTURE: тестовый клиент Flask с app_context
# ============================================================
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        with app.test_client() as client:
            yield client


# ============================================================
# HEALTH CHECKS
# ============================================================
def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


# ============================================================
# LOGIN / LOGOUT
# ============================================================

def test_login_success(client):
    """Мокаем доступ к БД: Admin.query.filter_by().first()"""

    mock_admin = type("AdminMock", (), {
        "id": 1,
        "login": "test",
        "password_hash": "hash123"
    })()

    with patch("app.Admin.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = mock_admin

        with patch("app.check_password_hash", return_value=True):
            resp = client.post("/login", data={
                "login": "test",
                "password": "pass"
            }, follow_redirects=True)

    assert "Вход выполнен успешно" in resp.data.decode()


def test_login_fail(client):
    with patch("app.Admin.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None

        resp = client.post("/login", data={
            "login": "nope",
            "password": "wrong"
        }, follow_redirects=True)

    assert "Неверные учетные данные" in resp.data.decode()


def test_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "admin"

    resp = client.get("/logout", follow_redirects=True)
    assert "Вы вышли из системы" in resp.data.decode()


# ============================================================
# ACCESS CONTROL
# ============================================================

def test_admin_access_denied_for_anon(client):
    resp = client.get("/admin/dashboard", follow_redirects=True)
    assert "Пожалуйста, войдите" in resp.data.decode()


def test_admin_access_denied_for_doctor(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 10
        sess["role"] = "doctor"

    resp = client.get("/admin/dashboard", follow_redirects=True)
    assert "Доступ запрещен" in resp.data.decode()


def test_admin_access_allowed(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "admin"

    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200


# ============================================================
# ADMIN: ADD ENTITIES
# ============================================================

def test_admin_add_doctor(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.add"), \
         patch("app.db.session.commit"):

        resp = client.post("/admin/add-doctor", data={
            "first_name": "John",
            "last_name": "Doe",
            "position": "Therapist",
            "login": "jdoe",
            "password": "1234"
        }, follow_redirects=True)

        assert "Врач успешно добавлен" in resp.data.decode()


def test_admin_add_patient(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.add"), \
         patch("app.db.session.commit"):

        resp = client.post("/admin/add-patient", data={
            "first_name": "Jane",
            "last_name": "Doe",
            "gender": "F",
            "date_of_birth": "1990-01-01",
            "address": "Street",
            "login": "jane",
            "password": "pass"
        }, follow_redirects=True)

    assert "Пациент успешно добавлен" in resp.data.decode()


def test_admin_add_medicine(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.add"), \
         patch("app.db.session.commit"):

        resp = client.post("/admin/add-medicine", data={
            "name": "Aspirin",
            "description": "Painkiller",
            "side_effects": "Nausea",
            "usage_method": "Oral"
        }, follow_redirects=True)

    assert "Лекарство успешно добавлено" in resp.data.decode()


# ============================================================
# DELETE ENTITIES
# ============================================================

def test_admin_delete_doctor(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.delete"), \
         patch("app.db.session.commit"), \
         patch("app.Doctor.query.get", return_value=True):

        resp = client.post("/admin/delete-doctor/1", follow_redirects=True)

    assert "Врач успешно удален" in resp.data.decode()


def test_admin_delete_patient(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.delete"), \
         patch("app.db.session.commit"), \
         patch("app.Patient.query.get", return_value=True):

        resp = client.post("/admin/delete-patient/1", follow_redirects=True)

    assert "Пациент успешно удален" in resp.data.decode()


def test_admin_delete_medicine(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.delete"), \
         patch("app.db.session.commit"), \
         patch("app.Medicine.query.get", return_value=True):

        resp = client.post("/admin/delete-medicine/1", follow_redirects=True)

    assert "Лекарство успешно удалено" in resp.data.decode()
