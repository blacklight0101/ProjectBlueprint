#!/usr/bin/env python3
"""Deterministic consistency linter for a project-blueprint repository.

Usage:
    python check_docs.py <repo> [--json] [--decision-prefix DEC] [--strict]
                         [--without legacy,design,flows,orchestration,agents,security,context]
                         [--exclude GLOB ...]

Scans every Markdown file under <repo> (skipping .git, node_modules, bin, obj,
.vs, dist, build and any --exclude glob) and runs these checks:

  ids           every referenced id (RF-nnn, RNF-nnn, Q-nn, ADR-nnn, DEC-nn or the
                configured decision prefix, DEF-nn, G-nn, RFC-nnn, card ids P<n>-nn)
                is defined somewhere. A definition is a heading that starts with
                the id, a bold line that starts with the id, the first cell of a
                table row that starts with the id, an ADR or RFC file name, or a
                card heading "### P1-03 - Title". Ranges such as "RF-001..RF-099",
                "RF-010..019" or "Q-01..Q-17" are not references. Code fences and
                HTML comments are ignored, and so are ids inside inline code
                (`Refs: ADR-004` is an example, not a reference).
  links         relative Markdown links resolve (error); cited "docs/..." paths
                that name a file or folder resolve (warning), unless a task card's
                Do or Delivers line or a "Planned documents" table plans them.
  tables        every Markdown table has the same column count in every row.
  placeholders  leftover "{{" and "<!-- FILL" (docs/adr/_template.md is exempt,
                because it stays a template).
  adr-index     docs/adr/README.md lists every ADR file, lists no missing file, and
                each listed status matches the Status line of the ADR file.
  cards         task-card "Depends on" entries exist and form no cycle; card
                headings are unique.
  questions     rows of the open-question table (first cell Q-nn) have a valid
                Status: Open, Default applies, Answered (DEC-nn), Withdrawn.
  size          warnings when a living file outgrows its budget: CLAUDE.md over 150
                lines, AGENTS.md over 60 lines, handoff.md over 30 KB.

--without names the optional parts the project skipped at scaffold time (same names as
scaffold.py); links to those files and ids defined only there (DEF-nn for legacy; cards and
G-nn for orchestration) are then not reported.

Output: findings grouped by check with file:line, then a summary line.
With --json the same findings are printed as one JSON object.

Exit codes:
    0  no errors (and no warnings with --strict)
    1  errors found (or warnings with --strict)
    2  usage problem (repo folder missing, bad arguments)
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

SKIP_DIRS = {".git", "node_modules", "bin", "obj", ".vs", "dist", "build", ".idea", ".vscode"}
CHECK_ORDER = ["ids", "links", "tables", "placeholders", "adr-index", "cards", "questions", "size"]
# living files loaded into every session: (repo-relative path, limit, unit)
SIZE_BUDGETS = (("CLAUDE.md", 150, "lines"), ("AGENTS.md", 60, "lines"), ("handoff.md", 30 * 1024, "bytes"))
KNOWN_PLACEHOLDERS = ("PROJECT", "PROJECT_SLUG", "CODE", "OWNER", "DATE")
STATUS_WORDS = ("proposed", "accepted", "superseded", "amended", "deprecated", "rejected", "withdrawn")
Q_STATUS_OK = ("open", "default applies", "answered", "withdrawn")

# --------------------------------------------------------------------------------------------
# Findings


class Report:
    def __init__(self) -> None:
        self.findings: list[dict] = []

    def add(self, check: str, severity: str, file: str, line: int, message: str) -> None:
        self.findings.append(
            {"check": check, "severity": severity, "file": file, "line": line, "message": message}
        )

    def count(self, severity: str) -> int:
        return sum(1 for f in self.findings if f["severity"] == severity)


# --------------------------------------------------------------------------------------------
# Text preparation


FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")


def blank(text: str) -> str:
    """Replace every character except newlines with a space (keeps offsets and line numbers)."""
    return re.sub(r"[^\n]", " ", text)


def strip_fences(lines: list[str]) -> tuple[list[str], set[int]]:
    """Return lines with fenced code blocks blanked, plus the set of 0-based fenced line indexes."""
    out: list[str] = []
    fenced: set[int] = set()
    fence: str | None = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0] * len(m.group(1))
                fenced.add(i)
                out.append("")
                continue
            out.append(line)
        else:
            fenced.add(i)
            out.append("")
            if m and m.group(1).startswith(fence) and line.strip().strip(fence[0]) == "":
                fence = None
    return out, fenced


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", lambda m: blank(m.group(0)), text, flags=re.S)


def strip_inline_code(line: str) -> str:
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)


class Doc:
    def __init__(self, root: Path, path: Path) -> None:
        self.path = path
        self.rel = path.relative_to(root).as_posix()
        raw = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        self.raw_lines = raw.split("\n")
        no_fence, self.fenced = strip_fences(self.raw_lines)
        # prose: fences blanked and HTML comments blanked, line count preserved
        self.prose_lines = strip_comments("\n".join(no_fence)).split("\n")
        # prose without inline code (for links and tables-with-code heuristics)
        self.plain_lines = [strip_inline_code(x) for x in self.prose_lines]


# --------------------------------------------------------------------------------------------
# Ids


def id_kinds(prefix: str) -> list[tuple[str, str]]:
    p = re.escape(prefix)
    return [
        ("RNF", r"RNF-\d{3,4}"),
        ("RFC", r"RFC-\d{3}"),
        ("RF", r"RF-\d{3,4}"),
        ("Q", r"Q-\d{2,3}"),
        ("ADR", r"ADR-\d{3,4}"),
        ("DEC", p + r"-\d{2,3}[a-z]?"),
        ("DEF", r"DEF-\d{2,3}"),
        ("G", r"G-\d{2,3}"),
        ("CARD", r"P\d{1,2}-\d{2,3}"),
    ]


class IdScanner:
    def __init__(self, prefix: str) -> None:
        kinds = id_kinds(prefix)
        alt = "|".join(f"(?P<{k}>{r})" for k, r in kinds)
        lb = r"(?<![A-Za-z0-9_/.\\-])"
        la = r"(?![A-Za-z0-9_])"
        self.any_id = re.compile(lb + r"(?:" + alt + r")" + la)
        # a range: ID sep (ID | digits); both ends are skipped
        range_parts = []
        for k, r in kinds:
            head = r.split("-")[0]
            range_parts.append(
                rf"{r}\s*(?:\.\.\.?|\u2026|\u2013|\u2014|\bto\b|\bthrough\b)\s*(?:{head}-)?\d+[a-z]?"
            )
        self.range_re = re.compile(lb + r"(?:" + "|".join(range_parts) + r")" + la)
        self.start_id = re.compile(r"^(?:" + "|".join(r for _, r in kinds) + r")" + la)

    def refs(self, line: str):
        """Yield ids referenced on a line (ranges removed)."""
        cleaned = self.range_re.sub(lambda m: " " * len(m.group(0)), line)
        for m in self.any_id.finditer(cleaned):
            yield m.group(0)

    def leading_id(self, text: str) -> str | None:
        """Id at the very start of text (after markup), unless it opens a range."""
        t = text.strip()
        t = re.sub(r"^[\s*_`\[~]+", "", t)
        m = self.start_id.match(t)
        if not m:
            return None
        after = t[m.end():m.end() + 3]
        if after.startswith("..") or after[:1] in ("\u2026", "\u2013", "\u2014"):
            return None
        return m.group(0)


HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
BOLD_START_RE = re.compile(r"^\s*(?:[-*+]\s+)?\*\*(.+)")


def split_row(line: str) -> list[str]:
    """Split a table row into cells on unescaped pipes (GFM rules: pipes in code spans split too)."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells = re.split(r"(?<!\\)\|", s)
    return [c.strip() for c in cells]


