#!/usr/bin/env python3
"""Print the Mermaid diagrams of a process-flows Markdown file to a PDF with headless Microsoft Edge.

Usage:
    python flows_pdf.py <process-flows.md> --out <file.pdf> [--title "..."] [--subtitle "..."]
                        [--date YYYY-MM-DD] [--html-only] [--keep-html]
                        [--edge <path to msedge.exe>] [--mermaid-js <url or file>]

Each diagram section is a heading (## to ####), a ```mermaid fence and an optional caption
paragraph right after the fence (a leading "Caption:" is dropped). The PDF has a portrait A4
cover page (title, subtitle, date, table of contents) and one landscape A4 page per diagram
(heading, diagram scaled to fit, caption, footer).

Steps:
  1. build a print HTML page (Mermaid 11.4.1 from cdn.jsdelivr.net, run after document.fonts.ready,
     one mermaid.render call per diagram with its own id; it sets data-rendered on <body> to the
     number of rendered SVGs and data-failed to the diagrams that did not parse);
  2. run Edge with --dump-dom and check that data-rendered equals the diagram count, that no
     "Syntax error in text" appears and that every SVG id is unique;
  3. print with --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=30000
     --print-to-pdf, using a temporary --user-data-dir;
  4. count the pages ("/Type /Page" objects) and compare with diagrams + 1.

--html-only writes the HTML next to --out (same name, .html) and stops; --keep-html keeps it after
printing. Mermaid is loaded from the CDN, so the machine needs network access unless --mermaid-js
points to a local mermaid.min.js.

Exit codes:
    0  PDF written and page count matches (or HTML written with --html-only)
    1  no diagram sections found in the Markdown file
    2  usage problem (input missing, Edge not found, bad arguments)
    3  render check failed (Mermaid syntax error, missing diagrams, Edge failed)
    4  PDF missing or its page count differs from diagrams + 1
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*#*\s*$")
FENCE_OPEN_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*mermaid\s*$", re.I)


# --------------------------------------------------------------------------------------------
# Markdown parsing


def parse_flows(text: str) -> tuple[str | None, list[tuple[str, str, str]]]:
    """Return (h1 title, [(section title, mermaid code, caption)])."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # HTML comments (such as FILL guidance) are blanked, keeping line breaks
    text = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    lines = text.split("\n")
    h1 = None
    heading = None
    used: dict[str, int] = {}
    sections: list[tuple[str, str, str]] = []
    i = 0
    n = len(lines)
    other_fence = None
    while i < n:
        line = lines[i]
        if other_fence:
            if line.strip().startswith(other_fence):
                other_fence = None
            i += 1
            continue
        m = FENCE_OPEN_RE.match(line)
        if m:
            fence = m.group(1)
            code: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith(fence):
                code.append(lines[i])
                i += 1
            i += 1  # closing fence
            # caption: the first paragraph after the fence, unless a heading or fence comes first
            j = i
            while j < n and not lines[j].strip():
                j += 1
            cap: list[str] = []
            while j < n and lines[j].strip() and not HEADING_RE.match(lines[j]) \
                    and not lines[j].lstrip().startswith(("```", "~~~", "|")):
                cap.append(lines[j].strip())
                j += 1
            if cap:
                i = j
            caption = re.sub(r"^\**Caption\**\s*:\s*\**\s*", "", " ".join(cap), flags=re.I)
            caption = caption[:1].upper() + caption[1:]
            title = heading or f"Diagram {len(sections) + 1}"
            used[title] = used.get(title, 0) + 1
            if used[title] > 1:
                title = f"{title} ({used[title]})"
            sections.append((title, "\n".join(code).strip("\n"), caption))
            continue
        if re.match(r"^\s{0,3}(`{3,}|~{3,})", line):
            other_fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", line).group(1)
            i += 1
            continue
        h = HEADING_RE.match(line)
        if h:
            if len(h.group(1)) == 1 and h1 is None:
                h1 = h.group(2).strip()
            else:
                heading = h.group(2).strip()
        i += 1
    return h1, sections


