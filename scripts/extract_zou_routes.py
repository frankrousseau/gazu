"""Regenerate tests/fixtures/zou_routes.json from a Zou checkout.

Each Zou blueprint declares a ``routes = [("/path", Resource), ...]`` list. We
AST-parse those (no Zou import, no running server) and dump the sorted, unique
path patterns. The gazu test suite matches every mocked request against this
snapshot so an invented endpoint fails its test (see tests/zou_route_gate.py).

Usage:
    python scripts/extract_zou_routes.py [path-to-zou] \
        > tests/fixtures/zou_routes.json

Defaults to ../zou relative to the repo root.
"""

import ast
import glob
import json
import os
import sys


def extract(zou_path):
    routes = set()
    pattern = os.path.join(zou_path, "zou/app/blueprints/*/__init__.py")
    for f in sorted(glob.glob(pattern)):
        tree = ast.parse(open(f).read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(
                isinstance(t, ast.Name) and t.id == "routes"
                for t in node.targets
            ):
                continue
            if not isinstance(node.value, (ast.List, ast.Tuple)):
                continue
            for elt in node.value.elts:
                first = None
                if isinstance(elt, (ast.Tuple, ast.List)) and elt.elts:
                    first = elt.elts[0]
                elif isinstance(elt, ast.Constant):
                    first = elt
                if isinstance(first, ast.Constant) and isinstance(
                    first.value, str
                ):
                    routes.add(first.value.rstrip("/") or "/")
    return sorted(routes)


if __name__ == "__main__":
    zou = sys.argv[1] if len(sys.argv) > 1 else "../zou"
    print(json.dumps(extract(zou), indent=1))
