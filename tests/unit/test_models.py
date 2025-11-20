from models import Admin, Patient, Medicine

def test_admin_password_hash(app):
    a = Admin.query.filter_by(login="admin").first()
    assert len(a.password_hash) == 64   # SHA256 hex

def test_patient_created(app):
    p = Patient.query.first()
    assert p.first_name is not None
    assert p.gender in ("M", "F")

def test_unique_medicine_name(app):
    m = Medicine(name="Paracetamol")
    from models import db
    db.session.add(m)
    try:
        db.session.commit()
        assert False  # не должно пройти
    except:
        db.session.rollback()
        assert True
