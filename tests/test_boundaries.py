from tools.check_boundaries import inspect_sources


def source(tmp_path, name, content):
    path = tmp_path / "app" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return tmp_path / "app"


def test_sdk_outside_provider_denied(tmp_path):
    root = source(tmp_path, "catalog/module.py", "import openai\n")
    assert any("SDK" in error for error in inspect_sources(root))


def test_provider_sdk_is_allowed(tmp_path):
    root = source(tmp_path, "providers/module.py", "import openai\n")
    assert inspect_sources(root) == []


def test_evaluation_transitive_boundary(tmp_path):
    root = source(tmp_path, "evaluation/rules.py", "from app.shared import helper\n")
    source(tmp_path, "shared/helper.py", "from app.jobs import store\n")
    assert any("transitively" in error for error in inspect_sources(root))


def test_relative_evaluation_boundary(tmp_path):
    root = source(tmp_path, "evaluation/rules.py", "from .. import providers\n")
    assert inspect_sources(root)


def test_simulator_io_and_dynamic_import_denied(tmp_path):
    root = source(tmp_path, "execution/simulator/state.py", "import os\n__import__('socket')\n")
    failures = inspect_sources(root)
    assert any("I/O" in error for error in failures)
    assert any("dynamic" in error for error in failures)


def test_simulator_transitive_io_denied(tmp_path):
    root = source(tmp_path, "execution/simulator/state.py", "from . import helper\n")
    source(tmp_path, "execution/simulator/helper.py", "import pathlib\n")
    assert inspect_sources(root)


def test_pure_imports_allowed(tmp_path):
    root = source(
        tmp_path, "execution/simulator/state.py", "import json\nfrom dataclasses import dataclass\n"
    )
    assert inspect_sources(root) == []