SEP_CELL_RE = re.compile(r"^:?-{1,}:?$")


def is_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(SEP_CELL_RE.match(c.replace(" ", "")) for c in cells)


def table_blocks(lines: list[str]):
    """Yield (start_index, [lines]) for each block of consecutive pipe lines that is a GFM table."""
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith("|"):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            block = lines[i:j]
            if len(block) >= 2 and is_separator(block[1]):
                yield i, block
            i = j
        else:
            i += 1


CROSSREF_HEADING_RE = re.compile(r"traceab|coverage|cross.?ref|mapping", re.I)


def is_crossref_table(lines: list[str], start: int) -> bool:
    """True when the nearest heading above the table names a traceability, coverage or mapping table."""
    for k in range(start - 1, -1, -1):
        h = HEADING_RE.match(lines[k])
        if h:
            return bool(CROSSREF_HEADING_RE.search(h.group(2)))
    return False


def only_ids(cells: list[str], scanner: "IdScanner") -> bool:
    """True when every non-empty cell holds nothing but ids and separators (a row that cites, not defines)."""
    seen = False
    for c in cells:
        rest = c
        for ref in scanner.refs(c):
            rest = rest.replace(ref, " ")
        rest = re.sub(r"[\s,;/.\-*`()]|and|n/a|none", "", rest, flags=re.I)
        if c.strip():
            seen = True
        if rest:
            return False
    return seen


