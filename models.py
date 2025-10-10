import os
import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import current_app

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum("M", "F"), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Medicine(db.Model):
    __tablename__ = "medicines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    usage_method = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Visit(db.Model):
    __tablename__ = "visits"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False
    )
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescriptions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="visits", lazy=True)
    doctor = db.relationship("Doctor", backref="visits", lazy=True)


class VisitMedicine(db.Model):
    __tablename__ = "visit_medicines"
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(
        db.Integer, db.ForeignKey("visits.id", ondelete="CASCADE"), nullable=False
    )
    medicine_id = db.Column(
        db.Integer, db.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False
    )
    doctor_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    visit = db.relationship("Visit", backref="visit_medicines", lazy=True)
    medicine = db.relationship("Medicine", backref="visit_medicines", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("visit_id", "medicine_id", name="unique_visit_medicine"),
    )


class User(UserMixin):
    def __init__(self, id, login, role):
        self.id = id
        self.login = login
        self.role = role
        self._id = f"{role}_{id}"

    def get_id(self):
        return self._id

    @staticmethod
    def get(user_id):
        try:
            if "_" not in user_id:
                return None
            role, id_str = user_id.split("_", 1)
            user_id_int = int(id_str)
            model = {"admin": Admin, "doctor": Doctor, "patient": Patient}.get(role)
            if model:
                obj = model.query.get(user_id_int)
                if obj:
                    return User(obj.id, getattr(obj, "login", None), role)
            return None
        except Exception as e:
            print(f"Error loading user: {e}")
            return None

    @staticmethod
    def authenticate(login, password):
        try:
            entered_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
            for role, model in [
                ("admin", Admin),
                ("doctor", Doctor),
                ("patient", Patient),
            ]:
                user = model.query.filter_by(login=login).first()
                if user and user.password_hash.lower() == entered_hash.lower():
                    return User(user.id, user.login, role)
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None


# ---------- ИНИЦИАЛИЗАЦИЯ И ЗАПОЛНЕНИЕ БД ----------


