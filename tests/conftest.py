import os
import socket

import pytest


@pytest.fixture(autouse=True)
def offline_python_network(monkeypatch):
    """Python network transports have no network during foundation tests."""

    def refuse(*args, **kwargs):
        raise AssertionError("external_network_forbidden_in_foundation_tests")

    # Psycopg/libpq uses its own C loopback connection for real PostgreSQL tests.
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)


@pytest.fixture(autouse=True)
def real_postgres_access(request, django_db_blocker):
    if request.node.get_closest_marker("postgres"):
        if os.environ.get("AAP_TEST_POSTGRES") != "1":
            pytest.skip("UNVERIFIED: use tools/run_postgres_tests.py for real PostgreSQL")
        with django_db_blocker.unblock():
            yield
    else:
        yield
