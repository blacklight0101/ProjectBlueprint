# Build plan: from finished docs to task cards, difficulty bands, verifier and gates

Read this when the documentation set is complete enough to plan the build (stage "build plan" of the skill), when
the owner asks for the task cards, or when a review changes the plan. It tells you how to produce and maintain:

- `docs/orchestration/README.md` - the protocol (build settings, bands, card life cycle, merge rules, builder rules,
  verifier summary, human gates, parallelism and usage throttle, follow-up cards, stop conditions, count sync);
- `docs/orchestration/tasks.md` - the task cards with the canonical totals table and the ownership table;
- `.claude/agents/{orchestrator,builder-haiku,builder-sonnet,builder-opus,builder-fable,verifier,verifier-opus}.md` -
  the agent definitions. The report and verdict formats live only in the agent files; the protocol points to them.

All three start from `assets/templates/` and are filled, never written from scratch. Worked example of a finished
plan (read-only; never copy its content): `docs/orchestration/` in https://github.com/blacklight0101/Rosetta (a plan after 404 cards ran through
pull requests, with its `.claude/agents/`).

## 1. Preconditions

Plan only when these hold; otherwise go back to the interview or the docs set first.

- `docs/roadmap.md` has phases P0..Pn, each with scope and exit criteria. P0 is the documentation phase and gets no
  cards.
- `docs/spec/requirements.md` has RF/RNF ids with priorities (Must/Should/Could) and Given/When/Then, RF ranges
  reserved per module, and a Q-nn table where every open question has an owner, a "needed by" phase and a default.
- The ADRs that fix the stack, the data access, the authentication and the test discipline exist (Accepted or
  Proposed).
- `docs/architecture.md` names the layers, the solution layout and the components; `docs/data-model.md` names the
  tables and assigns sequence numbers (migrations) per block; `docs/design-system.md` names the shared components;
  `docs/environments-and-delivery.md` names environments, secrets placement and source control.
- `CLAUDE.md` lists the hard rules (they become builder rules and verifier greps).

If a card would need a decision that no document makes, do not make it inside the card. Add a Q-nn with a default (or
an ADR) first, then cut the card against it.

## 2. Phases from the roadmap

- One section in `tasks.md` per roadmap phase from P1 on, titled `## Phase <n> - <name>` with the roadmap's name.
- Every card belongs to exactly one phase; its id is `P<phase>-nn`, numbered from 01 in the order a reader should see
  them (usually dependency order). Ids are never renumbered later; new cards take the next free number of their phase.
- The phase's exit criteria from the roadmap must each be reachable by some card's *Done when*. A criterion no card
  delivers is either a missing card or a human gate.
- Typical shape for a line-of-business application (adapt, do not force):
  - P1 Foundation: scaffold, database bootstrap and migrations runner, authentication and authorization, UI shell and
    design tokens, logging and error handling, runbook and preview configuration, E2E harness and pyramid report.
  - P2..Pn-1: one phase per group of modules or integrations in roadmap order; inside each, vertical slices (domain,
    persistence, service, page) and one adapter card per external system with its fake and contract test; one E2E
    card per phase that delivers user journeys.
  - Every phase ends with a verification-matrix card (`docs/verification/<phase>-matrix.md`, format in
    `references/verification-matrix.md`): every requirement of the phase mapped to the tests that name it, the
    phase's measured targets, the owner's review, gaps turned into follow-up cards, the pyramid line. The last build
    phase adds the release matrix, a security review card, documentation and training cards.
  - Rollout phase (when the roadmap has one): rehearsal on the target environment, data import from the old system,
    parallel run, cutover. These are the cards human gates G-04 and G-05 block.
- Games and apps without a database drop the database cards and add the equivalents that matter (asset pipeline,
  save-game format, build and signing, store listing).
- There is no separate follow-up phase. A follow-up or fix card takes the next free `P<phase>-nn` of the phase that
  owns the affected work (the phase of the card whose verdict or defect produced it) and is appended at the end of
  that phase's section, with `Follow-up:` at the start of its title and the originating card in its Refs. This keeps
  every card id in the one `P<phase>-nn` scheme. Expect them to outnumber the planned cards: on the Rosetta build
  232 of 404 cards were follow-ups, so the follow-up rules matter more than the first cut. Before taking a number,
  check that no issue or pull request already used it (issues are sometimes opened for cards never appended).
