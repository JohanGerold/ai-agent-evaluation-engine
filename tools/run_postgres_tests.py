"""Own an isolated loopback-only real PostgreSQL 17 cluster; never use customer DBs."""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pg-bin", type=Path)
    parser.add_argument(
        "--external-port",
        type=int,
        help="Fresh synthetic Compose PostgreSQL on loopback; never customer DB",
    )
    args = parser.parse_args()
    if args.external_port:
        return external(args.external_port)
    bin_dir = args.pg_bin or Path(shutil.which("pg_ctl") or "").parent
    suffix = ".exe" if os.name == "nt" else ""
    commands = {name: bin_dir / (name + suffix) for name in ("pg_ctl", "initdb", "postgres")}
    if not all(path.is_file() for path in commands.values()):
        print("UNVERIFIED: PostgreSQL binaries unavailable; no substitute used.")
        return 2
    version = subprocess.check_output([str(commands["postgres"]), "--version"], text=True).strip()
    if not version.startswith("postgres (PostgreSQL) 17."):
        print("UNVERIFIED: PostgreSQL 17 required.")
        return 2
    artifacts = ROOT / ".artifacts"
    artifacts.mkdir(exist_ok=True)
    run_dir = artifacts / ("postgres-" + uuid.uuid4().hex)
    run_dir.mkdir()
    # Retain the synthetic cluster and logs; do not recursively delete computed paths.
    data_dir = run_dir / "data"
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    with socket.socket() as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        port = port_socket.getsockname()[1]
    with (run_dir / "initdb.log").open("w") as log:
        subprocess.run(
            [
                str(commands["initdb"]),
                "-D",
                str(data_dir),
                "-U",
                "aap_bootstrap",
                "-A",
                "trust",
                "--no-locale",
                "--encoding=UTF8",
            ],
            check=True,
            **hidden,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    with (data_dir / "postgresql.conf").open("a") as config:
        config.write(
            f"\nlisten_addresses='127.0.0.1'\nport={port}\nmax_connections=30\n"
            "log_statement='none'\n"
        )
    subprocess.run(
        [
            str(commands["pg_ctl"]),
            "-D",
            str(data_dir),
            "-l",
            str(run_dir / "server.log"),
            "-w",
            "start",
        ],
        check=True,
        **hidden,
    )
    result = 1
    try:
        conninfo = f"host=127.0.0.1 port={port} user=aap_bootstrap dbname=postgres"
        with psycopg.connect(conninfo, autocommit=True) as connection:
            connection.execute("CREATE ROLE aap_migration LOGIN NOSUPERUSER NOBYPASSRLS")
            connection.execute("CREATE ROLE aap_runtime LOGIN NOSUPERUSER NOBYPASSRLS")
            connection.execute("CREATE DATABASE aap_foundation OWNER aap_migration")
        with psycopg.connect(
            conninfo.replace("dbname=postgres", "dbname=aap_foundation"), autocommit=True
        ) as connection:
            connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        env = os.environ.copy()
        env.update(
            {
                "AAP_ENVIRONMENT": "test",
                "AAP_DB_HOST": "127.0.0.1",
                "AAP_DB_PORT": str(port),
                "AAP_DB_NAME": "aap_foundation",
                "AAP_ENTRYPOINT": "migration",
                "AAP_DB_USER": "aap_migration",
            }
        )
        commands_run = []

        def run(command, environment=env):
            completed = subprocess.run(
                command, env=environment, cwd=ROOT, **hidden, capture_output=True, text=True
            )
            output = completed.stdout + completed.stderr
            print(output, end="", flush=True)
            (run_dir / f"command-{len(commands_run) + 1}.log").write_text(output, encoding="utf-8")
            commands_run.append({"command": command, "exit_code": completed.returncode})
            if completed.returncode:
                raise RuntimeError("foundation_subcommand_failed")

        run([sys.executable, "manage.py", "migrate", "--noinput"])
        run([sys.executable, "manage.py", "migrate", "--check"])
        run([sys.executable, "manage.py", "migrate", "--noinput"])
        with psycopg.connect(
            conninfo.replace("dbname=postgres", "dbname=aap_foundation"), autocommit=True
        ) as connection:
            connection.execute("GRANT SELECT ON django_migrations TO aap_runtime")
        env.update(
            {
                "AAP_ENTRYPOINT": "web",
                "AAP_DB_USER": "aap_runtime",
                "AAP_TEST_POSTGRES": "1",
                "AAP_TEST_BOOTSTRAP_DSN": conninfo,
            }
        )
        run([sys.executable, "manage.py", "foundation_startup"])
        run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-m",
                "postgres",
                "--junitxml",
                str(run_dir / "tests.xml"),
            ]
        )
        result = 0
    finally:
        stopped = subprocess.run(
            [str(commands["pg_ctl"]), "-D", str(data_dir), "-m", "fast", "-w", "stop"], **hidden
        )
        summary = {
            "postgres_version": version,
            "result": result,
            "stop_exit_code": stopped.returncode,
            "commands": locals().get("commands_run", []),
            "finished_unix": int(time.time()),
        }
        (run_dir / "result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Real PostgreSQL evidence: {run_dir / 'result.json'}")
        if stopped.returncode:
            result = 1
    return result


