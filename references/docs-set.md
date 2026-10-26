# The documentation set: catalogue, order and consistency rules

Reference for Claude when generating, extending or reviewing a project's documentation set. It says, for every
document of the target layout: why it exists, when it is written, what it must contain, which ids it owns, which
other documents it must agree with, and the drift to watch for. The templates are in `assets/templates/` and mirror
the target repository layout exactly.

Worked example (read-only): https://github.com/blacklight0101/Rosetta is a complete set built this way, with a threat model with an AI
section, a journal and per-phase verification matrices after a full agent build. Read it to see what "filled"
looks like; never copy its content.

Contents: 1. The set at a glance | 2. Writing order and why | 3. Catalogue | 4. One canonical place per fact | 5. Facts that drift and how to check them | 6. Document headers and status | 7. Folding in a new need later | 8. Dropping optional documents | 9. Filling templates

## 1. The set at a glance

| Step | Document | Required | Owns (canonical for) | Template |
|---|---|---|---|---|
| 1 | `README.md` | always | the one-paragraph pitch, reading order | `README.md` |
| 1 | `CLAUDE.md` | always | rules for anyone changing the repo, source-of-truth order, read-only paths, commit policy | `CLAUDE.md` |
| 1 | `AGENTS.md` | always | a short tool-neutral index for other agents; links CLAUDE.md, never restates it | `AGENTS.md` |
| 1 | `handoff.md` | always | waiting-for-owner list, current state, resume point, agenda for the owner, gate state, session log | `handoff.md` |
| 1 | `docs/README.md` | always | document map, id schemes, where each count lives | `docs/README.md` |
| 1 | `docs/legacy-sources.md` | only when replacing a system | `DEF-nn`, citation keys, frozen facts | `docs/legacy-sources.md` |
| 2 | `docs/rfc/RFC-001-<slug>.md` | always | `RFC-nnn`; problem, goals, alternatives, design narrative, risks, success metrics | `docs/rfc/RFC-001-{{PROJECT_SLUG}}.md` |
| 3 | `docs/spec/requirements.md` | always | `RF-nnn`, `RNF-nnn`, `Q-nn`, id ranges per module, actors, glossary, traceability | `docs/spec/requirements.md` |
| 4 | `docs/adr/*` | always | `ADR-nnn`, ADR counts by status, deferred decisions | `docs/adr/_template.md`, `README.md`, `ADR-001-...` |
| 5 | `docs/architecture.md` | always | layers, solution layout, domain model and state lists, ports, data ownership, topology | `docs/architecture.md` |
| 6 | `docs/data-model.md` | always (sections marked Not applicable when there is no persistent data) | tables, constraints, grants, migration numbers, test database | `docs/data-model.md` |
| 7 | `docs/conventions.md` | always | names (code, data, routes, permission codes, resources, branches), error handling, degraded-mode behaviour | `docs/conventions.md` |
| 7 | `docs/environments-and-delivery.md` | always | environments, secrets placement, source control, CI, package baseline, versioning, deployment, observability | `docs/environments-and-delivery.md` |
| 7 | `docs/security/threat-model.md` | always, except a prototype with no users and no untrusted input | assets, boundaries, threats `T-nn` with controls, residual risks `R-nn` | `docs/security/threat-model.md` |
| 7 | `docs/context/README.md` | when agents need schemas or contracts | the index of generated or copied schemas, contracts and samples | `docs/context/README.md` |
| 8 | `docs/design-system-brief.md` | when there is a UI | the brief for an external design pass | `docs/design-system-brief.md` |
| 8 | `docs/design-system.md` | when there is a UI | tokens, components, patterns, accessibility | `docs/design-system.md` |
| 9 | `docs/roadmap.md` | always | phases `P0..Pn` with exit criteria, later releases, backlog by id, not-built list | `docs/roadmap.md` |
| 10 | `docs/process-flows.md` | always (skip only for a tiny project with one flow) | stakeholder diagrams | `docs/process-flows.md` |
| 11 | `docs/decision-log.md` | always (started at step 1 with the kick-off decisions) | `DEC-nn` | `docs/decision-log.md` |
| 12 | `docs/orchestration/README.md` | always, unless people build the project (section 8) | build protocol, difficulty bands, merge rules, usage throttle, verifier summary, `G-nn` criteria | `docs/orchestration/README.md` |
| 12 | `docs/orchestration/tasks.md` | always, unless people build the project (section 8) | task cards `P<phase>-nn`, card counts by band and phase, the ownership table | `docs/orchestration/tasks.md` |
| 12 | `.claude/agents/*.md` | always, unless people build the project (section 8) | agent definitions: orchestrator, builder-haiku, builder-sonnet, builder-opus, builder-fable, verifier, verifier-opus; the only copy of the report and verdict formats | `.claude/agents/` |
| build | `docs/verification/*.md` | created by the matrix card of each phase | the evidence that closes a phase (`references/verification-matrix.md`) | none |
| build | `docs/journal/*.md` | created when first needed | owner-session summaries, older handoff entries | none |

