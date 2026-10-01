"""Fail-closed T-002 configuration and global DB startup checks (no tenant SQL)."""

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections

LIVE_SECRET_NAMES = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AAP_PROVIDER_KEY",
    "AAP_PROVIDER_KEY_FILE",
    "DATABASE_URL",
    "AAP_DB_PASSWORD",
)


class UnsafeFoundation(ImproperlyConfigured):
    """Only fixed reason codes may cross the startup/error boundary."""


def configuration_errors():
    errors = []
    if settings.AAP_ENVIRONMENT not in {"local", "test"}:
        errors.append("deployment_prerequisites_not_implemented")
    if not settings.AAP_SYNTHETIC_ONLY or settings.AAP_PROVIDER_MODE != "offline":
        errors.append("offline_synthetic_required")
    if any(os.environ.get(name) for name in LIVE_SECRET_NAMES):
        errors.append("external_credentials_forbidden")
    if settings.DEBUG or any(t.get("OPTIONS", {}).get("debug") for t in settings.TEMPLATES):
        errors.append("debug_forbidden")
    if any("admin" in item or "debug_toolbar" in item for item in settings.INSTALLED_APPS):
        errors.append("admin_forbidden")
    if any("debug_toolbar" in item for item in settings.MIDDLEWARE):
        errors.append("debug_forbidden")
    if not settings.ALLOWED_HOSTS or any(
        host not in {"localhost", "127.0.0.1", "[::1]", "testserver"}
        for host in settings.ALLOWED_HOSTS
    ):
        errors.append("hosts_not_local")
    if not all(
        (
            settings.SESSION_COOKIE_SECURE,
            settings.SESSION_COOKIE_HTTPONLY,
            settings.SESSION_COOKIE_SAMESITE == "Lax",
            settings.CSRF_COOKIE_SECURE,
            settings.CSRF_COOKIE_HTTPONLY,
            settings.CSRF_COOKIE_SAMESITE == "Lax",
            not settings.CSRF_TRUSTED_ORIGINS,
        )
    ):
        errors.append("insecure_cookie_or_csrf_policy")
    if settings.AAP_POLICY_VERSION != "foundation-offline-1":
        errors.append("unsupported_policy")
    if settings.AAP_SCHEMA_VERSION != "foundation-1":
        errors.append("unsupported_schema")
    if settings.AAP_ENTRYPOINT not in {"web", "worker", "migration"}:
        errors.append("unsupported_entrypoint")
    db = settings.DATABASES["default"]
    if (
        db["ENGINE"] != "django.db.backends.postgresql"
        or db.get("ATOMIC_REQUESTS")
        or not db.get("AUTOCOMMIT", True)
        or db.get("CONN_MAX_AGE") != 0
        or db.get("HOST") not in {"127.0.0.1", "localhost", "::1", "postgres"}
        or db.get("PASSWORD")
    ):
        errors.append("unsafe_database_configuration")
    expected_user = "aap_migration" if settings.AAP_ENTRYPOINT == "migration" else "aap_runtime"
    if db.get("USER") != expected_user:
        errors.append("wrong_database_role")
    return errors


def validate_configuration():
    errors = configuration_errors()
    if errors:
        raise UnsafeFoundation(",".join(sorted(set(errors))))


def validate_database(*, migration=False, require_baseline=True):
    """Global configuration probe only; tenant wrapper belongs to T-003a."""
    connection = connections["default"]
    if migration != (settings.AAP_ENTRYPOINT == "migration"):
        raise UnsafeFoundation("wrong_entrypoint_for_database_probe")
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT current_setting('server_version_num')::int,
                   r.rolsuper, r.rolbypassrls, r.rolcreaterole, r.rolcreatedb, r.rolreplication,
                   d.datdba = r.oid,
                   has_schema_privilege(current_user, 'public', 'CREATE'),
                   current_setting('app.workspace_id', true),
                   current_setting('lock_timeout'), current_setting('statement_timeout'),
                   EXISTS (
                     SELECT 1 FROM pg_db_role_setting s,
                       unnest(s.setconfig) AS c(value)
                     WHERE s.setrole IN (0, r.oid) AND s.setdatabase IN (0, d.oid)
                       AND c.value LIKE 'app.workspace_id=%%'
                       AND c.value <> 'app.workspace_id='
                   )
            FROM pg_roles r JOIN pg_database d ON d.datname = current_database()
            WHERE r.rolname = current_user
            """
        )
        row = cursor.fetchone()
        if row is None or not 170000 <= row[0] < 180000:
            raise UnsafeFoundation("postgresql_17_required")
        if any(row[1:6]) or (not migration and (row[6] or row[7])):
            raise UnsafeFoundation("unsafe_database_privileges")
        if row[8] or row[11]:
            raise UnsafeFoundation("tenant_session_default_forbidden")
        if row[9:11] != ("5s", "5min"):
            raise UnsafeFoundation("migration_timeouts_required")
        if require_baseline:
            cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
            if cursor.fetchall() != [("foundation", "0001_initial")]:
                raise UnsafeFoundation("unsupported_database_schema")


def startup():
    validate_configuration()
    validate_database()
