# Authorized PostgreSQL compatibility amendment — 2 October 2026

The Product Owner explicitly authorized changing the supported baseline from
PostgreSQL 17.x to **PostgreSQL 18.x**, with **18.6** as the currently tested
development/test patch. This narrow amendment applies to local, CI, container and
future deployment baselines. No production/customer data is being upgraded.
No other architecture decision, task dependency, AC or production gate changes.
T-003a remains unstarted and blocked by D-07.

[Django 5.2 database support](https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes)
includes PostgreSQL 14 and higher. The [PostgreSQL support policy](https://www.postgresql.org/support/versioning/)
lists PostgreSQL 18 as supported. The [official PostgreSQL image contract](https://hub.docker.com/_/postgres)
requires PostgreSQL 18 volume mounts at `/var/lib/postgresql`, with default data
directory `/var/lib/postgresql/18/docker`.

## Reference inventory and classification

The tracked source/documentation/configuration tree was searched for PostgreSQL
17 wording, `17.11`, versioned PostgreSQL URLs, `postgresql_17_required`, and
`170000`/`180000` guards. Ignored local binaries, caches and generated evidence are
excluded from normative source searches. Django 5.2.17 is unrelated and unchanged.

| Original occurrence | Classification | Disposition |
|---|---|---|
| `docs/PROJECT_BRIEF.md`, selected platform: managed PostgreSQL 17 | Normative baseline | PostgreSQL 18.x, currently tested baseline 18.6 |
| `docs/TEST_STRATEGY.md`, real PostgreSQL17 test layer | Normative baseline | PostgreSQL 18.x, currently tested baseline 18.6 |
| `README.md`, development version, binary directory/example and CI description | Normative baseline | 18.x / 18.6; installed PostgreSQL 18 binary example |
| `infra/compose.local.yml`, postgres:17.11-bookworm image and data mount | Normative configuration | Digest-pinned 18.6-bookworm; fresh major-specific volume at PostgreSQL 18 mount |
| `.github/workflows/foundation.yml`, PostgreSQL 17 integration label | Normative configuration | 18.6 integration using the amended Compose file |
| `pyproject.toml`, PostgreSQL 17 pytest marker description | Normative test contract | PostgreSQL 18 |
| `app/foundation/safety.py`, 17-major numeric guard and error code | Normative runtime contract | 18-major guard (`180000 <= version < 190000`) and 18 error code |
| `tools/run_postgres_tests.py`, docstring, binary version prefix, rejection text, external-server guard/error | Normative verification contract | Require PostgreSQL 18; preserve exact server patch in external evidence |
| `tests/test_postgres.py`, 17-major numeric assertion | Normative verification contract | Assert PostgreSQL 18 |
| `docs/evidence/T-002.md`, original portable 17.11 download, command and 16-test result | Historical evidence | Retained unchanged in the historical execution record |
| `docs/evidence/REPOSITORY_SETUP.md`, then-approved 17 baseline and retained 17.11 runtime | Historical evidence | Retained unchanged; superseded by this dated amendment |
| `docs/ARCHITECTURE.md`, `/docs/17/sql-set.html` supporting SET LOCAL reference | Incidental versioned source reference | Retained; reference explains transaction scope, not supported baseline |

## Configuration scope

Application startup and both DB harness modes now require PostgreSQL 18.x.
Compose uses `postgres:18.6-bookworm@sha256:3725f4e2499eef5134592b3b4ab79a543ed7f8e533b05b5b637af926630f6650`.
The volume changes from `aap_local_pg` to `aap_local_pg18`, preventing an existing
17 data directory from being opened by 18. Existing volumes and the user's native
5432 service are not modified. Verification owns a separate Compose project and
isolated native cluster. No Python dependency was added or upgraded.

The only image compatibility adjustment is the officially required PostgreSQL 18
volume layout. Database-sensitive results are recorded in the
[T-002 closure evidence](T-002-CLOSURE.md); historical 17.11 results do not establish
18.6 compatibility. All production gates remain **NOT RUN**.
