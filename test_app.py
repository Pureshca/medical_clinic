import os
import pytest

# Перед импортом приложения подменяем БД
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app  # noqa


@pytest.fixture
def client():
    """
    Создаём тестовый клиент Flask.
    Не выполняет wait_for_db(), initialize_database(),
    так как это запускается только при __main__.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Проверяем, что endpoint /health работает без БД."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok"}
