# docs/ - index

Source of truth for the design of {{PROJECT}}. Notes kept elsewhere (a vault, a wiki) may mirror this table and link
here; they never hold a second copy of these documents.

<!-- FILL: Keep one row per document that exists. Status is one of Proposed, Accepted, Living, Reference, Superseded
(see the Status vocabulary below). Date is the last date the document changed in substance. Remove the rows of
optional documents this project does not have (legacy-sources.md when nothing is replaced; design-system.md and
design-system-brief.md when there is no user interface; security/threat-model.md for a prototype with no users and
no untrusted input; context/README.md when there is no schema or contract to hand agents) and say why in one line
under the table. -->

| Document | Purpose | Status | Date |
|---|---|---|---|
| [rfc/RFC-001-{{PROJECT_SLUG}}.md](rfc/RFC-001-{{PROJECT_SLUG}}.md) | Design proposal: problem, goals and non-goals, alternatives, proposed design, impact, phases, success metrics | Proposed | {{DATE}} |
| [spec/requirements.md](spec/requirements.md) | Requirements with Given/When/Then acceptance criteria, non-functional requirements, open questions, reserved ranges, traceability | Proposed | {{DATE}} |
| [decision-log.md](decision-log.md) | The product owner's decisions (DEC-nn), what each answers and where it is applied | Living | {{DATE}} |
| [adr/README.md](adr/README.md) | Architecture decision records index, counts by status, deferred decisions | Living | {{DATE}} |
| [architecture.md](architecture.md) | Layers and dependency rule, solution layout, domain model, services, ports, data ownership, background work, security, deployment, testing approach | Living | {{DATE}} |
| [data-model.md](data-model.md) | Every table by schema or area, constraints that carry business rules, grants, migration numbering, test database, data import | Proposed | {{DATE}} |
| [conventions.md](conventions.md) | Naming (code, data, routes, permission codes, resources, tests, branches), error handling per layer, what the user sees when something is down | Proposed | {{DATE}} |
| [environments-and-delivery.md](environments-and-delivery.md) | Environments, configuration and secrets placement, source control, CI, package baseline, versioning and releases, deployment, observability | Proposed | {{DATE}} |
| [design-system.md](design-system.md) | Principles, tokens, layout, component inventory, patterns, states, print, accessibility, verification | Proposed | {{DATE}} |
| [design-system-brief.md](design-system-brief.md) | The brief sent to an external design pass; Superseded by design-system.md v2 after the round trip | Proposed | {{DATE}} |
| [roadmap.md](roadmap.md) | Phases P0..Pn with exit criteria, later releases with entry conditions, backlog by requirement id, deliberately not built | Living | {{DATE}} |
| [legacy-sources.md](legacy-sources.md) | Where the behaviour of the system being replaced is documented, citation scheme, defect register DEF-nn, frozen facts | Living | {{DATE}} |
| [security/threat-model.md](security/threat-model.md) | Assets, trust boundaries, threats with controls and checks, supply chain, AI-specific threats, residual risks the owner accepted | Proposed | {{DATE}} |
| [context/README.md](context/README.md) | Schemas, API contracts and sample payloads agents use instead of guessing, each with its source | Living | {{DATE}} |
| [process-flows.md](process-flows.md) | Stakeholder flowcharts (Mermaid) with requirement ids in captions; source of any exported page or PDF | Reference | {{DATE}} |
| [orchestration/README.md](orchestration/README.md) | Build protocol: settings, roles and difficulty bands, card life cycle, merge rules, verifier summary, human gates G-nn, parallelism and usage throttle, stop conditions | Living | {{DATE}} |
| [orchestration/tasks.md](orchestration/tasks.md) | Task cards P1-01..Pn-nn with difficulty, size, dependencies, gate, reads, do, delivers, done-when checks, refs and status; totals by band and phase; the ownership table | Living | {{DATE}} |

Agent definitions used by the orchestration protocol live in `.claude/agents/` (`orchestrator`, `builder-haiku`,
`builder-sonnet`, `builder-opus`, `builder-fable`, `verifier`, `verifier-opus`). Two folders are created by the
build when first needed: `journal/` (curated owner-session summaries and older handoff entries) and `verification/`
(one verification matrix per phase and release, written by the matrix cards).

## Identifier schemes

Ids are never renumbered or reused. A withdrawn item keeps its id and reads `Withdrawn YYYY-MM-DD - see <id>`.