def inline(text: str) -> str:
    """Minimal Markdown inline rendering: links to text, code spans, bold, italics."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", text)
    return text


# --------------------------------------------------------------------------------------------
# HTML


def build_html(title: str, subtitle: str, date_text: str, source_name: str,
               sections: list[tuple[str, str, str]], mermaid_src: str) -> str:
    total = len(sections)
    pages = []
    for i, (heading, code, caption) in enumerate(sections, 1):
        cap = f'\n  <p class="cap">{inline(caption)}</p>' if caption else ""
        pages.append(f"""
<section class="page wide">
  <header class="ph">
    <span class="no">{i:02d} / {total:02d}</span>
    <h2>{inline(heading)}</h2>
  </header>
  <div class="canvas"><pre class="mermaid">{html.escape(code)}</pre></div>{cap}
  <footer class="pf">{html.escape(title)} &middot; source <code>{html.escape(source_name)}</code> &middot; {html.escape(date_text)}</footer>
</section>""")
    toc = "".join(f"<li><span>{i:02d}</span>{inline(t)}</li>" for i, (t, _, _) in enumerate(sections, 1))
    toc_cls = ' class="two"' if total > 14 else ""
    initial = html.escape((re.sub(r"[^A-Za-z0-9]", "", title)[:1] or "F").upper())
    sub = f"\n  <p class=\"lead\">{inline(subtitle)}</p>" if subtitle else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  @page {{ size: A4 landscape; margin: 0; }}
  @page cover {{ size: A4 portrait; margin: 0; }}
  @page wide {{ size: A4 landscape; margin: 0; }}
  :root {{ --ink:#16191d; --soft:#3c434a; --muted:#5d656d; --rule:#dde1e5; --brand:#2f5d8a; --tint:#e6eef6; --bg:#ffffff; }}
  * {{ box-sizing: border-box; }}
  html, body {{ page: wide; margin: 0; background: var(--bg); color: var(--ink); font-family: "IBM Plex Sans", "Segoe UI", sans-serif; }}
  code {{ font-family: "IBM Plex Mono", Consolas, monospace; font-size: .92em; }}
  .cover {{ page: cover; width: 210mm; height: 296mm; overflow: hidden; padding: 28mm 22mm; display: flex; flex-direction: column; gap: 9mm; page-break-after: always; }}
  .tile {{ width: 16mm; height: 16mm; background: var(--brand); color: #fff; display: grid; place-items: center; font-weight: 600; font-size: 9mm; border-radius: 2mm; }}
  .eyebrow {{ font-family: "IBM Plex Mono", monospace; font-size: 9pt; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 0; }}
  .cover h1 {{ font-size: 26pt; line-height: 1.15; margin: 0; font-weight: 600; }}
  .cover .lead {{ font-size: 11.5pt; line-height: 1.55; color: var(--soft); max-width: 160mm; margin: 0; }}
  .cover ol {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 2.2mm; font-size: 11pt; }}
  .cover ol.two {{ grid-template-columns: 1fr 1fr; column-gap: 8mm; font-size: 9.5pt; }}
  .cover li {{ display: flex; gap: 4mm; border-bottom: 1px solid var(--rule); padding-bottom: 2mm; }}
  .cover li span {{ font-family: "IBM Plex Mono", monospace; color: var(--brand); min-width: 8mm; }}
  .page.wide {{ page: wide; width: 297mm; height: 209mm; overflow: hidden; padding: 12mm 14mm 10mm; display: flex; flex-direction: column; gap: 5mm; page-break-after: always; }}
  section.page.wide:last-of-type {{ page-break-after: auto; }}
  .ph {{ display: flex; align-items: baseline; gap: 5mm; border-bottom: 2px solid var(--brand); padding-bottom: 3mm; }}
  .ph h2 {{ font-size: 16pt; margin: 0; font-weight: 600; flex: 1; }}
  .no {{ font-family: "IBM Plex Mono", monospace; font-size: 9pt; color: var(--muted); }}
  .canvas {{ flex: 1; min-height: 0; position: relative; overflow: hidden; }}
  .canvas pre.mermaid {{ margin: 0; position: absolute; inset: 0; }}
  .canvas svg {{ width: 100% !important; height: 100% !important; max-width: none !important; }}
  .cap {{ font-size: 9.5pt; line-height: 1.5; color: var(--soft); margin: 0; }}
  .pf {{ font-size: 7.5pt; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 2mm; }}
</style></head><body>
<section class="cover">
  <div class="tile">{initial}</div>
  <p class="eyebrow">Process flows &middot; {html.escape(date_text)}</p>
  <h1>{inline(title)}</h1>{sub}
  <ol{toc_cls}>{toc}</ol>
  <p class="eyebrow">Source of truth: {html.escape(source_name)}</p>
</section>
{''.join(pages)}
<script src="{html.escape(mermaid_src)}"></script>
<script>
  // deterministicIds: under --virtual-time-budget Date.now() is frozen, so the default time-based ids
  // repeat and every diagram is laid out into the first SVG.
  mermaid.initialize({{ startOnLoad: false, securityLevel: 'strict', theme: 'base', deterministicIds: true, suppressErrorRendering: true,
    flowchart: {{ useMaxWidth: true }}, sequence: {{ useMaxWidth: true }}, state: {{ useMaxWidth: true }},
    themeVariables: {{ fontFamily: 'IBM Plex Sans, Segoe UI, sans-serif', fontSize: '14px',
      primaryColor: '#e6eef6', primaryTextColor: '#16191d', primaryBorderColor: '#2f5d8a', lineColor: '#3c434a',
      secondaryColor: '#eef3e6', tertiaryColor: '#f6f7f8', clusterBkg: '#f6f7f8', clusterBorder: '#dde1e5',
      actorBkg: '#e6eef6', actorBorder: '#2f5d8a', signalColor: '#3c434a', noteBkgColor: '#fdf3dc', noteBorderColor: '#a0660a' }} }});
  // Each diagram is rendered with its own id (flow-1, flow-2, ...); a failing diagram is recorded in
  // data-failed and replaced by a visible "Syntax error in text" note, the others still render.
  async function renderAll() {{
    const pres = [...document.querySelectorAll('pre.mermaid')];
    const failed = [];
    for (let i = 0; i < pres.length; i++) {{
      const code = pres[i].textContent;
      try {{
        const out = await mermaid.render('flow-' + (i + 1), code);
        pres[i].innerHTML = out.svg;
        pres[i].setAttribute('data-processed', 'true');
      }} catch (e) {{
        const msg = String(e && e.message ? e.message : e);
        failed.push((i + 1) + ': ' + msg.split(String.fromCharCode(10)).slice(0, 4).join(' / '));
        pres[i].textContent = 'Syntax error ' + 'in text: ' + msg;
      }}
    }}
    const rendered = pres.filter(p => p.getAttribute('data-processed') === 'true' && p.querySelector('svg')).length;
    document.body.setAttribute('data-failed', JSON.stringify(failed));
    document.body.setAttribute('data-rendered', String(rendered));
    document.body.setAttribute('data-measure', JSON.stringify([...document.querySelectorAll('section')].map(x => [Math.round(x.getBoundingClientRect().height), x.scrollHeight])));
  }}
  document.fonts.ready.then(renderAll)
    .catch(e => {{ document.body.setAttribute('data-error', String(e && e.message ? e.message : e)); }});
</script>
</body></html>
"""


