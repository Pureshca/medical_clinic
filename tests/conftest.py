import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from models import db, populate_db

@pytest.fixture()
def app():

    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_db()

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