def external(port):
    """Fresh unique test DB in the CI Compose cluster; ownership is explicit."""
    if not 1024 <= port <= 65535:
        raise ValueError("invalid_synthetic_port")
    artifacts = ROOT / ".artifacts"
    artifacts.mkdir(exist_ok=True)
    run_dir = artifacts / ("postgres-" + uuid.uuid4().hex)
    run_dir.mkdir()
    database = "aap_foundation_" + uuid.uuid4().hex
    conninfo = f"host=127.0.0.1 port={port} user=aap_bootstrap dbname=postgres"
    with psycopg.connect(conninfo, autocommit=True) as connection:
        version = connection.execute("SHOW server_version_num").fetchone()[0]
        if not 170000 <= int(version) < 180000:
            raise RuntimeError("postgresql_17_required")
        # Names are generated internally, never supplied by a caller.
        connection.execute(
            psycopg.sql.SQL("CREATE DATABASE {} OWNER aap_migration").format(
                psycopg.sql.Identifier(database)
            )
        )
    with psycopg.connect(
        conninfo.replace("dbname=postgres", f"dbname={database}"), autocommit=True
    ) as connection:
        connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    env = os.environ.copy()
    env.update(
        {
            "AAP_ENVIRONMENT": "test",
            "AAP_DB_HOST": "127.0.0.1",
            "AAP_DB_PORT": str(port),
            "AAP_DB_NAME": database,
            "AAP_ENTRYPOINT": "migration",
            "AAP_DB_USER": "aap_migration",
        }
    )
    commands_run = []
    result = 1
    try:

        def run(command):
            completed = subprocess.run(command, env=env, cwd=ROOT)
            commands_run.append({"command": command, "exit_code": completed.returncode})
            if completed.returncode:
                raise RuntimeError("foundation_subcommand_failed")

        run([sys.executable, "manage.py", "migrate", "--noinput"])
        run([sys.executable, "manage.py", "migrate", "--check"])
        run([sys.executable, "manage.py", "migrate", "--noinput"])
        with psycopg.connect(
            conninfo.replace("dbname=postgres", f"dbname={database}"), autocommit=True
        ) as connection:
            connection.execute("GRANT SELECT ON django_migrations TO aap_runtime")
        env.update(
            {
                "AAP_ENTRYPOINT": "web",
                "AAP_DB_USER": "aap_runtime",
                "AAP_TEST_POSTGRES": "1",
                "AAP_TEST_BOOTSTRAP_DSN": conninfo,
            }
        )
        run([sys.executable, "manage.py", "foundation_startup"])
        run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-m",
                "postgres",
                "--junitxml",
                str(run_dir / "tests.xml"),
            ]
        )
        result = 0
    finally:
        # Preserve the unique synthetic database for evidence; Compose down -v is explicit cleanup.
        (run_dir / "result.json").write_text(
            json.dumps(
                {"postgres_version_num": version, "result": result, "commands": commands_run},
                indent=2,
            ),
            encoding="utf-8",
        )
    return result


if __name__ == "__main__":
    sys.exit(main())
