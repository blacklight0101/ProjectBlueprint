# Workflows: the multi-agent kit

How to run the parallel steps of the skill (review, plan, apply, final pass; also any large drafting step) with
the Workflow tool, and how to run the same steps without it. The step-by-step method is in `review-loop.md`;
this file covers the machinery.

## When the Workflow tool may be used

Use the Workflow tool only when the user has opted in:

- the user said "ultracode", or a system reminder says ultracode is on;
- the user asked for a workflow, or for multi-agent orchestration, for this work.

Otherwise run the same steps as **parallel Agent-tool subagents** (see "Fallback" below), or offer the
workflow in one or two lines with the agent count and a rough cost, and wait for a yes. Example offer: "The
review can run as a workflow of 7 agents (3 reviewers, 3 skeptics, 1 merger); each reads 10-20 documents, so
expect roughly 1-2 M tokens in total. Run it as a workflow, or with parallel subagents here?"

Rough cost guide for a full docs set (15-40 files): a reviewer or editor that reads its slice fully uses
roughly 100-300 k tokens; a planner or critic that reads the plan plus the repository uses 200-500 k. Say the
agent count and the range; never promise a precise number.

## The kit

| Template | Step | Agents (defaults) | Reads | Writes |
|---|---|---|---|---|
| `assets/workflows/review.js` | 1 Review | 3 reviewers, up to 3 skeptics, 1 merger (7) | the repository, optional check_docs output | `<scratch>/review-findings-DATE.md` |
| `assets/workflows/plan-changes.js` | 4 Plan and 5 Amend | 0-n researchers, 1 planner, 3 critics, 1 reviser (5 plus research) | findings, decisions, research, repository | `<scratch>/change-plan.md`, `research-*.md`, `change-plan.vN.bak.md` |
| `assets/workflows/apply-changes.js` | 6 Apply and 7 lenses | 1 preflight, 3 per group, 4 checkers plus up to one fixer per group per round | plan, decisions | the repository files of each group |
| `assets/workflows/final-pass.js` | 7 Final pass | 4 checkers plus 1 fixer per round | decisions, optional plan | any documentation file |

Every template returns structured data the main agent uses next: `review.js` returns the high findings to
spot-verify; `plan-changes.js` returns the groups (copy them into `apply-changes.js`), the key choices and
surprising facts to show the user, the open items, and a stale-term list for the sweeps; `apply-changes.js`
returns per-group results, cross-check rounds and the issues no group owns (seed them into `final-pass.js`).

Agent count: keep a workflow under about ten agents unless the user asked for more. `review.js` and
`plan-changes.js` fit. `apply-changes.js` does not for a full change set (six groups mean 18 agents before the
checkers): say so in the offer, or merge groups (3-4 groups for a medium change), or run the small-change
pattern of `review-loop.md` (one editor, one verifier, one fix) when only a few files change.

## Adapting a template

1. Copy the template into the session scratchpad with a project-specific name, for example
   `<scratch>/workflows/<project-slug>-review.js`. Never edit the skill's own copy.
2. Edit the constants at the top (the block ends with `---- end of configuration ----`). Every template
   refuses to start while a required constant still holds its ALL-CAPS placeholder. The same keys can be
   passed in the Workflow `args` object instead (args values win), which lets one saved script serve
   several runs.
3. Check the file is pure ASCII with LF endings (snippet below).
4. Launch with the Workflow tool, `scriptPath` = the copied file (or pass the filled script inline as
   `script`). Keep the returned run id for resume.

Constants per template (args key in brackets):

| Constant | review | plan | apply | final | Meaning |
|---|---|---|---|---|---|
| `PROJECT` (project) | yes | yes | yes | yes | display name |
| `REPO` (repo) | yes | yes | yes | yes | absolute repository path; double the backslashes in JS strings |
| `SCRATCH` (scratch) | yes | yes | yes | - | session scratchpad; outputs go here |
| `DATE` (date) | yes | yes | yes | yes | today, `YYYY-MM-DD`; scripts cannot read the clock |
| `OWNER` (owner) | yes | yes | yes | yes | product owner |
| `CONTEXT` (context) | yes | yes | yes | yes | 2-4 sentences: product, stack, current release |
| `SLICES` (slices) | yes | - | - | - | reviewer slices: key, title, files, focus |
| `CHECK_DOCS_OUT` (checkDocsOut) | yes | - | - | - | saved check_docs.py output, so reviewers skip mechanical issues |
| `VERIFY_HIGH` (verifyHigh) | yes | - | - | - | adversarial check of each slice's high findings |
| `FINDINGS` (findings) | - | yes | - | - | the review findings file |
| `DECISIONS` (decisions) | - | yes | yes | yes | every decisions file, oldest first |
| `MODE`, `NEW_DECISIONS`, `AMEND_TITLE`, `CRITIQUE_AFTER_AMEND` (mode, newDecisions, amendTitle, critiqueAfterAmend) | - | yes | - | - | `new` plan, or `amend` with the addendum files; critics also check an amendment unless switched off |
| `RESEARCH`, `SOURCES` (research, sources) | - | yes | - | - | optional research tasks (`{ key, task }`) and read-only sources |
| `GROUP_HINT` (groupHint) | - | yes | - | - | suggested editor groups for the planner |
| `PLAN` (plan) | - | yes | yes | optional | the canonical change plan |
| `AMENDMENTS` (amendments) | - | - | yes | - | names of the amendment sections editors must read |
| `GROUPS` (groups) | - | - | yes | - | editor groups from plan section 6: key, sections, files |
| `STALE_TERMS` (staleTerms) | - | - | yes | yes | grep list from the old design |
| `EXCLUDE`, `CHECK_DOCS` (exclude, checkDocs) | - | - | yes | yes | paths the checkers skip; path of the skill's scripts/check_docs.py |
| `PROTECTED` (protected) | - | - | - | yes | files the final fixer must never edit |
| `MAX_ROUNDS` (maxRounds) | - | - | yes | yes | cross-check rounds (defaults 3 and 4) |
| `FIX_LOW`, `SEED_ISSUES`, `EXTRA_LENSES` (fixLow, seedIssues, extraLenses) | - | - | - | yes | fix low issues once before stopping; issues carried over from apply; extra lens texts |
| `ALLOW_DIRTY` (allowDirty) | - | - | yes | - | apply on a dirty tree only when the owner accepted it |

