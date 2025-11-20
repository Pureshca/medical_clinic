import os
import pytest
from flask import session

# Перед импортом приложения — подменяем базу
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db, User   # noqa


@pytest.fixture
def client():
    """Создает тестовый клиент с sqlite in-memory."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


# ---------------------------
#   HEALTH CHECK
# ---------------------------

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_db(client):
    """Даже с пустой БД эндпоинт должен отвечать db: up."""
    response = client.get("/health/db")
    data = response.get_json()
    assert response.status_code == 200
    assert data["db"] == "up"


# ---------------------------
#   AUTH
# ---------------------------

def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"login" in response.data.lower()


def test_login_wrong_credentials(client):
    """Если пользователя нет — должен вернуть ошибку."""
    response = client.post("/login", data={
        "login": "unknown",
        "password": "wrong"
    }, follow_redirects=True)

    assert "Неверные учетные данные" in response.data


# ---------------------------
#   LOGIN SIMULATION
# ---------------------------

class DummyUser:
    """Минимальный мок User для принудительной авторизации."""
    def __init__(self, role):
        self.id = 1
        self.role = role
        self.login = "test"
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return "1"


@pytest.fixture
def login_as_admin(client, monkeypatch):
    """Принудительная авторизация как admin."""
    monkeypatch.setattr("flask_login.utils._get_user", lambda: DummyUser("admin"))
    return client


@pytest.fixture
def login_as_doctor(client, monkeypatch):
    monkeypatch.setattr("flask_login.utils._get_user", lambda: DummyUser("doctor"))
    return client


@pytest.fixture
def login_as_patient(client, monkeypatch):
    monkeypatch.setattr("flask_login.utils._get_user", lambda: DummyUser("patient"))
    return client


# ---------------------------
#   ROLE REDIRECTS
# ---------------------------

def test_redirect_admin(login_as_admin):
    response = login_as_admin.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/admin/dashboard" in response.location


def test_redirect_doctor(login_as_doctor):
    response = login_as_doctor.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/doctor/dashboard" in response.location


def test_redirect_patient(login_as_patient):
    response = login_as_patient.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/patient/dashboard" in response.location


# ---------------------------
#   ACCESS BLOCK
# ---------------------------

def test_admin_route_forbidden_for_doctor(login_as_doctor):
    response = login_as_doctor.get("/admin/dashboard", follow_redirects=True)
    assert "Доступ запрещен" in response.data


def test_admin_route_forbidden_for_patient(login_as_patient):
    response = login_as_patient.get("/admin/dashboard", follow_redirects=True)
    assert "Доступ запрещен" in response.data


# ---------------------------
#   LOGOUT
# ---------------------------

def test_logout(login_as_admin):
    response = login_as_admin.get("/logout", follow_redirects=True)
    assert "Вы вышли из системы" in response.data
