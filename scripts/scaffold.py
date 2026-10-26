#!/usr/bin/env python3
"""Scaffold a project-blueprint documentation repository from the skill's templates.

Usage:
    python scaffold.py --target <dir> --name "<Project>" --code <CODE> --owner "<Owner>"
                       [--slug <kebab>] [--date YYYY-MM-DD]
                       [--without legacy,design,flows,orchestration,agents,security,context]
                       [--force] [--dry-run]

Copies ../assets/templates (relative to this script) into <dir>, substituting these
placeholders in file contents and file names:

    {{PROJECT}}       display name            (--name)
    {{PROJECT_SLUG}}  kebab-case slug          (--slug, default derived from --name)
    {{CODE}}          short uppercase code     (--code, e.g. ABC)
    {{OWNER}}         product owner name       (--owner)
    {{DATE}}          YYYY-MM-DD               (--date, default today)

--without skips optional parts (comma-separated, repeatable):
    legacy         docs/legacy-sources.md (only needed when replacing an existing system)
    design         docs/design-system.md, docs/design-system-brief.md
    flows          docs/process-flows.md
    orchestration  docs/orchestration/**
    agents         .claude/agents/**
    security       docs/security/threat-model.md
    context        docs/context/**

Existing files are never overwritten unless --force is given (nothing is written when a
conflict is found). Text files are written as UTF-8 without BOM with LF line endings.
The script prints the created files, the "<!-- FILL" comments still to fill per file,
and the places that mention a skipped part (edit or remove those references).

Exit codes:
    0  scaffolded (or dry run finished)
    1  refused: files already exist in the target (use --force to overwrite)
    2  usage problem (bad argument, template folder missing)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

OPTIONAL_PARTS: dict[str, tuple[str, ...]] = {
    "legacy": ("docs/legacy-sources.md",),
    "design": ("docs/design-system.md", "docs/design-system-brief.md"),
    "flows": ("docs/process-flows.md",),
    "orchestration": ("docs/orchestration/",),
    "agents": (".claude/agents/",),
    "security": ("docs/security/",),
    "context": ("docs/context/",),
}
# text that marks a reference to a skipped part inside the remaining documents
PART_MARKERS: dict[str, tuple[str, ...]] = {
    "legacy": ("legacy-sources.md",),
    "design": ("design-system.md", "design-system-brief.md"),
    "flows": ("process-flows.md",),
    "orchestration": ("orchestration/",),
    "agents": (".claude/agents",),
    "security": ("threat-model.md",),
    "context": ("context/README.md",),
}
IGNORED_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
FILL_EXEMPT = ("docs/adr/_template.md",)  # stays a template in the target repository


def default_templates() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "templates"


def slugify(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name.strip())
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def parse_without(values: list[str]) -> set[str]:
    parts: set[str] = set()
    for v in values:
        for item in v.split(","):
            item = item.strip().lower()
            if not item:
                continue
            if item not in OPTIONAL_PARTS:
                raise ValueError(
                    f"unknown part '{item}' for --without (choose from {', '.join(OPTIONAL_PARTS)})"
                )
            parts.add(item)
    return parts


def skipped(rel: str, without: set[str]) -> bool:
    for part in without:
        for p in OPTIONAL_PARTS[part]:
            if (p.endswith("/") and rel.startswith(p)) or rel == p:
                return True
    return False


def substitute(text: str, values: dict[str, str]) -> str:
    return PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), text)


def read_text(path: Path) -> str | None:
    data = path.read_bytes()
    if b"\x00" in data[:4096]:
        return None
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None
    return text.replace("\r\n", "\n").replace("\r", "\n")


def plan(templates: Path, target: Path, values: dict[str, str], without: set[str]):
    """Return a list of (source, template_rel, dest_path, dest_rel)."""
    items = []
    for src in sorted(templates.rglob("*")):
        if not src.is_file() or src.name in IGNORED_NAMES:
            continue
        rel = src.relative_to(templates).as_posix()
        if skipped(rel, without):
            continue
        dest_rel = substitute(rel, values)
        items.append((src, rel, target / Path(dest_rel), dest_rel))
    return items


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Create a project-blueprint documentation structure from the skill templates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0 done, 1 refused (existing files, use --force), 2 usage problem.",
    )
    ap.add_argument("--target", required=True, help="repository folder to create or fill")
    ap.add_argument("--name", required=True, help='display name, e.g. "Order Desk"')
    ap.add_argument("--code", required=True, help="short uppercase code, e.g. ODK")
    ap.add_argument("--owner", required=True, help='product owner name, e.g. "Ana Ruiz"')
    ap.add_argument("--slug", help="kebab-case slug (default: derived from --name)")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--without", action="append", default=[], metavar="PARTS",
                    help="skip optional parts: " + ",".join(OPTIONAL_PARTS))
    ap.add_argument("--force", action="store_true", help="overwrite files that already exist")
    ap.add_argument("--dry-run", action="store_true", help="show what would be written, write nothing")
    ap.add_argument("--templates", help=argparse.SUPPRESS)  # testing: alternative template tree
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    def fail(msg: str) -> int:
        print(f"scaffold: {msg}", file=sys.stderr)
        return 2

    name = args.name.strip()
    owner = args.owner.strip()
    if not name or not owner:
        return fail("--name and --owner must not be empty")
    code = args.code.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9]{1,9}", code):
        return fail("--code must be 2-10 letters or digits starting with a letter, e.g. ODK")
    slug = (args.slug or slugify(name)).strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        return fail(f"--slug must be kebab-case (lowercase letters, digits, hyphens), got '{slug}'")
    date = args.date or _dt.date.today().isoformat()
    try:
        _dt.date.fromisoformat(date)
    except ValueError:
        return fail(f"--date must be YYYY-MM-DD, got '{date}'")
    try:
        without = parse_without(args.without)
    except ValueError as e:
        return fail(str(e))

    templates = Path(args.templates).expanduser().resolve() if args.templates else default_templates()
    if not templates.is_dir():
        return fail(f"template folder not found: {templates}")
    target = Path(args.target).expanduser().resolve()
    if target.exists() and not target.is_dir():
        return fail(f"target exists and is not a folder: {target}")

    values = {"PROJECT": name, "PROJECT_SLUG": slug, "CODE": code, "OWNER": owner, "DATE": date}
    items = plan(templates, target, values, without)
    if not items:
        return fail(f"no template files found in {templates}")

    conflicts = [dest_rel for _, _, dest, dest_rel in items if dest.exists()]
    if conflicts and not args.force:
        print(f"scaffold: refusing to overwrite {len(conflicts)} existing file(s) in {target}:", file=sys.stderr)
        for c in conflicts:
            print(f"  {c}", file=sys.stderr)
        print("scaffold: nothing was written. Use --force to overwrite.", file=sys.stderr)
        return 1

    created: list[str] = []
    fills: dict[str, int] = {}
    unknown: dict[str, set[str]] = {}
    texts: dict[str, str] = {}
    for src, rel, dest, dest_rel in items:
        text = read_text(src)
        if text is not None:
            out = substitute(text, values)
            left = {m for m in PLACEHOLDER_RE.findall(out)}
            if left:
                unknown[dest_rel] = left
            if dest_rel not in FILL_EXEMPT:
                n = out.count("<!-- FILL")
                if n:
                    fills[dest_rel] = n
            texts[dest_rel] = out
            data = out.encode("utf-8")
        else:
            data = src.read_bytes()
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as fh:
                fh.write(data)
        created.append(dest_rel + ("  (overwritten)" if dest_rel in conflicts else ""))

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {len(created)} file(s) in {target}")
    print(f"  project={name}  slug={slug}  code={code}  owner={owner}  date={date}")
    if without:
        print(f"  skipped parts: {', '.join(sorted(without))}")
    for c in created:
        print(f"  {c}")

    total = sum(fills.values())
    print(f"\nFILL comments left to fill: {total} in {len(fills)} file(s)")
    for f, n in sorted(fills.items()):
        print(f"  {n:4d}  {f}")

    if unknown:
        print("\nUnknown placeholders left (not one of PROJECT, PROJECT_SLUG, CODE, OWNER, DATE):")
        for f, names in sorted(unknown.items()):
            print(f"  {f}: {', '.join('{{' + x + '}}' for x in sorted(names))}")

    if without:
        refs = []
        for dest_rel, text in texts.items():
            for i, line in enumerate(text.split("\n"), 1):
                hit = sorted(p for p in without if any(mk in line for mk in PART_MARKERS[p]))
                if hit:
                    refs.append(f"  {dest_rel}:{i}  mentions skipped part(s): {', '.join(hit)}")
        if refs:
            print("\nReferences to skipped parts (edit or remove them):")
            print("\n".join(refs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
