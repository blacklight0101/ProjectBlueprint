# Flows and sharing: stakeholder material from the docs

Stakeholders who will never read the spec still need to see what the system does. This reference covers the three
forms of the same content and how to keep them in step:

| Form | Source | Tool | Audience |
|---|---|---|---|
| `docs/process-flows.md` | written by Claude from the RFC and the spec | Markdown + Mermaid | the team; the source of truth for the other two |
| `docs/<project-slug>-flows.pdf` | generated from `docs/process-flows.md` | `scripts/flows_pdf.py` (headless Microsoft Edge) | e-mail, meetings, print |
| a shareable web page | generated from `docs/process-flows.md` | the Artifact tool | a link the user decides to share |

The PDF and the page are exports: they are never edited by hand and never ahead of or behind the Markdown. Talk to
the user in their language; the diagrams, captions and exports are in English like every repository document.
Worked example: `docs/process-flows.md` in https://github.com/blacklight0101/Rosetta.

## 1. Writing docs/process-flows.md

Start from the template, [`assets/templates/docs/process-flows.md`](../assets/templates/docs/process-flows.md). Its
FILL comment gives the exact section shape the PDF builder parses; the rules below are the ones that matter most.

- **Derived, never first.** Every step in a diagram comes from the RFC or the spec. When a flow changes, change the
  RFC or the spec first and this page in the same branch. A diagram that shows a step no requirement backs is a
  review finding.
- **Section shape.** One flow per section: a `##` (or `###` under a "Later releases" heading) title, one blank line,
  a fenced `mermaid` block, one blank line, the caption paragraph. Nothing between the heading and the fence. One
  diagram per heading.
- **Captions.** One paragraph under the diagram: the one thing a reader must take away, then the requirement ids it
  rests on ("Sources RF-020..RF-029, ADR-004."). Ranges are fine; `scripts/check_docs.py` checks every single id.
- **Plain words.** Boxes use the words the stakeholders use. No class, table, column or permission names.
- **Diagram kinds.** `flowchart TB` for processes; `sequenceDiagram` for people and systems talking over time;
  `stateDiagram-v2` for the life cycle of a record. Use `LR` only for short loops (five or six boxes): a long
  left-to-right chain prints unreadably small on A4.
- **Size.** A flow must fit one landscape A4 page: about 20 boxes or 12 messages at most. Split a bigger flow into
  two sections rather than shrinking it.
- **Failure paths.** Show what the user sees when a step fails (a rejected input, an unreachable external system),
  not only the happy path. These are the questions stakeholders ask.
- **Later releases.** Flows of a later release go under a "Later releases" heading, with the release in the title,
  so nobody mistakes them for release 1 scope.
- **Mermaid syntax.** Quote a label that contains parentheses, brackets, quotes or a colon: `A["Save (draft)"]`.
  Avoid `end` as a node id. Keep node ids short (`A`, `B1`, `CF`); the label carries the words.
- **Header table.** The page starts with Audience, Source and Published rows. Published names the PDF file, the
  page link once it exists, and the date of the last regeneration.

## 2. The PDF: scripts/flows_pdf.py

```bash
python "<skill>/scripts/flows_pdf.py" "<repo>/docs/process-flows.md" \
  --out "<repo>/docs/<project-slug>-flows.pdf" \
  --title "<Project> - process flows" \
  --subtitle "<one or two sentences: what the system does and what release 1 covers>" \
  --date YYYY-MM-DD
```

`<skill>` is this skill's folder (for example `~/.claude/skills/project-blueprint`). Use the date of the Status
line in `docs/process-flows.md`, so the cover, the footers and the page agree.

What it produces: an A4 portrait cover (title, subtitle, date, numbered table of contents) and one A4 landscape page
per diagram (number, heading, diagram scaled to the page, caption, footer with the source file and date).

What it checks before and after printing:

1. It builds a print HTML page. Mermaid 11.4.1 is loaded from `cdn.jsdelivr.net`, fonts load first
   (`document.fonts.ready`), then each diagram is rendered with its own id.
2. A first Edge run with `--dump-dom` must report `data-rendered` equal to the number of diagrams, no diagram
   failure, no "Syntax error in text" and unique SVG ids.
3. Edge prints with `--headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=30000
   --print-to-pdf`, using a temporary `--user-data-dir` that is deleted afterwards.
4. The PDF page count (the `/Type /Page` objects) must equal the number of diagrams plus one.

| Exit code | Meaning | What to do |
|---|---|---|
| 0 | PDF written, page count right | commit the PDF with the Markdown change |
| 1 | no `mermaid` sections found | check the section shape (section 1) |
| 2 | input missing, Edge not found, bad argument | pass `--edge "<path>\msedge.exe"` |
| 3 | render check failed | the message names the diagram and the Mermaid parse error; fix the Markdown |
| 4 | PDF missing or page count wrong | see the troubleshooting list below; the HTML is kept for inspection |