# --------------------------------------------------------------------------------------------
# Edge


def find_edge(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.is_file() else None
    candidates = []
    for var in ("ProgramFiles(x86)", "ProgramFiles", "ProgramW6432", "LOCALAPPDATA"):
        base = os.environ.get(var)
        if base:
            candidates.append(Path(base) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    candidates += [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    for name in ("msedge", "msedge.exe", "microsoft-edge", "microsoft-edge-stable"):
        w = shutil.which(name)
        if w:
            return Path(w)
    return None


def run_edge(edge: Path, extra: list[str], url: str, timeout: int = 180) -> subprocess.CompletedProcess:
    profile = tempfile.mkdtemp(prefix="flows-pdf-edge-")
    cmd = [
        str(edge), "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
        "--no-first-run", "--no-default-browser-check", "--virtual-time-budget=30000",
        *extra, url,
    ]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout)
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def count_pdf_pages(path: Path) -> int:
    data = path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data))


# --------------------------------------------------------------------------------------------
# Main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Print the Mermaid diagrams of a process-flows Markdown file to PDF with headless Edge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit codes: 0 ok, 1 no diagrams, 2 usage, 3 render check failed, 4 PDF missing or page count off.",
    )
    ap.add_argument("source", help="the process-flows Markdown file (e.g. docs/process-flows.md)")
    ap.add_argument("--out", required=True, help="PDF file to write")
    ap.add_argument("--title", help="cover title (default: the file's first # heading)")
    ap.add_argument("--subtitle", default="", help="cover lead paragraph (optional)")
    ap.add_argument("--date", help="date shown on the cover and footers (default: today, YYYY-MM-DD)")
    ap.add_argument("--html-only", action="store_true", help="write the print HTML next to --out and stop")
    ap.add_argument("--keep-html", action="store_true", help="keep the print HTML next to --out")
    ap.add_argument("--edge", help="path to msedge.exe (default: search the usual install folders)")
    ap.add_argument("--mermaid-js", default=MERMAID_CDN,
                    help="Mermaid script URL or local file (default: jsdelivr, mermaid@11.4.1)")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    src = Path(args.source).expanduser().resolve()
    if not src.is_file():
        print(f"flows_pdf: source not found: {src}", file=sys.stderr)
        return 2
    out = Path(args.out).expanduser().resolve()
    if out.suffix.lower() != ".pdf":
        print("flows_pdf: --out must end with .pdf", file=sys.stderr)
        return 2
    date_text = args.date or _dt.date.today().isoformat()

    h1, sections = parse_flows(src.read_text(encoding="utf-8-sig"))
    if not sections:
        print(f"flows_pdf: no ```mermaid sections found in {src}", file=sys.stderr)
        return 1
    title = args.title or h1 or src.stem.replace("-", " ").capitalize()

    mermaid_src = args.mermaid_js
    if "://" not in mermaid_src:
        mp = Path(mermaid_src).expanduser().resolve()
        if not mp.is_file():
            print(f"flows_pdf: --mermaid-js file not found: {mp}", file=sys.stderr)
            return 2
        mermaid_src = mp.as_uri()

    page = build_html(title, args.subtitle, date_text, src.name, sections, mermaid_src)
    out.parent.mkdir(parents=True, exist_ok=True)
    html_path = out.with_suffix(".html")
    with open(html_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)
    print(f"{len(sections)} diagram(s) -> {html_path}")
    for i, (t, _, _) in enumerate(sections, 1):
        print(f"  {i:02d}  {t}")
    if args.html_only:
        return 0

    def cleanup_html() -> None:
        if not args.keep_html:
            try:
                html_path.unlink()
            except OSError:
                pass

    edge = find_edge(args.edge)
    if edge is None:
        print("flows_pdf: Microsoft Edge not found; pass --edge <path to msedge.exe> "
              "(the HTML was kept so it can be printed by hand)", file=sys.stderr)
        return 2
    url = html_path.as_uri()

    # 1. render check
    try:
        dump = run_edge(edge, ["--dump-dom"], url)
    except subprocess.TimeoutExpired:
        print("flows_pdf: Edge timed out during the render check", file=sys.stderr)
        return 3
    dom = dump.stdout.decode("utf-8", errors="replace")
    dom = re.sub(r"<script\b.*?</script>", "", dom, flags=re.S | re.I)  # check the rendered content only
    m = re.search(r'data-rendered="(\d+)"', dom)
    rendered = int(m.group(1)) if m else -1
    err = re.search(r'data-error="([^"]*)"', dom)
    problems = []
    fm = re.search(r'data-failed="([^"]*)"', dom)
    failed = []
    if fm:
        try:
            failed = json.loads(html.unescape(fm.group(1)))
        except ValueError:
            failed = [html.unescape(fm.group(1))]
    for f in failed:
        problems.append(f"diagram {f}")
    if "Syntax error in text" in dom and not failed:
        problems.append("Mermaid reported 'Syntax error in text' (check each diagram in a Mermaid live editor)")
    if err:
        problems.append(f"Mermaid error: {html.unescape(err.group(1))}")
    if rendered < 0:
        problems.append("no data-rendered attribute: Mermaid did not load or finish (network access to "
                        "cdn.jsdelivr.net? use --mermaid-js with a local mermaid.min.js). Edge output: "
                        + dump.stderr.decode("utf-8", errors="replace").strip()[-300:])
    elif rendered != len(sections):
        problems.append(f"rendered {rendered} of {len(sections)} diagrams")
    if problems:
        for p in problems:
            print(f"flows_pdf: render check failed: {p}", file=sys.stderr)
        print(f"flows_pdf: HTML kept for inspection: {html_path}", file=sys.stderr)
        return 3
    svg_ids = re.findall(r'<svg[^>]*\sid="([^"]+)"', dom)
    if len(set(svg_ids)) != len(svg_ids):
        print("flows_pdf: render check failed: diagrams share SVG ids, so they would be drawn on top of each "
              "other (set deterministicIds in mermaid.initialize)", file=sys.stderr)
        print(f"flows_pdf: HTML kept for inspection: {html_path}", file=sys.stderr)
        return 3
    print(f"render check: {rendered}/{len(sections)} diagrams rendered, unique SVG ids, no syntax errors")
    mm = re.search(r"data-measure=\"([^\"]*)\"", dom)
    if mm:
        try:
            for k, (h, sh) in enumerate(json.loads(html.unescape(mm.group(1)))):
                if sh > h + 1:
                    label = "cover" if k == 0 else f"page {k + 1}"
                    print(f"  warning: {label} content is taller than the page ({sh}px > {h}px) and is clipped")
        except (ValueError, TypeError):
            pass

    # 2. print
    if out.exists():
        out.unlink()
    try:
        res = run_edge(edge, ["--no-pdf-header-footer", f"--print-to-pdf={out}"], url)
    except subprocess.TimeoutExpired:
        print("flows_pdf: Edge timed out while printing", file=sys.stderr)
        return 3
    if not out.is_file() or out.stat().st_size == 0:
        print("flows_pdf: Edge did not write the PDF: "
              + res.stderr.decode("utf-8", errors="replace").strip()[-400:], file=sys.stderr)
        print(f"flows_pdf: HTML kept for inspection: {html_path}", file=sys.stderr)
        return 4

    # 3. page count
    pages = count_pdf_pages(out)
    expected = len(sections) + 1
    print(f"PDF: {out} ({out.stat().st_size // 1024} KB, {pages} page(s), expected {expected})")
    if pages != expected:
        print(f"flows_pdf: page count {pages} differs from {expected} (cover + one per diagram); "
              "look for overflowing pages or a trailing blank page. HTML kept: " + str(html_path), file=sys.stderr)
        return 4
    cleanup_html()
    return 0


if __name__ == "__main__":
    sys.exit(main())
