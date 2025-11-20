# tests/test_app.py
import os
import pytest
from unittest.mock import patch

# Перед импортом приложения подменяем БД
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db  # noqa


# ============================================================
# FIXTURE: тестовый клиент Flask
# ============================================================
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================
# HEALTH CHECKS
# ============================================================
def test_health_check(client):
    """Проверяем, что endpoint /health работает без БД."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


# ============================================================
# LOGIN / LOGOUT
# ============================================================

def test_login_success(client):
    """Успешный вход (мокаем поиск в БД и проверку пароля)."""

    mock_admin = type("AdminMock", (), {"id": 1, "login": "test", "password_hash": "hash123"})()

    with patch("app.Admin.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = mock_admin

        with patch("app.check_password_hash", return_value=True):
            resp = client.post("/login", data={
                "login": "test",
                "password": "pass"
            }, follow_redirects=True)

    assert "Вход выполнен успешно" in resp.data


def test_login_fail(client):
    """Неуспешный вход: пользователя нет."""
    with patch("app.Admin.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None

        resp = client.post("/login", data={
            "login": "nope",
            "password": "wrong"
        }, follow_redirects=True)

    assert "Неверные учетные данные" in resp.data


def test_logout(client):
    """Проверяем, что logout работает без БД."""

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "admin"

    resp = client.get("/logout", follow_redirects=True)
    assert "Вы вышли из системы" in resp.data


# ============================================================
# ACCESS CONTROL
# ============================================================

def test_admin_access_denied_for_anon(client):
    resp = client.get("/admin/dashboard", follow_redirects=True)
    assert "Пожалуйста, войдите" in resp.data


def test_admin_access_denied_for_doctor(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 10
        sess["role"] = "doctor"

    resp = client.get("/admin/dashboard", follow_redirects=True)
    assert "Доступ запрещен" in resp.data


def test_admin_access_allowed(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "admin"

    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200


# ============================================================
# ADMIN: ADD ENTITIES (DOCTOR, PATIENT, MEDICINE)
# ============================================================

def test_admin_add_doctor(client):
    """Добавление врача — мокаем session.add/commit"""

    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.add") as mock_add, \
         patch("app.db.session.commit") as mock_commit:

        resp = client.post("/admin/add-doctor", data={
            "first_name": "John",
            "last_name": "Doe",
            "position": "Therapist",
            "login": "jdoe",
            "password": "1234"
        }, follow_redirects=True)

        assert "Врач успешно добавлен" in resp.data
        mock_add.assert_called_once()
        mock_commit.assert_called_once()


def test_admin_add_patient(client):
    """Добавление пациента без БД."""
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.add") as mock_add, \
         patch("app.db.session.commit") as mock_commit:

        resp = client.post("/admin/add-patient", data={
            "first_name": "Jane",
            "last_name": "Doe",
            "gender": "F",
            "date_of_birth": "1990-01-01",
            "address": "Street",
            "login": "jane",
            "password": "pass"
        }, follow_redirects=True)

        assert "Пациент успешно добавлен" in resp.data
        mock_add.assert_called_once()
        mock_commit.assert_called_once()


def test_admin_add_medicine(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.add") as mock_add, \
         patch("app.db.session.commit") as mock_commit:

        resp = client.post("/admin/add-medicine", data={
            "name": "Aspirin",
            "description": "Painkiller",
            "side_effects": "Nausea",
            "usage_method": "Oral"
        }, follow_redirects=True)

        assert "Лекарство успешно добавлено" in resp.data
        mock_add.assert_called_once()
        mock_commit.assert_called_once()


# ============================================================
# DELETE ENTITIES
# ============================================================

def test_admin_delete_doctor(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.delete") as mock_delete, \
         patch("app.db.session.commit") as mock_commit, \
         patch("app.Doctor.query.get", return_value=True):

        resp = client.post("/admin/delete-doctor/1", follow_redirects=True)

        assert "Врач успешно удален" in resp.data
        mock_delete.assert_called_once()
        mock_commit.assert_called_once()


def test_admin_delete_patient(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.delete") as mock_delete, \
         patch("app.db.session.commit") as mock_commit, \
         patch("app.Patient.query.get", return_value=True):

        resp = client.post("/admin/delete-patient/1", follow_redirects=True)

        assert "Пациент успешно удален" in resp.data
        mock_delete.assert_called_once()
        mock_commit.assert_called_once()


def test_admin_delete_medicine(client):
    with patch("app.is_admin", return_value=True), \
         patch("app.db.session.delete") as mock_delete, \
         patch("app.db.session.commit") as mock_commit, \
         patch("app.Medicine.query.get", return_value=True):

        resp = client.post("/admin/delete-medicine/1", follow_redirects=True)

        assert "Лекарство успешно удалено" in resp.data
        mock_delete.assert_called_once()
        mock_commit.assert_called_once()