| Id | Meaning | Owned by (canonical list) |
|---|---|---|
| `RF-nnn` | Functional requirement; three digits, one range of a hundred per module (for example RF-001..RF-099 module A, RF-100..RF-199 module B) | [spec/requirements.md](spec/requirements.md) section 5, ranges in section 1 |
| `RNF-nnn` | Non-functional requirement | [spec/requirements.md](spec/requirements.md) section 6 |
| `Q-nn` | Open question with owner, needed-by phase, default and status (`Open`, `Default applies`, `Answered (DEC-nn)`, `Withdrawn`) | [spec/requirements.md](spec/requirements.md) section 4 |
| `DEC-nn` | Product owner decision, with what it answers and where it is applied | [decision-log.md](decision-log.md) |
| `ADR-nnn` | Architecture decision record, file `adr/ADR-nnn-kebab-title.md`; status `Proposed`, `Accepted`, `Superseded by ADR-nnn` or `Amended` (dated note) | [adr/README.md](adr/README.md) |
| `RFC-nnn` | Design proposal | [rfc/](rfc/) |
| `DEF-nn` | Defect of the system being replaced that the rewrite must not reproduce | [legacy-sources.md](legacy-sources.md) |
| `G-nn` | Human gate; criteria in the orchestration protocol, state in `handoff.md` | [orchestration/README.md](orchestration/README.md) |
| `P0..Pn` | Phase with exit criteria | [roadmap.md](roadmap.md) |
| `P<phase>-nn` | Task card, for example `P1-03` | [orchestration/tasks.md](orchestration/tasks.md) |

## Where counts and shared lists live

State each of these in its canonical place only; other documents link there.

| Fact | Canonical place |
|---|---|
| ADRs by status | [adr/README.md](adr/README.md) (Totals line under the index) |
| Cards by band and by phase | [orchestration/tasks.md](orchestration/tasks.md) (Totals table at the top) |
| Open questions and their defaults | [spec/requirements.md](spec/requirements.md) section 4 |
| Requirement id ranges per module | [spec/requirements.md](spec/requirements.md) section 1 |
| State lists (life cycle of the main entities) | [architecture.md](architecture.md) (domain model) |
| Permission codes | [conventions.md](conventions.md) |
| Tables, grants and migration numbers | [data-model.md](data-model.md) |
| Package baseline and versions | [environments-and-delivery.md](environments-and-delivery.md) |
| Phase scope and exit criteria | [roadmap.md](roadmap.md) |
| Gate criteria / gate state | [orchestration/README.md](orchestration/README.md) / [../handoff.md](../handoff.md) |

## Status vocabulary for documents

- **Proposed** - written, not yet reviewed by the product owner and the reviewers named in the document.
- **Accepted** - reviewed and approved; changes go through a decision (DEC-nn) or an ADR.
- **Living** - an index, register or plan that changes as work proceeds; always current.
- **Reference** - kept for the record or derived from other documents; never the source of a fact.
- **Superseded** - replaced by the document named in its header; kept, never deleted.

## Planned documents (not written yet)

<!-- FILL: Documents that a card or phase will create later (runbooks, integration contracts, testing strategy,
release notes). One row each; the creating card is the only one that creates it, later cards add sections. Remove
the section when empty. -->

| Document | When | Content |
|---|---|---|
| <!-- FILL: path --> | <!-- FILL: phase and creating card, e.g. P1 (P1-14) --> | <!-- FILL: one line --> |

## How to add things

- **A requirement**: next free id in its module's range in `spec/requirements.md`; fill title, release, MoSCoW,
  source, story, Given/When/Then, verification. Add it to the traceability matrix. Never renumber.
- **An open question**: next free `Q-nn` in the spec's section 4 with owner, needed-by phase and a default; Status
  `Open`, or `Default applies` once work proceeds on the default.
- **A decision by the product owner**: next free `DEC-nn` in `decision-log.md`; name what it answers; apply it and
  fill "Where applied"; set the answered question to `Answered (DEC-nn)`.
- **An ADR**: copy `adr/_template.md` to `adr/ADR-nnn-<kebab-title>.md`, status `Proposed`, add a row to
  `adr/README.md` and update its Totals line. When superseding, set the old one to `Superseded by ADR-nnn`; never
  delete. A decision the product owner took directly may be written as `Accepted` with its DEC-nn in References.
- **A task card**: next free `P<phase>-nn` in `orchestration/tasks.md`, in the card format of that file; update the
  Totals table.
- **A legacy citation**: use the scheme in `legacy-sources.md`.
