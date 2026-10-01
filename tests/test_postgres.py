import os
import subprocess
import sys

import psycopg
import pytest
from django.conf import settings
from django.db import ProgrammingError, connection, connections

from app.foundation.safety import UnsafeFoundation, validate_database

pytestmark = pytest.mark.postgres


def admin():
    info = psycopg.conninfo.conninfo_to_dict(os.environ["AAP_TEST_BOOTSTRAP_DSN"])
    info["dbname"] = settings.DATABASES["default"]["NAME"]
    return psycopg.connect(**info, autocommit=True)


def reset_pool():
    connection.close()
    connection.close_pool()


def test_actual_runtime_role_and_supported_postgres():
    validate_database()
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_user, current_setting('server_version_num')::int")
        user, version = cursor.fetchone()
    assert user == "aap_runtime"
    assert 180000 <= version < 190000


def test_baseline_creates_no_later_task_tables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        assert cursor.fetchall() == [("django_migrations",)]


def test_runtime_cannot_create_or_write_migration_table():
    with (
        pytest.raises(psycopg.errors.InsufficientPrivilege),
        psycopg.connect(
            host="127.0.0.1",
            port=settings.DATABASES["default"]["PORT"],
            dbname=settings.DATABASES["default"]["NAME"],
            user="aap_runtime",
            autocommit=True,
        ) as runtime,
    ):
        runtime.execute("CREATE TABLE forbidden_fixture(id int)")
    with pytest.raises(ProgrammingError), connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations")


def test_migration_role_timeouts_and_transactional_ddl_rollback():
    with psycopg.connect(
        host="127.0.0.1",
        port=settings.DATABASES["default"]["PORT"],
        dbname=settings.DATABASES["default"]["NAME"],
        user="aap_migration",
        options="-c lock_timeout=5s -c statement_timeout=300000",
    ) as migration:
        assert migration.execute("SHOW lock_timeout").fetchone() == ("5s",)
        assert migration.execute("SHOW statement_timeout").fetchone() == ("5min",)
        with pytest.raises(RuntimeError), migration.transaction():
            migration.execute("CREATE TABLE rollback_fixture(id int)")
            raise RuntimeError("synthetic_migration_failure")
        assert migration.execute("SELECT to_regclass('public.rollback_fixture')").fetchone() == (
            None,
        )


@pytest.mark.parametrize(
    "sql,reverse",
    [
        ("ALTER ROLE aap_runtime SUPERUSER", "ALTER ROLE aap_runtime NOSUPERUSER"),
        ("ALTER ROLE aap_runtime BYPASSRLS", "ALTER ROLE aap_runtime NOBYPASSRLS"),
        (
            "GRANT CREATE ON SCHEMA public TO aap_runtime",
            "REVOKE CREATE ON SCHEMA public FROM aap_runtime",
        ),
        (
            "ALTER DATABASE {database} OWNER TO aap_runtime",
            "ALTER DATABASE {database} OWNER TO aap_migration",
        ),
    ],
)
def test_real_unsafe_role_rejected(sql, reverse):
    database = settings.DATABASES["default"]["NAME"]
    with admin() as bootstrap:
        bootstrap.execute(sql.format(database=database))
        try:
            with pytest.raises(UnsafeFoundation, match="unsafe_database_privileges"):
                validate_database()
        finally:
            bootstrap.execute(reverse.format(database=database))
    validate_database()


def test_real_session_tenant_setting_rejected():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config('app.workspace_id', %s, false)",
            ["00000000-0000-0000-0000-000000000001"],
        )
    try:
        with pytest.raises(UnsafeFoundation, match="tenant_session_default_forbidden"):
            validate_database()
    finally:
        with connection.cursor() as cursor:
            cursor.execute("RESET app.workspace_id")
        reset_pool()


def test_real_role_default_rejected():
    with admin() as bootstrap:
        bootstrap.execute("ALTER ROLE aap_runtime SET app.workspace_id = 'synthetic-canary'")
        reset_pool()
        try:
            with pytest.raises(UnsafeFoundation, match="tenant_session_default_forbidden"):
                validate_database()
        finally:
            bootstrap.execute("ALTER ROLE aap_runtime RESET app.workspace_id")
            reset_pool()
    validate_database()


def test_real_database_default_rejected():
    database = settings.DATABASES["default"]["NAME"]
    with admin() as bootstrap:
        bootstrap.execute(
            psycopg.sql.SQL("ALTER DATABASE {} SET app.workspace_id = 'synthetic'").format(
                psycopg.sql.Identifier(database)
            )
        )
        reset_pool()
        try:
            with pytest.raises(UnsafeFoundation, match="tenant_session_default_forbidden"):
                validate_database()
        finally:
            bootstrap.execute(
                psycopg.sql.SQL("ALTER DATABASE {} RESET app.workspace_id").format(
                    psycopg.sql.Identifier(database)
                )
            )
            reset_pool()
    validate_database()


def test_missing_baseline_rejected():
    with admin() as bootstrap:
        bootstrap.execute("DELETE FROM django_migrations")
        try:
            with pytest.raises(UnsafeFoundation, match="unsupported_database_schema"):
                validate_database()
        finally:
            bootstrap.execute(
                "INSERT INTO django_migrations(app, name, applied) "
                "VALUES ('foundation', '0001_initial', now())"
            )
    validate_database()


def test_changed_timeout_rejected():
    with connection.cursor() as cursor:
        cursor.execute("SET lock_timeout='0'")
    try:
        with pytest.raises(UnsafeFoundation, match="migration_timeouts_required"):
            validate_database()
    finally:
        with connection.cursor() as cursor:
            cursor.execute("SET lock_timeout='5s'")
    validate_database()


def test_foundation_ready_still_reports_execution_unavailable(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "foundation_ready", "execution_ready": False}


def test_separate_worker_entrypoint_refuses_execution():
    result = subprocess.run(
        [sys.executable, "-m", "app.worker"], capture_output=True, text=True, timeout=15
    )
    assert result.returncode == 2
    assert '"event":"worker_unavailable"' in result.stderr


def test_runtime_migration_command_refused():
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 1
    assert "migration_entrypoint_required" in result.stderr


@pytest.fixture(autouse=True)
def close_connections():
    yield
    connections.close_all()
