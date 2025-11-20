# test_app.py
import pytest
from app import app, db  # предполагается, что у тебя есть app.py с Flask app и db = SQLAlchemy(app)

@pytest.fixture
def client():
    # Используем in-memory SQLite
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # создаём таблицы только в памяти
        yield client
        with app.app_context():
            db.drop_all()  # очищаем после теста

def test_health_route(client):
    """Простейший тест, проверяющий доступность корневого маршрута"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello' in response.data  # подставь текст, который реально возвращает твой '/' маршрут
