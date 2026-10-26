# {{PROJECT}} - Handoff

_Last updated {{DATE}}. Phase **P0 - documentation**. No code yet._

<!-- FILL: Keep the line above to one sentence: date, current phase in bold with a few words of state, and whether
code exists. Rewrite it at the end of every session. This file is the living state: read it first when resuming,
update it last before stopping. It is not a design document; link to docs/ instead of restating their content. Keep
it under about 30 KB: move resume entries older than the last two or three and finished agenda items to
docs/journal/. A long handoff full of stale claims misleads the next session. -->

## Waiting for the owner

<!-- FILL: Everything only the owner can do, newest first, one line each with the date it started waiting and what it
blocks: pull requests labelled needs-owner, owner checks pending, escalations, approvals (fable escalation, a merge
run), hand-in steps (record, upload, submit). Remove a line when it is done and note the date in the session log.
Write "Nothing." when empty. -->

- Nothing.

## Current state

<!-- FILL: One bullet per document or package that exists, newest additions first once the list is long, each with
its status and the one fact a person resuming needs (for example "Status: Proposed", "ids RF-001..RF-045").
Do not repeat counts that have a canonical home: link docs/adr/README.md for ADR counts and
docs/orchestration/tasks.md for card counts. -->

- `README.md`, `CLAUDE.md` (rules), this file.
- `docs/rfc/RFC-001-{{PROJECT_SLUG}}.md` - design proposal, **Status: Proposed**.
- `docs/spec/requirements.md` - release 1 requirements, **Status: Proposed**; open questions in its section 4.
- `docs/adr/` - decision records; counts by status in the [index](docs/adr/README.md).
- `docs/decision-log.md` - the product owner's decisions.

## Resume point

<!-- FILL: Where work stopped and what happens next, written so that someone with no memory of the last session can
continue. Before writing it, check every "in flight", "running" or "pending" claim against the repository. Three parts:
State: one or two sentences (what is complete and reconciled, what is half done and where).
Next, in this order: a numbered list of the next three to six actions, each naming the document, card or question.
Blockers: what cannot move until the owner or a third party answers (name the Q-nn or G-nn). -->

State: <!-- FILL: one or two sentences -->

Next, in this order:
1. <!-- FILL: next action -->

Blockers: <!-- FILL: Q-nn / G-nn and who owes the answer, or "none" -->

## Agenda for the next session (ask the owner first)

<!-- FILL: What to ask or settle with the product owner before any other work, numbered, one topic per item, each
with the decision needed and the document it lands in. Ask with defaults (see CLAUDE.md). When an item is settled,
strike it through and add the result, so the history stays readable:
"1. ~~Data model walk-through~~ DONE YYYY-MM-DD: docs/data-model.md + ADR-00n; decisions DEC-nn..DEC-nn."
Typical pre-build agenda: data model walk-through; design system (brief, board, fold back); environments, secrets,
source control and CI, package baseline, naming, error handling and user-facing behaviour when something is down,
observability, release and versioning; the date of the review that opens gate G-01. -->

1. <!-- FILL: topic - decision needed - lands in <document> -->

## Gates

Criteria for each gate are defined once in [docs/orchestration/README.md](docs/orchestration/README.md) (section
Human gates). This table records only their state. Open a gate by setting State to `Open` with the date and who
opened it; a `Provisional` gate names the only cards it releases.

| Gate | Name | State | Since | Note |
|---|---|---|---|---|
| G-01 | Requirements and RFC accepted | Closed | - | <!-- FILL: who reviews, when; e.g. "review date to be set by the owner" --> |
| G-02 | Design board approved | Closed | - | |
| G-03 | Source control remote ready | Closed | - | |
| G-04 | Production access granted | Closed | - | |
| G-05 | Cutover approved | Closed | - | |

<!-- FILL: One row per gate defined in docs/orchestration/README.md, same ids and names (drop the rows of gates the
protocol drops, add the project's own). State is one of Closed, Provisional, Open. -->

## Decisions pending

<!-- FILL: ADRs still Proposed and what accepts them (a spike, a gate, an answer); open questions whose default is
currently applied (list the Q-nn ids and link the spec's section 4, do not restate the defaults); deferred topics
with the trigger that brings them back. Remove the section when empty. -->

## Session log

<!-- FILL: Newest first. One bullet per session: bold date (add a short label in brackets when there were several
sessions that day), then what changed in one to four sentences, naming the ids touched (RF, ADR, DEC, cards) and
whether the work was committed. Never edit an old entry; correct it in a new one. -->

- **{{DATE}}** - Documentation set created from the kick-off interview with {{OWNER}}. Kick-off decisions recorded in
  `docs/decision-log.md`. No code.
