#необходимо выполнить файл, чтобы обновить хэш в бд
import mysql.connector
from werkzeug.security import generate_password_hash
import os

# подключение к базе (используются те же переменные окружения, что и в app.py/models.py)
conn = mysql.connector.connect(
    host=os.getenv("DATABASE_HOST", "localhost"),
    user=os.getenv("DATABASE_USER", "root"),
    password=os.getenv("DATABASE_PASSWORD", ""),
    database=os.getenv("DATABASE_NAME", "medical_clinic"),
)
cursor = conn.cursor()

# генерируем хеши
admin_hash = generate_password_hash("admin123")
doctor_hash = generate_password_hash("doctor123")
patient_hash = generate_password_hash("password123")

# обновляем пароли
cursor.execute("UPDATE admins SET password_hash = %s", (admin_hash,))
cursor.execute("UPDATE doctors SET password_hash = %s", (doctor_hash,))
cursor.execute("UPDATE patients SET password_hash = %s", (patient_hash,))

conn.commit()
cursor.close()
conn.close()

print("✅ Пароли успешно сброшены:")
print("Администраторы → admin123")
print("Доктора       → doctor123")
print("Пациенты      → password123")
