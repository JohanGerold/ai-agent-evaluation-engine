# T-002 closure verification — 2 October 2026

**Status: COMPLETE. T-002 completion criteria are satisfied.**
The Product Owner authorized this closure work and the narrow PostgreSQL 18
compatibility amendment. Implementation/evidence author: Codex. T-001's D-07
exception permits T-002 without an assigned Experienced Reviewer; no independent
ER review or production approval is claimed. T-003a is unstarted and BLOCKED by
D-07. Every production gate remains **NOT RUN**.

This record supplements the [original historical execution record](T-002.md).
The original 17.11 results, source fingerprint and package hashes remain historical
evidence; they are not relabeled as PostgreSQL 18 tests. No unrelated local unit or
package reproducibility suite was repeated. The changed wheel was built for OCI,
and the required hosted workflow ran its normal unit/build/DB stages.

## Verified source and artifact identity

- PostgreSQL amendment and OCI smoke source commit:
  `cad9f3d43a9d7ec43ff36db58ad198a52d1f8beb`.
- Hosted evidence-retention fix/source commit:
  `074191b01ba03a9f63d712a5ab3f20f6027ee877`. Its only difference from the previous
  commit is enabling the hidden evidence directory upload and failing if empty.
- Local Docker Engine **29.8.1**, Linux/amd64; Compose **v5.5.1**.
- Native version: `postgres (PostgreSQL) 18.6`.
- Compose/CI version: `18.6 (Debian 18.6-1.pgdg12+2)`, server version number
  **180006**. Data directory: `/var/lib/postgresql/18/docker`.
- PostgreSQL image:
  `postgres:18.6-bookworm@sha256:3725f4e2499eef5134592b3b4ab79a543ed7f8e533b05b5b637af926630f6650`.
- Local OCI image identity:
  `sha256:cef63ad63e1f25039e441c021c123a570b365cb81e6814cce97d7c38aa004eaa`;
  image revision label equals `cad9f3d43a9d7ec43ff36db58ad198a52d1f8beb`.
- CI OCI image identity:
  `sha256:266844f12ce1ad8bf4a05e3786113fad611e9a6a3eed6534cf52a69491fdc85c`;
  image revision label equals `074191b01ba03a9f63d712a5ab3f20f6027ee877`.
  These are recorded build identities; no cross-environment identity equality or
  registry publication is claimed.
- CI source-tree fingerprint:
  `2dac1f1fbfcc4ba2ba902a3e5bf01ff3cc939031164650172cdc0161f5a4a798`.
  The content manifest has `git_commit: null`; the actual Git source SHA is proven
  separately by the hosted run and OCI revision label.
- CI independently built wheel pair SHA-256:
  `7976d968d248d73015105ae4901371ca1307f57cc866d5c5be44bf4b1463b787`.
- CI independently built sdist pair SHA-256:
  `89cc35a286481d458629e457627ea93b48f85ecc40ea4c0c62922cda21fa7d8f`.
  Both pairs are byte-identical, with zero content/reproducibility failures.

## Exact local commands and results

Commands ran from `C:\Code\AAP`. Every positive command below returned **exit 0**;
expected refusal exits are explicitly distinguished.

