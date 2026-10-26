# {{PROJECT}}

<!-- FILL: One paragraph, three to five sentences, for a reader who has never heard of the project: who uses it,
what it does for them end to end, what it replaces (if anything) and the one or two qualities that make it
different (for example "every external write is idempotent", "works offline"). No architecture here. -->

**Status: documentation phase (P0).** No code exists yet. This repository holds the design documents that
development will follow. See [docs/README.md](docs/README.md) for the full map.

<!-- FILL: When the build starts, replace the status line with the current phase from docs/roadmap.md, for example
"Status: Phase P2 in progress". Keep it to one line; the detail lives in handoff.md. -->

## Release 1 scope in three lines

<!-- FILL: Three bullets, no more. What release 1 covers (users, modules, sites), what it deliberately leaves to
later releases, and anything delivered underneath it (a platform, an integration framework). The canonical scope is
docs/spec/requirements.md section 1 and docs/roadmap.md; this is a summary that links there. -->

- Release 1 covers <!-- FILL: the first users and modules, end to end -->.
- Later releases add <!-- FILL: what waits, one line -->.
- Underneath: <!-- FILL: shared capabilities delivered in the foundation phases, or remove this bullet -->.

## Scope decisions (agreed at kick-off)

<!-- FILL: The kick-off scope table from the interview, one row per decision. It is a snapshot for readers; the
canonical record is docs/decision-log.md, where each row is a DEC-nn entry. When a later decision changes a row, do
not rewrite it: append "(changed by DEC-nn)" to the Chosen cell. -->

| Question | Chosen | Instead of |
|---|---|---|
| <!-- FILL: e.g. First deliverable --> | <!-- FILL: e.g. **Documents only** --> | <!-- FILL: e.g. documents plus a compiling skeleton --> |

## Read the documents in this order

1. [docs/rfc/RFC-001-{{PROJECT_SLUG}}.md](docs/rfc/RFC-001-{{PROJECT_SLUG}}.md) - the design proposal: problem, goals and non-goals, alternatives, proposed design, phases, success metrics.
2. [docs/spec/requirements.md](docs/spec/requirements.md) - requirements with acceptance criteria, open questions and traceability.
3. [docs/adr/README.md](docs/adr/README.md) - the architecture decision records.
4. [docs/decision-log.md](docs/decision-log.md) - the product owner's decisions (DEC-nn) and where each is applied.
5. [docs/architecture.md](docs/architecture.md) - the living architecture reference.
6. [docs/roadmap.md](docs/roadmap.md) - phases with exit criteria, later releases and what is deliberately not built.
7. [docs/legacy-sources.md](docs/legacy-sources.md) - where the behaviour of the system being replaced is documented and the defect register the rewrite must not reproduce.

<!-- FILL: Remove item 7 when the project replaces no existing system (docs/legacy-sources.md is then not written).
Add docs/design-system.md after item 5 when the project has a user interface. -->

Rules for anyone (human or AI agent) changing this repository are in [CLAUDE.md](CLAUDE.md).
The current state and next steps are in [handoff.md](handoff.md).

## Stack (decided in the ADRs)

<!-- FILL: One or two lines naming the stack as decided in the ADRs (runtime, UI, data access, database, hosting,
authentication, test framework), each part pointing to its ADR. Write "to be decided (Q-nn)" for any part that is
still open; never guess. -->

## Related

<!-- FILL: Links a newcomer needs outside this repository: the notes vault or wiki page for the project, the system
being replaced (read-only), a convention source repository. Owner: {{OWNER}}. Remove the section if there is
nothing outside the repository. -->

- Product owner: {{OWNER}}.
- Repository created {{DATE}}.
