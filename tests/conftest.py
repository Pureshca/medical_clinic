import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import app as flask_app  # используем существующий объект app
from models import db, populate_db

@pytest.fixture(scope="session")
def app():
    # Используем существующее приложение
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # in-memory база для тестов
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        populate_db()

    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()