- A phase the owner wants to hold (polish, a later module set) gets a phase-start gate and the line "No card of this
  phase starts until the owner opens the phase" under its heading. A phase with a deadline carries its postponement
  order (which features leave first if it runs late).

## 3. Cutting cards

A card is one unit a builder can finish and a verifier can check in one sitting. Signals:

Sizes are agent working time, not person days: agents finish a card in minutes to hours.

| Size | Agent working time | Typical content |
|---|---|---|
| S | up to about 1 hour | one component, one page, one adapter method set, a document; a handful of files |
| M | about 2 to 3 hours | one vertical slice (domain + persistence + service + page) or one integration adapter with its fake |
| L | about 4 to 6 hours | a foundation piece many cards build on (authentication, the shell, the aggregate and its state machine) |

- Nothing larger than L. Split when a card spans two modules, carries two very different difficulty levels (cut the
  hard part out into its own fable card), touches two serialized resources, or has a *Done when* list longer than
  about eight checks.
- Merge when a card cannot be verified on its own (a "create the interface" card whose only check is that it compiles
  belongs with its first implementation).
- **Ownership**: every shared component, table, sequence-number block, script and module has exactly one owning card.
  A card that needs it depends on the owner. Keep the owners in the ownership table of `tasks.md` (card, what it
  owns); on the Rosetta build that table reached about 25 rows and stopped parallel cards from creating the same file.
- **Pre-allocated numbers**: when parallel cards each need a new value of a numbered series (error codes, migration
  numbers, prompt versions, ports), the orchestrator allocates the numbers in the briefs.
- **One creator per shared document**: a card that creates a document (for example `docs/testing-strategy.md`) is the
  only one that creates it; later cards add sections.
- **Standard cards to consider**: scaffold; database bootstrap; authentication and authorization; UI shell and tokens
  (gated by G-02); logging and error handling; runbook and preview configuration (`.claude/launch.json` so the
  verifier can walk pages); E2E harness and pyramid report; one E2E card per phase with journeys; verification matrix;
  security review; data import; cutover. Also:
  - **Docs consistency tests** (P1): tests that parse the ADR index Totals and the `tasks.md` Totals and fail when a
    count drifts. On the worked build they caught a status change committed without its count.
  - **Demo seed** (the phase that delivers the main workflow): a real legacy sample (bank 7.7) so the owner's
    hands-on review shows familiar data; local and dev only; every row in a state the app could have produced.
  - **Master-data maintenance** (bank 1.10): the admin screen or the documented script for people, teams and
    other rows that change after go-live. A plan where release 1 has no way to add a person is a hole.

## 4. Rating difficulty and choosing the model

Every card gets a **Difficulty** from 1 to 10, and the difficulty picks the builder's model band. The bands are named
after the Claude model aliases the Agent tool accepts; when models change, keep the criteria and change only the
`model:` lines of the agent files and the band table of the protocol.

| Difficulty | Band | Choose when | Examples |
|---|---|---|---|
| 1-5 | `haiku` | routine and fully specified; a pattern exists to copy; the probes are written; a mistake is cheap and visible | text and wording, resource strings, docs, small fixes with a reproducing test, CRUD on an existing pattern, fakes from a written contract |
| 6-8 | `sonnet` | substantial; several collaborators; needs judgement inside a documented design | vertical slices, adapters against a documented protocol, background jobs, multi-step UI flows, E2E journeys, the E2E harness |
| 9-10 | `opus` | a mistake leaks a secret, grants access wrongly, loses or corrupts data, doubles an external side effect or needs a manual production fix | authentication and authorization, secrets, concurrency and idempotency, money or legal records, migration and import, cutover, the security review |
| escalation | `fable` | never at plan time; only for the third attempt at a card, with the owner's approval in chat | - |

- The cost-of-a-mistake test decides ties: if in doubt, take the higher band. A card on a security or privacy
  boundary is at least `sonnet`, and its verifier is the strongest available.
