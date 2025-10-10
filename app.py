from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Admin, Doctor, Patient, Medicine, Visit, VisitMedicine, User, populate_db
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key')

# Инициализация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:rootpassword@db/medical_clinic"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Создание таблиц при запуске
with app.app_context():
    db.create_all()
    populate_db()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        print(f"DEBUG: User {current_user.login} with role {current_user.role} authenticated")
        
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Неизвестная роль пользователя', 'error')
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        user = User.authenticate(login, password)
        if user:
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверные учетные данные', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        # Получаем все визиты с информацией о пациентах и врачах
        visits_data = db.session.query(
            Visit,
            Patient.first_name.label('patient_first_name'),
            Patient.last_name.label('patient_last_name'),
            Doctor.first_name.label('doctor_first_name'),
            Doctor.last_name.label('doctor_last_name')
        ).join(Patient, Visit.patient_id == Patient.id)\
         .join(Doctor, Visit.doctor_id == Doctor.id)\
         .order_by(Visit.date.desc()).all()

        # Преобразуем в удобный формат для шаблона
        visits = []
        for visit_data in visits_data:
            visit, patient_first_name, patient_last_name, doctor_first_name, doctor_last_name = visit_data
            visits.append({
                'id': visit.id,
                'patient_id': visit.patient_id,
                'doctor_id': visit.doctor_id,
                'date': visit.date,
                'location': visit.location,
                'symptoms': visit.symptoms,
                'diagnosis': visit.diagnosis,
                'prescriptions': visit.prescriptions,
                'patient_first_name': patient_first_name,
                'patient_last_name': patient_last_name,
                'doctor_first_name': doctor_first_name,
                'doctor_last_name': doctor_last_name
            })

        # Статистика
        total_visits = Visit.query.count()
        total_patients = Patient.query.count()
        total_doctors = Doctor.query.count()
        
        return render_template('admin/dashboard.html', 
                             visits=visits,
                             total_visits=total_visits,
                             total_patients=total_patients,
                             total_doctors=total_doctors)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('admin/dashboard.html', visits=[])