The build plan (step 12) is described in `references/build-plan.md`; process flows and their exports in
`references/flows-and-sharing.md`; the review loop that keeps the set consistent in `references/review-loop.md`.

## 2. Writing order and why

1. **README + CLAUDE.md + handoff.md + docs/README.md** (and `legacy-sources.md` when something is replaced), right
   after the kick-off interview. They fix the name, the scope in three lines, the rules, the map and the citation
   scheme before any content is written, so every later document cites the same things the same way. The kick-off
   decisions go into `decision-log.md` as the first `DEC` rows at the same time.
2. **RFC-001.** The narrative: problem, goals and non-goals, alternatives, the proposed design at concept level,
   risks. It is the document reviewers read first; writing it before the spec forces the big shape to be argued
   once.
3. **Requirements.** Every behaviour the RFC promises becomes an `RF` with Given/When/Then; every quality an `RNF`;
   every gap a `Q-nn` with a default. Ranges per module are fixed here.
4. **ADRs.** One per decision the RFC and the spec rely on (stack, hosting, identity, data access, integration
   style, state model, testing discipline). ADR-001 (record architecture decisions) is scaffolded; the stack ADR is
   usually next.
5. **Architecture.** How the pieces fit, derived from the RFC and the ADRs; the canonical home of the solution layout
   and the state lists.
6. **Data model.** Every table, constraint and grant, walked through with the owner (a pre-build agenda item).
7. **Conventions + environments and delivery.** The "other things to settle" before building: naming, error
   handling, what users see when something is down, environments, secrets, source control and CI, package baseline,
   versioning, deployment, observability.
8. **Design system brief, then board, then design system.** Write the brief, let the owner run it through a design
   tool, fold the result back as the design system (the brief is marked `Superseded`, kept for history).
9. **Roadmap.** Phases with exit criteria, once the scope, the ADRs and the prerequisites are known.
10. **Process flows.** Stakeholder diagrams derived from everything above; exported for sharing.
11. **Decision log.** Kept from step 1; at this point every decision so far is applied and has a Where applied cell.
12. **Orchestration.** The protocol, the task cards and the agents, written last because each card cites
    requirements, ADRs, data-model migration numbers and conventions that must already exist.

Ask before writing, not after: the owner is interviewed before step 1 (`references/interview.md`), and the
pre-build agenda in `handoff.md` (data model, design system, "other things to settle") is worked through with the
owner before steps 6-8 are written. Steps 2-5 may be drafted in one sitting; steps 6-8 each start with questions.

## 3. Catalogue

Each entry: **Purpose** - **When** - **Must contain** - **Owns** - **Must agree with** - **Drift to watch**.

### README.md
- **Purpose**: the front page for a person who has never heard of the project.
- **When**: step 1; the status line changes at every phase change.
- **Must contain**: a one-paragraph pitch; the status line; release 1 scope in three lines; the kick-off scope
  decisions table (Question | Chosen | Instead of, a snapshot of the first DEC rows); the reading order of the
  documents; links to CLAUDE.md and handoff.md; the stack in one or two lines pointing to ADRs; related places.
