#!/usr/bin/env python3
"""Count lines of code in src/ and test/ directories."""

from pathlib import Path

ROOT = Path(__file__).parent
TARGETS = ["src", "test"]

SKIP_DIRS = {"__pycache__"}
CODE_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".sh", ".sql", ".html", ".css",
}
DOC_EXTS = {".md", ".rst", ".txt"}
CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}


def classify(path: Path) -> str | None:
    if path.suffix in CODE_EXTS:
        return "code"
    if path.suffix in DOC_EXTS:
        return "doc"
    if path.suffix in CONFIG_EXTS:
        return "config"
    return None


def count_dir(base: Path) -> dict:
    stats = {"code": 0, "doc": 0, "config": 0, "blank": 0, "files": 0}
    by_ext: dict[str, dict] = {}

    if not base.exists():
        return {"stats": stats, "by_ext": by_ext}

    for f in base.rglob("*"):
        if any(part in SKIP_DIRS for part in f.relative_to(base).parts):
            continue
        if not f.is_file():
            continue

        kind = classify(f)
        if kind is None:
            continue

        lines = f.read_text(errors="ignore").splitlines()
        blank = sum(1 for l in lines if not l.strip())
        total = len(lines)

        stats[kind] += total - blank
        stats["blank"] += blank
        stats["files"] += 1

        ext = f.suffix
        if ext not in by_ext:
            by_ext[ext] = {"lines": 0, "blank": 0, "files": 0}
        by_ext[ext]["lines"] += total - blank
        by_ext[ext]["blank"] += blank
        by_ext[ext]["files"] += 1

    return {"stats": stats, "by_ext": by_ext}


def print_section(title: str, data: dict):
    s = data["stats"]
    total = s["code"] + s["doc"] + s["config"] + s["blank"]
    print(f"  {title}")
    print(f"  {'─'*40}")
    print(f"  Code:    {s['code']:>7}   Blank: {s['blank']:>6}")
    print(f"  Doc:     {s['doc']:>7}   Config:{s['config']:>6}")
    print(f"  Total:   {total:>7}   Files: {s['files']:>6}")
    if data["by_ext"]:
        print(f"  {'Ext':<8} {'Code':>7} {'Blank':>7} {'Files':>6}")
        for ext, d in sorted(data["by_ext"].items(), key=lambda x: -x[1]["lines"]):
            print(f"  {ext:<8} {d['lines']:>7} {d['blank']:>7} {d['files']:>6}")
    print()


overall = {"code": 0, "doc": 0, "config": 0, "blank": 0, "files": 0}

for target in TARGETS:
    data = count_dir(ROOT / target)
    print_section(target + "/", data)
    for k in overall:
        overall[k] += data["stats"][k]

total = overall["code"] + overall["doc"] + overall["config"] + overall["blank"]
print(f"  {'='*40}")
print(f"  Combined")
print(f"  {'─'*40}")
print(f"  Code:    {overall['code']:>7}   Blank: {overall['blank']:>6}")
print(f"  Doc:     {overall['doc']:>7}   Config:{overall['config']:>6}")
print(f"  Total:   {total:>7}   Files: {overall['files']:>6}")
