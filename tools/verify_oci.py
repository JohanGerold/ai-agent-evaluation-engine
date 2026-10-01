"""T-002 smoke proof using one image and an owned synthetic Compose database."""

import argparse
import json
import subprocess
import time
import uuid
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--network", required=True)
    parser.add_argument("--evidence-dir", type=Path, default=Path(".artifacts/oci"))
    args = parser.parse_args()
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    commands = []
    container = "aap-t002-web-" + uuid.uuid4().hex
    restrictions = ["--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges"]
    database = ["-e", "AAP_DB_HOST=postgres", "-e", "AAP_DB_PORT=5432"]
    result = 1

    def run(command, *, expected=0, input_text=None, timeout=45):
        completed = subprocess.run(
            command, input=input_text, capture_output=True, text=True, timeout=timeout
        )
        output = completed.stdout + completed.stderr
        print(output, end="", flush=True)
        (args.evidence_dir / f"command-{len(commands) + 1}.log").write_text(
            output, encoding="utf-8"
        )
        commands.append(
            {"command": command, "exit_code": completed.returncode, "expected": expected}
        )
        if completed.returncode != expected:
            raise RuntimeError("oci_smoke_command_failed")
        return completed.stdout

    try:
        metadata = json.loads(run(["docker", "image", "inspect", args.image]))[0]
        assert metadata["Config"]["User"] == "10001:10001"
        assert metadata["Config"]["Labels"]["org.opencontainers.image.revision"]
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                *restrictions,
                args.image,
                "python",
                "-c",
                "import django; assert django.get_version() == '5.2.17'",
            ]
        )
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                args.network,
                *restrictions,
                *database,
                "-e",
                "AAP_ENTRYPOINT=migration",
                "-e",
                "AAP_DB_USER=aap_migration",
                args.image,
                "python",
                "manage.py",
                "migrate",
                "--noinput",
            ]
        )
        # Compose initialization grants runtime SELECT on migration-role-created tables.
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                args.network,
                *restrictions,
                *database,
                args.image,
                "python",
                "manage.py",
                "foundation_startup",
            ]
        )
        run(
            [
                "docker",
                "run",
                "--detach",
                "--name",
                container,
                "--network",
                args.network,
                *restrictions,
                *database,
                args.image,
            ]
        )
        # The foundation server binds container loopback; no public port is published.
        health_script = """
import json, time, urllib.request
for attempt in range(30):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2) as response:
            assert response.status == 200
            assert json.load(response) == {'status': 'alive'}
            assert response.headers['X-Request-ID']
            assert response.headers['Content-Security-Policy']
        break
    except OSError:
        time.sleep(0.5)
else:
    raise RuntimeError('web_startup_timeout')
with urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=5) as response:
    assert response.status == 200
    assert json.load(response) == {'status': 'foundation_ready', 'execution_ready': False}
print('HTTP liveness/readiness, correlation and CSP smoke passed; execution_ready=false')
"""
        run(["docker", "exec", "-i", container, "python", "-"], input_text=health_script)
        run(["docker", "logs", container])
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                args.network,
                *restrictions,
                *database,
                args.image,
                "python",
                "-m",
                "app.worker",
            ],
            expected=2,
        )
        for setting in ("AAP_DEBUG=true", "AAP_ENVIRONMENT=production", "AAP_PROVIDER_MODE=live"):
            run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    "none",
                    *restrictions,
                    "-e",
                    setting,
                    args.image,
                    "python",
                    "manage.py",
                    "foundation_startup",
                ],
                expected=1,
            )
        run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                *restrictions,
                args.image,
                "python",
                "manage.py",
                "foundation_startup",
            ],
            expected=1,
        )
        result = 0
    finally:
        cleanup = subprocess.run(
            ["docker", "rm", "--force", container], capture_output=True, text=True, timeout=30
        )
        summary = {
            "result": result,
            "image": args.image,
            "image_id": locals().get("metadata", {}).get("Id"),
            "source_revision": locals()
            .get("metadata", {})
            .get("Config", {})
            .get("Labels", {})
            .get("org.opencontainers.image.revision"),
            "network": args.network,
            "commands": commands,
            "cleanup_exit_code": cleanup.returncode,
            "finished_unix": int(time.time()),
        }
        (args.evidence_dir / "result.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        print(f"OCI evidence: {args.evidence_dir / 'result.json'}")
        if cleanup.returncode:
            result = 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
