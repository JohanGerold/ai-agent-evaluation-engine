# Repository setup and installation check — 2 October 2026

Repository: https://github.com/JohanGerold/ai-agent-evaluation-engine

The existing GitHub `main` history contained commit
`f7b2e01a2a0d68a28872bd8f7876f3d7a83dc59e` (initial README). It was fetched and
preserved as the parent of the first workspace project commit. The local foundation
README replaces that brief README; all existing workspace source, design documents,
rules and the separate `creation/` prototype are versioned without integrating the
prototype into the application.

Git configuration is repository-local: `main`, `origin` pointing to the supplied
repository, author `Johan Gerold`, and the GitHub no-reply email
`181932151+JohanGerold@users.noreply.github.com`. Global Git configuration was not
changed. `.gitattributes` keeps text LF-normalized and images binary. `.gitignore`
excludes virtual environments, downloaded runtimes, dependency caches, synthetic
test databases, local build/test evidence, and environment secret files. The
repository guard and import-boundary checks reported zero violations; staged
whitespace validation passed.

Installation observations:

- PostgreSQL **18.6** is installed under `C:\Program Files\PostgreSQL\18`; service
  `postgresql-x64-18` is running. `pg_isready -h 127.0.0.1 -p 5432` reports accepting
  connections. No password, database contents, grants or server configuration were
  accessed or changed. The approved application requirement remains PostgreSQL 17;
  the existing isolated 17.11 test runtime is retained. PostgreSQL 18 was not used
  as a substitute for the task's required integration tests.
- Docker CLI **29.8.1** and Compose **v5.5.1** are installed in the per-user Docker
  Desktop directory. They are not in this already-running shell's PATH, so the
  installation was checked by absolute executable path.
- `docker desktop start --detach` reported successful Desktop startup. The subsequent
  `docker version` probe selected `desktop-linux`, but its engine returned HTTP 500.
  `wsl --status` reports WSL is not installed. Docker's installation is confirmed;
  usable Linux-engine/container operation is **UNVERIFIED**. No OS components were
  installed and no Docker containers or project volumes were created by this check.

These checks do not change T-002's original test results or close it as complete.
Production gates remain **NOT RUN**, and T-003a remains unstarted and blocked by D-07.