- The owner may move the bands (opus builders everywhere, no haiku, fable as a native band when usage allows): record
  it as a DEC-nn and change only the `model:` lines, the band table and the Difficulty field's band names.
- **haiku** works for code when the card is fully specified, names a pattern file, lists its probes and has a
  reproducing test to make pass; it fails on judgement (on an earlier build a haiku builder given a vague
  code-and-test card delivered a placeholder test). Keep vague or cross-cutting cards out of the haiku band.
- **Local models** (for example a 9B model through Ollama) are not builders: on the Rosetta trial one reformatted
  generated files, reported success while its Done-when check failed and lost track on the second round. Use them only
  for scripted difficulty 1-2 cards with exact commands, never as verifiers, and re-run every check yourself.
- **Verifier band**: `verifier` (sonnet) for difficulty 1-8 and `verifier-opus` for 9-10; the verifier moves up with
  the builder when a card is promoted. A model never verifies its own work at a lower band.
- **Retry ladder**: FAIL 1 goes back to the same builder (its context is intact); FAIL 2 goes to a fresh builder one
  band up (never down); FAIL 3 runs `builder-fable` only after the owner approves it in chat; a later FAIL escalates
  the card to the owner and blocks its chain. A follow-up of a card that failed twice is rated one band above it.
- **The mix depends on the plan, not on a target.** With fable available as a native band, a line-of-business plan
  lands near a quarter sonnet, two fifths opus and a quarter fable; under a subscription plan with fable as
  escalation only, the Rosetta build landed at a quarter haiku, two thirds sonnet and less than a tenth opus. Far
  more of the top band than the risk warrants usually means cards are too big; nearly all of the bottom band usually
  means the risky parts are hidden inside routine cards.

## 5. Writing each field

Fields in this order, one per line (template `assets/templates/docs/orchestration/tasks.md`): Difficulty, Size,
Depends on, Gate, Status, Reads, Do, Behaviour to preserve (optional), Review probes (optional), Delivers, Done when,
Refs.

- **Difficulty**: `n (band)`, for example `7 (sonnet)`. **Size**: `S` | `M` | `L`.
- **Depends on**: direct prerequisites only, as card ids, or `none`. Do not list transitive ones.
- **Gate**: `G-nn` ids or `none`. A gate that blocks only part of a card names the part in the Status.
- **Status**: `Todo` when planned; `Blocked (G-nn)` when a gate on the card itself is closed; `Todo; <part> Blocked
  (Q-nn)` when one part waits on a question without a safe default.
- **Reads**: the exact sections the builder needs, beyond the common reads stated once in the `tasks.md` header, for
  example "`docs/data-model.md` sections on conventions, the identity tables and grants". Name a pattern file by path
  when the card copies one. Aim for at most six entries; more means the card is too big.
- **Do**: imperative sentences naming types, paths, tables, routes and rules, with every decision already made by the
  documents. No "consider", "maybe", "choose between". If the builder would have to decide something, it is a Q-nn or
  an ADR first.
  State the rule the card protects (the invariant) and give concrete hostile Given/When/Then examples, not "fix X".
  Name the rule, not a list of blocked spellings: on the Rosetta build a secret masker patched one spelling per round
  took five rounds until the card said "mask the value after these options, whatever its shape". Contract examples
  come from the spec or the owner, never from the builder: a test written by the same agent as the code mirrors its
  misunderstanding.
- **Behaviour to preserve** (follow-up, fix and hardening cards): what must not change, with the test that pins it.
  When a builder is unsure and a default would change today's behaviour, it keeps `main`'s behaviour and raises an
  open question instead.
- **Review probes** (cards with a guard, a parser or a security rule): the adversarial inputs the verifier will try.
  The builder gets the same list and runs it before the pull request; most first-round FAILs on the Rosetta build
  were bypasses only the verifier knew to try. Every guard the card adds needs a test that fails when the guard is
  removed. Keep the list to what matters: longer self-invented probe lists cost more and did not raise the first-pass
  rate (measured over four cards).