def populate_db():
    """Заполняет базу тестовыми данными, если таблицы пустые."""
    try:
        if not Admin.query.first():
            admins = [
                Admin(
                    login="admin",
                    password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
                ),
                Admin(
                    login="admin2",
                    password_hash=hashlib.sha256("admin456".encode()).hexdigest(),
                ),
                Admin(
                    login="admin3",
                    password_hash=hashlib.sha256("admin789".encode()).hexdigest(),
                ),
                Admin(
                    login="admin4",
                    password_hash=hashlib.sha256("admin000".encode()).hexdigest(),
                ),
                Admin(
                    login="admin5",
                    password_hash=hashlib.sha256("admin111".encode()).hexdigest(),
                ),
                Admin(
                    login="admin6",
                    password_hash=hashlib.sha256("admin222".encode()).hexdigest(),
                ),
                Admin(
                    login="admin7",
                    password_hash=hashlib.sha256("admin333".encode()).hexdigest(),
                ),
                Admin(
                    login="admin8",
                    password_hash=hashlib.sha256("admin444".encode()).hexdigest(),
                ),
                Admin(
                    login="admin9",
                    password_hash=hashlib.sha256("admin555".encode()).hexdigest(),
                ),
                Admin(
                    login="admin10",
                    password_hash=hashlib.sha256("admin666".encode()).hexdigest(),
                ),
                Admin(
                    login="admin11",
                    password_hash=hashlib.sha256("admin777".encode()).hexdigest(),
                ),
                Admin(
                    login="admin12",
                    password_hash=hashlib.sha256("admin888".encode()).hexdigest(),
                ),
                Admin(
                    login="admin13",
                    password_hash=hashlib.sha256("admin999".encode()).hexdigest(),
                ),
                Admin(
                    login="admin14",
                    password_hash=hashlib.sha256("admin001".encode()).hexdigest(),
                ),
                Admin(
                    login="admin15",
                    password_hash=hashlib.sha256("admin002".encode()).hexdigest(),
                ),
            ]
            db.session.add_all(admins)
            print("✅ Admins added")

        if not Patient.query.first():
            patients = [
                Patient(
                    first_name="Ivan",
                    last_name="Ivanov",
                    gender="M",
                    date_of_birth=datetime(1985, 3, 15),
                    address="10 Lenin St, Apt 5",
                    login="ivanov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Maria",
                    last_name="Petrova",
                    gender="F",
                    date_of_birth=datetime(1990, 7, 22),
                    address="25 Pushkin St, Apt 12",
                    login="petrova",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Alexey",
                    last_name="Sidorov",
                    gender="M",
                    date_of_birth=datetime(1978, 11, 3),
                    address="7 Gagarin St, Apt 33",
                    login="sidorov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Elena",
                    last_name="Kuznetsova",
                    gender="F",
                    date_of_birth=datetime(1982, 5, 18),
                    address="15 Sovetskaya St, Apt 8",
                    login="kuznetsova",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Dmitry",
                    last_name="Popov",
                    gender="M",
                    date_of_birth=datetime(1995, 9, 30),
                    address="3 Mira St, Apt 17",
                    login="popov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Olga",
                    last_name="Vasilieva",
                    gender="F",
                    date_of_birth=datetime(1988, 12, 12),
                    address="21 Sadovaya St, Apt 9",
                    login="vasilieva",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Sergey",
                    last_name="Smirnov",
                    gender="M",
                    date_of_birth=datetime(1975, 2, 28),
                    address="45 Tsentralnaya St, Apt 22",
                    login="smirnov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Natalia",
                    last_name="Novikova",
                    gender="F",
                    date_of_birth=datetime(1992, 6, 7),
                    address="12 Lesnaya St, Apt 4",
                    login="novikova",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Andrey",
                    last_name="Fedorov",
                    gender="M",
                    date_of_birth=datetime(1980, 8, 14),
                    address="8 Shkolnaya St, Apt 11",
                    login="fedorov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Tatyana",
                    last_name="Morozova",
                    gender="F",
                    date_of_birth=datetime(1987, 1, 25),
                    address="17 Zarechnaya St, Apt 6",
                    login="morozova",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Pavel",
                    last_name="Volkov",
                    gender="M",
                    date_of_birth=datetime(1993, 4, 9),
                    address="5 Parkovaya St, Apt 14",
                    login="volkov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Yulia",
                    last_name="Alekseeva",
                    gender="F",
                    date_of_birth=datetime(1984, 10, 17),
                    address="11 Solnechnaya St, Apt 7",
                    login="alekseeva",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Anton",
                    last_name="Lebedev",
                    gender="M",
                    date_of_birth=datetime(1979, 7, 3),
                    address="9 Naberezhnaya St, Apt 19",
                    login="lebedev",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Irina",
                    last_name="Semenova",
                    gender="F",
                    date_of_birth=datetime(1991, 3, 28),
                    address="14 Yubileynaya St, Apt 10",
                    login="semenova",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
                Patient(
                    first_name="Maxim",
                    last_name="Egorov",
                    gender="M",
                    date_of_birth=datetime(1986, 11, 11),
                    address="6 Rabochaya St, Apt 13",
                    login="egorov",
                    password_hash=hashlib.sha256("password123".encode()).hexdigest(),
                ),
            ]
            db.session.add_all(patients)
            print("✅ Patients added")

        if not Doctor.query.first():
            doctors = [
                Doctor(
                    first_name="Alexander",
                    last_name="Belov",
                    position="Therapist",
                    login="belov",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Ekaterina",
                    last_name="Kozlova",
                    position="Surgeon",
                    login="kozlova",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Mikhail",
                    last_name="Orlov",
                    position="Cardiologist",
                    login="orlov",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Svetlana",
                    last_name="Andreeva",
                    position="Neurologist",
                    login="andreeva",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Artem",
                    last_name="Makarov",
                    position="Ophthalmologist",
                    login="makarov",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Nadezhda",
                    last_name="Zakharova",
                    position="ENT Specialist",
                    login="zakharova",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Vladimir",
                    last_name="Sokolov",
                    position="Endocrinologist",
                    login="sokolov",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Oksana",
                    last_name="Pavlova",
                    position="Gastroenterologist",
                    login="pavlova",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Grigory",
                    last_name="Stepanov",
                    position="Urologist",
                    login="stepanov",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Lyudmila",
                    last_name="Nikolaeva",
                    position="Gynecologist",
                    login="nikolaeva",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Stanislav",
                    last_name="Ivanov",
                    position="Pediatrician",
                    login="ivanov_doc",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Victoria",
                    last_name="Dmitrieva",
                    position="Dermatologist",
                    login="dmitrieva",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Roman",
                    last_name="Kuznetsov",
                    position="Oncologist",
                    login="kuznetsov_doc",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Anastasia",
                    last_name="Soloveva",
                    position="Psychiatrist",
                    login="soloveva",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
                Doctor(
                    first_name="Konstantin",
                    last_name="Vasiliev",
                    position="Traumatologist",
                    login="vasiliev_doc",
                    password_hash=hashlib.sha256("doctor123".encode()).hexdigest(),
                ),
            ]
            db.session.add_all(doctors)

        if not Medicine.query.first():
            medicines = [
                Medicine(
                    name="Paracetamol",
                    description="Painkiller and fever reducer",
                    side_effects="Nausea, abdominal pain, allergic reactions",
                    usage_method="1 tablet 3-4 times a day after meals",
                ),
                Medicine(
                    name="Ibuprofen",
                    description="Non-steroidal anti-inflammatory drug",
                    side_effects="Headache, dizziness, nausea, heartburn",
                    usage_method="1 tablet 3 times a day during meals",
                ),
                Medicine(
                    name="Amoxicillin",
                    description="Broad-spectrum antibiotic",
                    side_effects="Nausea, diarrhea, allergic reactions",
                    usage_method="1 tablet 3 times a day for 7-10 days",
                ),
                Medicine(
                    name="Aspirin",
                    description="Painkiller, fever reducer, anti-inflammatory",
                    side_effects="Stomach irritation, bleeding",
                    usage_method="1 tablet 2-3 times a day after meals",
                ),
                Medicine(
                    name="Loratadine",
                    description="Antiallergic drug",
                    side_effects="Headache, drowsiness, dry mouth",
                    usage_method="1 tablet once a day",
                ),
                Medicine(
                    name="Omeprazole",
                    description="Reduces stomach acid",
                    side_effects="Nausea, constipation, headache",
                    usage_method="1 capsule once a day in the morning on empty stomach",
                ),
                Medicine(
                    name="Metformin",
                    description="Antidiabetic drug",
                    side_effects="Nausea, diarrhea, metallic taste",
                    usage_method="1 tablet 2-3 times a day with meals",
                ),
                Medicine(
                    name="Atorvastatin",
                    description="Reduces cholesterol",
                    side_effects="Headache, muscle pain, nausea",
                    usage_method="1 tablet once a day in the evening",
                ),
                Medicine(
                    name="Amlodipine",
                    description="Lowers blood pressure",
                    side_effects="Headache, leg swelling, dizziness",
                    usage_method="1 tablet once a day",
                ),
                Medicine(
                    name="Salbutamol",
                    description="Bronchodilator",
                    side_effects="Rapid heartbeat, tremor, headache",
                    usage_method="Inhale 1-2 puffs as needed",
                ),
                Medicine(
                    name="Cetirizine",
                    description="Antiallergic drug",
                    side_effects="Drowsiness, dry mouth, fatigue",
                    usage_method="1 tablet once a day",
                ),
                Medicine(
                    name="Diclofenac",
                    description="Non-steroidal anti-inflammatory drug",
                    side_effects="Stomach pain, nausea, dizziness",
                    usage_method="1 tablet 2-3 times a day after meals",
                ),
                Medicine(
                    name="Enalapril",
                    description="Lowers blood pressure",
                    side_effects="Dizziness, cough, fatigue",
                    usage_method="1 tablet 1-2 times a day",
                ),
                Medicine(
                    name="Fluoxetine",
                    description="Antidepressant",
                    side_effects="Nausea, insomnia, headache",
                    usage_method="1 capsule once a day in the morning",
                ),
                Medicine(
                    name="Warfarin",
                    description="Anticoagulant",
                    side_effects="Bleeding, bruising",
                    usage_method="1 tablet once a day under INR monitoring",
                ),
            ]
            db.session.bulk_save_objects(medicines)

        if not Visit.query.first():
            visits = [
                Visit(
                    patient_id=1,
                    doctor_id=1,
                    date=datetime(2024, 1, 15, 9, 0, 0),
                    location="Office 101",
                    symptoms="Headache, temperature 37.5",
                    diagnosis="Acute respiratory infection",
                    prescriptions="Bed rest, plenty of fluids",
                ),
                Visit(
                    patient_id=2,
                    doctor_id=2,
                    date=datetime(2024, 1, 15, 10, 30, 0),
                    location="Office 102",
                    symptoms="Acute abdominal pain, nausea",
                    diagnosis="Acute appendicitis",
                    prescriptions="Immediate hospitalization",
                ),
                Visit(
                    patient_id=3,
                    doctor_id=3,
                    date=datetime(2024, 1, 16, 11, 0, 0),
                    location="Office 103",
                    symptoms="Chest pain, shortness of breath",
                    diagnosis="Angina",
                    prescriptions="Limit physical activity",
                ),
                Visit(
                    patient_id=4,
                    doctor_id=4,
                    date=datetime(2024, 1, 16, 14, 0, 0),
                    location="Office 104",
                    symptoms="Dizziness, numbness in arm",
                    diagnosis="Cerebral circulatory disorder",
                    prescriptions="Inpatient treatment",
                ),
                Visit(
                    patient_id=5,
                    doctor_id=5,
                    date=datetime(2024, 1, 17, 9, 30, 0),
                    location="Office 105",
                    symptoms="Vision deterioration, eye pain",
                    diagnosis="Glaucoma",
                    prescriptions="Eye drops, IOP monitoring",
                ),
                Visit(
                    patient_id=6,
                    doctor_id=6,
                    date=datetime(2024, 1, 17, 11, 15, 0),
                    location="Office 106",
                    symptoms="Sore throat, nasal congestion",
                    diagnosis="Acute pharyngitis",
                    prescriptions="Gargle, inhalation",
                ),
                Visit(
                    patient_id=7,
                    doctor_id=7,
                    date=datetime(2024, 1, 18, 10, 0, 0),
                    location="Office 107",
                    symptoms="Thirst, frequent urination",
                    diagnosis="Type 2 diabetes",
                    prescriptions="Diet, hypoglycemic drugs",
                ),
                Visit(
                    patient_id=8,
                    doctor_id=8,
                    date=datetime(2024, 1, 18, 15, 30, 0),
                    location="Office 108",
                    symptoms="Epigastric pain, heartburn",
                    diagnosis="Gastritis",
                    prescriptions="Diet, antacids",
                ),
                Visit(
                    patient_id=9,
                    doctor_id=9,
                    date=datetime(2024, 1, 19, 9, 45, 0),
                    location="Office 109",
                    symptoms="Pain during urination",
                    diagnosis="Cystitis",
                    prescriptions="Antibiotics, plenty of fluids",
                ),
                Visit(
                    patient_id=10,
                    doctor_id=10,
                    date=datetime(2024, 1, 19, 13, 20, 0),
                    location="Office 110",
                    symptoms="Menstrual cycle disorder",
                    diagnosis="Ovarian dysfunction",
                    prescriptions="Hormone therapy",
                ),
                Visit(
                    patient_id=11,
                    doctor_id=11,
                    date=datetime(2024, 1, 20, 10, 10, 0),
                    location="Office 111",
                    symptoms="High fever, cough",
                    diagnosis="Pneumonia",
                    prescriptions="Antibiotics, bed rest",
                ),
                Visit(
                    patient_id=12,
                    doctor_id=12,
                    date=datetime(2024, 1, 20, 14, 45, 0),
                    location="Office 112",
                    symptoms="Skin rash, itching",
                    diagnosis="Allergic dermatitis",
                    prescriptions="Antihistamines",
                ),
                Visit(
                    patient_id=13,
                    doctor_id=13,
                    date=datetime(2024, 1, 21, 11, 30, 0),
                    location="Office 113",
                    symptoms="Breast lump",
                    diagnosis="Fibroadenoma",
                    prescriptions="Ultrasound, oncologist consultation",
                ),
                Visit(
                    patient_id=14,
                    doctor_id=14,
                    date=datetime(2024, 1, 21, 16, 0, 0),
                    location="Office 114",
                    symptoms="Anxiety, insomnia",
                    diagnosis="Anxiety disorder",
                    prescriptions="Psychotherapy, sedatives",
                ),
                Visit(
                    patient_id=15,
                    doctor_id=15,
                    date=datetime(2024, 1, 22, 9, 15, 0),
                    location="Office 115",
                    symptoms="Knee pain after injury",
                    diagnosis="Ligament sprain",
                    prescriptions="Rest, ice, elevation",
                ),
            ]
            db.session.bulk_save_objects(visits)

        if not VisitMedicine.query.first():
            visit_medicines = [
                VisitMedicine(
                    visit_id=1,
                    medicine_id=1,
                    doctor_instructions="Take if temperature exceeds 38 degrees",
                ),
                VisitMedicine(
                    visit_id=1,
                    medicine_id=2,
                    doctor_instructions="Take for severe headache",
                ),
                VisitMedicine(
                    visit_id=2,
                    medicine_id=3,
                    doctor_instructions="7-day course after surgery",
                ),
                VisitMedicine(
                    visit_id=3,
                    medicine_id=8,
                    doctor_instructions="Take regularly, monitor cholesterol",
                ),
                VisitMedicine(
                    visit_id=3,
                    medicine_id=9,
                    doctor_instructions="Take daily, monitor blood pressure",
                ),
                VisitMedicine(
                    visit_id=4,
                    medicine_id=13,
                    doctor_instructions="Take morning and evening, monitor BP",
                ),
                VisitMedicine(
                    visit_id=5,
                    medicine_id=6,
                    doctor_instructions="1 drop in each eye twice a day",
                ),
                VisitMedicine(
                    visit_id=6,
                    medicine_id=5,
                    doctor_instructions="Take once a day for allergy",
                ),
                VisitMedicine(
                    visit_id=7,
                    medicine_id=7,
                    doctor_instructions="Take twice a day with meals",
                ),
                VisitMedicine(
                    visit_id=8,
                    medicine_id=6,
                    doctor_instructions="Take 30 minutes before meals",
                ),
                VisitMedicine(
                    visit_id=9,
                    medicine_id=3,
                    doctor_instructions="5-day course, drink plenty of water",
                ),
                VisitMedicine(
                    visit_id=10,
                    medicine_id=14,
                    doctor_instructions="Take in the morning, do not skip",
                ),
                VisitMedicine(
                    visit_id=11,
                    medicine_id=3,
                    doctor_instructions="10-day course, do not stop early",
                ),
                VisitMedicine(
                    visit_id=12,
                    medicine_id=5,
                    doctor_instructions="Take once a day until symptoms disappear",
                ),
                VisitMedicine(
                    visit_id=13,
                    medicine_id=15,
                    doctor_instructions="Take at the same time daily, monitor INR",
                ),
            ]
            db.session.commit()
            print("✅ Database populated successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error populating database: {e}")
        raise