def collect_definitions(docs: list[Doc], scanner: IdScanner, report: Report, root: Path) -> set[str]:
    defs: set[str] = set()
    for d in docs:
        for i, line in enumerate(d.prose_lines):
            h = HEADING_RE.match(line)
            if h:
                lid = scanner.leading_id(h.group(2))
                if lid:
                    defs.add(lid)
                continue
            b = BOLD_START_RE.match(line)
            if b:
                lid = scanner.leading_id(b.group(1))
                if lid:
                    defs.add(lid)
        for start, block in table_blocks(d.prose_lines):
            if is_crossref_table(d.prose_lines, start):
                continue  # a traceability or coverage table cites ids; it does not define them
            for row in block[2:]:
                cells = split_row(row)
                if cells:
                    lid = scanner.leading_id(cells[0])
                    if lid and not only_ids(cells[1:], scanner):
                        defs.add(lid)
    # ADR and RFC file names
    for sub, pat in (("docs/adr", r"^(ADR-\d{3,4})-"), ("docs/rfc", r"^(RFC-\d{3})-")):
        folder = root / sub
        if folder.is_dir():
            for f in folder.iterdir():
                m = re.match(pat, f.name)
                if m and f.suffix.lower() == ".md":
                    defs.add(m.group(1))
    return defs


OPTIONAL_PARTS: dict[str, tuple[str, ...]] = {
    "legacy": ("docs/legacy-sources.md",),
    "design": ("docs/design-system.md", "docs/design-system-brief.md"),
    "flows": ("docs/process-flows.md",),
    "orchestration": ("docs/orchestration/",),
    "agents": (".claude/agents/",),
    "security": ("docs/security/",),
    "context": ("docs/context/",),
}
# id kinds that are defined only inside an optional part
PART_ID_KINDS: dict[str, tuple[str, ...]] = {"legacy": ("DEF",), "orchestration": ("CARD", "G")}


def in_absent_part(rel: str, without: set[str]) -> bool:
    rel = re.sub(r"^(?:\./)+", "", rel.replace("\\", "/"))
    for part in without:
        for p in OPTIONAL_PARTS[part]:
            if rel == p.rstrip("/") or (p.endswith("/") and rel.startswith(p)):
                return True
    return False


def check_ids(docs: list[Doc], scanner: IdScanner, defs: set[str], report: Report,
              without: set[str] = frozenset()) -> None:
    skip_kinds = {k for part in without for k in PART_ID_KINDS.get(part, ())}
    kind_res = {k: re.compile(r) for k, r in id_kinds("X") if k in skip_kinds}
    for d in docs:
        seen_on_line: set[tuple[int, str]] = set()
        # ids inside inline code are examples or literals (`Refs: ADR-004`), not references
        for i, line in enumerate(d.plain_lines):
            for ref in scanner.refs(line):
                if ref in defs or (i, ref) in seen_on_line:
                    continue
                if any(rx.fullmatch(ref) for rx in kind_res.values()):
                    continue  # defined in an optional part that this project does not have
                seen_on_line.add((i, ref))
                report.add("ids", "error", d.rel, i + 1, f"{ref} is referenced but never defined")


# --------------------------------------------------------------------------------------------
# Links and cited paths


LINK_RE = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+[\"'(][^)]*)?\)")
REFDEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)")
CITED_RE = re.compile(r"(?<![\w./\\-])((?:\.\./)*docs/[\w./-]*[\w/])")