- **Delivers**: files and artifacts by path, and the tests by level ("unit tests for every invariant; integration tests
  for the repository"). Cards that might touch the same files never run in parallel.
- **Done when**: only checks the verifier can run, beyond its standard checklist: commands with expected results, test
  filters, greps with the expected empty result, schema or file comparisons, browser checks with page, viewport and
  expected behaviour, and the requirement ids whose Given/When/Then must each have a passing test. Bad: "the page works
  well". Good: "the verifier walks `/admin/users` at 1366x768 light and dark, adds a user from the fake directory and
  sees it in the list; RF-012 and RF-013 scenarios each have a passing test".
- **Refs**: RF, RNF, ADR, DEC, Q and DEF ids the card implements or must respect. Every Must requirement of the phase
  appears in at least one card's Refs, and the spec's traceability matrix names the card in the row of every
  requirement it refs (follow-up cards included).

## 6. Dependencies

- The graph must be acyclic. Fan out early: after the scaffold, the database, domain and shell cards should be able to
  run in parallel.
- Find the critical path (the longest chain of M and L cards) and shorten it: split long L cards on it, move
  work that does not need to be on it to parallel cards.
- Cards that touch the same serialized resource (migrations folder, composition root, package manifests) still get an
  explicit dependency only when one needs the other's output; otherwise the orchestrator serializes them at run time
  (protocol section 8).
- Check the plan with the snippet in section 11 before handing it over.

## 7. Human gates

Gates are points where a person must approve before cards may run. Each has an id `G-nn`, a holder (a named person,
usually the product owner), an opening condition and the exact cards it blocks. Default set (keep those that apply,
add project-specific ones with the next free id):

| Gate | Held by | Opens when | Blocks |
|---|---|---|---|
| G-01 Requirements and RFC accepted | product owner | RFC and spec set to Accepted; open questions answered or defaults accepted | P1-01, hence everything |
| G-02 Design board approved | product owner | design board from the brief approved and folded into the design system | UI shell card and every page card |
| G-03 Source control remote ready | product owner or IT | remote exists and `main` is pushed | the Phase 1 exit |
| G-04 Production access granted | product owner or IT | production environment exists, access granted | first production deployment card |
| G-05 Cutover approved | product owner | verification matrix without Must gaps, security review without BLOCKING, runbook signed | cutover or go-live card |

- **Phase-start gates**: a phase the owner holds (polish, a later module set) gets its own gate; no card of it starts
  until the owner opens it.
- **Partial blocks**: a gate that blocks only part of a card names the part ("live checks Blocked (G-04); the rest
  runs") so the rest is not held up.
- **Owner checks do not block a merge.** Checks only the owner can make (watch a real run, sign in on the hosted URL)
  are listed by the verifier as "owner check pending", go to the owner's agenda in `handoff.md`, and close when the
  owner reports them; the card waits in `In review` until then, its code merged.
- **A phase may close with an unmet target** when the verification matrix states the gap plainly and each gap has a
  follow-up card; the owner decides, and the decision is recorded.

- Project-specific gates: an external team's approval, hardware or credentials becoming available, a spike reviewed
  before its ADR becomes Accepted.
- A provisional G-01 (the owner's go-ahead before the formal review) may release P1-01 only; record it as
  `Provisional` in `handoff.md` with a note naming the released cards.
- Gate state (`Closed`, `Provisional`, `Open`) lives only in the Gates table of `handoff.md`, written by or for the
  holder with the date; the criteria live only in protocol section 7, with the same ids and names. The orchestrator
  never opens a gate.

## 8. Test discipline as configuration

The protocol's section 1 (build settings) holds every test setting; builder rules and verifier steps refer to it.
House defaults (from the .NET house preset, `references/presets/dotnet-house.md`), all on unless the owner decides
otherwise with a DEC-nn and, for the pyramid, an ADR:

- Test-first: failing test, code, refactor; branch history shows tests before or with code.
- Pyramid 60/30/10 unit/integration/E2E by test count per release, 10 points tolerance, every test marked with a
  Level (xUnit `[Trait("Level", ...)]`, or simply the test folder: `tests/unit`, `tests/integration`, `tests/e2e`);
  a pyramid report script delivered by the E2E harness card that also fails on a stale report or a test outside the
  level folders. Test names start with the requirement id they prove.
- Coverage per module tier (bank 7.8) instead of one global number; a test that can never fail is a finding. Whether the
  share blocks or only warns is bank 7.2 (default: warns, with an opt-in switch such as `-EnforcePyramid`); a test
  without a Level marker, or a run that counts zero tests, always fails the gate. Do not file rebalancing cards for a
  guideline pyramid.
- SOLID and KISS as verifier findings (MAJOR at a port or service boundary, MINOR otherwise).
- E2E cards: one harness card in P1, one journey card per phase that delivers user journeys.
- Red check by the verifier: check out the `test:` commit in a detached worktree and confirm the new tests fail on an
  assertion (not on a missing import); a guard test must fail when the guard is removed.
- Mutation check by the verifier (stub one type in a disposable worktree, a test must fail).
- Page walk by the verifier with the browser preview tools for every card that delivers or changes a page.

Other stacks keep the same shape with their own markers: NUnit `[Category]` for Unity (EditMode as unit, PlayMode as
integration or E2E), Vitest plus Playwright for a Phaser or web front end (file suffixes or tags as the level marker),
JUnit, Robolectric and Espresso for Android. A project without UI sets the page walk to off; a prototype may lower the
pyramid, recorded as a DEC-nn.

## 9. Filling the protocol and the agent files

- Section 1 of the protocol: the build and test commands, level marker, pyramid, E2E tool, preview entry and
  viewports (from `docs/design-system.md`), serialized resources, requirement comment syntax.
- Section 2: one project-specific sentence on what is difficulty 9-10 here; delete the band rows nobody uses.
- Section 5.1: one grep row per greppable hard rule of `CLAUDE.md` and `docs/conventions.md`, with exact patterns and
  an "allowed where" column. With CI, add a row for `${{` inside a `run:` step (shell injection). Write patterns that
  a secret scanner looks for in a self-safe form (`Passwor[d]=`).
- Section 7: the gates with holders and blocked card ids, matching the Gate fields of the cards.
- Agent files: replace `{{PROJECT}}` and `{{OWNER}}`; fill each builder's short hard-rule list with the rules that band
  breaks most often; keep the frontmatter keys (`name`, `description`, `model`, and `tools` on the verifiers) and the
  report and verdict blocks exactly. Delete the files of bands the owner does not use.
- Also fill `AGENTS.md` (the tool-neutral index) with the same start order, verify command and top rules.
- Remove every `<!-- FILL` comment; run `scripts/check_docs.py` (it also checks that every *Depends on* id is a card
  and that the dependencies form no cycle), then the snippet in section 11.

## 10. Running the build

The build starts in a later session, after G-01 (or a provisional G-01) is recorded in `handoff.md`.

1. The main session reads the protocol, `tasks.md` and `handoff.md`, either by following the protocol itself or
   by being started as the orchestrator (`claude --agent orchestrator`). The orchestrator is never launched as a
   subagent through the Agent tool: subagents cannot spawn subagents, so it could not dispatch any builder.
2. It computes the ready set: `Todo` cards whose dependencies are all `Done` and whose gates are open.
3. It dispatches ready cards in parallel, one builder subagent per card in its own git worktree (the Agent tool's
   worktree isolation when available, otherwise `git worktree add`), only when their
   *Delivers* paths are disjoint and they share no serialized resource, up to the builders-in-flight limit.
4. After each builder report it spawns the verifier of the card's band; on PASS it merges under the merge rules
   (10.1) and records `Done`; on FAIL it runs the retry ladder of section 4.
5. MINOR findings and later defects become follow-up cards in the owning phase (a failing reproducing test first).
6. It stops at gates, escalations, contradictions between documents, hard-rule conflicts and unreachable
   environments, and ends every session with `main` clean and `handoff.md` current.

### 10.1 Merge rules

Two variants; the protocol's section 3.1 holds the one the project uses (bank 8.10).

**Local only (no remote).** `git merge --ff-only` and check the exit code, not the printed text. A branch nobody has
pushed may be rebased onto `main` (`git rebase --onto main <old-base> <branch>`, `--update-refs` for stacked
branches); re-run the tests, then merge.

**Remote with pull requests (GitHub and similar).** Nothing reaches `main` except through a pull request: one issue
per card (milestone = phase), one branch per issue, one pull request per branch closing its issue. The orchestrator
merges only when all of these hold, re-checked right before the merge:

1. CI is green on the head commit.
2. The verifier's PASS is posted on the pull request.
3. The branch is up to date with `main`. A pushed branch is updated by merging `main` into it, never by a rebase and a
   force-push; the verifier re-confirms when the merge touched the card's files.
4. The pull request changes nothing in the spec, ADRs, RFCs, the decision log or `CLAUDE.md`. One that does gets the
   label `needs-owner`; only the owner merges it (or the owner delegates it for a session, recorded as a dated DEC).
5. `gh pr merge --squash --delete-branch` exits 0. The tool may ask the owner once per session before the first
   `gh pr merge`, even under a delegation; ask at the start of a merge run, not per pull request. GitHub auto-merge
   is off unless the owner turned it on.

Builders never edit `tasks.md` or `handoff.md` on task branches (parallel status edits conflict on every merge). The
orchestrator records `Done` lines, follow-up cards, gate releases and resume entries in one batched
`docs/build-status` pull request after a run of merges; until it merges, the closed issue is the record. The first
card (the scaffold) is the one exception: CI does not exist before it.

### 10.2 Usage throttle

On a subscription plan the usage window, not the card count, sets the pace. Read the plan usage before every launch
and after every finish, estimate the launch (a builder takes about 10-15 % of a 5-hour window, a verifier 5-10 %),
and start only what the band allows:

| Window used | What may start |
|---|---|
| below 50 % | any agent, up to the owner's limit in flight |
| 50-70 % | only verifiers and fix rounds |
| 70-85 % | only the orchestrator's own work (merges, status pull requests) |
| 85 % or more | nothing; record the hold in `handoff.md` and wake up after the reset |

The percentages and the agents-in-flight limit are the owner's (bank 8.7) and change during a build; record each
change as a DEC. Round-1 verifiers cap their probes (about 20-30); later rounds probe only the changed code and the
earlier findings. A running agent is never killed; to pause, it commits its work as `wip:` and stops, and on
"continue" it is resumed with SendMessage instead of starting over. For unattended work use a scheduled heartbeat that
resumes the build and reports only on a merge, a failure, a hold or a question; delete it when the work is done.
Prepare the handover before a usage pause or an account switch, not after.

### 10.3 Clean-up

The merge step removes the card's builder and verifier worktrees (`git worktree remove`, then `git worktree prune`)
and deletes its local and remote branch; the session-end checklist lists what is left and asks before deleting
folders. On the Rosetta build nobody cleaned up after merges and 107 worktrees, 138 local and 249 remote branches had
to be removed in bulk. Keep any worktree a running Docker Compose project uses as its working folder (check the
`com.docker.compose.project.working_dir` label of the containers first).

### 10.4 Lessons from running a build

From the worked builds (an earlier build: 211 cards with at most 3 agents in flight; Rosetta: 404 cards through pull
requests under a usage throttle):

- **Push after each merge or batch of merges** when the owner asked for it.
- **Never read success from a grep of build output.** A running preview locks the build output (in .NET the Debug
  DLLs: MSB3021/MSB3026 copy errors show as "N Error(s)"); build in another configuration (`-c Release`) or stop the
  preview, and read the exit code.
- **PR CI is the authority.** A full local verify run on every card was retired on the Rosetta build (CPU-bound,
  load time-outs); builders run the related tests and CI runs the whole gate. When CI fails on `main`, stop and fix
  that first. A flaky test may hide a real bug (one intermittent failure was a real upload defect); card it.
- **Verifier minors that are pure wording** (a resource string, a doc sentence) may be fixed by the orchestrator on
  the branch before merge, with the matching test updated; everything else becomes a follow-up card.
- **The owner's hands-on review changes the product.** On the worked build it removed a rule (an office minimum),
  added a screen (the manager sets fixed days) and found a bug in seeded data. Plan for it (bank 8.9): record each
  change as a DEC-nn, mark withdrawn requirements `Withdrawn YYYY-MM-DD - see DEC-nn`, add RF ids for new behaviour,
  amend ADRs, then cut cards.
- **A bug report from the owner** (an error id on screen) is traced in the logs first, reproduced by a failing test,
  then fixed in a follow-up card. When seeded data caused it, fix the seed and recreate the local database from the
  migrations (ask first; the owner may have test data in it).
- **Patterns that the secrets scan looks for** must not appear literally in documents (a security review listing
  `Password=`); write them self-safe, for example `Passwor[d]=`, instead of adding allow-list entries.
- **Parallel UI cards collide in shared files.** Resource files (`.resx`), architecture allow-lists and shared test
  files conflict on almost every merge of a parallel batch. Resolve resource conflicts by union (keep both blocks,
  check every `<data>` closes), and after each merge run a clean full build: a stale build output reported a resource
  key as missing, and a test stub broke because a parallel card had added a member to the interface it fakes.
- **Flaky keyboard or focus E2E steps point at a real defect.** On the worked build they came from the page heading
  rendering only after data loaded, so `FocusOnNavigate` missed it and the focus stayed on the body (an accessibility
  bug). A "wait until focus settles" in the test is a stopgap; cut a follow-up card that fixes the page (render the
  `h1` outside the loading branch) and removes the wait. Put "the heading renders before data loads" in UI cards'
  Done when.
- **Date navigation needs boundary tests.** A verifier failed a view whose previous/next week arrows ran past the
  supported years and crashed. Cards with date pickers or week arrows list the first and last supported dates in
  their tests.
- **Verifiers work only in the branch's worktree.** One verifier rewrote a file in the main checkout (encoding change).
  After each verifier, run `git status` on `main` and restore anything it touched.
- **Feature branches for the owner to walk.** When the owner wants to try a change before it lands ("make a branch,
  we test, then merge"), build the cards on one feature branch, start a preview from it, and merge to `main` only
  after the owner says so. Some owners also set a phase rule "never commit or push unless I ask": keep `main` local
  until asked, then push everything in one go with `handoff.md` updated.
- **Agent definitions load only from the session's project folder.** When the session's working directory is a
  parent folder, `.claude/agents/builder-*.md` are not available as agent types; launch a general-purpose subagent
  with the chosen model and tell it to read and follow the builder or verifier file.
- **Agents bypass hooks unless told otherwise.** Builders used `--no-verify` and overrode `core.hooksPath`. The brief
  says: never skip, override or bypass hooks; add files by explicit path; never a bare `git stash`; never kill
  processes by image name (one `taskkill /IM node.exe` killed every agent's work), only by the PID you started.
  Agents install with `--ignore-scripts` (or the stack's equivalent), because worktrees share one `.git/hooks`, and
  CI re-runs every hook check as the backstop.
- **One writer per seat.** Give every agent full paths and its own log folder (agents overwrote a shared
  `/tmp/verify.log`); when a second session or account may take over, a lease file stops two orchestrators driving
  the same build.
- **Evaluate the product on real inputs** after the main workflow runs, in a separate Compose project with its own
  ports and data, never against the owner's stack; give each finding an id (EV-nn) so cards cite it. A build trial
  from the delivered output alone shows what the documents lack better than any review.
- **Scope freeze near a deadline** (bank 8.11): fix only what stops the journey, gives wrong content or loses data;
  card the rest behind a phase gate.
- **Windows machine hygiene.** Reserved TCP ports (for example 56074-56473; check `netsh int ipv4 show
  excludedportrange`); the 8191-character command line of `npx` on Windows (call `node node_modules/<tool>/<bin>`
  instead); a running app locks build output; Docker Desktop stops when WSL stops; `MSYS_NO_PATHCONV=1` for
  `docker compose exec` with absolute container paths in Git Bash; Windows Update restarts during overnight runs.
- **Show the work at the end of a phase.** For a stakeholder deck, capture real screens with a small Playwright
  script on the installed browser (`Channel = "msedge"`), blur the focused element before each shot, and use the
  app's own impersonation or test mode to capture other roles' screens; say so to the owner, since it is logged.
- **Session end**: clean up as in 10.3; update `handoff.md` (status line, waiting-for-owner list, resume point) in the
  same push, and grep it for claims that are no longer true (an open pull request that merged, a card still listed as
  left); it goes stale fast during a build.

Builders and verifiers run as Agent-tool subagents. A Workflow script may drive the build only when the user has
opted in for this session (said "ultracode", asked for a workflow or multi-agent orchestration, or ultracode is on);
otherwise offer it with a rough cost and ask (see `references/workflows.md`).

## 11. Keeping the plan consistent

- **Counts**: the totals table at the top of `tasks.md` is the only canonical place for card counts per phase, band
  and size. `handoff.md` and the protocol link to it; if they repeat a number, re-check it on every change. Any change
  that adds, withdraws or re-rates a card updates the table in the same commit. Counts drift constantly; the review
  loop checks them (`references/review-loop.md`).
- **Stable ids**: never renumber or reuse a card id. A withdrawn card keeps its heading; its Status becomes
  `Blocked (withdrawn YYYY-MM-DD - see <id>)` and it stays in the Cards and Withdrawn columns of the totals.
- **Only Status lines move during the build**: the orchestrator edits Status lines and appends follow-up cards. Any
  other card change is a plan change made through the review loop, with a DEC-nn when the owner decided it.
- **Checks before handing over** (run from the repository root; the snippet parses the card format of the template):

```python
import re, collections
text = open("docs/orchestration/tasks.md", encoding="utf-8").read()
spec = open("docs/spec/requirements.md", encoding="utf-8").read()
cards = {}
for block in re.split(r"(?m)^### ", text)[1:]:
    head = block.splitlines()[0]
    m = re.match(r"(P\d+-\d{2,3}) - ", head)
    if not m:
        continue
    f = dict(re.findall(r"(?m)^- \*\*([A-Za-z ]+)\*\*: (.*)$", block))
    missing = [k for k in ("Difficulty", "Size", "Depends on", "Gate", "Status", "Reads", "Do",
                           "Delivers", "Done when", "Refs") if k not in f]
    if missing:
        print("MISSING FIELDS", m.group(1), missing)
    cards[m.group(1)] = f
deps = {c: [d for d in re.findall(r"P\d+-\d{2,3}", f.get("Depends on", ""))] for c, f in cards.items()}
for c, ds in deps.items():
    for d in ds:
        if d not in cards:
            print("UNKNOWN DEPENDENCY", c, "->", d)
state = {}
def visit(c, path):
    if state.get(c) == 1:
        print("CYCLE", " -> ".join(path + [c])); return
    if state.get(c) == 2:
        return
    state[c] = 1
    for d in deps.get(c, []):
        visit(d, path + [c])
    state[c] = 2
for c in cards:
    visit(c, [])
bands = collections.Counter(re.sub(r"[^a-z]", "", f.get("Difficulty", "? (?)").split("(")[-1]) or "?"
                            for f in cards.values())
print("cards", len(cards), dict(bands))
refs = " ".join(f.get("Refs", "") for f in cards.values())
musts = re.findall(r"(?m)^\*\*((?:RF|RNF)-\d{3})\b[^\n]*\bMust\b", spec)
uncovered = [r for r in musts if r not in refs]
print("Must ids without a card:", uncovered or "none")
```

  The Must detection assumes the spec template's requirement line: the bold id and title at the start of the line,
  followed on the same line by the release and the priority (`**RF-001 Title** ... R1 ... Must ...`); adjust the
  regular expression if the spec's layout differs. Ranges in Refs (`RF-010..RF-015`) are not expanded, so write
  explicit ids for Must requirements. Compare the printed counts with the totals table.
- **Review lenses for the plan** (used by the review loop): every Must covered; every gate in the protocol matches the
  cards' Gate fields; every *Reads* section exists; every sequence number assigned in `docs/data-model.md` belongs to
  exactly one card; no card makes a decision the documents do not; band distribution sane; counts match; every card
  in a requirement's Refs appears in that requirement's traceability row.
