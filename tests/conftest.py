import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import app, db

@pytest.fixture(scope="session")
def test_app():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def db_session(test_app):
    from app import db
    yield db.session
    db.session.rollback()

# <-- добавляем эту фикстуру
@pytest.fixture
def client(test_app):
    return test_app.test_client()

