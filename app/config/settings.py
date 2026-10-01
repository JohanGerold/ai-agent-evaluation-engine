"""Synthetic local settings only. Deployed startup is deliberately refused."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
AAP_ENVIRONMENT = os.environ.get("AAP_ENVIRONMENT", "local")
AAP_ENTRYPOINT = os.environ.get("AAP_ENTRYPOINT", "web")
AAP_SYNTHETIC_ONLY = os.environ.get("AAP_SYNTHETIC_ONLY", "true") == "true"
AAP_PROVIDER_MODE = os.environ.get("AAP_PROVIDER_MODE", "offline")
AAP_POLICY_VERSION = os.environ.get("AAP_POLICY_VERSION", "foundation-offline-1")
AAP_SCHEMA_VERSION = "foundation-1"
AAP_ENGINE_VERSION = "0.0.1-t002"
# Public synthetic values, never credentials for a deployed environment.
SECRET_KEY = "synthetic-local-only-not-a-deployed-secret-" + "x" * 32
DEBUG = os.environ.get("AAP_DEBUG", "false") == "true"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]
INSTALLED_APPS = ["app.foundation.apps.FoundationConfig"]
MIDDLEWARE = [
    "app.foundation.middleware.CorrelationMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "app.foundation.middleware.BrowserSecurityMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
ROOT_URLCONF = "app.config.urls"
WSGI_APPLICATION = "app.config.wsgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"debug": False},
    }
]
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = []
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 1_048_576

# No SQLite fallback. Migration credentials select a distinct connection without pooling.
_migration = AAP_ENTRYPOINT == "migration"
_db_user = "aap_migration" if _migration else "aap_runtime"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("AAP_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("AAP_DB_PORT", "55432"),
        "NAME": os.environ.get("AAP_DB_NAME", "aap_foundation"),
        "USER": os.environ.get("AAP_DB_USER", _db_user),
        "PASSWORD": "",  # Loopback-only isolated synthetic test cluster uses local trust.
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "connect_timeout": 3,
            "options": "-c lock_timeout=5s -c statement_timeout=300000",
            **({} if _migration else {"pool": {"min_size": 0, "max_size": 2, "timeout": 3}}),
        },
    }
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"safe": {"()": "app.foundation.logging.SafeJsonFormatter"}},
    "handlers": {"safe": {"class": "logging.StreamHandler", "formatter": "safe"}},
    "root": {"handlers": ["safe"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["safe"], "level": "WARNING", "propagate": False},
        "aap": {"handlers": ["safe"], "level": "INFO", "propagate": False},
    },
}