@app.route('/admin/visits/<int:visit_id>')
@login_required
def admin_visit_detail(visit_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    try:
        # Получаем детали визита
        visit_data = db.session.query(
            Visit,
            Patient.first_name.label('patient_first_name'),
            Patient.last_name.label('patient_last_name'),
            Patient.date_of_birth,
            Patient.gender,
            Patient.address,
            Doctor.first_name.label('doctor_first_name'),
            Doctor.last_name.label('doctor_last_name'),
            Doctor.position
        ).join(Patient, Visit.patient_id == Patient.id)\
         .join(Doctor, Visit.doctor_id == Doctor.id)\
         .filter(Visit.id == visit_id).first()
        
        if not visit_data:
            return jsonify({'error': 'Визит не найден'}), 404
        
        visit, patient_first_name, patient_last_name, date_of_birth, gender, address, doctor_first_name, doctor_last_name, position = visit_data
        
        # Получаем назначенные лекарства
        medicines_data = db.session.query(
            Medicine.name,
            Medicine.description,
            Medicine.side_effects,
            Medicine.usage_method,
            VisitMedicine.doctor_instructions
        ).join(VisitMedicine, Medicine.id == VisitMedicine.medicine_id)\
         .filter(VisitMedicine.visit_id == visit_id).all()
        
        medicines = [{
            'name': med.name,
            'description': med.description,
            'side_effects': med.side_effects,
            'usage_method': med.usage_method,
            'doctor_instructions': med.doctor_instructions
        } for med in medicines_data]
        
        result = {
            'id': visit.id,
            'patient_id': visit.patient_id,
            'doctor_id': visit.doctor_id,
            'date': visit.date.isoformat() if visit.date else None,
            'location': visit.location,
            'symptoms': visit.symptoms,
            'diagnosis': visit.diagnosis,
            'prescriptions': visit.prescriptions,
            'patient_first_name': patient_first_name,
            'patient_last_name': patient_last_name,
            'date_of_birth': date_of_birth.isoformat() if date_of_birth else None,
            'gender': gender,
            'address': address,
            'doctor_first_name': doctor_first_name,
            'doctor_last_name': doctor_last_name,
            'position': position,
            'medicines': medicines
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats/visits-by-date', methods=['POST'])
@login_required
def admin_stats_visits_by_date():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    date_str = request.json.get('date')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        visit_count = db.session.query(Visit).filter(
            db.func.date(Visit.date) == date_obj
        ).count()
        
        return jsonify({'date': date_str, 'visit_count': visit_count})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats/patients-by-diagnosis', methods=['POST'])
@login_required
def admin_stats_patients_by_diagnosis():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    diagnosis = request.json.get('diagnosis')
    try:
        patient_count = db.session.query(Visit.patient_id).filter(
            Visit.diagnosis.like(f'%{diagnosis}%')
        ).distinct().count()
        
        return jsonify({'diagnosis': diagnosis, 'patient_count': patient_count})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats/medicine-side-effects', methods=['POST'])
@login_required
def admin_stats_medicine_side_effects():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    medicine_name = request.json.get('medicine_name')
    try:
        medicine = Medicine.query.filter_by(name=medicine_name).first()
        
        if medicine:
            return jsonify({
                'medicine_name': medicine_name, 
                'side_effects': medicine.side_effects
            })
        else:
            return jsonify({'error': 'Лекарство не найдено'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/add-doctor', methods=['GET', 'POST'])
@login_required
def admin_add_doctor():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            position = request.form['position']
            login = request.form['login']
            password = request.form['password']
            
            # Проверяем, существует ли уже такой логин
            existing_doctor = Doctor.query.filter_by(login=login).first()
            if existing_doctor:
                flash('Логин уже существует', 'error')
                return redirect(url_for('admin_add_doctor'))
            
            # Добавляем врача
            new_doctor = Doctor(
                first_name=first_name,
                last_name=last_name,
                position=position,
                login=login,
                password_hash=hashlib.sha256(password.encode()).hexdigest()
            )
            
            db.session.add(new_doctor)
            db.session.commit()
            
            flash('Врач успешно добавлен', 'success')
            return redirect(url_for('admin_add_doctor'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('admin/add_doctor.html')

@app.route('/admin/add-patient', methods=['GET', 'POST'])
@login_required
def admin_add_patient():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            gender = request.form['gender']
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
            address = request.form['address']
            login = request.form['login']
            password = request.form['password']
            
            # Проверяем, существует ли уже такой логин
            existing_patient = Patient.query.filter_by(login=login).first()
            if existing_patient:
                flash('Логин уже существует', 'error')
                return redirect(url_for('admin_add_patient'))
            
            # Добавляем пациента
            new_patient = Patient(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                login=login,
                password_hash=hashlib.sha256(password.encode()).hexdigest()
            )
            
            db.session.add(new_patient)
            db.session.commit()
            
            flash('Пациент успешно добавлен', 'success')
            return redirect(url_for('admin_add_patient'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('admin/add_patient.html')

@app.route('/admin/add-medicine', methods=['GET', 'POST'])
@login_required
def admin_add_medicine():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            side_effects = request.form['side_effects']
            usage_method = request.form['usage_method']
            
            new_medicine = Medicine(
                name=name,
                description=description,
                side_effects=side_effects,
                usage_method=usage_method
            )
            
            db.session.add(new_medicine)
            db.session.commit()
            
            flash('Лекарство успешно добавлено', 'success')
            return redirect(url_for('admin_add_medicine'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('admin/add_medicine.html')

# Doctor routes
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        visits_data = db.session.query(
            Visit,
            Patient.first_name.label('patient_first_name'),
            Patient.last_name.label('patient_last_name')
        ).join(Patient, Visit.patient_id == Patient.id)\
         .filter(Visit.doctor_id == current_user.id)\
         .order_by(Visit.date.desc()).all()

        visits = []
        for visit_data in visits_data:
            visit, patient_first_name, patient_last_name = visit_data
            visits.append({
                'id': visit.id,
                'patient_id': visit.patient_id,
                'date': visit.date,
                'location': visit.location,
                'symptoms': visit.symptoms,
                'diagnosis': visit.diagnosis,
                'prescriptions': visit.prescriptions,
                'patient_first_name': patient_first_name,
                'patient_last_name': patient_last_name
            })
        
        return render_template('doctor/dashboard.html', visits=visits)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('doctor/dashboard.html', visits=[])

@app.route('/doctor/visits/<int:visit_id>')
@login_required
def doctor_visit_detail(visit_id):
    if current_user.role != 'doctor':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    try:
        # Получаем детали визита
        visit_data = db.session.query(
            Visit,
            Patient.first_name.label('patient_first_name'),
            Patient.last_name.label('patient_last_name'),
            Patient.date_of_birth,
            Patient.gender,
            Patient.address
        ).join(Patient, Visit.patient_id == Patient.id)\
         .filter(Visit.id == visit_id, Visit.doctor_id == current_user.id).first()
        
        if not visit_data:
            return jsonify({'error': 'Визит не найден'}), 404
        
        visit, patient_first_name, patient_last_name, date_of_birth, gender, address = visit_data
        
        # Получаем назначенные лекарства
        medicines_data = db.session.query(
            Medicine.name,
            Medicine.description,
            Medicine.side_effects,
            Medicine.usage_method,
            VisitMedicine.doctor_instructions
        ).join(VisitMedicine, Medicine.id == VisitMedicine.medicine_id)\
         .filter(VisitMedicine.visit_id == visit_id).all()
        
        medicines = [{
            'name': med.name,
            'description': med.description,
            'side_effects': med.side_effects,
            'usage_method': med.usage_method,
            'doctor_instructions': med.doctor_instructions
        } for med in medicines_data]
        
        result = {
            'id': visit.id,
            'patient_id': visit.patient_id,
            'doctor_id': visit.doctor_id,
            'date': visit.date.isoformat() if visit.date else None,
            'location': visit.location,
            'symptoms': visit.symptoms,
            'diagnosis': visit.diagnosis,
            'prescriptions': visit.prescriptions,
            'patient_first_name': patient_first_name,
            'patient_last_name': patient_last_name,
            'date_of_birth': date_of_birth.isoformat() if date_of_birth else None,
            'gender': gender,
            'address': address,
            'medicines': medicines
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/doctor/add-visit', methods=['GET', 'POST'])
@login_required
def doctor_add_visit():
    if current_user.role != 'doctor':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            patient_id = request.form['patient_id']
            date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
            location = request.form['location']
            symptoms = request.form['symptoms']
            diagnosis = request.form['diagnosis']
            prescriptions = request.form['prescriptions']
            medicines = request.form.getlist('medicines[]')
            instructions = request.form.getlist('instructions[]')
            
            # Создаем визит
            new_visit = Visit(
                patient_id=patient_id,
                doctor_id=current_user.id,
                date=date,
                location=location,
                symptoms=symptoms,
                diagnosis=diagnosis,
                prescriptions=prescriptions
            )
            
            db.session.add(new_visit)
            db.session.flush()  # Получаем ID нового визита
            
            # Добавляем лекарства
            for medicine_id, instruction in zip(medicines, instructions):
                if medicine_id:
                    visit_medicine = VisitMedicine(
                        visit_id=new_visit.id,
                        medicine_id=medicine_id,
                        doctor_instructions=instruction
                    )
                    db.session.add(visit_medicine)
            
            db.session.commit()
            
            flash('Визит успешно добавлен', 'success')
            return redirect(url_for('doctor_add_visit'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
    
    # Получаем пациентов и лекарства для формы
    patients = Patient.query.order_by(Patient.last_name, Patient.first_name).all()
    medicines = Medicine.query.order_by(Medicine.name).all()
    
    return render_template('doctor/add_visit.html', patients=patients, medicines=medicines)

@app.route('/admin/delete-visit/<int:visit_id>', methods=['POST'])
@login_required
def admin_delete_visit(visit_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        # Находим визит
        visit = Visit.query.get(visit_id)
        if not visit:
            flash('Визит не найден', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Удаляем связанные лекарства
        VisitMedicine.query.filter_by(visit_id=visit_id).delete()
        
        # Удаляем визит
        db.session.delete(visit)
        db.session.commit()
        
        flash('Визит успешно удален', 'success')
        return redirect(url_for('admin_dashboard'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении визита: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

# Patient routes
@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        visits_data = db.session.query(
            Visit,
            Doctor.first_name.label('doctor_first_name'),
            Doctor.last_name.label('doctor_last_name'),
            Doctor.position
        ).join(Doctor, Visit.doctor_id == Doctor.id)\
         .filter(Visit.patient_id == current_user.id)\
         .order_by(Visit.date.desc()).all()

        visits = []
        for visit_data in visits_data:
            visit, doctor_first_name, doctor_last_name, position = visit_data
            visits.append({
                'id': visit.id,
                'doctor_id': visit.doctor_id,
                'date': visit.date,
                'location': visit.location,
                'symptoms': visit.symptoms,
                'diagnosis': visit.diagnosis,
                'prescriptions': visit.prescriptions,
                'doctor_first_name': doctor_first_name,
                'doctor_last_name': doctor_last_name,
                'position': position
            })
        
        return render_template('patient/dashboard.html', visits=visits)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('patient/dashboard.html', visits=[])

@app.route('/patient/visits/<int:visit_id>')
@login_required
def patient_visit_detail(visit_id):
    if current_user.role != 'patient':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    try:
        # Получаем детали визита
        visit_data = db.session.query(
            Visit,
            Doctor.first_name.label('doctor_first_name'),
            Doctor.last_name.label('doctor_last_name'),
            Doctor.position
        ).join(Doctor, Visit.doctor_id == Doctor.id)\
         .filter(Visit.id == visit_id, Visit.patient_id == current_user.id).first()
        
        if not visit_data:
            return jsonify({'error': 'Визит не найден'}), 404
        
        visit, doctor_first_name, doctor_last_name, position = visit_data
        
        # Получаем назначенные лекарства
        medicines_data = db.session.query(
            Medicine.name,
            Medicine.description,
            Medicine.usage_method,
            VisitMedicine.doctor_instructions
        ).join(VisitMedicine, Medicine.id == VisitMedicine.medicine_id)\
         .filter(VisitMedicine.visit_id == visit_id).all()
        
        medicines = [{
            'name': med.name,
            'description': med.description,
            'usage_method': med.usage_method,
            'doctor_instructions': med.doctor_instructions
        } for med in medicines_data]
        
        result = {
            'id': visit.id,
            'patient_id': visit.patient_id,
            'doctor_id': visit.doctor_id,
            'date': visit.date.isoformat() if visit.date else None,
            'location': visit.location,
            'symptoms': visit.symptoms,
            'diagnosis': visit.diagnosis,
            'prescriptions': visit.prescriptions,
            'doctor_first_name': doctor_first_name,
            'doctor_last_name': doctor_last_name,
            'position': position,
            'medicines': medicines
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/search-patients', methods=['POST'])
@login_required
def admin_search_patients():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    search_type = request.json.get('search_type')
    search_query = request.json.get('search_query')
    
    try:
        if search_type == 'visit_date':
            # Поиск по дате визита
            date_obj = datetime.strptime(search_query, '%Y-%m-%d').date()
            patients = Patient.query.join(Visit).filter(
                db.func.date(Visit.date) == date_obj
            ).distinct().all()
        
        elif search_type == 'diagnosis':
            # Поиск по диагнозу
            patients = Patient.query.join(Visit).filter(
                Visit.diagnosis.like(f'%{search_query}%')
            ).distinct().all()
        
        elif search_type == 'side_effects':
            # Поиск по побочным эффектам лекарств
            patients = Patient.query.join(Visit).join(VisitMedicine).join(Medicine).filter(
                Medicine.side_effects.like(f'%{search_query}%')
            ).distinct().all()
        
        # Преобразуем в JSON-совместимый формат
        patients_data = []
        for patient in patients:
            patients_data.append({
                'id': patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'gender': patient.gender,
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                'address': patient.address,
                'login': patient.login
            })
        
        return jsonify(patients_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/search-suggestions', methods=['POST'])
@login_required
def admin_search_suggestions():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    search_type = request.json.get('search_type')
    search_query = request.json.get('search_query')
    
    try:
        if search_type == 'diagnosis':
            suggestions = db.session.query(Visit.diagnosis).filter(
                Visit.diagnosis.like(f'%{search_query}%')
            ).distinct().limit(10).all()
        
        elif search_type == 'side_effects':
            suggestions = db.session.query(Medicine.side_effects).filter(
                Medicine.side_effects.like(f'%{search_query}%')
            ).distinct().limit(10).all()
        
        suggestions_data = [{'suggestion': s[0]} for s in suggestions]
        return jsonify(suggestions_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete-doctor/<int:doctor_id>', methods=['POST'])
@login_required
def admin_delete_doctor(doctor_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            flash('Врач не найден', 'error')
            return redirect(url_for('admin_doctors_list'))
        
        # Проверяем, есть ли у врача визиты
        visit_count = Visit.query.filter_by(doctor_id=doctor_id).count()
        if visit_count > 0:
            flash('Нельзя удалить врача, у которого есть записи о визитах', 'error')
            return redirect(url_for('admin_doctors_list'))
        
        db.session.delete(doctor)
        db.session.commit()
        
        flash('Врач успешно удален', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении врача: {str(e)}', 'error')
    
    return redirect(url_for('admin_doctors_list'))

@app.route('/admin/delete-patient/<int:patient_id>', methods=['POST'])
@login_required
def admin_delete_patient(patient_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            flash('Пациент не найден', 'error')
            return redirect(url_for('admin_patients_list'))
        
        # Проверяем, есть ли у пациента визиты
        visit_count = Visit.query.filter_by(patient_id=patient_id).count()
        if visit_count > 0:
            flash('Нельзя удалить пациента, у которого есть записи о визитах', 'error')
            return redirect(url_for('admin_patients_list'))
        
        db.session.delete(patient)
        db.session.commit()
        
        flash('Пациент успешно удален', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пациента: {str(e)}', 'error')
    
    return redirect(url_for('admin_patients_list'))

@app.route('/admin/doctors')
@login_required
def admin_doctors_list():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        doctors = Doctor.query.order_by(Doctor.last_name, Doctor.first_name).all()
        return render_template('admin/doctors_list.html', doctors=doctors)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('admin/doctors_list.html', doctors=[])

@app.route('/admin/patients')
@login_required
def admin_patients_list():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        patients = Patient.query.order_by(Patient.last_name, Patient.first_name).all()
        return render_template('admin/patients_list.html', patients=patients)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('admin/patients_list.html', patients=[])

@app.route('/admin/delete-medicine/<int:medicine_id>', methods=['POST'])
@login_required
def admin_delete_medicine(medicine_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            flash('Лекарство не найдено', 'error')
            return redirect(url_for('admin_medicines_list'))
        
        # Проверяем, используется ли лекарство в визитах
        usage_count = VisitMedicine.query.filter_by(medicine_id=medicine_id).count()
        if usage_count > 0:
            flash('Нельзя удалить лекарство, которое используется в записях о визитах', 'error')
            return redirect(url_for('admin_medicines_list'))
        
        db.session.delete(medicine)
        db.session.commit()
        
        flash('Лекарство успешно удалено', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении лекарства: {str(e)}', 'error')
    
    return redirect(url_for('admin_medicines_list'))

@app.route('/admin/medicines')
@login_required
def admin_medicines_list():
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        medicines = Medicine.query.order_by(Medicine.name).all()
        return render_template('admin/medicines_list.html', medicines=medicines)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('admin/medicines_list.html', medicines=[])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')