Useful options: `--html-only` writes only the print HTML (next to `--out`) to inspect it in a browser;
`--keep-html` keeps it after printing; `--mermaid-js <file>` uses a local `mermaid.min.js` when the machine has no
network access; `--edge` points to a specific Edge.

### Troubleshooting

- **Diagrams drawn on top of each other on the first page, later pages empty.** Mermaid's default ids come from
  `Date.now()`, which is frozen under `--virtual-time-budget`, so all diagrams get the same id and are laid out in
  the first SVG. The script avoids it (one `mermaid.render` call per diagram with the ids `flow-1`, `flow-2`, and
  `deterministicIds`) and fails the render check if ids repeat. Keep that in any hand-made variant.
- **A blank page at the end.** The trailing `<script>` elements start a new page in the default page size. The
  script puts `page: wide` on `html` and `body` so the trailing content stays on a landscape page.
- **Extra blank pages between diagrams.** Sub-pixel rounding pushes a full-height box onto a second sheet. The page
  boxes are 1 mm shorter than the sheet (209 mm on 210 mm) with `overflow: hidden`; keep it so.
- **Mixed orientation.** Named pages do it: `@page cover { size: A4 portrait }` and
  `@page wide { size: A4 landscape }`, with `page: cover` on the cover section and `page: wide` on the others.
- **A diagram is tiny or cut off.** The diagram sits in an absolutely positioned box and its SVG gets `width: 100%;
  height: 100%; max-width: none`, which scales it uniformly. A tiny diagram is almost always a long `LR` chain:
  switch it to `TB` or split the flow. The script warns when a page's content is taller than the page.
- **Squashed actor boxes in a sequence diagram.** Caused by `max-height` with `height: auto` on the SVG; the
  uniform scaling above avoids it.
- **"Mermaid did not load or finish".** No network access to `cdn.jsdelivr.net`, or a proxy blocks it. Download
  `mermaid.min.js` 11.4.1 once and pass `--mermaid-js`.
- **Checking the result visually.** If PyMuPDF (`fitz`) is installed, render a page to PNG and look at it
  (`fitz.open(pdf)[1].get_pixmap(dpi=60).save("p2.png")`). Otherwise open the PDF in Edge. Edge `--screenshot`
  of the HTML shows the screen layout, not the printed one.
- **Never pipe the PDF through PowerShell redirection.** PowerShell re-encodes binary output. Let Edge write the
  file itself with `--print-to-pdf`, as the script does.

When the user should see the PDF on another device, send it with SendUserFile after it is written.

## 3. The shareable page (Artifact tool)

A web page of the same diagrams is easier to pass around than a PDF and renders crisply on any screen.

1. **Load the `artifact-design` skill first**, before writing the page, and follow its page contract (title, color
   tokens for light and dark mode, allowed CDNs, phone-width layout). Mermaid may be loaded from
   `cdn.jsdelivr.net/npm/mermaid@11.4.1`.
2. **Build the page from `docs/process-flows.md`**, not from memory: embed each section's heading, Mermaid source and
   caption, render them in the page, and set the Mermaid theme from the page's color tokens so the diagrams read in
   both themes. Add a short intro (what the system is, what release 1 covers), a table of contents and the date of
   the Status line. Write the HTML in the scratchpad (for example `<scratch>/flows-page/<project-slug>-flows.html`)
   and keep the generator next to it, so the next regeneration rebuilds the page the same way.
3. **Publish with the Artifact tool.** The page is private by default; the user decides whether and with whom to
   share it. Do not include secrets, server names, personal data or anything the user marked confidential, and do
   not dress the page in a real organisation's logo or branding.
4. **Keep one URL.** Republish updates to the same artifact: in the same conversation, publish the same file path
   again; from a later conversation, find the artifact (`action: "list"` or ask the user), read it first, then
   publish with its `url`.
5. **Record the link** in the Published row of `docs/process-flows.md` and in `handoff.md`, with the date.

## 4. When to regenerate

Regenerate the PDF and republish the page every time `docs/process-flows.md` changes, in the same branch as the
Markdown change:

- when the flows are first written (docs-set step 10, see `docs-set.md`);
- as part of the review loop's close step (step 8 in `review-loop.md`), after the edits are verified and before the
  commit, whenever the review touched `docs/process-flows.md`;
- whenever a decision removes, adds or reorders a step that a diagram shows (the review loop should have edited the
  flows too; if not, that is a finding).

Checklist for a regeneration:

1. `python "<skill>/scripts/check_docs.py" "<repo>"` has no errors in `docs/process-flows.md` (ids in captions
   defined, tables consistent, no leftover FILL comments).
2. Update the Status line date of `docs/process-flows.md`.
3. Run `flows_pdf.py` with that date; exit code 0; look at two or three pages.
4. Rebuild and republish the page to the same URL.
5. Update the Published row (PDF name, page link, date) and `handoff.md`.
6. Commit the Markdown, the PDF and the doc updates together when the user asks for a commit.