| Command | Actual result |
|---|---|
| `docker version`; `docker compose version`; `docker info --format '{{.OSType}} {{.ServerVersion}}'` | Engine/client 29.8.1, Compose v5.5.1, Linux engine responds |
| `& 'C:\Program Files\PostgreSQL\18\bin\postgres.exe' --version` | `postgres (PostgreSQL) 18.6` |
| `.venv/Scripts/python.exe tools/run_postgres_tests.py --pg-bin 'C:\Program Files\PostgreSQL\18\bin'` | **16 passed, 55 deselected**, 0 failed/skipped; harness result 0 and owned cluster stop 0 |
| `docker compose -p aap-t002-closure -f infra/compose.local.yml config --quiet` | Valid Compose configuration |
| `docker compose -p aap-t002-closure -f infra/compose.local.yml up -d --wait` | Fresh pinned 18.6 image/volume, SQL fixture roles/database initialized, healthcheck healthy |
| `.venv/Scripts/python.exe tools/run_postgres_tests.py --external-port 55432` | Real Compose PostgreSQL 18.6: **16 passed, 55 deselected**, 0 failed/skipped |
| Both harnesses: `manage.py migrate --noinput`, `manage.py migrate --check`, repeated `manage.py migrate --noinput`, `manage.py foundation_startup` | All exit 0: empty foundation baseline applied, none pending, repeat no-op, actual non-owner runtime role startup succeeds |
| `docker compose -p aap-t002-closure -f infra/compose.local.yml exec -T postgres psql -U aap_bootstrap -d postgres -Atc 'SHOW server_version; SHOW data_directory;'` | Exact container patch and 18 data directory shown above |
| `uv --cache-dir .tools/verified-uv-cache build --offline --no-build-isolation --wheel --out-dir dist`, `SOURCE_DATE_EPOCH=1790899200` | Updated wheel built for OCI; SHA-256 `5b471eb0231a994efd8eacbab64468421bfc289f9b4f1f50c76527463b768706` |
| `docker build --build-arg SOURCE_REVISION=cad9f3d43a9d7ec43ff36db58ad198a52d1f8beb --tag aap:t002-pg18 .` | OCI build succeeds using hash-locked runtime dependencies and built wheel |
| `.venv/Scripts/python.exe tools/verify_oci.py --image aap:t002-pg18 --network aap-t002-closure_default` | Smoke result 0, all 12 command exits match expectations; web cleanup 0 |
| `docker compose -p aap-t002-closure -f infra/compose.local.yml up -d --force-recreate --wait` | Container recreated and healthy with retained owned volume |
| `docker compose -p aap-t002-closure -f infra/compose.local.yml exec -T postgres psql -U aap_bootstrap -d aap_foundation_ac81d5bc52364cbba62144023b8f0179 -Atc 'SELECT app, name FROM django_migrations;'` | `foundation\|0001_initial`; migrated synthetic database survives recreation |
| `docker compose -p aap-t002-closure -f infra/compose.local.yml down -v` | Owned container, network and test volume removed; user's native 5432 service/other projects untouched |
| `.venv/Scripts/ruff.exe format tools/verify_oci.py tools/run_postgres_tests.py` | One new file formatted; harness already formatted |
| `.venv/Scripts/ruff.exe check app/foundation/safety.py tests/test_postgres.py tools/run_postgres_tests.py tools/verify_oci.py` | All checks passed |
| `.venv/Scripts/ruff.exe format --check tools/verify_oci.py tools/run_postgres_tests.py app/foundation/safety.py tests/test_postgres.py` | Four files already formatted |
| `.venv/Scripts/python.exe tools/check_repository.py`; `git diff --check` | Zero repository guard violations; no whitespace errors |

The two DB suites repeat all database-sensitive T-002 cases: actual major/roles,
runtime DDL/write refusal, migration timeouts/transactional rollback, unsafe
privilege/tenant-default/schema/timeout negatives, readiness, migration-role
separation and refusing worker startup. No tenant tables, RLS or worker execution
protocol was added.

OCI smoke uses the same image for migration, web and the refusing worker entry
point. Runtime UID/GID is **10001:10001**, root filesystem read-only, capabilities
dropped and `no-new-privileges` set. It verifies:

- Network-none import smoke with the installed Django 5.2.17.
- Actual image migration and runtime database startup, both exit 0.
- Running Waitress web entry point: `/health/live` HTTP 200 with `alive`,
  `/health/ready` HTTP 200 with `foundation_ready` and `execution_ready=false`,
  request correlation header and CSP. Requests run on container loopback; no host
  port is published.
- Worker startup exits **2**, emitting `worker_unavailable`; no job execution.
- Debug, production environment and live-provider mode each refuse startup with
  expected exit **1**, on network none. Missing DB startup also refuses with
  expected exit **1** and generic safe diagnostics.

## Hosted GitHub CI and retained evidence