def is_external(target: str) -> bool:
    t = target.lower()
    return (
        t.startswith("#")
        or "://" in t
        or t.startswith(("mailto:", "tel:", "data:", "javascript:"))
        or re.match(r"^[a-z]:[\\/]", t) is not None
    )


def check_links(docs: list[Doc], root: Path, report: Report, without: set[str] = frozenset()) -> None:
    for d in docs:
        for i, line in enumerate(d.plain_lines):
            targets = [m.group(1) for m in LINK_RE.finditer(line)]
            m = REFDEF_RE.match(line)
            if m:
                targets.append(m.group(1))
            for target in targets:
                t = target.strip("<>").strip()
                if not t or is_external(t):
                    continue
                t = unquote(t.split("#", 1)[0].split("?", 1)[0])
                if not t:
                    continue
                base = root if t.startswith("/") else d.path.parent
                p = (base / t.lstrip("/")).resolve()
                if not p.exists():
                    try:
                        rel_target = p.relative_to(root).as_posix()
                    except ValueError:
                        rel_target = ""
                    if rel_target and in_absent_part(rel_target, without):
                        continue
                    report.add("links", "error", d.rel, i + 1, f"link target not found: {target}")
    # cited docs/ paths: a path that a task card delivers is planned, not missing
    planned = planned_paths(docs)
    missing: dict[str, list[tuple[str, int]]] = {}
    for d in docs:
        for i, line in enumerate(d.prose_lines):
            line = LINK_RE.sub(lambda lm: " " * len(lm.group(0)), line)  # links are checked above
            for m in CITED_RE.finditer(line):
                cited = m.group(1).rstrip(".")
                name = cited.rstrip("/").rsplit("/", 1)[-1]
                if ".." in cited.replace("../", ""):
                    continue  # a range such as docs/adr/ADR-001..035
                if not (cited.endswith("/") or re.search(r"\.[A-Za-z0-9]{1,5}$", name)):
                    continue  # probably a partial path (spaces) or a prefix; not checkable
                # a cited path may be relative to the repository root or to the citing file
                if (root / cited).exists() or (d.path.parent / cited).exists():
                    continue
                if cited.rstrip("/") in planned or in_absent_part(cited, without):
                    continue
                missing.setdefault(cited, []).append((d.rel, i + 1))
    for cited, where in sorted(missing.items()):
        f, ln = where[0]
        more = f" (cited {len(where)} times, first here)" if len(where) > 1 else ""
        report.add("links", "warning", f, ln,
                   f"cited path does not exist and no task card delivers it: {cited}{more}")


def planned_table_path(d: "Doc", row: str) -> str | None:
    """Root-relative path named in the first cell of a 'Planned documents' table row, or None."""
    cells = split_row(row)
    if not cells:
        return None
    cell = cells[0].strip()
    m = re.search(r"\]\(\s*<?([^)>\s]+)>?", cell)  # [name](path) -> path
    target = m.group(1) if m else cell.strip("`* ")
    target = target.strip("`").split("#", 1)[0].strip()
    if not target or " " in target or not re.search(r"[\w-]\.[A-Za-z0-9]{1,5}/?$|/$", target):
        return None
    if target.startswith("docs/"):
        return target.rstrip("/")
    base = os.path.dirname(d.rel)
    return os.path.normpath(os.path.join(base, target)).replace("\\", "/").rstrip("/")


def planned_paths(docs: list["Doc"]) -> set[str]:
    """docs/ paths named on a card's Do or Delivers line, in a sentence saying a card creates them, or in the
    first column of a table under a heading that starts with 'Planned documents' (docs/README.md)."""
    planned: set[str] = set()
    for d in docs:
        in_card = False
        in_planned = False
        for line in d.prose_lines:
            h = HEADING_RE.match(line)
            if h:
                in_planned = h.group(2).strip().lower().startswith("planned documents")
            if in_planned and line.strip().startswith("|") and not re.match(r"^\s*\|[\s:|-]+\|?\s*$", line):
                p = planned_table_path(d, line)
                if p:
                    planned.add(p)
            if CARD_HEAD_RE.match(line):
                in_card = True
            elif h:
                in_card = False
            delivers = in_card and re.search(r"(?:^|[\s|*_-])(?:Do|Delivers)(?:\*\*|__)?\s*(?::|\||\*\*)", line)
            created = re.search(r"(created|written|delivered|produced) by\s+P\d{1,2}-\d{2}", line)
            if delivers or created:
                for m in CITED_RE.finditer(line):
                    planned.add(m.group(1).rstrip(".").rstrip("/"))
    return planned


