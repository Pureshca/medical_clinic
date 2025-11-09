from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

from sqlalchemy import text
from models import (
    db,
    Admin,
    Doctor,
    Patient,
    Medicine,
    Visit,
    VisitMedicine,
    User,
    populate_db,
)
from datetime import datetime
from dotenv import load_dotenv
import os
import time
import traceback
import hashlib


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-secret-key")


# Используем SQLite для простоты
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Fallback для разработки
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_url = f'sqlite:///{os.path.join(basedir, "medical_clinic.db")}'

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Инициализируем базу данных
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def wait_for_db():
    """Ждем пока база данных станет доступной"""
    max_retries = 30
    retry_interval = 2

    for i in range(max_retries):
        try:
            with app.app_context():
                db.session.execute(text("SELECT 1"))
                print("✅ Database connection successful!")
                return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"⏳ Waiting for database... ({i+1}/{max_retries}) - {e}")
                time.sleep(retry_interval)
            else:
                print(f"❌ Database connection failed after {max_retries} retries: {e}")
                return False


def initialize_database():
    """Инициализация базы данных с обработкой ошибок"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with app.app_context():
                print(
                    f"🔄 Creating database tables (attempt {attempt + 1}/{max_retries})..."
                )
                db.create_all()
                print("✅ Database tables created successfully!")

                print("🔄 Populating database with initial data...")
                populate_db()
                print("✅ Database populated successfully!")
                return True

        except Exception as e:
            print(
                f"❌ Error during database initialization (attempt {attempt + 1}): {e}"
            )
            if attempt < max_retries - 1:
                print("⏳ Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("❌ All retries failed")
                return False


@app.route("/health")
def health_check():
    try:
        # Проверяем подключение к базе данных
        db.session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500


# Routes
@app.route("/")
def index():
    if current_user.is_authenticated:
        print(
            f"DEBUG: User {current_user.login} with role {current_user.role} authenticated"
        )

        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif current_user.role == "doctor":
            return redirect(url_for("doctor_dashboard"))
        elif current_user.role == "patient":
            return redirect(url_for("patient_dashboard"))
        else:
            flash("Неизвестная роль пользователя", "error")
            return redirect(url_for("login"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_name = request.form["login"]
        password = request.form["password"]

        user = User.authenticate(login_name, password)
        if user:
            login_user(user)
            flash("Вход выполнен успешно!", "success")
            return redirect(url_for("index"))
        else:
            flash("Неверные учетные данные", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("login"))


# Admin routes
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        # Исправленный запрос с явным выбором полей
        visits = (
            db.session.query(
                Visit.id,
                Visit.date,
                Visit.location,
                Visit.diagnosis,
                Patient.first_name.label("patient_first_name"),
                Patient.last_name.label("patient_last_name"),
                Doctor.first_name.label("doctor_first_name"),
                Doctor.last_name.label("doctor_last_name"),
            )
            .join(Patient, Visit.patient_id == Patient.id)
            .join(Doctor, Visit.doctor_id == Doctor.id)
            .order_by(Visit.date.desc())
            .all()
        )

        # Статистика
        total_visits = Visit.query.count()
        total_patients = Patient.query.count()
        total_doctors = Doctor.query.count()

        return render_template(
            "admin/dashboard.html",
            visits=visits,
            total_visits=total_visits,
            total_patients=total_patients,
            total_doctors=total_doctors,
        )

    except Exception as e:
        flash(f"Ошибка: {str(e)}", "error")
        return render_template("admin/dashboard.html", visits=[])


@app.route("/admin/visits/<int:visit_id>")
@login_required
def admin_visit_detail(visit_id):
    if current_user.role != "admin":
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        # Получаем детали визита
        visit_data = (
            db.session.query(Visit, Patient, Doctor)
            .join(Patient, Visit.patient_id == Patient.id)
            .join(Doctor, Visit.doctor_id == Doctor.id)
            .filter(Visit.id == visit_id)
            .first()
        )

        if not visit_data:
            return jsonify({"error": "Визит не найден"}), 404

        visit, patient, doctor = visit_data

        # Получаем назначенные лекарства
        medicines = (
            db.session.query(VisitMedicine, Medicine)
            .join(Medicine, VisitMedicine.medicine_id == Medicine.id)
            .filter(VisitMedicine.visit_id == visit_id)
            .all()
        )

        result = {
            "id": visit.id,
            "patient_id": visit.patient_id,
            "doctor_id": visit.doctor_id,
            "date": visit.date.isoformat() if visit.date else None,
            "location": visit.location,
            "symptoms": visit.symptoms,
            "diagnosis": visit.diagnosis,
            "prescriptions": visit.prescriptions,
            "patient_first_name": patient.first_name,
            "patient_last_name": patient.last_name,
            "date_of_birth": (
                patient.date_of_birth.isoformat() if patient.date_of_birth else None
            ),
            "gender": patient.gender,
            "address": patient.address,
            "doctor_first_name": doctor.first_name,
            "doctor_last_name": doctor.last_name,
            "position": doctor.position,
            "medicines": [
                {
                    "name": medicine.name,
                    "description": medicine.description,
                    "side_effects": medicine.side_effects,
                    "usage_method": medicine.usage_method,
                    "doctor_instructions": visit_medicine.doctor_instructions,
                }
                for visit_medicine, medicine in medicines
            ],
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/add-doctor", methods=["GET", "POST"])
@login_required
def admin_add_doctor():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            position = request.form["position"]
            login_name = request.form["login"]
            password = request.form["password"]

            # Проверяем, существует ли уже такой логин
            existing_doctor = Doctor.query.filter_by(login=login_name).first()
            if existing_doctor:
                flash("Логин уже существует", "error")
                return redirect(url_for("admin_add_doctor"))

            # Добавляем врача
            new_doctor = Doctor(
                first_name=first_name,
                last_name=last_name,
                position=position,
                login=login_name,
                password_hash=hashlib.sha256(password.encode()).hexdigest(),
            )

            db.session.add(new_doctor)
            db.session.commit()

            flash("Врач успешно добавлен", "success")
            return redirect(url_for("admin_add_doctor"))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка: {str(e)}", "error")

    return render_template("admin/add_doctor.html")


@app.route("/admin/add-patient", methods=["GET", "POST"])
@login_required
def admin_add_patient():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            gender = request.form["gender"]
            date_of_birth = datetime.strptime(request.form["date_of_birth"], "%Y-%m-%d")
            address = request.form["address"]
            login_name = request.form["login"]
            password = request.form["password"]

            # Проверяем, существует ли уже такой логин
            existing_patient = Patient.query.filter_by(login=login_name).first()
            if existing_patient:
                flash("Логин уже существует", "error")
                return redirect(url_for("admin_add_patient"))

            # Добавляем пациента
            new_patient = Patient(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                login=login_name,
                password_hash=hashlib.sha256(password.encode()).hexdigest(),
            )

            db.session.add(new_patient)
            db.session.commit()

            flash("Пациент успешно добавлен", "success")
            return redirect(url_for("admin_add_patient"))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка: {str(e)}", "error")

    return render_template("admin/add_patient.html")


@app.route("/admin/add-medicine", methods=["GET", "POST"])
@login_required
def admin_add_medicine():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        if request.method == "POST":
            name = request.form["name"]
            description = request.form["description"]
            side_effects = request.form["side_effects"]
            usage_method = request.form["usage_method"]

            new_medicine = Medicine(
                name=name,
                description=description,
                side_effects=side_effects,
                usage_method=usage_method,
            )

            db.session.add(new_medicine)
            db.session.commit()

            flash("Лекарство успешно добавлено", "success")
            return redirect(url_for("admin_add_medicine"))

        return render_template("admin/add_medicine.html")

    except Exception as e:
        db.session.rollback()
        print(f"Error in admin_add_medicine: {str(e)}")
        print(traceback.format_exc())
        flash(f"Ошибка при добавлении лекарства: {str(e)}", "error")
        return redirect(url_for("admin_add_medicine"))


# Doctor routes
@app.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        # Исправленный запрос с явным выбором полей
        visits = (
            db.session.query(
                Visit.id,
                Visit.date,
                Visit.location,
                Visit.diagnosis,
                Patient.first_name.label("patient_first_name"),
                Patient.last_name.label("patient_last_name"),
            )
            .join(Patient, Visit.patient_id == Patient.id)
            .filter(Visit.doctor_id == current_user.id)
            .order_by(Visit.date.desc())
            .all()
        )

        return render_template("doctor/dashboard.html", visits=visits)

    except Exception as e:
        flash(f"Ошибка: {str(e)}", "error")
        return render_template("doctor/dashboard.html", visits=[])


@app.route("/doctor/add-visit", methods=["GET", "POST"])
@login_required
def doctor_add_visit():
    if current_user.role != "doctor":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            patient_id = request.form["patient_id"]
            date = datetime.strptime(request.form["date"], "%Y-%m-%dT%H:%M")
            location = request.form["location"]
            symptoms = request.form["symptoms"]
            diagnosis = request.form["diagnosis"]
            prescriptions = request.form["prescriptions"]
            medicines = request.form.getlist("medicines[]")
            instructions = request.form.getlist("instructions[]")

            # Создаем визит
            new_visit = Visit(
                patient_id=patient_id,
                doctor_id=current_user.id,
                date=date,
                location=location,
                symptoms=symptoms,
                diagnosis=diagnosis,
                prescriptions=prescriptions,
            )

            db.session.add(new_visit)
            db.session.flush()  # Получаем ID нового визита

            # Добавляем лекарства
            for medicine_id, instruction in zip(medicines, instructions):
                if medicine_id:
                    visit_medicine = VisitMedicine(
                        visit_id=new_visit.id,
                        medicine_id=medicine_id,
                        doctor_instructions=instruction,
                    )
                    db.session.add(visit_medicine)

            db.session.commit()

            flash("Визит успешно добавлен", "success")
            return redirect(url_for("doctor_add_visit"))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка: {str(e)}", "error")

    # Получаем пациентов и лекарства для формы
    patients = Patient.query.order_by(Patient.last_name, Patient.first_name).all()
    medicines = Medicine.query.order_by(Medicine.name).all()

    return render_template(
        "doctor/add_visit.html", patients=patients, medicines=medicines
    )


# Doctor visit details
@app.route("/doctor/visits/<int:visit_id>")
@login_required
def doctor_visit_detail(visit_id):
    if current_user.role != "doctor":
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        visit_data = (
            db.session.query(Visit, Patient, Doctor)
            .join(Patient, Visit.patient_id == Patient.id)
            .join(Doctor, Visit.doctor_id == Doctor.id)
            .filter(Visit.id == visit_id, Visit.doctor_id == current_user.id)
            .first()
        )

        if not visit_data:
            return jsonify({"error": "Визит не найден"}), 404

        visit, patient, doctor = visit_data

        medicines = (
            db.session.query(VisitMedicine, Medicine)
            .join(Medicine, VisitMedicine.medicine_id == Medicine.id)
            .filter(VisitMedicine.visit_id == visit_id)
            .all()
        )

        result = {
            "id": visit.id,
            "date": visit.date.isoformat() if visit.date else None,
            "location": visit.location,
            "symptoms": visit.symptoms,
            "diagnosis": visit.diagnosis,
            "prescriptions": visit.prescriptions,
            "patient_first_name": patient.first_name,
            "patient_last_name": patient.last_name,
            "date_of_birth": (
                patient.date_of_birth.isoformat() if patient.date_of_birth else None
            ),
            "gender": patient.gender,
            "address": patient.address,
            "doctor_first_name": doctor.first_name,
            "doctor_last_name": doctor.last_name,
            "position": doctor.position,
            "medicines": [
                {
                    "name": medicine.name,
                    "description": medicine.description,
                    "side_effects": medicine.side_effects,
                    "usage_method": medicine.usage_method,
                    "doctor_instructions": visit_medicine.doctor_instructions,
                }
                for visit_medicine, medicine in medicines
            ],
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Patient visit details
@app.route("/patient/visits/<int:visit_id>")
@login_required
def patient_visit_detail(visit_id):
    if current_user.role != "patient":
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        visit_data = (
            db.session.query(Visit, Patient, Doctor)
            .join(Patient, Visit.patient_id == Patient.id)
            .join(Doctor, Visit.doctor_id == Doctor.id)
            .filter(Visit.id == visit_id, Visit.patient_id == current_user.id)
            .first()
        )

        if not visit_data:
            return jsonify({"error": "Визит не найден"}), 404

        visit, patient, doctor = visit_data

        medicines = (
            db.session.query(VisitMedicine, Medicine)
            .join(Medicine, VisitMedicine.medicine_id == Medicine.id)
            .filter(VisitMedicine.visit_id == visit_id)
            .all()
        )

        result = {
            "id": visit.id,
            "date": visit.date.isoformat() if visit.date else None,
            "location": visit.location,
            "symptoms": visit.symptoms,
            "diagnosis": visit.diagnosis,
            "prescriptions": visit.prescriptions,
            "patient_first_name": patient.first_name,
            "patient_last_name": patient.last_name,
            "doctor_first_name": doctor.first_name,
            "doctor_last_name": doctor.last_name,
            "position": doctor.position,
            "medicines": [
                {
                    "name": medicine.name,
                    "description": medicine.description,
                    "side_effects": medicine.side_effects,
                    "usage_method": medicine.usage_method,
                    "doctor_instructions": visit_medicine.doctor_instructions,
                }
                for visit_medicine, medicine in medicines
            ],
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Patient routes
@app.route("/patient/dashboard")
@login_required
def patient_dashboard():
    if current_user.role != "patient":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        # Исправленный запрос с явным выбором полей
        visits = (
            db.session.query(
                Visit.id,
                Visit.date,
                Visit.location,
                Visit.diagnosis,
                Doctor.first_name.label("doctor_first_name"),
                Doctor.last_name.label("doctor_last_name"),
                Doctor.position,
            )
            .join(Doctor, Visit.doctor_id == Doctor.id)
            .filter(Visit.patient_id == current_user.id)
            .order_by(Visit.date.desc())
            .all()
        )

        return render_template("patient/dashboard.html", visits=visits)

    except Exception as e:
        flash(f"Ошибка: {str(e)}", "error")
        return render_template("patient/dashboard.html", visits=[])


# Управление данными
@app.route("/admin/doctors")
@login_required
def admin_doctors_list():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    # Простой запрос без join
    doctors = Doctor.query.order_by(Doctor.last_name, Doctor.first_name).all()
    return render_template("admin/doctors_list.html", doctors=doctors)


@app.route("/admin/patients")
@login_required
def admin_patients_list():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    # Простой запрос без join
    patients = Patient.query.order_by(Patient.last_name, Patient.first_name).all()
    return render_template("admin/patients_list.html", patients=patients)


@app.route("/admin/medicines")
@login_required
def admin_medicines_list():
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    # Простой запрос без join
    medicines = Medicine.query.order_by(Medicine.name).all()
    return render_template("admin/medicines_list.html", medicines=medicines)


@app.route("/admin/delete-doctor/<int:doctor_id>", methods=["POST"])
@login_required
def admin_delete_doctor(doctor_id):
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            flash("Врач успешно удален", "success")
        else:
            flash("Врач не найден", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", "error")

    return redirect(url_for("admin_doctors_list"))


@app.route("/admin/delete-patient/<int:patient_id>", methods=["POST"])
@login_required
def admin_delete_patient(patient_id):
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        patient = Patient.query.get(patient_id)
        if patient:
            db.session.delete(patient)
            db.session.commit()
            flash("Пациент успешно удален", "success")
        else:
            flash("Пациент не найден", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", "error")

    return redirect(url_for("admin_patients_list"))


@app.route("/admin/delete-medicine/<int:medicine_id>", methods=["POST"])
@login_required
def admin_delete_medicine(medicine_id):
    if current_user.role != "admin":
        flash("Доступ запрещен", "error")
        return redirect(url_for("index"))

    try:
        medicine = Medicine.query.get(medicine_id)
        if medicine:
            db.session.delete(medicine)
            db.session.commit()
            flash("Лекарство успешно удалено", "success")
        else:
            flash("Лекарство не найден", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении: {str(e)}", "error")

    return redirect(url_for("admin_medicines_list"))


@app.errorhandler(Exception)
def handle_exception(e):
    # Логируем ошибку, но не показываем пользователю
    print(f"Global error handler: {str(e)}")
    print(traceback.format_exc())

    # Если это ошибка атрибута, связанная с SQLAlchemy
    if "has no attribute" in str(e) and "sqlalchemy" in str(e):
        # Просто логируем, не показываем пользователю
        return redirect(request.referrer or url_for("index"))

    # Для других ошибок показываем стандартное сообщение
    flash("Произошла внутренняя ошибка сервера", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    if wait_for_db():
        if initialize_database():
            app.run(host="0.0.0.0", port=5000, debug=False)
        else:
            print("❌ Failed to initialize database")
    else:
        print("❌ Failed to connect to database")
else:
    # Для запуска в gunicorn
    with app.app_context():
        if wait_for_db():
            initialize_database()
