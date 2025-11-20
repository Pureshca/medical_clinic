import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import app as flask_app, db as _db

@pytest.fixture(scope="session")
def test_app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # <-- in-memory
    flask_app.config["WTF_CSRF_ENABLED"] = False

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def db_session(test_app):
    yield _db.session
    _db.session.rollback()

@pytest.fixture
def client(test_app):
    return test_app.test_client()
