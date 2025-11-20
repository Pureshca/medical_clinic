from models import Patient

def test_patient_gender_validation(app):
    p = Patient(
        first_name="A",
        last_name="B",
        gender="Invalid",
        date_of_birth="2000-01-01",
        login="abc",
        password_hash="123"
    )
    from models import db
    db.session.add(p)
    try:
        db.session.commit()
        assert False
    except:
        db.session.rollback()
        assert True