- **Owns**: nothing canonical except the pitch.
- **Must agree with**: spec section 1 (scope), roadmap (phase in the status line), ADRs (stack).
- **Drift**: the status line left at P0 after the build starts; a scope-decision row rewritten instead of annotated
  "(changed by DEC-nn)"; a stack line that names a technology an ADR has since replaced; scope lines that restate
  details instead of linking.

### CLAUDE.md
- **Purpose**: the rules every agent reads first; the reason agents stay inside the design.
- **When**: step 1; grows whenever a decision creates a rule a builder could break unnoticed.
- **Must contain**: what the repo is (mission and scope), a repository and deployment table, the source-of-truth
  order, hard rules for the documents (never renumber ids; ADRs superseded, not deleted; never invent answers; ask
  with defaults; counts in one place; English), hard rules specific to the system (from ADRs and the defect
  register), the stack rules block between `<!-- STACK-RULES:BEGIN -->` and `<!-- STACK-RULES:END -->` (a preset
  pastes there), read-only paths, commit policy (commit only when asked, branch per change, linear history), the
  documentation protocol, and the top-level solution layout.
- **Owns**: the rules and the read-only path list.
- **Must agree with**: ADRs (every rule cites its ADR), conventions.md (branch names, naming), architecture.md
  (layout), environments-and-delivery.md (package baseline and prohibited packages).
- **Drift**: a rule that still names a superseded ADR; a prohibition contradicting the package baseline; a layout
  block deeper than the top level (it then diverges from architecture.md).

### handoff.md
- **Purpose**: the living state; what a session with no memory needs to continue.
- **When**: step 1; updated at the end of every session, before stopping.
- **Must contain**: a one-line dated status; current state (what exists, with statuses); the resume point (state,
  next actions in order, blockers); the agenda of what to ask the owner next (items struck through with a dated
  result when settled); the gates table (state only: Closed, Provisional, Open, with date); decisions pending;
  session log, newest first.
- **Owns**: gate state, the resume point, the session history.
- **Must agree with**: orchestration/README.md (gate ids and names), spec section 4 (the questions it lists as
  pending), decision-log.md (the DEC range it mentions).
- **Drift**: counts restated here (ADRs, cards) instead of linked; a resume point that describes a session two
  sessions ago; agenda items settled but not struck through; gate criteria copied here and then diverging.

### docs/README.md
- **Purpose**: the map of the documentation and the id schemes.
- **When**: step 1; a row changes whenever a document's status or substance changes.
- **Must contain**: one row per document (purpose, status, date), the agents line, the id-scheme table with the owner
  of each scheme, the "where counts live" table, the status vocabulary, planned documents, how to add things.
- **Owns**: the document list and statuses; the id-scheme table.
- **Must agree with**: the files that actually exist; each document's own status header.
- **Drift**: a row for a document that was dropped (legacy-sources, design system); statuses out of step with the
  document headers; purpose lines that grow into summaries with numbers in them.

### docs/rfc/RFC-001-<slug>.md
- **Purpose**: the design proposal reviewers accept; the argument for the shape of the system.
- **When**: step 2; changes later only by dated subsections ("added YYYY-MM-DD") and by links, not by rewriting.
- **Must contain**: header table (status, date, author, reviewers, related); context and problem (with DEF classes
  when replacing); numbered goals and explicit non-goals; the kick-off scope decisions snapshot (same table as the
  README); alternatives including "do nothing"; proposed design with a system-context diagram, containers, domain
  concepts, the main life cycle, key flows with failure paths, identity and authorization, deployment topology; impact (risks with mitigations, costs, migrations, rollback);
  implementation plan as a one-line-per-phase summary linking the roadmap; success criteria with targets and how
  they are measured; open questions as a link to the spec only.
- **Owns**: `RFC-nnn`, the goals and success metrics.
- **Must agree with**: spec (every promised behaviour has an RF), ADRs (each sub-decision), roadmap (phase summary,
  non-goals vs "deliberately not built"), architecture (state diagram vs canonical state list).