Adjusting the prompts: the lens texts and the reviewer `focus` lines are the places to add project-specific
checks (for example "the run-state list is identical in the data model, the ADR and the flows"). Keep them
generic in the skill copy; put project terms only in the scratch copy.

ASCII and line-ending check (Python, run before launching):

```python
import pathlib, sys
for p in sys.argv[1:]:
    b = pathlib.Path(p).read_bytes()
    bad = [i for i, c in enumerate(b) if c > 127]
    cr = b.count(b"\r")
    print(p, "OK" if not bad and not cr else "non-ASCII at %s, CR bytes %d" % (bad[:5], cr))
```

When a script is generated or rewritten from Python, write it with
`open(path, "w", encoding="ascii", newline="\n")`; Python on Windows writes CRLF unless `newline="\n"` is given.

## Rules learned

- **Pure ASCII, LF only.** Scripts launched by `scriptPath` are rejected ("control characters") when they
  contain CR bytes or non-ASCII characters such as typographic quotes, section signs, arrows or en dashes.
  Write `section 3.1` instead of the section sign, `->` instead of an arrow, `-` instead of a dash.
- **meta is a pure literal**: no variables, function calls, spreads or template interpolation inside
  `export const meta = {...}`. Phase titles in `meta.phases` must match the `phase()` calls exactly.
- **No unescaped quotes in `meta.description`**: avoid apostrophes and double quotes entirely ("the owner
  decisions", not the possessive form).
- **Schemas for structured returns**: every agent whose output feeds code uses `schema`; the script never
  parses free text. `required` must be a subset of `properties`.
- **Disjoint file groups for parallel editors**: every file belongs to exactly one group; an editor edits only
  its files. Two editors on one file lose edits.
- **A single fixer for cross-file issues**: group-restricted fixers skip anything that spans groups, so the
  last step is one sequential fixer that may edit any file (`final-pass.js`).
- **Clean tree before applying**: `apply-changes.js` refuses a dirty tree. The only safe rollback of a
  partial run is `git checkout` of tracked files plus deleting the untracked files that run created.
- **Stopping and restarting**: when new decisions arrive mid-run, stop the workflow with TaskStop, revert the
  partial edits, amend the plan (`plan-changes.js` with `MODE = 'amend'`), and start the apply step again as a
  fresh run.
- **Never re-run a completed step that mutates a file in place** (an amend that backs up and rewrites the
  plan). Before a fresh run, remove or switch off that step; `apply-changes.js` never rewrites the plan for
  this reason.
- **Resume cache**: relaunching with `resumeFromRunId` reuses the longest unchanged prefix of agent calls.
  Changing ANY text of an agent prompt, including a constant interpolated into it, invalidates that call and
  every call after it. Fix constants before the first launch.
- **No clock or randomness**: `Date.now()`, `Math.random()` and `new Date()` throw inside scripts; pass the
  date as a constant or arg.
- **Pipelines by default**: use `pipeline()` when each item's stages are independent (editor -> verifier ->
  fix per group); use a barrier (`parallel()`) only when the next step needs all results (merging findings,
  routing cross-check issues).
- **Read the journal before re-running**: when a workflow returns something unexpected, read the run's
  `journal.jsonl` for each agent's actual return before changing the script.
- **Python or SQL with backslashes**: on Windows, bash heredocs mangle `\\` and `\U...` sequences; write the script
  to a file in the scratchpad and run it, or build paths without escapes.
- **Model and effort**: omit `model` so agents inherit the session model; set `effort` per agent (low for
  mechanical checks, high for reviewers, editors, verifiers and critics, xhigh for the planner).

## Fallback without the Workflow tool

Run each step as Agent-tool calls; independent agents go in ONE message so they run in parallel.

| Step | Agent calls |
|---|---|
| 1 Review | one message with 3 reviewer Agent calls (prompt = the reviewer prompt of `review.js` with the slice filled in); then merge the answers yourself and write the findings file; spot-verify the high ones yourself |
| 4 Plan | one message with the research agents (if any); then one planner Agent; then one message with 3 critic Agents; then the planner again for the revision |
| 5 Amend | one planner Agent with the amend prompt of `plan-changes.js` |
| 6 Apply | one message with one editor Agent per group; then one message with one verifier Agent per group; then fix Agents for the groups with issues |
| 7 Lenses | one message with 4 checker Agents; then one fixer Agent (any file); repeat until only low issues remain |

Copy the prompts from the templates so the fallback checks the same things, and ask each agent to end with the
same structured report (as a JSON block) so you can route issues.
