from flask_login import UserMixin
from flask import current_app
import mysql.connector
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DATABASE_HOST', 'localhost'),
        user=os.getenv('DATABASE_USER', 'root'),
        password=os.getenv('DATABASE_PASSWORD', ''),
        database=os.getenv('DATABASE_NAME', 'medical_clinic'),
        autocommit=True
    )

class User(UserMixin):
    def __init__(self, id, login, role):
        self.id = id
        self.login = login
        self.role = role

    @staticmethod
    def get(user_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Проверяем во всех таблицах
            cursor.execute("SELECT id, login, 'admin' as role FROM admins WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute("SELECT id, login, 'doctor' as role FROM doctors WHERE id = %s", (user_id,))
                user = cursor.fetchone()
            
            if not user:
                cursor.execute("SELECT id, login, 'patient' as role FROM patients WHERE id = %s", (user_id,))
                user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if user:
                return User(user['id'], user['login'], user['role'])
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    @staticmethod
    def authenticate(login, password):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Проверяем во всех таблицах с проверкой пароля
            cursor.execute("SELECT id, login, password_hash, 'admin' as role FROM admins WHERE login = %s", (login,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute("SELECT id, login, password_hash, 'doctor' as role FROM doctors WHERE login = %s", (login,))
                user = cursor.fetchone()
            
            if not user:
                cursor.execute("SELECT id, login, password_hash, 'patient' as role FROM patients WHERE login = %s", (login,))
                user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
<<<<<<< HEAD
            # Проверяем пароль с помощью werkzeug.security
=======
            # ✅ теперь используем хеш-проверку
>>>>>>> a46b4113fc683a3b6b3a4ad2fa756cc3d2ec8262
            if user and check_password_hash(user['password_hash'], password):
                return User(user['id'], user['login'], user['role'])
            
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
<<<<<<< HEAD

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)
