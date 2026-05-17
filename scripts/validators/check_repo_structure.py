#!/usr/bin/env python3
"""Validate the bounded PUNNARAJ Control Plane repository structure."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "index.html",
    "README.md",
    "wrangler.jsonc",
    "_routes.json",
    "docs/control-plane.md",
    "schema/processing_jobs.sql",
    "functions/_middleware.ts",
    "functions/_lib/response.ts",
    "functions/_lib/env.ts",
    "functions/_lib/jobs.ts",
    "functions/_lib/crypto.ts",
    "functions/api/health.ts",
    "functions/api/system.ts",
    "functions/api/jobs/index.ts",
    "functions/api/jobs/[id].ts",
    "functions/api/compile.ts",
    "functions/api/hooks/github.ts",
]

PRESERVED_DIRS = [
    "10_MANIFEST",
    "20_METHODOLOGY",
    "30_DELIVERABLES",
    "40_REFERENCE",
    "90_ARCHIVE",
    "docs",
    "portal",
    "SSOT",
    "index",
]


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            errors.append(f"missing required path: {relative}")

    for relative in PRESERVED_DIRS:
        if not (ROOT / relative).is_dir():
            errors.append(f"missing preserved directory: {relative}")

    routes_path = ROOT / "_routes.json"
    if routes_path.exists():
        try:
            routes = json.loads(routes_path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"_routes.json is invalid JSON: {exc}")
        else:
            if routes.get("version") != 1:
                errors.append("_routes.json version must be 1")
            if "/api/*" not in routes.get("include", []):
                errors.append("_routes.json must include /api/*")
            for route in ["/assets/*", "/favicon.ico", "/robots.txt", "/images/*"]:
                if route not in routes.get("exclude", []):
                    errors.append(f"_routes.json must exclude {route}")

    wrangler_path = ROOT / "wrangler.jsonc"
    if wrangler_path.exists():
        wrangler_text = wrangler_path.read_text()
        if '"pages_build_output_dir"' not in wrangler_text:
            errors.append("wrangler.jsonc must declare pages_build_output_dir")
        if '"compatibility_date"' not in wrangler_text:
            errors.append("wrangler.jsonc must declare compatibility_date")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("PUNNARAJ Control Plane repository structure OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
