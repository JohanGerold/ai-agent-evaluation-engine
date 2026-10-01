"""Compare clean artifacts and record source identity; no Git commit is fabricated."""

import hashlib
import json
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files():
    roots = [ROOT / name for name in ("app", "tests", "tools", "infra", ".github")]
    files = [
        path
        for root in roots
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    files.extend(
        ROOT / name
        for name in (
            "README.md",
            "manage.py",
            "pyproject.toml",
            "uv.lock",
            "requirements.txt",
            "Dockerfile",
            ".dockerignore",
            ".gitignore",
            ".python-version",
            "docs/IMPLEMENTATION_PLAN.md",
        )
    )
    return sorted(files)


def main():
    paths = source_files()
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in paths}
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    artifacts, failures = {}, []
    for name in ("aap-0.0.1-py3-none-any.whl", "aap-0.0.1.tar.gz"):
        first = ROOT / ".artifacts" / "build-one" / name
        second = ROOT / ".artifacts" / "build-two" / name
        artifacts[name] = {
            "first_sha256": digest(first),
            "second_sha256": digest(second),
            "identical": first.read_bytes() == second.read_bytes(),
        }
        if not artifacts[name]["identical"]:
            failures.append("artifact_not_reproducible:" + name)
        if name.endswith(".whl"):
            with zipfile.ZipFile(first) as archive:
                members = archive.namelist()
            if any(not member.startswith(("app/", "aap-0.0.1.dist-info/")) for member in members):
                failures.append("wheel_unexpected_content")
        else:
            with tarfile.open(first) as archive:
                members = archive.getnames()
        for member in members:
            if any(
                part in {".tools", ".artifacts", ".venv", "creation", "__pycache__"}
                or part.startswith(".env")
                for part in member.split("/")
            ):
                failures.append("artifact_contains_excluded_material")
    result = {
        "source_tree_sha256": fingerprint,
        "git_commit": None,
        "source_hashes": hashes,
        "artifacts": artifacts,
        "failures": sorted(set(failures)),
        "production_gates": "NOT RUN",
    }
    (ROOT / ".artifacts/build-evidence.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(f"Source tree SHA256: {fingerprint}")
    print(f"Reproducible artifact/content checks: {len(set(failures))} failures")
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
