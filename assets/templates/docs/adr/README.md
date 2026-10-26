# Architecture Decision Records

**Rule**: if a decision affects several developers or agents, or is hard to revert, write an ADR before implementing
it. Copy [`_template.md`](_template.md), number it with the next free id (three digits, never reused), keep it to
300-500 words, always include the "do nothing" option, and justify with evidence. **ADRs are never deleted**: a
replaced decision is marked `Superseded by ADR-nnn` and stays in place; a partly changed decision is marked `Amended`
with a dated note. Reference the ADR from commits (`Refs: ADR-004`) and, once code exists, from a one-line comment at
the place that implements it.

Status values: `Proposed` (written, not yet accepted), `Accepted`, `Superseded by ADR-nnn`, `Amended` (accepted and
changed in part by a later decision; see the ADR's Notes).

<!-- FILL: One row per ADR, in id order, added in the same change that adds the ADR. Title is the ADR's title; a
short parenthesis may say what superseded or amended part of it. Date is the date the ADR was written. -->

| Id | Title | Status | Date |
|---|---|---|---|
| [ADR-001](ADR-001-record-architecture-decisions.md) | Record architecture decisions | Accepted | {{DATE}} |

**Totals**: 1 in total - Accepted 1, Proposed 0, Amended 0, Superseded 0.

<!-- FILL: This Totals line is the canonical count of ADRs by status. Update it in the same change as any row above.
Other documents (handoff.md, roadmap.md exit criteria, docs/README.md) link to this index instead of repeating the
numbers. Amended counts as its own status here, not as Accepted. -->

## Relationships

<!-- FILL: One sentence per relationship that is not obvious from the titles: "ADR-00x refines ADR-00y (does not
supersede it)", "ADR-00x supersedes ADR-00y", "ADR-00x amends ADR-00y and ADR-00z (what changed)". Decisions by the
product owner behind ADRs are listed in ../decision-log.md. Remove the section while there are none. -->

## Deferred decisions (write the ADR when the trigger fires)

<!-- FILL: Decisions that are known to be needed but not yet, each with the event that makes it due. Remove a row
when its ADR is written (the ADR cites the row's trigger in its Context). -->

| Candidate | Trigger |
|---|---|
| <!-- FILL: e.g. "Single sign-on for devices outside the domain" --> | <!-- FILL: e.g. "first user who cannot use the domain sign-in" --> |
