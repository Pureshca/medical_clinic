from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, get_db_connection
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv
import os
import hashlib
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient_dashboard'))
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all visits with patient and doctor info
        cursor.execute('''
            SELECT v.*, p.first_name as patient_first_name, p.last_name as patient_last_name,
                   d.first_name as doctor_first_name, d.last_name as doctor_last_name
            FROM visits v
            JOIN patients p ON v.patient_id = p.id
            JOIN doctors d ON v.doctor_id = d.id
            ORDER BY v.date DESC
        ''')
        visits = cursor.fetchall()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) as total_visits FROM visits")
        total_visits = cursor.fetchone()['total_visits']
        
        cursor.execute("SELECT COUNT(*) as total_patients FROM patients")
        total_patients = cursor.fetchone()['total_patients']
        
        cursor.execute("SELECT COUNT(*) as total_doctors FROM doctors")
        total_doctors = cursor.fetchone()['total_doctors']
        
        cursor.close()
        conn.close()
        
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get visit details
        cursor.execute('''
            SELECT v.*, p.first_name as patient_first_name, p.last_name as patient_last_name,
                   p.date_of_birth, p.gender, p.address,
                   d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.position
            FROM visits v
            JOIN patients p ON v.patient_id = p.id
            JOIN doctors d ON v.doctor_id = d.id
            WHERE v.id = %s
        ''', (visit_id,))
        visit = cursor.fetchone()
        
        # Get prescribed medicines
        cursor.execute('''
            SELECT m.name, m.description, m.side_effects, m.usage_method, vm.doctor_instructions
            FROM visit_medicines vm
            JOIN medicines m ON vm.medicine_id = m.id
            WHERE vm.visit_id = %s
        ''', (visit_id,))
        medicines = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        visit['medicines'] = medicines
        return jsonify(visit)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats/visits-by-date', methods=['POST'])
@login_required
def admin_stats_visits_by_date():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    date = request.json.get('date')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT COUNT(*) as visit_count
            FROM visits
            WHERE DATE(date) = %s
        ''', (date,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'date': date, 'visit_count': result['visit_count']})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats/patients-by-diagnosis', methods=['POST'])
@login_required
def admin_stats_patients_by_diagnosis():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    diagnosis = request.json.get('diagnosis')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT COUNT(DISTINCT patient_id) as patient_count
            FROM visits
            WHERE diagnosis LIKE %s
        ''', (f'%{diagnosis}%',))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'diagnosis': diagnosis, 'patient_count': result['patient_count']})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats/medicine-side-effects', methods=['POST'])
@login_required
def admin_stats_medicine_side_effects():
    if current_user.role != 'admin':
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    medicine_name = request.json.get('medicine_name')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT side_effects
            FROM medicines
            WHERE name = %s
        ''', (medicine_name,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return jsonify({'medicine_name': medicine_name, 'side_effects': result['side_effects']})
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
            
            # Хешируем пароль
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Проверяем, существует ли уже такой логин
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM doctors WHERE login = %s", (login,))
            existing_doctor = cursor.fetchone()
            
            if existing_doctor:
                flash('Логин уже существует', 'error')
                return redirect(url_for('admin_add_doctor'))
            
            # Добавляем врача
            cursor.execute('''
                INSERT INTO doctors (first_name, last_name, position, login, password_hash)
                VALUES (%s, %s, %s, %s, %s)
            ''', (first_name, last_name, position, login, password_hash))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Врач успешно добавлен', 'success')
            return redirect(url_for('admin_add_doctor'))
        
        except Exception as e:
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
            date_of_birth = request.form['date_of_birth']
            address = request.form['address']
            login = request.form['login']
            password = request.form['password']
            
            # Хешируем пароль
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Проверяем, существует ли уже такой логин
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM patients WHERE login = %s", (login,))
            existing_patient = cursor.fetchone()
            
            if existing_patient:
                flash('Логин уже существует', 'error')
                return redirect(url_for('admin_add_patient'))
            
            # Добавляем пациента
            cursor.execute('''
                INSERT INTO patients (first_name, last_name, gender, date_of_birth, address, login, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (first_name, last_name, gender, date_of_birth, address, login, password_hash))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Пациент успешно добавлен', 'success')
            return redirect(url_for('admin_add_patient'))
        
        except Exception as e:
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
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO medicines (name, description, side_effects, usage_method)
                VALUES (%s, %s, %s, %s)
            ''', (name, description, side_effects, usage_method))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Лекарство успешно добавлено', 'success')
            return redirect(url_for('admin_add_medicine'))
        
        except Exception as e:
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT v.*, p.first_name as patient_first_name, p.last_name as patient_last_name
            FROM visits v
            JOIN patients p ON v.patient_id = p.id
            WHERE v.doctor_id = %s
            ORDER BY v.date DESC
        ''', (current_user.id,))
        visits = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT v.*, p.first_name as patient_first_name, p.last_name as patient_last_name,
                   p.date_of_birth, p.gender, p.address
            FROM visits v
            JOIN patients p ON v.patient_id = p.id
            WHERE v.id = %s AND v.doctor_id = %s
        ''', (visit_id, current_user.id))
        visit = cursor.fetchone()
        
        if not visit:
            return jsonify({'error': 'Визит не найден'}), 404
        
        cursor.execute('''
            SELECT m.name, m.description, m.side_effects, m.usage_method, vm.doctor_instructions
            FROM visit_medicines vm
            JOIN medicines m ON vm.medicine_id = m.id
            WHERE vm.visit_id = %s
        ''', (visit_id,))
        medicines = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        visit['medicines'] = medicines
        return jsonify(visit)
    
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
            date = request.form['date']
            location = request.form['location']
            symptoms = request.form['symptoms']
            diagnosis = request.form['diagnosis']
            prescriptions = request.form['prescriptions']
            medicines = request.form.getlist('medicines[]')
            instructions = request.form.getlist('instructions[]')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert visit
            cursor.execute('''
                INSERT INTO visits (patient_id, doctor_id, date, location, symptoms, diagnosis, prescriptions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (patient_id, current_user.id, date, location, symptoms, diagnosis, prescriptions))
            
            visit_id = cursor.lastrowid
            
            # Insert prescribed medicines
            for medicine_id, instruction in zip(medicines, instructions):
                if medicine_id:
                    cursor.execute('''
                        INSERT INTO visit_medicines (visit_id, medicine_id, doctor_instructions)
                        VALUES (%s, %s, %s)
                    ''', (visit_id, medicine_id, instruction))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Визит успешно добавлен', 'success')
            return redirect(url_for('doctor_add_visit'))
        
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'error')
    
    # Get patients and medicines for the form
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT id, first_name, last_name FROM patients ORDER BY last_name, first_name')
        patients = cursor.fetchall()
        
        cursor.execute('SELECT id, name FROM medicines ORDER BY name')
        medicines = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('doctor/add_visit.html', patients=patients, medicines=medicines)
    
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
        return render_template('doctor/add_visit.html', patients=[], medicines=[])
    