# --------------------------------------------------------------------------------------------
# Tables


def check_tables(docs: list[Doc], report: Report) -> None:
    for d in docs:
        for start, block in table_blocks(d.prose_lines):
            width = len(split_row(block[0]))
            for k, row in enumerate(block[1:], start=1):
                n = len(split_row(row))
                if n != width:
                    hint = ""
                    code_pipes = sum(m.group(2).count("|") for m in INLINE_CODE_RE.finditer(row))
                    if code_pipes:
                        hint = " (a '|' inside inline code also splits cells; escape it as \\|)"
                    report.add(
                        "tables", "error", d.rel, start + k + 1,
                        f"row has {n} columns, header has {width}{hint}",
                    )


# --------------------------------------------------------------------------------------------
# Placeholders


PLACEHOLDER_IN_CODE_RE = re.compile(r"\{\{(?:" + "|".join(KNOWN_PLACEHOLDERS) + r")\}\}")


def is_template_file(rel: str) -> bool:
    return rel.endswith("/_template.md") or rel == "_template.md"


def check_placeholders(docs: list[Doc], report: Report) -> None:
    for d in docs:
        if is_template_file(d.rel):
            continue
        no_comments = strip_comments("\n".join(d.raw_lines)).split("\n")
        for i, raw in enumerate(d.raw_lines):
            if "<!-- FILL" in raw:
                n = raw.count("<!-- FILL")
                report.add("placeholders", "error", d.rel, i + 1,
                           "unfilled FILL comment" + (f" ({n} on this line)" if n > 1 else ""))
            text = no_comments[i]
            if i in d.fenced:
                if PLACEHOLDER_IN_CODE_RE.search(text):
                    report.add("placeholders", "error", d.rel, i + 1,
                               f"template placeholder left in code: {PLACEHOLDER_IN_CODE_RE.search(text).group(0)}")
            else:
                prose = strip_inline_code(text)
                m = re.search(r"\{\{[^}\n]*\}?\}?", prose)
                if m:
                    report.add("placeholders", "error", d.rel, i + 1, f"template placeholder left: {m.group(0)}")
                else:
                    m2 = PLACEHOLDER_IN_CODE_RE.search(text)
                    if m2:
                        report.add("placeholders", "error", d.rel, i + 1,
                                   f"template placeholder left in code: {m2.group(0)}")


# --------------------------------------------------------------------------------------------
# ADR index


STATUS_LINE_RE = re.compile(r"^\s*(?:[-*]\s+)?\**\s*Status\s*\**\s*:?\s*\**\s*:?\s*(.+)$", re.I)


def adr_file_status(path: Path) -> tuple[str | None, int]:
    lines = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n").split("\n")
    for i, line in enumerate(lines):
        # table form: | **Status** | Accepted |
        if line.strip().startswith("|"):
            cells = split_row(line)
            if len(cells) >= 2 and re.sub(r"[*_`]", "", cells[0]).strip().lower() == "status":
                return cells[1].strip(), i + 1
            continue
        m = STATUS_LINE_RE.match(line)
        if m and m.group(1).strip():
            return m.group(1).strip(), i + 1
        # heading form: ## Status \n\n Accepted
        h = HEADING_RE.match(line)
        if h and h.group(2).strip().lower() == "status":
            for j in range(i + 1, min(i + 6, len(lines))):
                if lines[j].strip():
                    return lines[j].strip(), j + 1
    return None, 0


def normalize_status(text: str) -> tuple[str, str | None]:
    t = re.sub(r"[*_`\[\]]", "", text).strip().lower()
    word = next((w for w in STATUS_WORDS if t.startswith(w)), t.split(" ")[0] if t else "")
    target = None
    if word == "superseded":
        m = re.search(r"adr-\d{3,4}", t)
        target = m.group(0).upper() if m else None
    return word, target


