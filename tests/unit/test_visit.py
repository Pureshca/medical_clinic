import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models import Visit, VisitMedicine, Medicine, Doctor, Patient

def test_visit_medicine_relation(db_session):
    doctor = Doctor.query.first()
    patient = Patient.query.first()
    med = Medicine(name="TestMed", description="Desc", side_effects="", usage_method="Oral")
    db_session.add(med)
    db_session.commit()

    visit = Visit(patient_id=patient.id, doctor_id=doctor.id, location="Room 1")
    db_session.add(visit)
    db_session.commit()

    vm = VisitMedicine(visit_id=visit.id, medicine_id=med.id, doctor_instructions="Take daily")
    db_session.add(vm)
    db_session.commit()

    retrieved_vm = VisitMedicine.query.filter_by(visit_id=visit.id).first()
    assert retrieved_vm.medicine_id == med.id
    assert retrieved_vm.doctor_instructions == "Take daily"
