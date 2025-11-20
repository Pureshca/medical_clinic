import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models import Visit

def test_visit_created(app):
    v = Visit.query.first()
    assert v.patient_id > 0
    assert v.doctor_id > 0
    assert v.date is not None
