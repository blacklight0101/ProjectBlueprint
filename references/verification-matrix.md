# Verification matrix: the evidence that closes a phase

Read this when cutting a phase's verification-matrix card, when building one, or when the owner asks whether a phase
is done. A matrix is a document in the project's `docs/verification/` folder, one per phase and one per release:
`m1-matrix.md` for a milestone, `p2-matrix.md` for phase 2, `r1-matrix.md` for release 1. It is written by a card
(Difficulty 9, opus), never by the orchestrator, and it changes no code. Worked examples (read-only):
`docs/verification/` in https://github.com/blacklight0101/Rosetta (`m1-matrix.md` with a security review, `r1-matrix.md` with
journeys, `p2-matrix.md` with a golden-set section).

## 1. What it must answer

1. Does every requirement of the phase have evidence (tests that name it, or a recorded manual or owner check)?
2. Does any Must lack evidence? (The exit rule: no Must without evidence or a follow-up card.)
3. Did the phase meet its measured targets (the RFC's success criteria, the roadmap's exit criteria)?
4. What did the owner's hands-on review change?
5. What is left, and which card holds each gap?

## 2. Sections

| # | Section | Content |
|---|---|---|
| - | Header table | Card, Date, Commit reviewed (and what later commits changed, if any), Reviewer, Inputs |
| 1 | Summary | requirements in scope by priority; how many have tests; Musts without evidence; phase cards Done; targets met or not; owner review; pyramid line |
| 2 | Method | what ran (local or CI run id), the counting rule (section 3), where the counts came from; a later matrix may point to an earlier one instead of repeating this |
| 3 | Requirement matrix | Id, Requirement, Priority, Tests U / I / E, one example `path:line`, State (`Tests pass`, `Owner check pending`, `Gap: card P<n>-nn`) |
| 4 | Targets | each measured target with its value, the run it came from, and Met / **Not met** with the card that takes it |
| 5 | Owner review | date, what was reviewed, the DEC rows and cards it produced |
| 6 | Findings (optional) | F-nn with severity, for a matrix that also reviews (security, journeys) |
| 7 | Gaps and follow-up cards | Id, priority, what is missing, card, card state |
| 8 | Open questions | Q-nn raised by the review, with defaults |
| 9 | Pyramid | the CI test-levels line, shares against the target and tolerance |

Optional sections: a security review (threat-model rows, OWASP or LLM Top 10 checks, hard-rule greps) for the first
milestone or release; the release journeys for a release matrix; an evaluation section (golden set) when the
product calls an AI model.

## 3. Counting rule

- A test counts for a requirement when its own title carries the id, or a range that holds it (`RF-260..RF-263`). A
  test that names the id only in its `describe` title is not counted; say so in the method, since counts then differ
  from an earlier matrix that counted differently.
- Take the titles from the test runner's list command rather than a full run: `vitest list --json` and
  `playwright test --list --reporter=json` (or the stack's equivalent). On Windows, call the runner through `node`
  (`node node_modules/vitest/vitest.mjs list ...`) and pass the files in batches: `npx` runs through `cmd` and fails
  past 8191 characters. Files that only hold a shared contract suite (no test of their own) make `list` fail; leave
  them out and say so.
- "Tests pass" means a named CI run on the same content passed; give its run id.
- The pyramid numbers come from the CI test-levels step, not from the list.
- One example per requirement, an end-to-end test when there is one. Check that the line is inside a test whose title
  carries the id.

## 4. Rules

- **No Must without evidence or a follow-up card.** A Must whose only tests check a document (a runbook, a checklist)
  waits on a hosted or owner check; name the card that holds it.
- **Owner checks are recorded as reported.** "The owner opened the sample report on 2026-10-26" or "reported done by
  the owner on 2026-10-26", never a measured value nobody pasted.
- **A phase may close with an unmet target.** State it plainly in the summary and the targets table (**Not met**), and
  give each gap a follow-up card; the owner decides whether the phase closes. On the Rosetta build phase 2 closed with
  the cost-estimate target unmet and two follow-up cards.
- **Gaps become cards in the owning phase**, appended under the follow-up rules of `references/build-plan.md`
  section 2, traced in the spec's traceability matrix, and the totals table updated in the same change.
- **A decision the review produces is applied everywhere**, the threat model included (`SKILL.md` section 4).
- The matrix is checked by a verifier like any card: the scope equals the roadmap backlog row, priorities match the
  spec, examples exist and sit inside a test that names the id, figures match their source.
