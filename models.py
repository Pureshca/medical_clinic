from flask_login import UserMixin
from flask import current_app
import mysql.connector
from datetime import datetime
import os


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
            print(f"Attempting authentication for login: {login}")
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Проверяем во всех таблицах
            cursor.execute("SELECT id, login, password_hash, 'admin' as role FROM admins WHERE login = %s", (login,))
            user = cursor.fetchone()
            
            if not user:
                print("User not found in admins table")
                cursor.execute("SELECT id, login, password_hash, 'doctor' as role FROM doctors WHERE login = %s", (login,))
                user = cursor.fetchone()
            
            if not user:
                print("User not found in doctors table")
                cursor.execute("SELECT id, login, password_hash, 'patient' as role FROM patients WHERE login = %s", (login,))
                user = cursor.fetchone()
            
            if not user:
                print("User not found in patients table")
            
            cursor.close()
            conn.close()
            
            if user:
                print(f"User found: {user}")
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                print(f"Input password hash: {password_hash}")
                print(f"Stored password hash: {user['password_hash']}")
                
                if user['password_hash'] == password_hash:
                    print("Password matches!")
                    return User(user['id'], user['login'], user['role'])
                else:
                    print("Password does not match!")
            
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None