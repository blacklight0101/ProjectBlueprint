# AGENTS.md - {{PROJECT}}

A short, tool-neutral index for any coding agent. The full rules are in [CLAUDE.md](CLAUDE.md); when the two differ,
CLAUDE.md wins and this file is corrected. Keep this file under about 60 lines.

## Start here

1. [handoff.md](handoff.md) - current state, what waits for the owner, where to resume.
2. [CLAUDE.md](CLAUDE.md) - sources of truth, hard rules, commit policy.
3. [docs/orchestration/README.md](docs/orchestration/README.md) - how cards are built, verified and merged.
4. The card you were given in [docs/orchestration/tasks.md](docs/orchestration/tasks.md) and its Reads list.

## Commands

<!-- FILL: the exact commands from docs/orchestration/README.md section 1. -->

| What | Command |
|---|---|
| Install | <!-- FILL --> |
| Build | <!-- FILL --> |
| Test | <!-- FILL --> |
| Verify (every gate, as CI runs it) | <!-- FILL --> |

## Rules that are broken most often

<!-- FILL: five to eight one-line rules copied from CLAUDE.md, e.g. "no secret in any committed file",
"requirements get an id before code", "never weaken a gate to get green". -->

- Never renumber or reuse an id; never edit `docs/spec`, `docs/adr` or `docs/decision-log.md` from a card.
- Test first: the failing test is committed before the code that makes it pass.
- Never skip hooks, never force-push, add files by explicit path.

## Layout

<!-- FILL: the top-level folders, one line each; the detailed layout is docs/architecture.md. -->