def check_adr_index(root: Path, report: Report) -> None:
    adr_dir = root / "docs" / "adr"
    if not adr_dir.is_dir():
        return
    files = {}
    for f in sorted(adr_dir.iterdir()):
        m = re.match(r"^(ADR-\d{3,4})-.+\.md$", f.name)
        if m:
            if m.group(1) in files:
                report.add("adr-index", "error", f"docs/adr/{f.name}", 1,
                           f"{m.group(1)} is used by more than one file ({files[m.group(1)].name})")
            files[m.group(1)] = f
    index = adr_dir / "README.md"
    rel_index = "docs/adr/README.md"
    if not index.exists():
        if files:
            report.add("adr-index", "error", rel_index, 1, "ADR index docs/adr/README.md is missing")
        return
    doc = Doc(root, index)
    listed: dict[str, tuple[int, str | None, str | None]] = {}
    for start, block in table_blocks(doc.prose_lines):
        header = [re.sub(r"[*_`]", "", c).strip().lower() for c in split_row(block[0])]
        status_col = next((k for k, h in enumerate(header) if h.startswith("status")), None)
        for k, row in enumerate(block[2:], start=2):
            cells = split_row(row)
            if not cells:
                continue
            m = re.match(r"^[\s*_`\[]*(ADR-\d{3,4})(?![0-9])", cells[0])
            if not m:
                continue
            link = re.search(r"\]\(([^)]+)\)", row)
            status = cells[status_col] if status_col is not None and status_col < len(cells) else None
            listed[m.group(1)] = (start + k + 1, status, link.group(1) if link else None)
    for adr, f in files.items():
        if adr not in listed:
            report.add("adr-index", "error", rel_index, 1, f"{f.name} is not listed in the ADR index")
            continue
        line, status, link = listed[adr]
        if link and unquote(link.split("#")[0]).lstrip("./") != f.name:
            report.add("adr-index", "error", rel_index, line, f"{adr} links to {link}, file is {f.name}")
        file_status, _ = adr_file_status(f)
        if status is None:
            report.add("adr-index", "warning", rel_index, line, f"{adr}: the index has no Status column")
            continue
        if file_status is None:
            report.add("adr-index", "error", f"docs/adr/{f.name}", 1, f"{adr} has no Status line")
            continue
        if normalize_status(status) != normalize_status(file_status):
            report.add(
                "adr-index", "error", rel_index, line,
                f"{adr} status in index '{status}' does not match the file '{file_status}'",
            )
    for adr, (line, _, _) in listed.items():
        if adr not in files:
            report.add("adr-index", "error", rel_index, line, f"{adr} is listed but no docs/adr/{adr}-*.md file exists")


# --------------------------------------------------------------------------------------------
# Task cards


CARD_HEAD_RE = re.compile(r"^\s{0,3}(#{2,4})\s+[*`]*(P\d{1,2}-\d{2,3})(?![0-9])")
DEPENDS_RE = re.compile(r"Depends\s+on(?:\*\*|__)?\s*:?\s*(?:\*\*|__)?\s*:?\s*(?P<rest>.*)", re.I)
CARD_ID_RE = re.compile(r"(?<![A-Za-z0-9_-])P\d{1,2}-\d{2,3}(?![0-9])")
CARD_RANGE_RE = re.compile(r"(P\d{1,2})-(\d{2,3})\s*(?:\.\.|\u2026|\u2013)\s*(?:(P\d{1,2})-)?(\d{2,3})")


def expand_deps(text: str) -> list[str]:
    ids: list[str] = []

    def repl(m: re.Match) -> str:
        phase, a, phase2, b = m.group(1), int(m.group(2)), m.group(3) or m.group(1), int(m.group(4))
        width = len(m.group(2))
        if phase2 == phase and a <= b and b - a < 100:
            ids.extend(f"{phase}-{n:0{width}d}" for n in range(a, b + 1))
        else:
            ids.extend([f"{phase}-{m.group(2)}", f"{phase2}-{m.group(4)}"])
        return " "

    rest = CARD_RANGE_RE.sub(repl, text)
    ids.extend(CARD_ID_RE.findall(rest))
    return ids


