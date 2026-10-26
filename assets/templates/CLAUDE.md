# {{PROJECT}} - Project Instructions

Rules of the road for anyone (including Claude) working in this repository. The user-facing overview is
[README.md](README.md); the current state is [handoff.md](handoff.md); the design is under `docs/`; a short
tool-neutral index for other agents is [AGENTS.md](AGENTS.md). Keep this file under about 150 lines: it is loaded
into every session, so detail belongs in the document that owns it.

## Mission and scope

<!-- FILL: Three to five lines. What the system replaces or creates, the core flow in one arrow chain
(input -> step -> step -> output), what release 1 is, and what is explicitly later (link docs/roadmap.md). Name the
audience and the hosting context in one phrase (intranet, public web, desktop, mobile, game). -->

## Repository and deployment

| Key | Value |
|---|---|
| Local path | <!-- FILL: absolute path of this repository --> |
| Short code | `{{CODE}}` (prefix for names that must be unique across systems, see `docs/conventions.md`) |
| Product owner | {{OWNER}} |
| Version control | <!-- FILL: git local / remote name and host; system of record if different --> |
| Branching | branch off `main` per change -> review -> fast-forward or squash merge -> linear history <!-- FILL: with a remote: "pull request per change, squash merge under docs/orchestration/README.md section 3.1" --> |
| Hosting target | <!-- FILL: where it runs, per ADR --> |
| Data store | <!-- FILL: database or storage and where it is described (docs/data-model.md) --> |
| Read-only references | <!-- FILL: every path Claude may read but never edit (system being replaced, convention source); "none" if none --> |

## Sources of truth

When two documents disagree, the one higher in this list wins and the other is corrected in the same change. A
decision-log row that is newer than the conflicting text always wins: the text was not updated when the decision was
applied, and fixing it is part of applying the decision.

1. `docs/spec/requirements.md` - what the system must do (`RF-nnn` / `RNF-nnn`) and the open questions (`Q-nn`).
   New behaviour gets an id there **before** code is written.
2. `docs/decision-log.md` - the product owner's decisions (`DEC-nn`) and where each is applied.
3. `docs/adr/` - why it is built this way. A decision that affects several developers or is hard to revert gets an
   ADR **before** it is implemented. ADRs are never deleted; they are superseded or amended with a dated note.
4. `docs/architecture.md` - how the pieces fit; updated in the same change that alters the structure.
   `docs/data-model.md` - every table, constraint and grant; a migration and this document change together.
   `docs/conventions.md` - names, error handling, user-facing behaviour when something is down.
   `docs/environments-and-delivery.md` - environments, secrets placement, package baseline, versioning, deployment.
   `docs/design-system.md` - tokens, components, patterns; a screen uses only what is documented there.
5. `docs/roadmap.md` - phases with exit criteria; `docs/process-flows.md` - stakeholder diagrams derived from 1-4.
6. `docs/legacy-sources.md` - where the behaviour of the system being replaced is documented and the defect register
   `DEF-nn`. **Cite the sources; never copy them into this repository.**
7. `handoff.md` - the living state. Update it at the end of every working session.
8. `docs/orchestration/` - the build plan: `README.md` (protocol, difficulty bands, merge rules, usage throttle,
   verifier, human gates `G-nn`) and `tasks.md` (task cards `P<phase>-nn`). Agents live in `.claude/agents/`. The
   orchestrator edits only the Status line of a card; every finished card is verified before it is merged.
9. `docs/journal/` - curated summaries of owner sessions and older resume entries moved out of `handoff.md`; history,
   never a source of rules.

<!-- FILL: Remove the lines for documents this project does not have (no legacy system -> no item 6; no user interface
-> no design-system line). Keep the numbering continuous. -->

## Hard rules for the documents

- **Never renumber or reuse an id** (`RF`, `RNF`, `Q`, `ADR`, `DEC`, `DEF`, `G`, `P<phase>-nn`, `RFC`). A dropped item
  keeps its id and reads `Withdrawn YYYY-MM-DD - see <id>`.
- **ADRs are never deleted.** A replaced decision is marked `Superseded by ADR-nnn`; a partial change adds a dated
  note and the status `Amended`. The index `docs/adr/README.md` is updated in the same change.
- **Never invent an answer.** Anything the product owner has not decided becomes an open question `Q-nn` in the spec
  with an owner, a "needed by" phase and a stated default; the Status reads `Default applies` until answered.
- **Ask with defaults.** When asking the product owner, explain what each question changes, number the questions and
  give a default for each, so that "defaults except 4 and 9" is a complete answer. Record every answer as a `DEC-nn`
  row and apply it everywhere it lands in the same change, `docs/security/threat-model.md` included when it accepts
  a risk.
