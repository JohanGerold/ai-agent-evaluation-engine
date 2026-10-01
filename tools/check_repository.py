"""Small foundation guard: secret patterns and pinned CI/build inputs."""

import re
import sys
from pathlib import Path

ROOTS = ("app", "tests", "tools", "infra", ".github")
PATTERNS = (
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{24,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def main():
    failures = []
    for root in ROOTS:
        for path in Path(root).rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yml", ".yaml", ".sql", ".json", ".ps1"}:
                content = path.read_text(encoding="utf-8")
                if any(pattern.search(content) for pattern in PATTERNS):
                    failures.append(f"{path}: suspected credential (value suppressed)")
                if path.suffix in {".yml", ".yaml"}:
                    for line in content.splitlines():
                        if "uses:" in line and not re.search(r"@[a-f0-9]{40}\b", line):
                            failures.append(f"{path}: action is not SHA pinned")
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    if not re.search(r"FROM .*@sha256:[a-f0-9]{64}", dockerfile):
        failures.append("Dockerfile: base image is not digest pinned")
    for failure in failures:
        print(failure)
    print(f"Repository guard violations: {len(failures)}")
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
