# AAP — T-002 offline foundation

The approved Revision 2 design is production-oriented / production-capable in design.
This repository contains only the T-002 foundation and is **NOT PRODUCTION-READY**.
All production gates remain **NOT RUN**. T-003a remains unstarted and blocked by D-07.
`creation/` is an independent visual prototype and is not integrated.

Implemented: minimal Django package/module boundaries, PostgreSQL-only settings,
an empty migration baseline, safe JSON metadata logs and request IDs, startup
refusal, local health endpoints, pinned dependencies/build inputs, synthetic local
PostgreSQL infrastructure and offline CI checks. Domain packages are empty reserved
boundaries, not implemented features. DRF is installed but no product API is exposed.
No provider SDK, transport, live key, identity integration, tenant model/wrapper/RLS,
agent engine, queue, budget ledger or operational service exists yet.

## Development and verification

Use Python **3.13.15**, uv **0.12.15**, Django **5.2.17**, and real PostgreSQL **18.x**
(currently tested patch **18.6**). See the [authorized baseline amendment](docs/evidence/POSTGRESQL_18_AMENDMENT.md).
Versions and all transitive hashes are recorded in `uv.lock`; `requirements.txt`
is the hash-locked runtime export for the OCI recipe. No SQLite fallback is supported.
Dependency installation is a preparation step; tests and builds use locked offline inputs.

```powershell
uv sync --locked
uv run --offline --locked ruff check app tests tools manage.py
uv run --offline --locked ruff format --check app tests tools manage.py
uv run --offline --locked python tools/check_boundaries.py
uv run --offline --locked python tools/check_repository.py
uv run --offline --locked python manage.py check
uv run --offline --locked python manage.py makemigrations --check --dry-run
uv run --offline --locked pytest -m "not postgres"
```

For the owned PostgreSQL harness, supply a PostgreSQL 18 binary directory:

```powershell
uv run --offline --locked python tools/run_postgres_tests.py --pg-bin "C:/Program Files/PostgreSQL/18/bin"
```

It initializes a fresh synthetic cluster under `.artifacts/`, binds only loopback on
an available port, migrates with a distinct non-superuser DDL role, verifies the
non-owner runtime role, runs actual PostgreSQL integration tests, and stops its
cluster in `finally`. The synthetic cluster/logs are retained locally for inspection.
Missing binaries exit **2 / UNVERIFIED**, rather than substituting another database.
Standalone `pytest` skips DB tests explicitly; a skipped DB suite is not passing evidence.
The local test roles are fixtures only, not T-003b's production bootstrap.

Alternatively, with Docker/Compose:

```powershell
docker compose -f infra/compose.local.yml up -d --wait
uv run --offline --locked python tools/run_postgres_tests.py --external-port 55432
```

The external-port mode is exclusively for that synthetic loopback Compose cluster
and creates a unique database. It never accepts an arbitrary DSN/customer database.
Synthetic trust authentication is confined to this disposable local environment;
it is not a staging/production credential or topology.

For a local preview using the Compose-created `aap_foundation` database, set
`AAP_ENTRYPOINT=migration` and `AAP_DB_USER=aap_migration`, run `manage.py migrate`,
then remove those overrides before starting the web entry point. Bind only loopback:

```powershell
uv run --offline --locked waitress-serve --host=127.0.0.1 --port=8000 --threads=2 app.config.wsgi:application
```

Only `/health/live` and `/health/ready` exist. Liveness has no DB/provider probe;
readiness checks the foundation DB/schema/role and always reports
`execution_ready=false`. There is no worker readiness claim. `python -m app.worker`
validates startup, closes its DB pool, and exits **2 / worker_unavailable** without
executing tasks. Four execution processes, heartbeat threads, leases, groups and
the independent supervisor/reaper belong to T-020a/b and are not implemented here.

The settings reject all staging/production startup until later prerequisites are
implemented. Debug/admin/toolbar, nonlocal hosts, unsafe cookies/CSRF, unknown policy
or schema, online provider mode, live secret environment variables, non-PostgreSQL
configuration and unsafe actual DB roles are refused. No model registry/rate card
or secret/network proof is fabricated to allow deployed startup. Known-secret
canaries exercise logs/errors; unknown customer secret detection is not guaranteed.

## Build and CI

```powershell
$env:SOURCE_DATE_EPOCH='1790899200'
uv build --offline --no-build-isolation
docker build --tag aap:foundation .
```

The sdist explicitly includes source/documentation and excludes runtime downloads,
test databases, caches and the prototype. The wheel contains only `app/` and package
metadata. The OCI recipe pins the official Python image digest, installs hash-locked
runtime dependencies and the wheel, and uses UID/GID 10001. Web and the refusing
worker entry point are in the same wheel/image. Container execution should use
`--read-only --cap-drop ALL --security-opt no-new-privileges` and bounded resources;
deployment containment proof remains T-036a/b, not a T-002 claim.

The SHA-pinned GitHub workflow has read-only repository permission, no retained
checkout credential or deployment secrets, real PostgreSQL 18.6 migration tests,
offline tests, build and container smoke steps. It neither provisions staging nor
dispatches providers. A recipe's existence is not evidence that hosted CI or Docker
ran. Results, command transcripts, AC contributions and unavailable checks are in
`docs/evidence/T-002.md`.

Migration convention: separate `AAP_ENTRYPOINT=migration` and `aap_migration`
credentials, `lock_timeout=5s`, `statement_timeout=5min`, normal migrations enabled,
clean baseline plus repeated no-op migration checks. No cluster roles are created
by app migrations. There are no tenant tables; only `django_migrations` is created.
Production upgrade, partial-failure repair and prior-image rollback are T-038 evidence.