- **Record what the owner reports as reported.** "Reported done by the owner on YYYY-MM-DD", never a figure nobody
  pasted. A standing permission from the owner ("merge everything this session") is a dated `DEC-nn` with its scope.
- **One canonical place per fact.** Counts (ADRs by status, cards by band and phase), state lists, permission codes,
  migration numbers and id ranges are stated in the one document that owns them (see `docs/README.md`); every other
  document links there instead of repeating the number.
- **Documents are written in English.** Plain, direct prose; Markdown tables for registers; Mermaid for diagrams;
  no emojis.
- **Traceability both ways.** A requirement names its ADRs and cards in the spec's traceability matrix; a card names
  the requirement and ADR ids it implements; a decision names where it is applied.

## Hard rules specific to this system

<!-- FILL: The domain rules that a builder could break without noticing, one bullet each, stated as "always" or
"never" with the reason and the ADR or RF id. Typical sources: every external write, every state change, every time
or money value, every place where a literal would hide configuration, every security boundary. If a legacy system is
replaced, turn each high-severity DEF-nn into a rule here (for example "no status strings or sentinel values; state
changes only through the aggregate"). Five to fifteen bullets. -->

- <!-- FILL: rule - reason (ADR-nnn, RF-nnn) -->

## Stack rules

<!-- STACK-RULES:BEGIN -->
<!-- FILL: A stack preset pastes its rules here (layering, data access, naming, testing discipline, prohibitions).
With no preset, write the stack rules decided in the ADRs: architecture and dependency direction, data access,
error handling, test levels and the command that must pass before reporting done, packages that need an ADR. -->
<!-- STACK-RULES:END -->

## Read-only paths

<!-- FILL: Every path outside this repository that may be read and must never be edited, with the reason (for example
"the system being replaced; a working copy of another version control system: never run git there"). Write "None."
when there are none. -->

## Commit policy

<!-- FILL: keep the variant that matches the repository (local only, or a remote with pull requests) and delete the
other bullet that starts with "Local only" or "With a remote". -->

- Commit only when the product owner asks or the build protocol says so. Never push, force-push or rewrite pushed
  history without being asked.
- One branch per change (`task/<card-id>-<slug>` for a task card, `docs/<topic>` for a documentation change that
  belongs to no card, `fix/<issue>-<slug>` for a defect outside the cards; exact names in `docs/conventions.md`).
- Local only: merged into `main` by fast-forward so the history stays linear.
- With a remote: nothing reaches `main` except through a pull request with green CI, squash-merged; a pushed branch
  is updated by merging `main` into it, never by a rebase and a force-push. A pull request that changes `docs/spec`,
  `docs/adr`, `docs/rfc`, `docs/decision-log.md` or this file carries the `needs-owner` label and only the product
  owner merges it.
- Conventional Commits in lower case, header at most 72 characters (`docs/conventions.md`); the message names the ids
  it touches (`Refs: RF-012, ADR-004, DEC-07`).
- Add files by explicit path; never skip or bypass hooks; never a bare `git stash`.
- The working tree is clean before a multi-file change starts, so a partial change can be reverted as a whole.

## Documentation protocol

- Requirement change -> edit `docs/spec/requirements.md` (keep ids stable, add new ones in the module's range, never
  renumber) and its traceability matrix.
- Decision by the product owner -> new row in `docs/decision-log.md`, then apply it and fill "Where applied".
- Architectural decision -> new `docs/adr/ADR-nnn-<kebab-title>.md` from `docs/adr/_template.md`, plus a row in
  `docs/adr/README.md`.
- Structural change -> `docs/architecture.md` in the same change; schema change -> `docs/data-model.md`.
- Flow change -> `docs/process-flows.md`, then regenerate any exported page or PDF made from it.
- Owner session with decisions -> a short summary in `docs/journal/YYYY-MM-DD-<topic>.md` naming the DEC ids.
- Session end -> `handoff.md` (waiting-for-owner list, resume point, agenda, gates, session log entry at the top);
  keep only the last two or three resume entries there and move older ones to `docs/journal/`.

## Planned solution layout (scaffolded in Phase 1, not before)

<!-- FILL: A short code block with the top-level folders and projects the first card scaffolds, one line each with
its responsibility. The canonical, detailed layout (folders inside each project) is docs/architecture.md; this block
never goes deeper than the top level, so the two cannot drift. -->

The detailed layout is in [docs/architecture.md](docs/architecture.md).