- **Drift**: a phase table that repeats exit criteria; a state diagram with a state the architecture no longer has;
  a non-goal that later became a requirement; an open-questions section that lists questions instead of linking.

### docs/spec/requirements.md
- **Purpose**: what the system must do, testably; the first source of truth.
- **When**: step 3; every new behaviour gets an id here before code.
- **Must contain**: header table; scope; how to read an id; the id-range table per module; acceptance-criteria
  rules; actors; glossary; open questions `Q-nn` (Id | Question | Owner | Needed by | Default | Status); functional
  requirements per module with Given/When/Then and a Verification line; non-functional requirements (Id |
  Requirement | Verification); deferred ranges; traceability matrix (requirement group | source | ADR | phase |
  cards).
- **Owns**: `RF-nnn`, `RNF-nnn`, `Q-nn`, id ranges, the glossary.
- **Must agree with**: decision log (every `Answered (DEC-nn)` has that row), ADRs (cited ids exist and are not
  superseded without note), roadmap (backlog by id), tasks.md (cards column vs cards' Refs), data-model.md (constraints
  that carry business rules), conventions.md (permission codes used in criteria).
- **Drift**: a question answered in the decision log but still `Open` here; a default in the Q table that differs
  from the default applied in a card; a requirement with no card; traceability rows whose ranges no longer match the
  section headings; renumbered ids (never allowed).

### docs/adr/ (template, index, ADR-001, the rest)
- **Purpose**: why it is built this way, one decision per file, with history.
- **When**: step 4 for the decisions the design rests on; afterwards whenever a decision affects several builders or
  is hard to revert, before implementing it.
- **Must contain**: per ADR - date, status, deciders, context, options (with "do nothing"), decision, rationale with
  evidence, consequences positive and negative, references, dated notes. Index - one row per ADR, the Totals line,
  relationships (supersedes, amends, refines), deferred decisions with triggers.
- **Owns**: `ADR-nnn`; the count of ADRs by status (Totals line).
- **Must agree with**: CLAUDE.md rules, architecture.md, the spec's traceability, the decision log (DEC ids cited).
- **Drift**: an ADR file with no index row or the reverse; an index status that differs from the file's Status line;
  a superseded ADR still cited as the reason for a rule; the Totals line not updated; a deferred-decision row kept
  after its ADR was written.

### docs/architecture.md
- **Purpose**: the living reference of how the pieces fit.
- **When**: step 5; updated in the same change that alters the structure.
- **Must contain**: layers and the dependency rule; the solution layout (canonical, folder level); the domain model
  with every state list; application services; ports and adapters; integrations; background work; data ownership;
  identity and authorization; time and localisation when relevant; observability; deployment topology; testing
  approach summary; open items.
- **Owns**: solution layout, state lists, port names.
- **Must agree with**: ADRs, data-model.md (enum values vs state lists), RFC diagrams, CLAUDE.md layout block,
  tasks.md (paths cards create).
- **Drift**: a state added in a card or the data model but not here; a port renamed in one place; layout paths that
  differ from the paths in card Delivers fields.

### docs/data-model.md
- **Purpose**: every table, column rule, constraint and grant; the contract migrations implement.
- **When**: step 6, after a walk-through with the owner (a pre-build agenda item); a migration and this document
  change together.
- **Must contain**: conventions (keys, naming, types, time, collation), schema or area map, tables by area with the
  requirement ids they serve, constraints that carry business rules, grants per login or role, migration numbering
  (blocks per card or module), test database strategy, data import mapping when replacing a system, open points.