@app.route('/admin/delete-visit/<int:visit_id>', methods=['POST'])
@login_required
def admin_delete_visit(visit_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Сначала удаляем связанные записи о лекарствах
        cursor.execute('DELETE FROM visit_medicines WHERE visit_id = %s', (visit_id,))
        
        # Затем удаляем сам визит
        cursor.execute('DELETE FROM visits WHERE id = %s', (visit_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Визит успешно удален', 'success')
        return redirect(url_for('admin_dashboard'))
    
    except Exception as e:
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT v.*, d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.position
            FROM visits v
            JOIN doctors d ON v.doctor_id = d.id
            WHERE v.patient_id = %s
            ORDER BY v.date DESC
        ''', (current_user.id,))
        visits = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT v.*, d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.position
            FROM visits v
            JOIN doctors d ON v.doctor_id = d.id
            WHERE v.id = %s AND v.patient_id = %s
        ''', (visit_id, current_user.id))
        visit = cursor.fetchone()
        
        if not visit:
            return jsonify({'error': 'Визит не найден'}), 404
        
        cursor.execute('''
            SELECT m.name, m.description, m.usage_method, vm.doctor_instructions
            FROM visit_medicines vm
            JOIN medicines m ON vm.medicine_id = m.id
            WHERE vm.visit_id = %s
        ''', (visit_id,))
        medicines = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        visit['medicines'] = medicines
        return jsonify(visit)
    
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if search_type == 'visit_date':
            # Поиск по дате визита
            cursor.execute('''
                SELECT DISTINCT p.* 
                FROM patients p
                JOIN visits v ON p.id = v.patient_id
                WHERE DATE(v.date) = %s
            ''', (search_query,))
        
        elif search_type == 'diagnosis':
            # Поиск по диагнозу
            cursor.execute('''
                SELECT DISTINCT p.* 
                FROM patients p
                JOIN visits v ON p.id = v.patient_id
                WHERE v.diagnosis LIKE %s
            ''', (f'%{search_query}%',))
        
        elif search_type == 'side_effects':
            # Поиск по побочным эффектам лекарств
            cursor.execute('''
                SELECT DISTINCT p.* 
                FROM patients p
                JOIN visits v ON p.id = v.patient_id
                JOIN visit_medicines vm ON v.id = vm.visit_id
                JOIN medicines m ON vm.medicine_id = m.id
                WHERE m.side_effects LIKE %s
            ''', (f'%{search_query}%',))
        
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(patients)
    
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if search_type == 'diagnosis':
            cursor.execute('''
                SELECT DISTINCT diagnosis as suggestion 
                FROM visits 
                WHERE diagnosis LIKE %s 
                LIMIT 10
            ''', (f'%{search_query}%',))
        
        elif search_type == 'side_effects':
            cursor.execute('''
                SELECT DISTINCT side_effects as suggestion 
                FROM medicines 
                WHERE side_effects LIKE %s 
                LIMIT 10
            ''', (f'%{search_query}%',))
        
        suggestions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(suggestions)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)