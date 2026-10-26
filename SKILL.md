---
name: project-blueprint
description: Turns a project idea into a complete, consistent, build-ready docs repository by interviewing the user first (every question with a default), then writing README, CLAUDE.md, handoff, RFC, requirements, ADRs, architecture, data model, conventions, environments, design system, roadmap, process flows, decision log and an agent build plan (task cards, difficulty bands, verifier, merge rules, gates). Later it reviews that set, asks the owner questions and applies the answers everywhere. Use it whenever the user wants to start, plan, design, structure or document a new project or app, turn an idea into a spec, RFC, ADRs, roadmap or build plan, set up a docs-first repository, review or audit a project plan for holes and inconsistencies, fold new requirements or answers into one, or prepare a build hand-off to agents - even if they never say blueprint. Any language, any stack; includes a .NET house preset.
---

# Project blueprint

Take a project from an idea to a documentation repository that agents can build from without guessing, and keep
it consistent as decisions arrive. The skill always starts by asking, because every document downstream is only as
good as the decisions it records; it then writes from templates, plans the build, and checks itself.

`<skill>` below means this folder (for example `~/.claude/skills/project-blueprint`). Paths inside the skill are
relative to it.

## 1. What it produces

```text
<repo>/
  README.md                  pitch, status, release-1 scope, scope-decisions snapshot, reading order
  CLAUDE.md                  rules for every agent, source-of-truth order, stack rules block, commit policy
  AGENTS.md                  short tool-neutral index for any agent (Codex, Claude): where to start, commands, top rules
  handoff.md                 living state: waiting-for-owner list, resume point, agenda, gate state, session log
  docs/
    README.md                document map, id schemes, where counts live
    rfc/RFC-001-<slug>.md    the design proposal
    spec/requirements.md     RF-nnn, RNF-nnn, Q-nn open questions, traceability
    adr/                     _template.md, README.md (index + Totals), ADR-001..., one decision per file
    architecture.md          layers, solution layout, state lists, ports, deployment view
    data-model.md            tables, constraints, grants, migration numbers, test database
    conventions.md           naming, permission codes, error codes, branches and commits
    environments-and-delivery.md   environments, secrets, CI, package baseline, releases, observability
    design-system.md         tokens and components (v2 after the design round trip)
    design-system-brief.md   brief for an external design tool
    roadmap.md               phases P0..Pn with exit criteria, not-built list
    legacy-sources.md        only when replacing an existing system: citations, DEF-nn defects
    process-flows.md         Mermaid diagrams for stakeholders (exported to PDF and a web page)
    decision-log.md          DEC-nn owner decisions and where each was applied
    security/threat-model.md assets, trust boundaries, threats, controls, residual risks (optional; with an AI section)
    context/README.md        schemas, API contracts and a glossary agents read instead of guessing (optional)
    journal/                 curated summaries of owner sessions, decisions with DEC ids (created when first needed)
    verification/            phase verification matrices, written by the matrix card of each phase (created by cards)
    orchestration/README.md  build protocol: settings, bands, merge rules, usage throttle, verifier, gates G-nn
    orchestration/tasks.md   task cards P<phase>-nn with the canonical Totals table and the ownership table
  .claude/agents/            orchestrator, builder-haiku, builder-sonnet, builder-opus, builder-fable, verifier, verifier-opus
```

Worked example (read-only; read it to see what "filled" looks like, never copy its content): https://github.com/blacklight0101/Rosetta
(a public GitHub build run through pull requests: 404 cards over
P1..P6 of which 232 were follow-ups, DEC-01..DEC-174, difficulty bands, usage throttle, batched status pull requests and
phase verification matrices in `docs/verification/`).

## 2. Language

Talk to the user in the language they write or dictate in; write every repository document in English unless the
user explicitly asks for another language (record that as a scope decision). Ids (`RF-001`, `Q-07`, `DEC-12`,
`P1-03`) and code names are never translated. Plain, direct prose, no emojis, Markdown tables for registers,
Mermaid for diagrams. The reason for the split: the user thinks best in their own language, while builders, reviewers
and tools work from one consistent English text.

## 3. Pick a mode

