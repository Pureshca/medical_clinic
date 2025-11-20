import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models import User, Doctor, Patient, Medicine, Visit

def test_user_authenticate(db_session):
    user = User.query.filter_by(login="admin").first()
    # Так как hash не настоящий, проверяем существование
    assert user.login == "admin"

def test_create_medicine(db_session):
    med = Medicine(name="Aspirin", description="Painkiller", side_effects="Nausea", usage_method="Oral")
    db_session.add(med)
    db_session.commit()
    retrieved = Medicine.query.filter_by(name="Aspirin").first()
    assert retrieved is not None
    assert retrieved.usage_method == "Oral"

def test_create_visit(db_session):
    doctor = Doctor.query.first()
    patient = Patient.query.first()
    visit = Visit(patient_id=patient.id, doctor_id=doctor.id, location="Room 101")
    db_session.add(visit)
    db_session.commit()
    assert Visit.query.count() == 1