def check_cards(docs: list[Doc], report: Report) -> None:
    cards: dict[str, tuple[str, int]] = {}
    deps: dict[str, list[tuple[str, str, int]]] = {}
    for d in docs:
        current: str | None = None
        level = 0
        for i, line in enumerate(d.prose_lines):
            h = CARD_HEAD_RE.match(line)
            if h:
                cid = h.group(2)
                if cid in cards:
                    f, ln = cards[cid]
                    report.add("cards", "error", d.rel, i + 1, f"card {cid} is defined twice (also {f}:{ln})")
                else:
                    cards[cid] = (d.rel, i + 1)
                current, level = cid, len(h.group(1))
                deps.setdefault(cid, [])
                continue
            hh = HEADING_RE.match(line)
            if hh and current and len(hh.group(1)) <= level:
                current = None
                continue
            if current:
                m = DEPENDS_RE.search(line)
                if m:
                    rest = m.group("rest").lstrip("| ").strip()
                    rest = re.split(r"\s\u00b7\s|\*\*|\s\|\s|\|$", rest)[0]
                    for dep in expand_deps(rest):
                        deps[current].append((dep, d.rel, i + 1))
    for cid, lst in deps.items():
        for dep, f, ln in lst:
            if dep not in cards:
                report.add("cards", "error", f, ln, f"{cid} depends on {dep}, which is not a card")
            elif dep == cid:
                report.add("cards", "error", f, ln, f"{cid} depends on itself")
    # cycles (iterative DFS, report each cycle once)
    graph = {c: sorted({d for d, _, _ in lst if d in cards and d != c}) for c, lst in deps.items()}
    color: dict[str, int] = {}
    reported: set[frozenset] = set()
    for startnode in sorted(graph):
        if color.get(startnode):
            continue
        stack = [(startnode, iter(graph[startnode]))]
        path = [startnode]
        color[startnode] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = 2
                stack.pop()
                path.pop()
                continue
            c = color.get(nxt, 0)
            if c == 0:
                color[nxt] = 1
                stack.append((nxt, iter(graph.get(nxt, []))))
                path.append(nxt)
            elif c == 1:
                cyc = path[path.index(nxt):] + [nxt]
                key = frozenset(cyc)
                if key not in reported:
                    reported.add(key)
                    f, ln = cards[nxt]
                    report.add("cards", "error", f, ln, "dependency cycle: " + " -> ".join(cyc))


# --------------------------------------------------------------------------------------------
# Open questions


def check_questions(docs: list[Doc], prefix: str, report: Report) -> None:
    dec_re = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(prefix) + r"-\d{2,3}[a-z]?")
    for d in docs:
        for start, block in table_blocks(d.prose_lines):
            header = [re.sub(r"[*_`]", "", c).strip().lower() for c in split_row(block[0])]
            rows = [(k, split_row(r)) for k, r in enumerate(block[2:], start=2)]
            q_rows = [(k, c) for k, c in rows if c and re.match(r"^[*_`\[]*Q-\d{2,3}(?![0-9])", c[0])]
            if not q_rows:
                continue
            status_col = next((k for k, h in enumerate(header) if h.startswith("status")), None)
            if status_col is None:
                continue  # a table that mentions questions but is not the register
            for k, cells in q_rows:
                ln = start + k + 1
                qid = re.search(r"Q-\d{2,3}", cells[0]).group(0)
                status = cells[status_col] if status_col < len(cells) else ""
                s = re.sub(r"[*_`]", "", status).strip()
                low = s.lower()
                if not s:
                    report.add("questions", "error", d.rel, ln, f"{qid} has an empty Status")
                elif low.startswith("answered"):
                    if not dec_re.search(s):
                        report.add("questions", "error", d.rel, ln,
                                   f"{qid} is Answered but names no decision id ({prefix}-nn)")
                elif low.startswith(Q_STATUS_OK):
                    pass
                elif low.startswith("partly answered"):
                    report.add("questions", "warning", d.rel, ln,
                               f"{qid} status 'Partly answered' is not in the scheme; use Open or "
                               f"Default applies with a note, or split the question")
                else:
                    report.add("questions", "error", d.rel, ln,
                               f"{qid} status '{s[:40]}' is not one of Open, Default applies, "
                               f"Answered ({prefix}-nn), Withdrawn")