Decide from the request and from what the folder already holds. Look before asking: check whether `<repo>/docs/`,
`handoff.md` and `docs/decision-log.md` exist, and read `handoff.md` first when they do.

| Mode | Pick it when | Read first |
|---|---|---|
| New blueprint | an idea, a new project, or a folder with no `docs/` set | `references/interview.md`, `references/docs-set.md`, `references/presets/README.md` |
| Extend | the set exists and new needs arrive (a module, an integration, a policy) | `references/docs-set.md` section 7, `references/interview.md` for the new questions |
| Review | "review", "audit", "find holes", "is this consistent", or before a gate | `references/review-loop.md` steps 0-2, `references/workflows.md` |
| Apply answers | the owner answers a review's questions or brings a batch of decisions | `references/review-loop.md` steps 3-8, `references/workflows.md` |
| Build hand-off | "plan the build", "task cards", "hand it to agents", or the pre-build agenda is closed | `references/build-plan.md` |
| Share | "PDF of the flows", "something to show stakeholders", flows changed | `references/flows-and-sharing.md` |

- When the user says "continue" and `handoff.md` has an open agenda for the owner, raise that agenda first; the
  resume point was written for exactly this moment.
- A request can chain modes (Review, then Apply answers, then Share). Finish one mode's stop point before the next.
- If the mode is unclear, ask one AskUserQuestion with the likely modes as options, the best guess first.

## 4. Principles

Each rule exists because breaking it cost time on the worked example.

- **Ask before writing, and give every question a default.** A default makes answering cheap ("defaults except #4")
  and keeps work moving; asking first means documents record decisions instead of guesses.
- **Never invent an answer.** Anything undecided becomes a `Q-nn` row (Id | Question | Owner | Needed by | Default |
  Status) with Status `Default applies` or `Open`. A guess written as a fact is a defect nobody will notice until it
  is built.
- **Ids are stable.** RF, RNF, Q, ADR, DEC, DEF, G, RFC and card ids are never renumbered or reused. A withdrawn item
  keeps its id with "Withdrawn YYYY-MM-DD - see ...". Every cross-reference, card and test relies on the id meaning
  one thing forever.
- **ADRs are superseded or amended, never deleted or rewritten.** The history of why is the point of an ADR; a dated
  note or a new ADR keeps it.
- **One canonical place per fact.** Other documents link or cite the id (table in `references/docs-set.md` section 4).
  A fact stated twice drifts.
- **Counts live in one place.** ADRs by status in the `docs/adr/README.md` Totals line; cards by phase and band in the
  `docs/orchestration/tasks.md` Totals table. Everywhere else links. Counts were the most frequent drift.
- **`docs/` is the source of truth; `handoff.md` is the living state.** Every session ends with a resume point that a
  reader with no memory can act on. Notes outside the repo only index and mirror.
- **The owner decides at gates.** Gates `G-nn` are opened by the named holder and recorded in `handoff.md`; agents
  never open one, because a gate is where a person accepts responsibility.
- **Every release has a path for its master data.** If people, teams or other rows that change after go-live can be
  added only by editing a seed, say so in the spec and the runbook and ask (bank 1.10). On the worked build the owner
  asked "how do I add a team member?" after the build was done.
- **Plan the owner's hands-on review.** A demo seed from real legacy data and a review once the main workflow runs
  (bank 7.7, 8.9) surface the rule changes early; on the worked build they withdrew a rule and added a screen.
- **Commit only when asked; branch per change.** `docs/<topic>`, `task/<card-id>-<slug>` or `fix/<issue>-<slug>`
  branches, linear history on `main`, never push unless asked. The user owns the repository's history. With a remote,
  changes reach `main` only through pull requests; a pushed branch is brought up to date by merging `main` into it,
  never by a rebase and a force-push.
- **Apply a decision everywhere it lands, the threat model included.** A DEC that accepts a risk adds a residual-risk
  line to `docs/security/threat-model.md`; one that pins a version updates the package baseline. On the Rosetta build
  a verifier caught a risk decision recorded in the decision log and nowhere else.
- **What the owner reports is recorded as reported.** "It works" in chat becomes "reported done by the owner on
  YYYY-MM-DD", never a measured value or a figure nobody pasted.
