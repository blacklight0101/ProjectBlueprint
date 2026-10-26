# Context for agents

| | |
|---|---|
| **Status** | Living ({{DATE}}) |
| **Scope** | the exact shapes agents must use instead of guessing: schemas, API contracts, sample payloads, a glossary of names in code |
| **Related** | [architecture](../architecture.md), [data model](../data-model.md), [conventions](../conventions.md), [requirements](../spec/requirements.md) glossary |

Agents read this folder when a card names it. Each file here is either generated from the source of truth (and says
by what command) or copied from an external contract with its version and date. Nothing here is a design decision:
when a file disagrees with the architecture or the data model, those win and this file is regenerated.

<!-- FILL: one row per file in this folder. Add files only when a card needs them; delete this folder when there is no
schema or contract to hand agents (scaffold.py --without context). -->

| File | What it holds | Source | Refreshed by |
|---|---|---|---|
| <!-- FILL: example row, replace --> `schema.sql` | the current database schema | generated from the migrations | `<command>` after every migration card |
| <!-- FILL: example row, replace --> `external-system-a-openapi.json` | the external API contract, version n | copied from the vendor on YYYY-MM-DD | by hand when the vendor publishes a new version |
| <!-- FILL: example row, replace --> `samples/` | measured real-shaped sample inputs (no personal data) | built by the fixtures card | the fixtures card |
