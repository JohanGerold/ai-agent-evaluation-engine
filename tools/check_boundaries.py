"""AST import/call checks for the documented modular-monolith boundaries."""

import ast
import sys
from pathlib import Path

PURE_IMPORTS = {
    "math",
    "json",
    "decimal",
    "dataclasses",
    "typing",
    "enum",
    "collections",
    "copy",
    "functools",
    "itertools",
    "operator",
    "hashlib",
    "unicodedata",
    "uuid",
}
UNSAFE_CALLS = {"open", "eval", "exec", "compile", "__import__"}


def inspect_sources(root):
    paths = sorted(root.rglob("*.py"))
    modules = {}
    for path in paths:
        parts = path.relative_to(root.parent).with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        modules[".".join(parts)] = path
    graph, errors = {}, []
    for module, path in modules.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                prefix = node.module or ""
                if node.level:
                    package = module if path.name == "__init__.py" else module.rsplit(".", 1)[0]
                    base = package.split(".")[: len(package.split(".")) - node.level + 1]
                    prefix = ".".join(base + ([prefix] if prefix else []))
                imports.add(prefix)
                imports.update(f"{prefix}.{alias.name}" for alias in node.names)
            elif isinstance(node, ast.Call):
                call = node.func
                if isinstance(call, ast.Name) and call.id in UNSAFE_CALLS:
                    errors.append(f"{module}:{node.lineno}: forbidden dynamic/I/O call {call.id}")
                if isinstance(call, ast.Attribute) and call.attr in {"import_module", "__import__"}:
                    errors.append(f"{module}:{node.lineno}: dynamic import forbidden")
        graph[module] = imports
        for imported in imports:
            if imported.split(".")[0] == "openai" and not module.startswith("app.providers"):
                errors.append(f"{module}: SDK import outside providers")

    def closure(module, visited=None):
        visited = set() if visited is None else visited
        if module in visited:
            return set()
        visited.add(module)
        result = set(graph.get(module, set()))
        for imported in tuple(result):
            if imported in graph:
                result.update(closure(imported, visited))
        return result

    for module in graph:
        imported = closure(module)
        if module.startswith("app.evaluation") and any(
            name == target or name.startswith(target + ".")
            for name in imported
            for target in ("app.providers", "app.jobs", "openai")
        ):
            errors.append(f"{module}: evaluation imports providers/jobs transitively")
        if module.startswith("app.execution.simulator"):
            if any(
                not name.startswith("app.execution.simulator")
                and name.split(".")[0] not in PURE_IMPORTS
                for name in imported
            ):
                errors.append(f"{module}: simulator imports an I/O or unapproved module")
    return sorted(set(errors))


if __name__ == "__main__":
    failures = inspect_sources(Path("app"))
    for failure in failures:
        print(failure)
    print(f"Module boundary violations: {len(failures)}")
    sys.exit(bool(failures))
