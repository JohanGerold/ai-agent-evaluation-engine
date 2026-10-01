import os
import subprocess
import sys

import pytest
from django.conf import settings

from app.foundation.safety import UnsafeFoundation, validate_configuration


def test_safe_offline_configuration():
    validate_configuration()
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert "django.contrib.admin" not in settings.INSTALLED_APPS


@pytest.mark.parametrize(
    "change",
    [
        {"DEBUG": True},
        {"AAP_ENVIRONMENT": "production"},
        {"AAP_ENVIRONMENT": "staging"},
        {"AAP_PROVIDER_MODE": "live"},
        {"AAP_SYNTHETIC_ONLY": False},
        {"AAP_POLICY_VERSION": ""},
        {"AAP_SCHEMA_VERSION": "unknown"},
        {"AAP_ENTRYPOINT": "unknown"},
        {"ALLOWED_HOSTS": []},
        {"ALLOWED_HOSTS": ["*"]},
        {"ALLOWED_HOSTS": ["example.com"]},
        {"SESSION_COOKIE_SECURE": False},
        {"SESSION_COOKIE_HTTPONLY": False},
        {"SESSION_COOKIE_SAMESITE": "None"},
        {"CSRF_COOKIE_SECURE": False},
        {"CSRF_COOKIE_HTTPONLY": False},
        {"CSRF_TRUSTED_ORIGINS": ["https://example.com"]},
        {"INSTALLED_APPS": ["django.contrib.admin"]},
        {"MIDDLEWARE": ["debug_toolbar.middleware.DebugToolbarMiddleware"]},
        {
            "TEMPLATES": [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "OPTIONS": {"debug": True},
                }
            ]
        },
    ],
)
def test_unsafe_configuration_refused(change, monkeypatch):
    for key, value in change.items():
        monkeypatch.setattr(settings, key, value)
    with pytest.raises(UnsafeFoundation):
        validate_configuration()


@pytest.mark.parametrize("name", ["OPENAI_API_KEY", "AAP_PROVIDER_KEY_FILE", "DATABASE_URL"])
def test_external_credentials_refused_without_disclosure(monkeypatch, name):
    canary = "SYNTHETIC_CANARY_PLATFORM_KEY"
    monkeypatch.setenv(name, canary)
    with pytest.raises(UnsafeFoundation) as caught:
        validate_configuration()
    assert canary not in str(caught.value)


@pytest.mark.parametrize(
    "change",
    [
        {"ENGINE": "django.db.backends.sqlite3"},
        {"ATOMIC_REQUESTS": True},
        {"AUTOCOMMIT": False},
        {"CONN_MAX_AGE": 60},
        {"USER": "postgres"},
        {"PASSWORD": "SYNTHETIC_CANARY"},
        {"HOST": "example.com"},
    ],
)
def test_unsafe_db_configuration_refused(change, monkeypatch):
    database = {**settings.DATABASES["default"], **change}
    monkeypatch.setattr(settings, "DATABASES", {"default": database})
    with pytest.raises(UnsafeFoundation):
        validate_configuration()


@pytest.mark.parametrize(
    "name,value",
    [
        ("AAP_DEBUG", "true"),
        ("OPENAI_API_KEY", "SYNTHETIC_CANARY_PLATFORM_KEY"),
        ("AAP_ENVIRONMENT", "production"),
        ("AAP_PROVIDER_MODE", "live"),
    ],
)
def test_process_startup_rejects_before_any_network(name, value):
    env = {**os.environ, name: value}
    result = subprocess.run(
        [sys.executable, "manage.py", "check"], env=env, capture_output=True, text=True, timeout=10
    )
    assert result.returncode != 0
    assert "SYNTHETIC_CANARY_PLATFORM_KEY" not in result.stdout + result.stderr
    assert "UnsafeFoundation" in result.stderr
