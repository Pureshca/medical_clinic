import pytest
from app import create_app
from models import db, populate_db

@pytest.fixture()
def app():
    app = create_app(testing=True)

    with app.app_context():
        db.drop_all()
        db.create_all()
        populate_db()

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
