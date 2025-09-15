from flask_login import UserMixin
from flask import current_app, session
import mysql.connector
from datetime import datetime
import os
import hashlib

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
        # Сохраняем составной идентификатор: role_id
        self._id = f"{role}_{id}"

    def get_id(self):
        # Возвращаем составной идентификатор вместо простого id
        return self._id

    @staticmethod
    def get(user_id):
        try:
            print(f"Loading user with composite ID: {user_id}")
            
            # Разбираем составной идентификатор
            if '_' in user_id:
                role, id_str = user_id.split('_', 1)
                user_id_int = int(id_str)
            else:
                # Для обратной совместимости
                return None
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Загружаем пользователя в зависимости от роли
            if role == 'admin':
                cursor.execute("SELECT id, login, 'admin' as role FROM admins WHERE id = %s", (user_id_int,))
            elif role == 'doctor':
                cursor.execute("SELECT id, login, 'doctor' as role FROM doctors WHERE id = %s", (user_id_int,))
            elif role == 'patient':
                cursor.execute("SELECT id, login, 'patient' as role FROM patients WHERE id = %s", (user_id_int,))
            else:
                return None
            
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                print(f"User loaded: {user}")
                return User(user['id'], user['login'], user['role'])
            
            print("User not found")
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
            
            cursor.close()
            conn.close()
            
            # ПРАВИЛЬНАЯ проверка пароля
            if user:
                print(f"User found: {user}")
                entered_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                print(f"Input password hash: {entered_hash}")
                print(f"Stored password hash: {user['password_hash']}")
                
                if entered_hash == user['password_hash']:
                    print("Authentication SUCCESSFUL")
                    # Возвращаем пользователя с составным идентификатором
                    return User(user['id'], user['login'], user['role'])
                else:
                    print("Authentication FAILED - password mismatch")
            else:
                print("User not found in any table")
            
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None