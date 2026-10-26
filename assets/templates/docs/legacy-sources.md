# Legacy sources, citation scheme and defect register

<!-- FILL: Write this document only when {{PROJECT}} replaces an existing system. With nothing to replace, do not
scaffold it, and remove its rows from docs/README.md, README.md and CLAUDE.md, and the DEF-nn mentions from the
requirements and the RFC. -->

The behaviour of the system being replaced is documented once, in the source notes listed below. This repository
cites those notes and never copies them. The legacy code is read-only reference material: builders read it to
understand behaviour and contracts, then re-derive the behaviour from the requirements; they never copy its logic.

| Key | Value |
|---|---|
| System being replaced | <!-- FILL: name and one line on what it is (technology, age, who uses it) --> |
| Legacy code location | <!-- FILL: absolute path; state "read-only, never edit, never run version-control commands there" --> |
| Source notes location | <!-- FILL: where the analysis notes live (a vault folder, a wiki space) --> |
| Citation prefix | <!-- FILL: a short uppercase prefix for citation keys, e.g. LEG --> |

## Source notes

<!-- FILL: One row per analysis note: the citation key, the note's name as it appears where it lives, and what it
holds (sections that matter, with their numbers). Typical notes: index (architecture, environments, vocabulary),
functional overview (menu map, business rules, message catalogue, defect list), one functional spec per area,
integrations (every external call with inputs and outputs), data model (tables, sentinel values, formats), findings
(risk register with file:line evidence). -->

| Citation key | Source note | What it holds |
|---|---|---|
| `[LEG-Overview]` | <!-- FILL: note name --> | <!-- FILL: e.g. purpose, menu map, business rules (section 4), defect list (section 6) --> |

Citation form: `[LEG-Overview sec. 4]` (note and section), or `[LEG-Integrations sec. 1 <call name>]` when one row matters.
Requirements carry the citation in their **Source** field; ADRs in Context or References.

<!-- FILL: Replace the prefix LEG in this document with the prefix chosen above, or keep LEG. -->

## Defect register (what the rewrite must not reproduce)

Numbered once here; the requirements, the RFC, the ADRs and CLAUDE.md cite `DEF-nn`. Decisions by the product owner
use `DEC-nn` in [decision-log.md](decision-log.md); they are not defects. Every row names where the defect is closed
(requirement, ADR or CLAUDE.md rule); a row with nothing in that column is a finding in review.

<!-- FILL: One row per structural defect, highest impact first (correctness with money or legal impact, security,
reliability, maintainability). Bold the short name of the worst ones. The example row is generic; replace it. -->

| Id | Legacy defect | Where it is closed |
|---|---|---|
| DEF-01 | <!-- FILL: e.g. "**Duplicate external writes**: a retry button re-sends the request with no idempotency key" [LEG-Findings sec. 3] --> | <!-- FILL: e.g. ADR-00n, RF-0nn, CLAUDE.md hard rule --> |

## Facts that are frozen because others depend on them

<!-- FILL: Formats, identifiers, contracts and calls that customers, regulators or other systems depend on, which the
rewrite must keep exactly (with the citation). Changing any of them needs an ADR. Remove the section if there are
none. -->

- <!-- FILL: frozen fact [LEG-... sec. n] -->

## Additional legacy variants

<!-- FILL: When a second copy or variant of the legacy system is analysed later (another site, another country,
another version), add a subsection with its own citation prefix and source-note table, and a defect closure table for
the defects that have no equivalent above (ids continue the DEF-nn sequence; shared defects cite the existing
DEF-nn). Remove this section while there is only one variant. -->