Latest verified implementation run:
[36920066651](https://github.com/JohanGerold/ai-agent-evaluation-engine/actions/runs/36920066651),
source `074191b01ba03a9f63d712a5ab3f20f6027ee877`: **completed / success**.
`gh run watch 36920066651 --repo JohanGerold/ai-agent-evaluation-engine --exit-status --interval 10`
returned exit 0. `gh run view ... --json status,conclusion,headSha,url` independently
confirmed its source/status. All workflow steps succeeded, including:

- Locked dependency preparation, Ruff lint/format, import boundaries (0 violations)
  and repository secret/pinning guards (0 violations).
- Django checks (0 issues), migration drift check (no changes), offline units
  (**55 passed, 16 deselected**, 0 failed/skipped).
- Real Compose PostgreSQL **18.6**, migrations/check/no-op/runtime startup and
  integration suite (**16 passed, 55 deselected**, 0 failed/skipped).
- Two clean offline package builds, zero reproducibility/content failures,
  OCI build/identity, all startup/smoke cases and cleanup.
- Actual evidence upload, subsequently downloaded successfully using
  `gh run download 36920066651 --repo JohanGerold/ai-agent-evaluation-engine --name foundation-evidence --dir .artifacts/ci-36920066651` (exit 0).

Hosted artifact `foundation-evidence`: ID **11192030166**, **261309 bytes**,
SHA-256 `81f2501f4575da0aab795bab629f77c9bda95b133da1f98a2162e55c34f9e0d5`,
not expired when checked. Hosted retention is seven days; the downloaded copy is
retained locally. Run logs and this tracked summary preserve source/result linkage.

The preceding runs 36917333637 (original baseline) and 36919631059 (18 amendment)
also concluded success, but run 36919631059 warned that hidden `.artifacts/` was
excluded from upload; a download found no artifact. That is not retained-artifact
evidence. Commit 074191b enables hidden files only for the owned synthetic evidence
path and makes missing files an error. Run 36920066651 proves the repair. A hosted
Node action deprecation annotation remains informational; no test/check failed.

## Evidence locations and integrity

- Native DB: [.artifacts/postgres-2760f7d0f7db448cb758b28770f40e5f/result.json](../../.artifacts/postgres-2760f7d0f7db448cb758b28770f40e5f/result.json)
  and adjacent five command logs/JUnit. Result SHA-256:
  `1e67660cd0f617646043ef49afbcae301ed248af6f812d0ed74191072579a729`.
- Compose DB: [.artifacts/postgres-7a27ca755b0e4b15844578e0e2490299/result.json](../../.artifacts/postgres-7a27ca755b0e4b15844578e0e2490299/result.json)
  and adjacent five command logs/JUnit. Result SHA-256:
  `453e1b25290c0ecf5ea6c8a764840db6dd80b8be2d6f00d20918df612fd7c631`.
- Local OCI: [.artifacts/oci/result.json](../../.artifacts/oci/result.json), 12
  command logs, `oci-build.log`, `oci-smoke.log`. Result SHA-256:
  `cc0588f8f913b3a6239ddf9a77c60a1193a72bfca095a7920868ae04c46046f7`.
- Compose: `compose-healthy.json`, `compose-version.txt`, `compose-recreate.log`,
  `compose-persistence.txt`, `compose-cleanup.log` under `.artifacts/`.
- [Local transcript integrity manifest](../../.artifacts/t002-closure-hashes.json).
- Downloaded CI: `.artifacts/ci-36920066651/`: `build-evidence.json`, `unit.xml`,
  `postgres-0ed9ba2dd3be4ada8635545978060338/{result.json,tests.xml,command-*.log}`,
  `oci/{result.json,command-*.log}`, `oci-image-id.txt`, both package build directories.
  API status, artifact metadata and complete run logs sit beside this directory.

These generated outputs are ignored local artifacts, not committed binaries or
customer data. The tracked summary deliberately preserves exact identities and
results without pretending local files have indefinite hosted retention.

## Files and dependencies changed by this closure

Documents: `README.md`, `docs/PROJECT_BRIEF.md`, `docs/TEST_STRATEGY.md`,
`docs/IMPLEMENTATION_PLAN.md`, `docs/evidence/T-002.md`; new
`docs/evidence/POSTGRESQL_18_AMENDMENT.md` and this closure record.

Configuration: `infra/compose.local.yml`, `.github/workflows/foundation.yml`,
`pyproject.toml` (test marker wording only).

Runtime/verification: `app/foundation/safety.py`, `tests/test_postgres.py`,
`tools/run_postgres_tests.py`; new `tools/verify_oci.py`.

Dependencies added: **none**. Python pins/lockfile are unchanged. PostgreSQL image
baseline is updated as authorized; native 18.6 was already installed.

## AC evidence and deferred scope

| AC | T-002 foundation evidence now established | Still deferred |
|---|---|---|
| AC-029 | Earlier safe structured logging/IDs/error tests plus real 18.6 startup and container liveness/readiness; explicitly execution_ready=false | Worker/provider operational readiness, integrity dashboards and named alert delivery |
| AC-031 | Earlier source/package/migration evidence plus 18.6 clean/no-op/check migrations, actual image build identities/revision labels and hosted reproducible package pairs | Real upgrade/partial migration repair, promotion/prior-image rollback and recovery drills |
| AC-037 | Earlier browser/debug/admin/import guards plus successful pinned CI, retained artifacts and non-root/read-only/capability-restricted OCI startup smoke | Full namespace egress containment, deployed browser/supply-chain/security gates |
| AC-043 | Actual 18.6 unsafe-role/default/schema/timeout tests plus container debug/deployed/live-mode refusal | Expiring audited break-glass, MFA, secret access and production bootstrap/RLS |
| AC-013 foundation | Earlier 55-test synthetic canary/exception/log/error evidence, reconfirmed by hosted offline unit suite; container startup failure diagnostics | Prompt/trace/telemetry sweeps, worker-only live keys and rotation/revocation |

**No PostgreSQL 18 database incompatibility was discovered** in these checks.
The official image's changed volume layout was handled explicitly.
Architecture changes are limited to the user-approved PostgreSQL baseline
amendment; **no unrelated deviation**. No `creation/` integration, live keys,
provider calls, customer data, staging/deployment provisioning or later task work.
All full AC/release obligations remain deferred to their scheduled tasks.
T-002 is closed; stop before T-003a.