# --------------------------------------------------------------------------------------------
# Size budgets


def check_sizes(root: Path, report: Report) -> None:
    for rel, limit, unit in SIZE_BUDGETS:
        p = root / rel
        if not p.is_file():
            continue
        if unit == "lines":
            size = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
        else:
            size = p.stat().st_size
        if size > limit:
            report.add("size", "warning", rel, 1,
                       f"{size} {unit}, budget {limit}: move detail to the document that owns it "
                       f"(handoff.md: older resume entries to docs/journal/)")


# --------------------------------------------------------------------------------------------
# Driver


def find_docs(root: Path, excludes: list[str]) -> list[Path]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(x for x in dirnames if x not in SKIP_DIRS)
        for name in sorted(filenames):
            if not name.lower().endswith(".md"):
                continue
            p = Path(dirpath) / name
            rel = p.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, g) for g in excludes):
                continue
            out.append(p)
    return out


def run(root: Path, prefix: str, excludes: list[str],
        without: set[str] = frozenset()) -> tuple[Report, int]:
    report = Report()
    paths = find_docs(root, excludes)
    docs = [Doc(root, p) for p in paths]
    scanner = IdScanner(prefix)
    defs = collect_definitions(docs, scanner, report, root)
    check_ids(docs, scanner, defs, report, without)
    check_links(docs, root, report, without)
    check_tables(docs, report)
    check_placeholders(docs, report)
    check_adr_index(root, report)
    check_cards(docs, report)
    check_questions(docs, prefix, report)
    check_sizes(root, report)
    return report, len(docs)


def print_text(report: Report, root: Path, nfiles: int) -> None:
    out = sys.stdout
    out.write(f"check_docs: {root} ({nfiles} Markdown files)\n")
    for check in CHECK_ORDER:
        items = [f for f in report.findings if f["check"] == check]
        errs = sum(1 for f in items if f["severity"] == "error")
        warns = len(items) - errs
        out.write(f"\n[{check}] {errs} error(s), {warns} warning(s)\n")
        for f in sorted(items, key=lambda x: (x["severity"] != "error", x["file"], x["line"])):
            tag = "ERROR" if f["severity"] == "error" else "WARN "
            out.write(f"  {tag} {f['file']}:{f['line']}  {f['message']}\n")
    out.write(f"\nSummary: {report.count('error')} error(s), {report.count('warning')} warning(s)\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Consistency linter for a project-blueprint documentation repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0 clean, 1 errors (or warnings with --strict), 2 usage problem.",
    )
    ap.add_argument("repo", help="repository root (the folder that holds README.md and docs/)")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--decision-prefix", default="DEC", metavar="PREFIX",
                    help="prefix of owner decision ids (default DEC, i.e. DEC-nn)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--without", action="append", default=[], metavar="PARTS",
                    help="optional parts the project does not have (as given to scaffold.py): "
                         "legacy,design,flows,orchestration,agents,security,context; links to them and ids defined only "
                         "in them are not reported")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="skip Markdown files whose repo-relative path matches GLOB (repeatable)")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    root = Path(args.repo).expanduser().resolve()
    if not root.is_dir():
        print(f"check_docs: not a folder: {root}", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,9}", args.decision_prefix):
        print("check_docs: --decision-prefix must be uppercase letters/digits, e.g. DEC", file=sys.stderr)
        return 2
    without: set[str] = set()
    for v in args.without:
        for item in (x.strip().lower() for x in v.split(",")):
            if not item:
                continue
            if item not in OPTIONAL_PARTS:
                print(f"check_docs: unknown part '{item}' for --without "
                      f"(choose from {', '.join(OPTIONAL_PARTS)})", file=sys.stderr)
                return 2
            without.add(item)
    report, nfiles = run(root, args.decision_prefix, args.exclude, without)
    if args.json:
        json.dump(
            {
                "repo": str(root),
                "files": nfiles,
                "errors": report.count("error"),
                "warnings": report.count("warning"),
                "findings": report.findings,
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print_text(report, root, nfiles)
    if report.count("error") or (args.strict and report.count("warning")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
