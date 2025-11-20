from models import Visit

def test_visit_created(app):
    v = Visit.query.first()
    assert v.patient_id > 0
    assert v.doctor_id > 0
    assert v.date is not None