- **A standing permission is a dated decision.** When the owner delegates something for a while ("merge everything
  this session"), record it as a DEC with its date and scope instead of leaving `CLAUDE.md` contradicting practice.
- **Keep the living files small.** `handoff.md` keeps the last two or three resume entries and moves older ones to
  `docs/journal/`; on the Rosetta build it grew to 98 KB and stale claims in it misled the next session.

Identifier schemes in one line each: `RF-nnn` functional (ranges reserved per module by hundreds), `RNF-nnn`
non-functional, `Q-nn` open questions, `ADR-nnn` in `docs/adr/ADR-nnn-kebab-title.md`, `DEC-nn` owner decisions,
`DEF-nn` legacy defects, `G-nn` human gates, `P0..Pn` phases, `P1-03` task cards, `RFC-nnn`. Full rules:
`references/docs-set.md` and the scaffolded `docs/README.md`.

## 5. New blueprint

Work in rounds. After each step, show the result briefly and stop where the step says to wait. Keep two running
tables in the conversation from the first answer: the scope-decisions table and the open questions.

### Step 0 - Scale check

Docs-first pays only when the goal is clear and the work is big enough; for trivial work a full set becomes dead
documentation. Use bank 0.13: a small, clear project gets the light set (README, CLAUDE.md, AGENTS.md, handoff.md,
the requirements, the roadmap and `tasks.md`; scaffold everything and drop the rest as in `references/docs-set.md`
section 8); an unclear goal gets a spike or a prototype first and the blueprint after. Record the choice as the RFC's
"Spec level" line (spec-first, spec-anchored or spec-as-source) and as a scope decision.

### Step 1 - Framing interview (wait for answers)

Read `references/interview.md` sections 1-4 and `references/presets/README.md` sections 1-2. Ask the framing
questions (bank phase 0, Timing "Before writing": name and code, one-line purpose, product owner, whether it
replaces a system, first deliverable, release-1 slice, repository folder and system of record, project kind) plus
the stack question, with AskUserQuestion: at most 4 questions per call, 2 to 4 options each, the recommended option
first and labelled "(Recommended)". The project kind (0.12) decides which preset the stack question offers as
"(Recommended)" - for an intranet business web app that is `references/presets/dotnet-house.md` - or which
checklist applies to games, Android and plain web apps; never push a web-server preset onto a game. Free-text items
(the purpose, the owner's name) go in a short plain question next to the call. Stop and wait; nothing is written
before these are answered.

### Step 2 - Play back the preset (if taken)

Show the preset's "Answers it fills" as a "What I recorded" table and let the user override rows. Record one scope
decision for the preset plus one per override, and put the preset's open questions into the next batch. From here
on, skip every bank row the preset answers.

### Step 3 - Deeper rounds before scaffolding (wait after each)

Ask bank phases 1 (users and workflows) and 2 (integrations) with the numbered table
`# | Question | Default | Why it matters`, 6 to 12 rows, numbers running on across the session, ending with
"reply `defaults`, or `defaults except #4, #9`". Play back long or dictated answers as a "What I recorded" table and
re-ask unclear ones in plain words with an example. Raise the follow-ups the answers create in the next batch.
Phases 3 to 9 come after the first documents exist (step 6); rows with Timing "Pre-build" wait for the pre-build
agenda, and rows nobody answers become `Q-nn` with their defaults.

### Step 4 - Scope-decisions table

Show the table `Question | Chosen | Instead of` after each round. An explicitly accepted default is a decision; a
question the user never saw is a `Q-nn`, not a decision. At scaffold time each row becomes a `DEC-nn` in
`docs/decision-log.md` and the table is copied as a snapshot into the README and the RFC scope section (later only
annotated "(changed by DEC-nn)", never rewritten).

### Step 5 - Scaffold

The `--target` is the folder recorded for bank 0.9; confirm it in the scaffold preview. Decide the optional parts
first: `legacy` when nothing is replaced, `design` when there is no user interface, `security` only for a prototype
with no users and no untrusted input (bank 6.10), `context` when there is no schema or API contract to hand agents.
`flows` is rarely skipped; `orchestration` and `agents` are skipped only when people, not agents, build the project,
recorded as a `DEC-nn`.
Preview, then write:

```bash
python "<skill>/scripts/scaffold.py" --target "<repo>" \
  --name "Order Desk" --code ODK --owner "Ana Ruiz" --date YYYY-MM-DD --without legacy --dry-run
python "<skill>/scripts/scaffold.py" --target "<repo>" \
  --name "Order Desk" --code ODK --owner "Ana Ruiz" --date YYYY-MM-DD --without legacy
```

The slug defaults to the kebab-case of `--name` (pass `--slug` to override). The script refuses to overwrite existing
files (exit 1) unless `--force`; exit 2 is a usage problem. It prints the created files, the FILL comments left per
file and every line that still mentions a skipped part: edit or remove those lines as `references/docs-set.md`
section 8 lists. If the user chose local git (bank 0.9) and the folder is not a repository, run `git init` there; do
not commit until asked. Then write the first `DEC-nn` rows (from step 4) and the `Q-nn` rows (from the open
questions) straight away.

### Step 6 - Fill the documents in order

Follow the writing order in `references/docs-set.md` section 2 and each document's catalogue entry: README,
CLAUDE.md, handoff.md, docs/README.md (and legacy-sources.md) -> RFC -> requirements -> ADRs (ADR-001 is scaffolded;
preset ADRs take the next free ids) -> architecture. Replace or remove every `<!-- FILL: ... -->` comment; a section
with nothing to say goes, together with its comment. Keep the `<!-- STACK-RULES:BEGIN -->` / `END` markers in
CLAUDE.md and paste the preset's hard-rules block between them. Leave `docs/adr/_template.md` as it is.

Show the user the README, the RFC goals and non-goals and the requirement ranges once written, so they see progress
and can correct the shape early. Then ask the remaining bank phases 3 to 9 (skipping rows the preset answers and
leaving "Pre-build" rows to step 7) and fold the answers in. Draft the RFC and the spec yourself, since they depend
on the whole conversation. Documents with disjoint files may be drafted by parallel Agent subagents once the
decisions are fixed; give each the scope-decisions table, the Q table and the ids it may use.

### Step 7 - Pre-build agenda (wait at each item)

Write the agenda into `handoff.md` as soon as it is agreed, then work it item by item as in
`references/interview.md` section 5, asking first each time:

1. **Data model walk-through** -> `docs/data-model.md`, convention and history ADRs, migration number blocks.
2. **Design system round trip** -> `docs/design-system.md` v1 and `docs/design-system-brief.md`; the user runs the
   brief in a design tool; fold the result back as v2 (exported board under `docs/design/board/`, brief marked
   Superseded). If the user skips it, v1 stands; record that as a decision.
3. **Other things to settle** (one numbered batch) -> `docs/conventions.md`, `docs/environments-and-delivery.md`,
   ADRs, gate dates; then the roadmap, process flows and decision log (docs-set steps 9-11).

Strike each item through in `handoff.md` with its date and result when it closes.

### Step 8 - Build plan

Read `references/build-plan.md` and fill `docs/orchestration/README.md`, `docs/orchestration/tasks.md` and the
agent files from the templates (keep the bands the owner chose in bank 8.2; delete agent files for bands nobody uses). Show the user the phases, the Totals table (cards by phase, band and size), the gates
with their holders, and any Must requirement no card covers. Cards the release-notes and runbook work creates
(`docs/releases.md`, deploy runbooks, `docs/design/board/`) must appear in some card's Do or Delivers line.

### Step 9 - Self-review

```bash
python "<skill>/scripts/check_docs.py" "<repo>" --without legacy
```

Pass the same `--without` parts as the scaffold. Exit 0 is clean, 1 means errors (or warnings with `--strict`), 2 a
usage problem; `--json` gives machine-readable output. Fix every error except one kind: a document whose pre-build
agenda item is still open (typically `docs/data-model.md` or the design documents when a session ends mid-agenda)
keeps its FILL comments. Report those errors as expected, name the documents in the `handoff.md` resume point, or
pass `--exclude` for them (which also skips their other checks). Warnings about files a card will create (for
example the flows PDF before its first generation) are expected; say so. Then run a light pass of the review
loop (`references/review-loop.md` steps 1-2: three slice reviewers as parallel Agent subagents, spot-verify the high
findings yourself), fix what is mechanical, and turn every real hole into a question with a default.

### Step 10 - Summary to the user (stop)

In the user's language: what exists (link the files, do not restate counts), the decisions taken (DEC range), the
open questions with their defaults as a numbered table, the gates and who holds them, and the resume point written
in `handoff.md`. Offer the flows PDF or page (section 8). Offer to commit on a `docs/<topic>` branch; commit only on
a yes.

### Step 11 - Persist memory

See section 9.

## 6. Extend

Fold a new need in without rewriting existing text, in the eleven-step order of `references/docs-set.md` section 7:
decision, questions, requirements (new range or free ten), ADR, RFC subsection "(added YYYY-MM-DD)", technical
documents, roadmap, build plan, flows, CLAUDE.md, decision-log "Where applied". Ask the new questions first
(`references/interview.md` formats). For one to five decisions over a few files, use the small-change pattern of
`references/review-loop.md` (one editor, one adversarial verifier, one fix); for more, use the full loop below.

## 7. Review and Apply answers

Follow `references/review-loop.md`; it has the steps, templates and recovery rules. In brief:

0. **Preflight**: detect the repository's shape (decision prefix, skipped optional parts, layout differences), note
   HEAD, run `check_docs.py` with the matching `--without` and `--decision-prefix` and save its output to the
   scratchpad. A clean git tree is needed only before step 6.
1. **Review**: three read-only slice reviewers (product, technical, delivery) return inconsistencies with
   `file:line` on both sides and holes with the exact question for the owner. Spot-verify every high finding.
2. **Report** high first, then medium and low compressed, then the numbered question table with a default per
   question, grouped Business rules / Architecture / Orchestration and design / Still owed. Stop and wait.
3. **Record** the answers ("What I recorded", re-asks, follow-ups) into a decisions file in the scratchpad.
4. **Plan**: research, one planner with a registry of every cross-file identifier, three critics, revision.
5. **Show the key choices** and amend with the user's corrections. Stop and wait before editing.
6. **Apply** with one editor per disjoint file group and a verifier per group.
7. **Lenses and final fixer**: cross-file lenses in rounds, then one final sequential fixer.
8. **Close** with spot checks, decision-log rows, `handoff.md`, a commit when asked, flows regeneration and
   memory.

Multi-agent machinery is in `references/workflows.md`. Use the Workflow tool only when the user has opted in: they
said "ultracode", asked for a workflow or multi-agent orchestration, or ultracode is on. Then copy the matching
template from `assets/workflows/` (`review.js`, `plan-changes.js`, `apply-changes.js`, `final-pass.js`) to the
scratchpad, fill its constants, check it is pure ASCII with LF endings, and launch it. Without the opt-in, run the
same steps as parallel Agent-tool subagents (independent calls in one message), or offer the workflow in one or two
lines with the agent count and a rough cost and wait for a yes. The opt-in matters because a workflow can spend
millions of tokens without further prompts.

## 8. Share

Read `references/flows-and-sharing.md`. The PDF comes from `docs/process-flows.md`:

```bash
python "<skill>/scripts/flows_pdf.py" "<repo>/docs/process-flows.md" \
  --out "<repo>/docs/<slug>-flows.pdf" --title "<Project> - process flows" --subtitle "<one line>" --date YYYY-MM-DD
```

Use the date from the page's Status line. Exit codes: 0 written, 1 no diagrams, 2 input or Edge missing, 3 a diagram
failed to render (the message names it), 4 wrong page count. The web page is built with the Artifact tool after
loading the `artifact-design` skill; it is private by default and the user decides whether to share it. Regenerate
both whenever the flows change and record the link and date in the page's Published row and in `handoff.md`.

## 9. Persisting memory

At the end of a session, and whenever the user asks to save progress:

- Update `handoff.md` first: status line, current state, resume point (state, next actions, blockers), agenda, gate
  table, session log entry. It is the state a session with no memory reads.
- If the workspace's `CLAUDE.md` defines a memory convention, follow it too. For example an Obsidian vault: the
  project's overview or index note, its TODO note, the session log, decision records for architectural decisions and
  a learning note for anything reusable, with frontmatter and wikilinks. Mirror and link; the repository stays the
  source of truth.
- With no such convention, `handoff.md` is the only state; do not scatter notes elsewhere.
- Never write secrets, passwords, connection strings with credentials or personal data into the repository or the
  notes; record where a secret lives, not its value.

## 10. When nobody can answer

In a batch run, a test run or any environment where no user can reply, do not stall and do not invent:

1. Write every question you would have asked, with its default, as `Q-nn` rows in the `docs/spec/requirements.md`
   open-question table with Status `Default applies` (or `Open` when there is no safe default), owner "Product owner"
   and a realistic "Needed by".
2. Add a short "Questions for the owner" section to `handoff.md` (under the agenda) that lists those `Q-nn` ids in the
   order they matter and links the spec's section 4, without restating the defaults.
3. Apply the defaults and continue through every step. Framing answers that were not given (name, purpose) are taken
   from the request; mark them provisional in the README status line and as `Q-nn`.
4. Record no `DEC-nn` for a default nobody accepted; decisions need an owner. Replace the body of the decision
   log's kick-off table (the example row and its FILL comments) with the single line "No decisions recorded; all
   answers are defaults, see [requirements](spec/requirements.md) section 4."
5. End with the same summary as step 10, stating clearly that all answers are defaults awaiting the owner.

## 11. Resources

| File | Read or run it when |
|---|---|
| `references/interview.md` | before asking anything: principles, AskUserQuestion and numbered-table formats, "What I recorded", Q-nn rules, the question bank with timings, the pre-build agenda |
| `references/docs-set.md` | before writing or checking any document: catalogue, writing order, canonical places, drift checks, folding in a new need, dropping optional documents, filling templates |
| `references/presets/README.md` | when the stack comes up: how a preset is applied, how to add one, checklists for Phaser, Unity, Android and plain web apps |
| `references/presets/dotnet-house.md` | when the user takes the .NET house preset (.NET 10, Blazor Server, Dapper, SQL Server, IIS, Windows auth, xUnit, 60/30/10) |
| `references/build-plan.md` | when planning the build: phases, card cutting, difficulty bands, fields, dependencies, gates, test discipline, running the build (merge rules 10.1, usage throttle 10.2, clean-up 10.3) and the lessons from running one (10.4) |
| `references/verification-matrix.md` | when cutting or building a phase's verification-matrix card: the document's sections, the counting rule, how a phase closes with gaps |
| `references/review-loop.md` | in Review, Apply answers and larger Extend changes: steps 0-8, templates, recovery rules, small-change pattern |
| `references/workflows.md` | before any multi-agent step: opt-in rule, the kit and its constants, lessons learned, fallback with Agent calls |
| `references/flows-and-sharing.md` | when writing process flows or producing the PDF or the shareable page |
| `assets/templates/**` | copied by `scaffold.py`; mirrors the target layout exactly; never edit per project |
| `assets/workflows/review.js` | Review step 1 as a workflow (opt-in only) |
| `assets/workflows/plan-changes.js` | Plan and amend steps 4-5 as a workflow (opt-in only) |
| `assets/workflows/apply-changes.js` | Apply step 6 and cross-file lenses as a workflow (opt-in only) |
| `assets/workflows/final-pass.js` | Final lens rounds with one sequential fixer (opt-in only) |
| `scripts/scaffold.py` | New blueprint step 5: `--target --name --code --owner [--slug] [--date] [--without legacy,design,flows,orchestration,agents,security,context] [--force] [--dry-run]`; exit 0 / 1 refused / 2 usage |
| `scripts/check_docs.py` | after filling, before and after every review, before a commit: `<repo> [--without ...] [--json] [--strict] [--decision-prefix DEC] [--exclude GLOB]`; exit 0 / 1 / 2; also warns when `CLAUDE.md` or `handoff.md` grows past its size budget |
| `scripts/flows_pdf.py` | Share: `<process-flows.md> --out <pdf> [--title] [--subtitle] [--date] [--html-only] [--keep-html] [--edge] [--mermaid-js]`; exit 0-4 |

Run the scripts with Python 3 from any folder; they use only the standard library (`flows_pdf.py` also needs
Microsoft Edge). Use forward slashes or quoted paths in Git Bash on Windows.
