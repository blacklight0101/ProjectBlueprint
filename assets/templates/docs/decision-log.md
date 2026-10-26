# Decision log

| | |
|---|---|
| **Status** | Living |
| **Date** | {{DATE}} |
| **Owner** | {{OWNER}} |
| **Related** | [Requirements](spec/requirements.md) - [ADRs](adr/README.md) - [Tasks](orchestration/tasks.md) |

Product decisions taken by {{OWNER}}, the product owner, in the order they were taken. `DEC-nn` ids are the owner's
decisions; `Q-nn` ids are the open questions in [requirements.md section 4](spec/requirements.md#4-open-questions);
`ADR-nnn` ids are architecture decisions that may implement a DEC. <!-- FILL: add "`DEF-nn` ids in
[legacy-sources.md](legacy-sources.md) are defects of the system being replaced, not decisions." when that document
exists; otherwise remove this comment. -->

Rules:

- **Append only.** The Decision text of a row is never edited. When a later decision changes an earlier one, add a
  new row that says so (`Replaces DEC-07: ...`) and add "replaced by DEC-nn" to the old row's Where applied cell.
- **Answer to** names what prompted the decision: an open question (`Q-nn`); the kick-off question it answers
  (its id in the interview bank, for example `0.7`); a review round (`Review YYYY-MM-DD`); or `Owner` when the owner
  raised it unprompted. Never a conversation handle such as `#4` or a plan-internal finding id: they mean nothing
  outside the session.
- **Where applied** lists every requirement, ADR, card and document section the decision changed, filled when the
  change is made. A decision whose Where applied cell is empty has not been applied yet; review treats that as a
  finding. An answered question's Status becomes `Answered (DEC-nn)` in the same change.
- A decision the owner has not actually taken is never written here. Undecided points stay open questions with a
  default in the requirements.

## Kick-off scope decisions

<!-- FILL: The decisions locked with the owner before any document was written (name, first deliverable, version
control, release 1 scope, main integrations, where the documents live, document language, stack or stack preset).
Phrase each as "Chosen: X. Instead of: Y." so the rejected option is on record. They take the first ids. -->

| Id | Date | Decision | Answer to | Where applied |
|---|---|---|---|---|
| DEC-01 | {{DATE}} | <!-- FILL: e.g. "Chosen: documents only as the first deliverable. Instead of: documents plus a compiling skeleton." --> | <!-- FILL: kick-off question id, e.g. 0.6 --> | <!-- FILL: e.g. README.md, roadmap.md P0 --> |

## Later decisions

<!-- FILL: One row per later decision, continuing the numbering from the table above (never restarting it). Group
rows under a dated sub-heading per session when there are many, for example "### YYYY-MM-DD - review of the
documentation set". -->

| Id | Date | Decision | Answer to | Where applied |
|---|---|---|---|---|
| <!-- FILL: DEC-nn --> | <!-- FILL: YYYY-MM-DD --> | <!-- FILL: the decision in one to three sentences, specific enough to check --> | <!-- FILL: Q-nn / Review YYYY-MM-DD / Owner --> | <!-- FILL: RF-nnn, ADR-nnn, P1-03, document section --> |
