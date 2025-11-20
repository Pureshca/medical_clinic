import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import app, db
from models import User, Admin, Doctor, Patient, Medicine, Visit, VisitMedicine

@pytest.fixture(scope="session")
def test_app():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        # populate test data
        admin = Admin(login="admin", password_hash="adminpass")
        doctor = Doctor(login="doctor", password_hash="doctorpass", first_name="John", last_name="Doe", position="Therapist")
        patient = Patient(login="patient", password_hash="patientpass", first_name="Jane", last_name="Doe", gender="F")
        db.session.add_all([admin, doctor, patient])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def db_session(test_app):
    from app import db
    yield db.session
    db.session.rollback()