- **Owns**: table and column names, grants, migration numbers and blocks.
- **Must agree with**: architecture (state lists as check constraints), conventions (naming), spec (business rules),
  tasks.md (each card's migration numbers), environments (logins and secrets).
- **Drift**: migration numbers reassigned in a card; a login or grant named differently in environments; a reserved
  name used for a schema (for example SQL Server reserves `sys`).

### docs/conventions.md
- **Purpose**: names and behaviours every builder must apply the same way.
- **When**: step 7 ("other things to settle").
- **Must contain**: naming for code and folders, data, routes and pages, permission codes (the canonical catalogue),
  resource keys, integrations, tests, branches and commits; error handling per layer; what the user sees when a
  dependency is down.
- **Owns**: permission codes, branch and commit naming, resource key format.
- **Must agree with**: CLAUDE.md commit policy, orchestration README (branch names used by builders), spec
  (permission codes in criteria), data-model (seeded permissions).
- **Drift**: a permission code spelled differently in a requirement, a card and the seed data; branch names in the
  orchestration protocol that differ from this document.

### docs/environments-and-delivery.md
- **Purpose**: where it runs and how it gets there.
- **When**: step 7.
- **Must contain**: environments and what exists when; configuration and secrets placement; source control and
  system of record; CI; the package baseline (anything outside needs an ADR); versioning and releases; deployment
  procedure; observability and alerting; client devices when relevant.
- **Owns**: package baseline, environment names, version scheme.
- **Must agree with**: CLAUDE.md prohibitions, ADRs on hosting and secrets, roadmap prerequisites, gates that depend
  on environments.
- **Drift**: a package allowed here and prohibited in CLAUDE.md; an environment a card assumes that does not exist
  before a given phase.

### docs/design-system-brief.md and docs/design-system.md
- **Purpose**: the brief asks an external design pass (for example Claude Design) for a coherent system; the design
  system is what pages must use.
- **When**: step 8: brief first; the owner runs it; the result (board, token file) is exported into the repo (for
  example `docs/design/board/`) and folded back as the design system, version 2 if one existed. The brief is then
  marked `Superseded` (kept for history); until then its status is `Proposed`.
- **Must contain**: brief - what is wanted back, hard constraints, users and devices, principles, token and component
  asks, key screens to mock up. Design system - principles, tokens (light and dark if needed), layout and
  breakpoints, input ergonomics, owned component inventory, state badges or colours, patterns, print when needed,
  accessibility baseline, naming, verification.
- **Owns**: tokens and the component inventory.
- **Must agree with**: architecture state lists (one badge per state), spec (screens named in requirements), cards
  that build pages.
- **Drift**: a state with no badge; a component a card uses that is not in the inventory; the brief still marked
  as the source after the fold-back.

### docs/roadmap.md
- **Purpose**: the order of delivery and what "done" means per phase.
- **When**: step 9; living.
- **Must contain**: phases with scope and checkable exit criteria; prerequisites; later releases with entry
  conditions; future backlog (not requirements); backlog by requirement id; deliberately not built.
- **Owns**: phases, exit criteria, the not-built list.
- **Must agree with**: RFC (phase summary, non-goals), spec (reserved ranges, traceability phase column), tasks.md
  (every card in a phase that exists here), gates.
- **Drift**: exit criteria that embed counts; a requirement in two phases or none; a later release whose range is not
  reserved in the spec.

### docs/legacy-sources.md (optional)
- **Purpose**: cite the replaced system's documented behaviour without copying it; list its defects so the rewrite
  does not reproduce them.
- **When**: step 1, before the spec, because requirements cite it.
- **Must contain**: where the legacy code and the analysis notes live (read-only); citation keys and form
  (`[LEG-Overview sec. 4]`); the defect register `DEF-nn` with where each is closed; facts frozen because others depend
  on them; further variants when analysed.
- **Owns**: `DEF-nn`, citation keys.
- **Must agree with**: spec Source fields and `Closes DEF-nn`, ADR contexts, CLAUDE.md hard rules.
- **Drift**: a defect with nothing in "Where it is closed"; a closing id that was withdrawn; decision ids mixed into
  the defect scheme.

### docs/process-flows.md
- **Purpose**: diagrams for stakeholders who will not read the spec.
- **When**: step 10; regenerated exports whenever a flow changes (see `references/flows-and-sharing.md`).
- **Must contain**: one section per flow, a Mermaid diagram each, a caption with the RF ids it shows, plain language.
- **Owns**: nothing canonical; it is derived.
- **Must agree with**: spec, architecture state lists, RFC flows.
- **Drift**: a flow that still shows a step a decision removed; exports (page, PDF) older than the Markdown.

### docs/decision-log.md
- **Purpose**: the owner's decisions, with what prompted each and where it landed.
- **When**: from step 1 (kick-off decisions) and after every question round.
- **Must contain**: header table; the id rules; kick-off scope decisions ("Chosen: X. Instead of: Y."); later
  decisions. Columns: Id | Date | Decision | Answer to | Where applied.
- **Owns**: `DEC-nn`.
- **Must agree with**: spec Q statuses, ADR references, card Refs, handoff session log.
- **Drift**: an empty Where applied; a decision text edited instead of a new row; an id scheme clash (never reuse a
  prefix already used for another register).

### docs/security/threat-model.md (optional)
- **Purpose**: one place that lists what is protected, the threats, the control and check for each, and the risks
  the owner accepted.
- **Contains**: assets, trust boundaries, threats `T-nn` with control, check and requirement, supply chain, an AI
  section when a model is called (bank 6.10), residual risks `R-nn` each with its `DEC-nn`.
- **Must agree with**: decision log (every DEC that accepts a risk has an `R-nn` row), security RNFs, environments
  (secrets, CI), the hard-rule greps of the orchestration protocol.
- **Drift**: a risk accepted in the decision log and nowhere else; a control with no check; a residual risk deleted
  instead of closed.

### docs/context/README.md (optional)
- **Purpose**: exact schemas, contracts and samples agents read instead of guessing.
- **Must agree with**: data model and architecture (they win; the context file is regenerated).
- **Drift**: a schema file older than the last migration card.

### docs/orchestration/README.md, docs/orchestration/tasks.md, .claude/agents/
- See `references/build-plan.md` for content and format. For consistency purposes: the protocol owns gate criteria
  `G-nn`, the bands, the merge rules and the throttle; `tasks.md` owns the cards, the Totals table of cards by band
  and phase, and the ownership table; the agent files own the builder report and the verifier verdict formats.
- **Must agree with**: spec (Refs), data model (migration numbers), conventions (branches), architecture (paths),
  roadmap (phases), handoff (gate state).
- **Drift**: card counts restated elsewhere; a card whose Refs cite a withdrawn requirement; a gate referenced in a
  card but not defined; Status values outside `Todo | In progress | In review | Done | Blocked`.

## 4. One canonical place per fact

Every fact that more than one document needs is stated in exactly one place; the others link to it or cite its id.
When a fact must appear elsewhere for readability (a summary line in README.md), it is phrased without the volatile
part ("see the index for counts").

| Fact | Canonical place | Others |
|---|---|---|
| What the system must do | spec section 5 and 6 | cite `RF`/`RNF` ids |
| Open questions and their defaults | spec section 4 | cite `Q-nn`; RFC section 8 only links |
| Owner decisions | decision-log.md | cite `DEC-nn` |
| Kick-off scope decisions | decision-log.md (first DEC rows) | README and RFC keep a snapshot table, never rewritten, only annotated "(changed by DEC-nn)" |
| Why it is built this way | the ADR | cite `ADR-nnn` |
| ADR counts by status | adr/README.md Totals line | link the index |
| Card counts by band and phase | tasks.md Totals table | link tasks.md |
| Owner of each shared component and number block | tasks.md Ownership table | cards depend on the owner card |
| Builder report and verifier verdict formats | `.claude/agents/` files | the protocol summarises and links |
| Accepted risks | security/threat-model.md residual risks | the DEC row names the `R-nn` |
| What waits for the owner | handoff.md waiting-for-owner list | nowhere else |
| Id ranges per module | spec section 1.3 | cite ranges only when needed |
| State lists | architecture.md domain model | RFC diagram, data-model constraint and design badges must match it |
| Permission codes | conventions.md | requirements, cards and seed data use the codes verbatim |
| Tables, grants, migration numbers | data-model.md | cards cite their migration numbers from there |
| Solution layout (folder level) | architecture.md | CLAUDE.md shows the top level only |
| Package baseline | environments-and-delivery.md | CLAUDE.md prohibitions link it |
| Phase scope and exit criteria | roadmap.md | RFC section 6 one line per phase |
| Not built in release 1 | roadmap.md | RFC non-goals agree with it |
| Gate criteria | orchestration/README.md | cards cite `G-nn` |
| Gate state | handoff.md | nowhere else |
| Glossary terms | spec section 3 | used as defined |
| Legacy behaviour | the cited source notes | cite `[LEG-... sec. n]`, never copy |

## 5. Facts that drift and how to check them

These drift in every project; review checks them every time (`references/review-loop.md`). `scripts/check_docs.py`
automates the mechanical ones.

| Fact | Check |
|---|---|
| ADR files vs index rows vs Totals | `ls docs/adr/ADR-*.md \| wc -l`; `grep -c '^\| \[ADR-' docs/adr/README.md`; `grep -h '^\*\*Status\*\*' docs/adr/ADR-*.md \| sort \| uniq -c` against the Totals line |
| Cards by band and phase vs Totals | count `### P<n>-nn - ` headings per phase and the `- **Difficulty**:` values per band (commands in the orchestration protocol section 11); compare with the Totals table in tasks.md |
| Accepted risks | every DEC that accepts a risk has an `R-nn` row in the threat model |
| Living-file size | `CLAUDE.md` under about 150 lines, `AGENTS.md` under about 60, `handoff.md` under about 30 KB (`scripts/check_docs.py` warns) |
| Counts restated outside their home | `grep -nE '[0-9]+ (ADRs\|cards\|task cards)' README.md handoff.md docs/*.md` and replace with links |
| State lists | list the states in architecture.md; grep each state name in RFC, data-model, design-system, process-flows; flag missing or extra names |
| Permission codes | extract codes from conventions.md; grep each across the spec, tasks.md and data-model.md; flag spellings that appear only outside conventions.md |
| Migration numbers | each number appears once in data-model.md and once in exactly one card; no two cards share a number |
| Question status vs decision log | every `Answered (DEC-nn)` has that DEC row; every DEC with Answer to `Q-nn` has that question marked answered |
| Decisions applied | no DEC row with an empty Where applied |
| Traceability | every RF group in the matrix has at least one card; every card's Refs cite existing, non-withdrawn ids |
| Superseded ADRs | `grep` for each superseded ADR id: cited only in history notes, not as the reason for a live rule |
| Placeholders | no `{{` and no `<!-- FILL` left in any filled document (`docs/adr/_template.md` is the only exception) |
| Links | every relative link resolves; anchors such as `requirements.md#4-open-questions` match the heading |

## 6. Document headers and status

The RFC, the spec and the decision log start with a two-column header table (`| | |`): Status, Date, Author or
Owner, Reviewers when relevant, Related links. ADRs use the bold-field header of the template. Document statuses are
`Proposed`, `Accepted`, `Living`, `Reference`, `Superseded` (defined in `docs/README.md`); the status in a document's
header and in the docs/README.md row are always the same.

Accepting the RFC and the spec (usually gate G-01) is a real review with the people named as reviewers, not a
formality; until then work that depends on them runs under a provisional gate named in handoff.md.

## 7. Folding in a new need later

A new need (a module, a platform capability, an integration, a policy) never rewrites existing text. Apply it in
this order, in one change, and record it in handoff.md's session log:

1. **Decision**: a `DEC-nn` row with Answer to `Owner` (or the question it answers).
2. **Questions**: anything not decided becomes `Q-nn` with owner, needed-by and default.
3. **Requirements**: a new RF range for a new module (next free hundred), or new ids in a free ten inside an existing
   range; new RNFs; update the range table, the actors and the glossary; add traceability rows.
4. **ADR**: a new ADR for the architectural part; mark older ADRs `Superseded by` or `Amended` with a dated note;
   update the index, the relationships paragraph and the Totals line.
5. **RFC**: a new subsection "(added YYYY-MM-DD)" under section 4, goals and non-goals adjusted, risks added.
6. **Architecture, data model, conventions, environments, design system**: the sections the need touches,
   including new tables with migration numbers in a free block and new permission codes.
7. **Roadmap**: the phase that delivers it, its exit criteria, backlog by id, the not-built list.
8. **Build plan**: new cards (next free id in the phase, never renumbering) or changed Do/Delivers/Done-when of
   existing cards; the Totals table; gates if the need brings one.
9. **Process flows**: a changed or new diagram; regenerate the exports.
10. **CLAUDE.md**: any new hard rule the need creates.
11. **Decision log**: fill Where applied with every id and section touched.

For a large change, use the review loop's plan-then-apply method (`references/review-loop.md`) instead of editing
file by file.

## 8. Dropping optional documents

Decide at the interview, record it as a kick-off decision, and keep the rest of the set coherent:

- **No system being replaced** -> no `docs/legacy-sources.md`. Remove its row from docs/README.md, item 7 of README.md's
  reading order, item 6 of CLAUDE.md's sources of truth, the `DEF-nn` bullet in the spec's id rules, the DEF column
  of the RFC's problem table (or the table), and "Closes DEF-nn" from the requirement format. Sources in the spec
  cite decisions and interviews instead.
- **No user interface** (a service, a worker, a library) -> no `docs/design-system.md` and no
  `docs/design-system-brief.md`. Remove their rows, the design-system line in CLAUDE.md, and the design step from
  the handoff agenda. Drop gate G-02 (design board approved) from the handoff.md gate table and from section 7 of
  `docs/orchestration/README.md`: before the first commit the remaining gates may be renumbered; after it, mark
  G-02 `Withdrawn YYYY-MM-DD - see DEC-nn` instead. Set Page walk to off in section 1 of the orchestration
  protocol, and remove the UI shell card and every gate reference to G-02 from the cards. Conventions still cover
  API error shapes and messages.
- **No persistent data** -> keep `docs/data-model.md` (it carries the ids and links the rest of the set expects) and
  mark each section "Not applicable: <reason>", as its own FILL comment says; conventions and architecture say
  where state lives instead.
- **A game** keeps the set but reads it differently: the design system covers the art direction and the HUD; the
  data model may cover save data only; requirements describe mechanics and levels.
- **A prototype with no users and no untrusted input** -> no `docs/security/threat-model.md`
  (`--without security`); record the decision, and add the threat model before the first real user.
- **No schema or contract to hand agents** -> no `docs/context/` (`--without context`).
- **A small, clear project** (SKILL.md step 0) -> the light set: README, CLAUDE.md, AGENTS.md, handoff.md, the
  requirements, the roadmap and `tasks.md`. Scaffold everything, then delete the rest and the references to them.
- Never drop the RFC, the spec, the ADRs, the decision log, the roadmap or handoff.md: they carry the ids that make
  the set checkable. Drop the build plan (`--without orchestration,agents`) only when people, not agents, build the
  project, and record that as a `DEC-nn`; the roadmap then carries the phases and gates on its own.

`scripts/scaffold.py` skips optional templates according to the interview answers; `scripts/check_docs.py` must be
told which optional documents are absent so that it does not flag the missing links.

## 9. Filling templates

- Placeholders `{{PROJECT}}`, `{{PROJECT_SLUG}}`, `{{CODE}}`, `{{OWNER}}`, `{{DATE}}` are replaced by the scaffold
  script, including in file names (`RFC-001-{{PROJECT_SLUG}}.md`).
- Guidance is in `<!-- FILL: ... -->` comments. Every one is replaced by content or removed when the document is
  filled; a section with nothing to say is removed together with its comment, not left empty.
- Example rows use obviously generic content and carry a FILL comment; they are replaced, never kept.
- `docs/adr/_template.md` keeps its FILL comments on purpose (it is copied for every new ADR); it is the only file
  allowed to contain them after scaffolding.
- The marker comments `<!-- STACK-RULES:BEGIN -->` and `<!-- STACK-RULES:END -->` in CLAUDE.md stay; only the FILL
  comment between them is replaced by the preset's rules or the rules from the ADRs.
- Write in English, plainly, without emojis; registers are Markdown tables; diagrams are Mermaid.
