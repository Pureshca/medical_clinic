import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models import User, Admin, Doctor, Patient
import hashlib

def test_user_roles(db_session):
    admin = Admin.query.first()
    doctor = Doctor.query.first()
    patient = Patient.query.first()

    assert admin.role == "admin"
    assert doctor.role == "doctor"
    assert patient.role == "patient"

def test_password_hash(db_session):
    doctor = Doctor.query.first()
    doctor.password_hash = hashlib.sha256("mypassword".encode()).hexdigest()
    db_session.commit()
    expected_hash = hashlib.sha256("mypassword".encode()).hexdigest()
    assert doctor.password_hash == expected_hash
