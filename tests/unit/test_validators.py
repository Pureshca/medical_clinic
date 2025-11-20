import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models import Patient
from datetime import datetime

def test_patient_date_of_birth(db_session):
    patient = Patient.query.first()
    patient.date_of_birth = datetime.strptime("2000-01-01", "%Y-%m-%d")
    db_session.commit()
    assert patient.date_of_birth.year == 2000
