import sys
import os

# Абсолютный путь к корню проекта (на уровень выше tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models import User, Admin
import hashlib

def test_authenticate_success(app):
    u = User.authenticate("admin", "admin123")
    assert u is not None
    assert u.role == "admin"
    assert u.login == "admin"

def test_authenticate_wrong_password(app):
    assert User.authenticate("admin", "wrong") is None

def test_authenticate_unknown_user(app):
    assert User.authenticate("nosuchuser", "123") is None

def test_get_user_success(app):
    u = User.get("admin_1")
    assert u is not None
    assert u.role == "admin"

def test_get_user_wrong_format(app):
    assert User.get("badformat") is None
