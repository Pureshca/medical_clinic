import pytest
from app import app, db, initialize_database
from models import User, Admin, Doctor, Patient, Medicine, Visit, VisitMedicine
from flask import url_for
from datetime import datetime
import hashlib

@pytest.fixture(scope="module")
def test_client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            initialize_database()
        yield testing_client
        with app.app_context():
            db.drop_all()

# ------------------------------
# Helper functions
# ------------------------------
def create_user(login, password, role):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if role == "admin":
        user = Admin(login=login, password_hash=password_hash)
    elif role == "doctor":
        user = Doctor(login=login, password_hash=password_hash, first_name="Doc", last_name="Tor", position="Therapist")
    elif role == "patient":
        user = Patient(login=login, password_hash=password_hash, first_name="Pat", last_name="Ient", gender="M", date_of_birth=datetime(2000,1,1), address="Street")
    db.session.add(user)
    db.session.commit()
    return user

def login_user(client, login, password):
    return client.post("/login", data={"login": login, "password": password}, follow_redirects=True)

# ------------------------------
# Health checks
# ------------------------------
def test_health_routes(test_client):
    rv = test_client.get("/health")
    assert rv.status_code == 200
    assert rv.json["status"] == "ok"

    rv_db = test_client.get("/health/db")
    assert rv_db.status_code == 200
    assert rv_db.json["db"] == "up"

# ------------------------------
# User login/logout
# ------------------------------
def test_login_logout(test_client):
    create_user("admin1", "pass123", "admin")
    rv = login_user(test_client, "admin1", "pass123")
    assert "Вход выполнен успешно!" in rv.data

    rv = test_client.get("/logout", follow_redirects=True)
    assert "Вы вышли из системы" in rv.data

def test_invalid_login(test_client):
    rv = login_user(test_client, "wrong", "wrong")
    assert "Неверные учетные данные" in rv.data

# ------------------------------
# Admin routes
# ------------------------------
def test_admin_add_doctor(test_client):
    create_user("admin2", "pass123", "admin")
    login_user(test_client, "admin2", "pass123")

    rv = test_client.post("/admin/add-doctor", data={
        "first_name": "John",
        "last_name": "Doe",
        "position": "Surgeon",
        "login": "jdoe",
        "password": "1234"
    }, follow_redirects=True)
    assert "Врач успешно добавлен" in rv.data

def test_admin_add_patient(test_client):
    login_user(test_client, "admin2", "pass123")

    rv = test_client.post("/admin/add-patient", data={
        "first_name": "Jane",
        "last_name": "Doe",
        "gender": "F",
        "date_of_birth": "1990-05-01",
        "address": "Some Street",
        "login": "jane",
        "password": "1234"
    }, follow_redirects=True)
    assert "Пациент успешно добавлен" in rv.data

def test_admin_add_medicine(test_client):
    login_user(test_client, "admin2", "pass123")
    rv = test_client.post("/admin/add-medicine", data={
        "name": "Aspirin",
        "description": "Painkiller",
        "side_effects": "Nausea",
        "usage_method": "Oral"
    }, follow_redirects=True)
    assert "Лекарство успешно добавлено" in rv.data

# ------------------------------
# Doctor routes
# ------------------------------
def test_doctor_add_visit(test_client):
    doc = create_user("doc1", "pass123", "doctor")
    pat = create_user("pat1", "pass123", "patient")
    med = Medicine(name="Ibuprofen", description="Anti-inflammatory", side_effects="None", usage_method="Oral")
    db.session.add(med)
    db.session.commit()

    login_user(test_client, "doc1", "pass123")

    rv = test_client.post("/doctor/add-visit", data={
        "patient_id": pat.id,
        "date": "2025-11-20T10:00",
        "location": "Room 101",
        "symptoms": "Headache",
        "diagnosis": "Migraine",
        "prescriptions": "Rest",
        "medicines[]": [med.id],
        "instructions[]": ["Take once daily"]
    }, follow_redirects=True)
    assert "Визит успешно добавлен" in rv.data

# ------------------------------
# Access control tests
# ------------------------------
def test_access_control(test_client):
    doc = create_user("doc2", "pass123", "doctor")
    pat = create_user("pat2", "pass123", "patient")

    login_user(test_client, "pat2", "pass123")
    rv = test_client.get("/admin/dashboard", follow_redirects=True)
    assert "Доступ запрещен" in rv.data

    login_user(test_client, "doc2", "pass123")
    rv = test_client.get("/admin/dashboard", follow_redirects=True)
    assert "Доступ запрещен" in rv.data

# ------------------------------
# CRUD delete tests
# ------------------------------
def test_admin_delete_entities(test_client):
    admin_user = create_user("admin3", "pass123", "admin")
    login_user(test_client, "admin3", "pass123")

    doc = create_user("docdel", "pass123", "doctor")
    pat = create_user("patdel", "pass123", "patient")
    med = Medicine(name="DeleteMed", description="Desc", side_effects="", usage_method="")
    db.session.add(med)
    db.session.commit()

    rv_doc = test_client.post(f"/admin/delete-doctor/{doc.id}", follow_redirects=True)
    assert "Врач успешно удален" in rv_doc.data

    rv_pat = test_client.post(f"/admin/delete-patient/{pat.id}", follow_redirects=True)
    assert "Пациент успешно удален" in rv_pat.data

    rv_med = test_client.post(f"/admin/delete-medicine/{med.id}", follow_redirects=True)
    assert "Лекарство успешно удалено" in rv_med.data
