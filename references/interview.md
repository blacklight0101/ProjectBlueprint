# Interview: asking before writing

How Claude interviews the user before any document exists, and the question bank it draws from. The same
question formats are reused later by the review loop (`references/review-loop.md`), so a user who has been
through one interview already knows how to answer the next batch.

Worked example: https://github.com/blacklight0101/Rosetta (its decision log, DEC-01..DEC-174: an interview that kept going through a
two-week agent build).

Contents: 1. Principles | 2. How to ask | 3. What must be answered before the first document | 4. Question bank | 5. The pre-build agenda | 6. From answers to documents

## 1. Principles

1. **Ask first, write second.** No document is written until the framing questions (section 4, Timing
   "Before writing") have an answer. Everything else can start from a stated default.
2. **Never invent an answer.** If the user has not decided something, it becomes an open question `Q-nn`
   with a stated default ("default applies until answered"). A guess written as a fact is a defect.
3. **Talk in the user's language, write in English.** Questions, playback tables and explanations follow
   the language the user writes or dictates in. Repository documents are always English. Ids (`RF-nnn`,
   `Q-nn`, `DEC-nn`, `ADR-nnn`, `G-nn`, `P1-03`) and code names are never translated.
4. **Every question carries a default and a reason.** The user can accept a whole batch with one word.
5. **Small batches, grouped by theme.** Better three short rounds than one wall of forty questions.
6. **Record as you go.** Two running tables (scope decisions, open questions) are kept in the conversation
   from the first answer and become `docs/decision-log.md` and the spec's open-question table at scaffold time.
7. **Plain words.** No emojis, no marketing tone, short sentences; explain a term the moment an answer shows
   it was not understood.
8. **Explain before asking, and never ask what the documents or the code already answer.** State what the thing
   does and what each option changes, then ask. On the Rosetta build the owner asked for this rule explicitly.
9. **When the owner is away, go on with the default and log it.** A question with a default never stalls the
   work: apply the default, record it as `Q-nn` with Status `Default applies`, and list it for the owner. Owners
   often answer a whole batch with "defaults".
10. **Check a default against the project's own limits before offering it.** A default that would break what
    users can do today (on Rosetta, a context size that made a default-cap run refuse to start) is not a default;
    keep today's behaviour and ask instead.

## 2. How to ask

### 2.1 The framing batch: AskUserQuestion

Open with the AskUserQuestion tool for the few questions that shape everything else.

- At most **4 questions per call**, each with **2 to 4 options**.
- The **recommended option goes first** and its label ends with `(Recommended)`.
- Every option has a one-line description saying what choosing it means in practice.
- The tool adds a free-text "Other" answer by itself; do not add one.
- Use multi-select only when several answers can be true at once (for example "which devices").
- Two calls are usually enough for framing (name and purpose, then deliverable, release slice, repository,
  project kind and stack). The stack question offers the preset that fits the project kind (0.12, 4.1), so
  the preset is known before the deeper rounds start.
- Open questions without natural options (the one-line purpose, the name of the product owner) go in a short
  plain-text question next to the call, not as fake options.

Example of one framing call (shape only):

| Question | Options (first = recommended) |
|---|---|
| What should the first deliverable be? | Docs only (Recommended) - the full design set, no code yet / Docs plus a compiling skeleton / Code straight away with lighter docs |
| Is this replacing an existing system? | No, it is new (Recommended when nothing is mentioned) / Yes, it replaces one system / Yes, it replaces several |
| Where does the repository live? | Local git, remote added later (Recommended) / New GitHub repository now / Company server (Azure DevOps, TFS, GitLab) |
| Which stack? | The house preset that fits the project kind (Recommended) / Another stack I will describe |

### 2.2 Larger batches: the numbered question table

When more than four questions are due, post a numbered markdown table instead of AskUserQuestion:

| # | Question | Default | Why it matters |
|---|---|---|---|
| 1 | Keep history of every change to master data? | Yes, an audit table per catalogue | Decides audit columns and one extra table per catalogue |
| 2 | How long is business data kept? | 3 years, then purged by a job | Decides the purge job and a retention setting |

Rules:
- Numbers `#1..#n` run on through the whole session so "#14" is unambiguous. They are conversation handles,
  not document ids; `Q-nn` and `DEC-nn` are assigned only when something is recorded.
- End the table with one line in the user's language, for example: "Reply `defaults` to accept all, or
  `defaults except #4, #9` and give your answers for those."
- 6 to 12 rows per table. Split by theme when there are more.
- The default is always a concrete answer, never "to be decided".
- "Why it matters" names the consequence (a table, a screen, a cost, a risk), not a generic benefit.

### 2.3 Group batches by theme

Follow the phases of the bank (section 4). Within a phase, put the questions with the widest consequences
first. In a review round, group as the review loop does: business rules, architecture, orchestration and
design, still owed from earlier rounds.

### 2.4 Explain jargon when an answer shows confusion

Signs of confusion: the user answers a different question, asks "what does that mean", or gives an answer
that contradicts an earlier one. Then re-ask that one question alone, in plain words, with a concrete
example from the user's own domain and the consequence of each answer. Example: instead of "Should the
outbox be at-least-once?" say "If the other system does not answer, should we keep the record and send it
again later (it may arrive twice, and the other side must ignore the copy), or stop and show an error so
someone retries by hand?". Never mark a question answered from a reply the user gave while confused.

### 2.5 Play back long or dictated answers

Voice-dictated or long answers are messy: numbers get lost, two answers merge, a "no" hides in a subordinate
clause. Before using them, show a "What I recorded" table, one row per answer:

| # | What you said (short) | Recorded as | Lands in |
|---|---|---|---|
| 4 | keep it three years, but never delete open items | Retention 3 years; unresolved records never purged | spec RNF, data model, ADR |
| 9 | (unclear: "same as the other one") | Not recorded - asked again below | - |

Then ask: "Correct anything that is wrong; silence means this is what I will write." Unclear answers are
re-asked in plain words right under the table, never guessed.

### 2.6 Raise the follow-ups the answers create

Every answer can open new questions. After each round, list them before moving on. Typical chains:
- "It must work when the other system is down" -> what is queued, how long a queue may grow, who is alerted,
  what the user sees while it waits.
- "Several people can work the same record" -> locking or last-write-wins, what the second person sees.
- "We replace the old system" -> history import or not, parallel run or big-bang cutover, who compares results.
- "Shared accounts on shared devices" -> how an individual is identified for the audit trail, which actions
  a shared account may never perform.

Follow-ups go into the next batch with their own defaults; they do not block the current round.

### 2.7 Undecided items become Q-nn

Anything the user does not decide (skips, says "not sure", "ask X", "later") becomes an open question in the
spec's open-question table (`docs/spec/requirements.md`):

| Id | Question | Owner | Needed by | Default | Status |
|---|---|---|---|---|---|
| Q-01 | How long is business data kept? | Product owner | P3 | 3 years, then purged by a job | Default applies |

- **Owner** is a role or a person who can answer (product owner, security team, vendor), not "TBD".
- **Needed by** is a phase (`P2`), a task card (`P2-04`) or a gate (`G-02`): the latest point at which the
  default stops being safe.
- **Status** is one of `Open` (no safe default, work that depends on it waits), `Default applies` (work goes
  on with the default), `Answered (DEC-nn)`, `Withdrawn` (the row keeps its id: "Withdrawn YYYY-MM-DD - see ...").
- Ids are never renumbered or reused.

### 2.8 The running scope-decisions table

From the first answer, keep one table in the conversation and show it again after each round:

| Question | Chosen | Instead of |
|---|---|---|
| First deliverable | Docs only | Docs plus skeleton; code first |
| Release 1 | One user group, the core workflow end to end | Every group at once |

- **Instead of** names the options that were rejected, so later readers see what was on the table.
- An explicitly accepted default ("defaults except #4") is a decision and gets a row. A question the user
  never saw or skipped is not a decision; it is a `Q-nn` with Status `Default applies`.
- At scaffold time every row becomes a `DEC-nn` entry in `docs/decision-log.md`
  (`Id | Date | Decision | Answer to | Where applied`), where "Answer to" is the bank id (for example `0.7`) or
  the `Q-nn` it closes (for a follow-up with neither, a few words naming the question; `#n` handles are not
  used because they mean nothing outside the conversation), and "Where applied" lists the documents,
  requirements and ADRs that carry it. The table itself is also copied into the RFC's scope section and the
  README.
- Later decisions add rows (and `DEC-nn` entries); old rows are never edited. A reversed decision gets a new
  row that says which earlier `DEC-nn` it replaces.

### 2.9 Pace and stopping

- The order is fixed:
  1. framing (phase 0, including the project kind and the stack or preset question);
  2. preset playback, when the user took one (`references/presets/README.md` section 2);
  3. bank phases 1 (users and workflows) and 2 (integrations), the rounds that shape the requirement
     ranges and the context diagram;
  4. scaffold and write the first documents (README, CLAUDE.md, RFC, spec skeleton) so the user sees progress;
  5. the remaining phases 3 to 9, one theme per round. Rows with Timing `Pre-build` may wait for the pre-build
     agenda (section 5); rows with Timing `Can default` that nobody answers become `Q-nn`.
- Do not ask about something a chosen preset already answers; show the preset's answers in one "What I
  recorded" table instead and let the user override rows. Skip those rows in every later round.
- Stop asking when the remaining questions all have safe defaults and their "Needed by" is later than the
  current work; they live on as `Q-nn`.
- When the user says "continue" or "go on" at the start of a session and an agenda of questions is recorded
  in `handoff.md`, raise that agenda first; do not start work around it.

## 3. What must be answered before the first document

Only the framing questions marked "Before writing" in section 4.0 block writing: the name and code, the
one-line purpose, the product owner, whether it replaces an existing system, the first deliverable, the
release-1 slice and the repository location (local folder and system of record). The project kind (0.12) and
the stack or preset choice (4.1) are also needed, because they decide which preset or checklist the rest of
the interview uses. Everything else can start from its default and is recorded as `Q-nn` (Status
`Default applies`) until answered.

## 4. Question bank

Columns: **Id** is the bank id (phase.number, cited in the decision log's "Answer to" column); **Default** is
what Claude proposes when the user has no preference; **Lands in** is the document that records the answer;
**Timing** is `Before writing` (blocks the first document), `Pre-build` (settled in the pre-build agenda,
section 5, before the build plan is handed over; default applies until then) or `Can default` (becomes a
`Q-nn` if unanswered).

Document short names: README, CLAUDE (`CLAUDE.md`), handoff, RFC (`docs/rfc/RFC-001-{{PROJECT_SLUG}}.md`),
spec (`docs/spec/requirements.md`), ADR (`docs/adr/`), arch (`docs/architecture.md`), data (`docs/data-model.md`),
conv (`docs/conventions.md`), env (`docs/environments-and-delivery.md`), design (`docs/design-system.md`),
brief (`docs/design-system-brief.md`), roadmap (`docs/roadmap.md`), legacy (`docs/legacy-sources.md`),
flows (`docs/process-flows.md`), decisions (`docs/decision-log.md`), orch (`docs/orchestration/README.md`),
tasks (`docs/orchestration/tasks.md`).

The bank is a menu, not a script. A small project may need only phase 0, phase 4 and a handful of others.

### 4.0 Framing

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 0.1 | What is the product called (display name)? | A working name proposed from the purpose, marked as provisional | README, all | Before writing |
| 0.2 | Short code and file slug? | Code = 3 to 4 uppercase letters from the name; slug = kebab-case of the name | README, CLAUDE, RFC file name | Before writing |
| 0.3 | In one sentence, what does it do and for whom? | None: the user must say it; Claude may offer a draft to correct | README, RFC summary | Before writing |
| 0.4 | Who sponsors it and who is the product owner (answers questions, signs off)? | The user is both | README, decisions, orch gates | Before writing |
| 0.5 | Does it replace an existing system? Which one, and can Claude read it? | No | legacy (only when yes), RFC context, roadmap cutover | Before writing |
| 0.6 | First deliverable: docs only, docs plus a compiling skeleton, or code with lighter docs? | Docs only | RFC, roadmap P0, handoff | Before writing |
| 0.7 | What is the release-1 slice (smallest useful end-to-end piece)? | One user group, the core workflow end to end, everything else later | RFC scope, spec, roadmap | Before writing |
| 0.8 | Any deadlines or fixed dates (demo, go-live, contract)? | None fixed; phases are sized, not dated | roadmap, RFC | Can default |
| 0.9 | Where does the repository live: the local folder path, and the system of record (local git, GitHub, company server such as TFS)? Will the code later move to a system without git? | A new folder `<parent of the current working directory>/<ProjectName in PascalCase>`, local git on `main`, remote added before the first code phase; build and verify scripts never depend on git (walk the file system instead of `git ls-files`), so the code survives a move to TFS or a plain folder | CLAUDE (local path), env, orch gates; the folder is the scaffold `--target` | Before writing |
| 0.10 | Who reviews the documents and signs off the acceptance gate? When? | The product owner; review date set at the end of the pre-build agenda | orch gates, handoff | Pre-build |
| 0.11 | Where do repository docs live versus personal notes (a notes vault, wiki)? | Repository `docs/` is the source of truth; notes only index and mirror | CLAUDE, README | Can default |
| 0.12 | What kind of project is it (business web app, browser game, Unity game, Android app, other)? | Inferred from the purpose; confirmed in the framing call | selects the preset or checklist (`references/presets/README.md`) | Before writing |
| 0.13 | How big and how clear is it? Small and clear: a light set; large or long-lived: the full set; goal still unclear: a spike first, documents after | The full set for more than one module or more than about a week of build; the light set (README, CLAUDE, AGENTS, handoff, requirements, roadmap, tasks) otherwise | the set itself (SKILL.md step 0), RFC "Spec level" line | Before writing |
| 0.14 | Which delivery steps can only the owner do (record a video, upload, submit a form, sign, deploy), and how long before the deadline must each start? | Each owner step is a dated item in the roadmap and the handoff agenda, started no later than three days before the deadline; a hand-in card keeps a checklist that a test reads | roadmap, handoff, tasks | Can default |

Documents are written in English; this is a convention of the skill, not a question. Ask only if the user
raises it, and record the answer as a scope decision.

### 4.1 Users, roles and main workflows

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 1.1 | Who uses it? List the actors and roughly how many of each. | Three roles: user, supervisor or approver, administrator | spec actors, RFC | Can default |
| 1.2 | What are the three to five main workflows, start to finish? | Drafted by Claude from the purpose, then corrected by the user | spec, flows | Pre-build |
| 1.3 | Which devices and where (office desktop, shared terminal, tablet, phone, kiosk)? | Office desktop browser | spec RNF, design | Can default |
| 1.4 | Personal accounts only, or shared accounts on shared devices? If shared, how is the individual identified for the audit trail? | Personal accounts only | spec, ADR | Can default |
| 1.5 | Permissions model: fixed roles, or roles made of permission codes an admin can edit? | Permission codes grouped into editable roles; code checks the permission, never the role name | spec, arch, conv, ADR | Can default |
| 1.6 | Where do users come from (company directory, self sign-up, admin-created)? | Company directory, admin grants access | spec, arch, ADR | Can default |
| 1.7 | Which user-interface languages at launch, and may more be added later without code changes? | English only, catalogue-ready | spec RNF, design, conv | Can default |
| 1.8 | Must any workflow keep working without the network or without another system? | No | spec RNF, arch, ADR | Can default |
| 1.9 | Is anything sensitive (personal data, pay, health, anonymity promises)? | No special category | spec RNF, data, ADR | Can default |
| 1.10 | How are people, teams and other master data (the rows that change after go-live) added, changed and deactivated in release 1: an admin screen, a documented script, or a seed migration? Who does it? | A minimal admin screen for whatever changes more than a few times a year; otherwise a documented, transactional script per entity named in the runbook. Never "later release" with no path at all | spec, roadmap, runbook, tasks | Pre-build |
| 1.11 | Which rules are fixed per person by a manager (usual days, quotas, limits) and which may the person change, and with whose approval? | Ask with a concrete example from the legacy process; the owner's real practice usually differs from the first description | spec, data, flows | Pre-build |

### 4.2 Integrations

Ask 2.2 to 2.7 once per external system named in 2.1.

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 2.1 | Which external systems does it talk to (read, write, receive from)? | None | RFC context diagram, arch, spec | Can default |
| 2.2 | Direction and trigger: we call them, they call us, file drop, shared database? | We call them through an API | arch, spec | Can default |
| 2.3 | Synchronous (user waits) or asynchronous (queued, user continues)? | Reads synchronous, writes queued with a retry | arch, ADR | Can default |
| 2.4 | What happens when that system is down: block, degrade, or queue and catch up? What does the user see? | Queue and catch up; the user sees a clear status, never "press again" | spec RNF, conv, ADR | Pre-build |
| 2.5 | Can a write reach them twice? Do they de-duplicate on a key we send? | Every write carries an idempotency key persisted before the call | arch, ADR | Can default |
| 2.6 | Who owns the contract (vendor, other team), and is there a test instance or documentation? | Other team owns it; Claude records the contract as a fixture when the card is built | spec Q, arch, roadmap gates | Can default |
| 2.7 | How do we authenticate to them, and where does the credential live? | Service account; secret outside the repository | env, ADR | Pre-build |
| 2.8 | Will other systems need to call us (inbound API)? | Not in release 1; framework only if a caller is already known | spec, arch, ADR | Can default |

### 4.3 Data

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 3.1 | What are the main things the system keeps (entities) and how do they relate? | Drafted by Claude from the workflows, walked through in the pre-build agenda | data, arch | Pre-build |
| 3.2 | Rough volumes: rows per day, users at the same time, largest table in five years? | Small (thousands of rows per day, tens of users) | data, spec RNF | Can default |
| 3.3 | Import history from an old system, start empty, or keep the old system read-only for lookups? | Start empty; old system kept read-only | data, legacy, roadmap, ADR | Pre-build |
| 3.4 | How long is data kept, and what is purged or archived? | 3 years, then purged by a job; unresolved records never purged automatically | spec RNF, data, ADR | Pre-build |
| 3.5 | One installation for everyone, or one per site, customer or tenant? One database or several? | One installation, one database | arch, env, ADR | Pre-build |
| 3.6 | Time zones, calendars, shifts or business days that affect rules? | One time zone; store UTC, display local; no business calendar | data, conv, spec | Can default |
| 3.7 | What must be audited (who changed what, when, before and after)? | Every write by a user is audited with before and after values | spec, data | Can default |
| 3.8 | Reports or exports needed at launch? | Two or three lists with Excel or CSV export | spec, roadmap | Can default |
| 3.9 | Who maintains reference data (catalogues, settings) and through which screens? | Administrators through admin pages; seeds only for fixed catalogues | spec, data | Can default |

### 4.4 Stack

The preset is offered in the framing call (`references/presets/README.md` section 2). If the user took one,
its answers were played back as a "What I recorded" table; ask only what the preset leaves open. Otherwise ask:

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 4.1 | Use a house preset? | The preset that matches the project kind (0.12) | ADR, arch, conv, env, CLAUDE | Pre-build (usually already answered in the framing call) |
| 4.2 | Runtime and language? | The one the user's other projects use | ADR, arch | Pre-build |
| 4.3 | User interface technology? | Server-rendered web UI | ADR, arch, design | Pre-build |
| 4.4 | Data access style (ORM or hand-written SQL)? | Hand-written, parameterised SQL through a thin mapper | ADR, conv | Pre-build |
| 4.5 | Database? | The one the team already operates | ADR, data, env | Pre-build |
| 4.6 | Hosting (on-premises server, cloud service, container, device store)? | Where the team's other apps run | ADR, env | Pre-build |
| 4.7 | Authentication (company sign-on, local accounts, external identity provider)? | Company single sign-on | ADR, arch | Pre-build |
| 4.8 | Background work (scheduled jobs, queues) and where it runs? | In-process hosted services with a lease, no scheduler product | ADR, arch | Can default |
| 4.9 | Package policy: which libraries are allowed, and is a new one an ADR? | Short baseline list with exact versions; anything else needs an ADR | env, CLAUDE | Pre-build |
| 4.10 | Package age: adopt a new version only after it has been public for a while? | Only versions at least two weeks old (the update bot's cooldown is 14 days); a release that fixes a published security advisory is adopted at once; every bump also updates the pinned version in the baseline table | env, conv, CLAUDE | Can default |

### 4.5 User interface and design system

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 5.1 | Is there a brand (colours, fonts, logo) to follow? Who approves it? | Neutral palette with one accent; values marked provisional until approved | design, brief | Pre-build |
| 5.2 | Target devices and screen sizes (smallest and largest)? | 1366x768 to 1920x1080 desktop | design, spec RNF | Pre-build |
| 5.3 | Theme: light, dark, both, follow the operating system? | Light default with a dark toggle | design | Can default |
| 5.4 | Accessibility level? | WCAG 2.1 AA | design, spec RNF | Can default |
| 5.5 | A UI component library, or a small own component set on design tokens? | Own small component set on tokens | design, ADR | Pre-build |
| 5.6 | Run a design round trip: Claude writes a brief, the user runs it in a design tool, the result is folded back as design system v2? | Yes, before the first UI card | brief, design, roadmap | Pre-build |
| 5.7 | Any printed or device output (labels, receipts, reports, badges)? | None | design, spec, ADR | Pre-build |
| 5.8 | Error and wait behaviour the user sees (messages, retries, reconnect)? | Plain message with an error code and a correlation id; never a stack trace; no "press again" | conv, design | Pre-build |

### 4.6 Environments and delivery

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 6.1 | Which environments (dev, test, pilot, production) and where does each run? | Dev on the developer machine; test and production on the team's servers | env, roadmap gates | Pre-build |
| 6.2 | Where do secrets live in each environment? | Dev: user secrets; servers: environment variables or protected config outside the repository | env, ADR, CLAUDE | Pre-build |
| 6.3 | Continuous integration: a server pipeline now, or a local verify script with a pipeline file prepared? | Local verify script now; pipeline file committed but inactive | env | Pre-build |
| 6.4 | Versioning and releases (scheme, release notes, who deploys, deployment windows)? | `MAJOR.MINOR.PATCH`, a release notes file, manual deployment by the product owner | env, roadmap | Pre-build |
| 6.5 | Observability: logs, health page, alerts, who watches? | Structured logs with correlation ids, a health page, alerts to developers only | env, arch, spec RNF | Pre-build |
| 6.6 | Backup and restore: who owns it, how often, tested when? | The team's standard server backups; a restore test before go-live | env, spec RNF | Pre-build |
| 6.7 | Who approves a deployment to production? | The product owner | env, orch gates | Can default |
| 6.8 | Cutover (only when replacing a system): big-bang, parallel run, or gradual? | Parallel run for a fixed period, then switch | roadmap, legacy, orch gates | Pre-build |
| 6.9 | Repository host settings (only with a remote such as GitHub): branch rules, required checks, auto-merge? | A ruleset on `main` (no direct push, no force-push, linear history, squash only, the required checks); auto-merge off unless the owner turns it on | env, orch | Pre-build |
| 6.10 | Does the application call an AI model or handle untrusted content (uploads, repositories, web pages)? | No. When yes: a threat model with an AI section (prompt injection, untrusted text rendered as text, no execution of model output, secrets never in prompts, invented package names), one API key per project, per-run and per-day cost caps, and an evaluation plan (7.9) | spec RNF, `docs/security/threat-model.md`, env, ADR | Pre-build |
| 6.11 | How is the configuration checked at start? | A typed configuration schema that refuses to start on a missing or invalid value (fail fast); a secret committed by mistake is rotated, never only deleted | env, conv | Can default |

### 4.7 Testing

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 7.1 | Test-first (write the failing test, then the code)? | Yes | ADR, CLAUDE, orch verifier | Can default |
| 7.2 | Test pyramid by count (unit / integration / end-to-end)? Enforced (the verify gate fails) or a guideline (it warns)? | 60 / 30 / 10 with ten points tolerance, each test labelled with its level; a guideline that warns, with an opt-in switch to enforce; a test without a level marker, or a run that counts zero tests, always fails | ADR, spec RNF, CLAUDE | Can default |
| 7.3 | Which journeys get end-to-end browser or device tests? | One per main workflow from 1.2 | tasks, arch | Pre-build |
| 7.4 | Test data: fresh database per test run, shared test database with cleanup, or in-memory? | Fresh database per run | data, ADR | Pre-build |
| 7.5 | External systems in tests: fakes, recorded contracts, or a real test instance? | Fakes that pass the same contract test as the real adapter; recorded contracts where available | arch, conv | Can default |
| 7.6 | Design principles the verifier checks (SOLID, KISS, others)? | SOLID and KISS with concrete checks | ADR, orch verifier | Can default |
| 7.8 | Which modules are core (money, security, data that must not be lost) and which are infrastructure? | Coverage per tier instead of one global number: core 100 %, important 80 %, infrastructure no target; a test that can never fail is a finding | conv, ADR, orch verifier | Pre-build |
| 7.9 | Only when the app calls an AI model: how is its output judged? | An evaluation, not a test: a hand-checked dataset (about 30-50 cases), scorers with thresholds, a judge model from a different provider than the one judged, each case run at least 3 times with the spread reported, results saved with models and prompt versions; a roadmap gate on the thresholds | spec RNF, roadmap, RFC success criteria | Pre-build |
| 7.10 | Fixtures from real data shapes? | Yes: measure the real inputs (sizes, names, encodings, folder layouts) and build fixtures from those numbers; never real personal data in fixtures | conv, tasks | Can default |
| 7.7 | Demo data for the owner's hands-on review: copy a real sample of the legacy data (a week, a month) so the owner recognises it? | Yes: a demo seed reproducing a real legacy sample, only for local and dev databases, created through the same states the app allows (no row the app could not have produced) | data, tasks | Pre-build |

### 4.8 Build orchestration

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 8.1 | Who builds: Claude agents, people, or both? | Claude agents under an orchestrator, the product owner reviews | orch | Pre-build |
| 8.2 | How are cards rated and which model builds each? | Difficulty 1-10 per card mapped to model bands (haiku 1-5, sonnet 6-8, opus 9-10); the strongest model (fable) only as an escalation the owner approves (`references/build-plan.md` section 4) | orch, tasks, agents | Can default |
| 8.3 | Which model verifies? | At least the builder's band (sonnet for 1-8, opus for 9-10), moving up when the builder is promoted; a card on a security or privacy boundary always gets the strongest available verifier; the verifier never edits the branch | orch, agents | Can default |
| 8.4 | Human gates (`G-nn`): which decisions or accesses must a person give, and who holds each gate? | Acceptance of the docs, repository remote, each external access, go-live | orch, roadmap | Pre-build |
| 8.5 | Parallel builders in isolated worktrees, branch per card, linear history on `main`? | Yes; a card's worktrees and branches are removed when it merges | orch, conv | Can default |
| 8.6 | What happens when a card fails verification? | FAIL 1: the same builder fixes it; FAIL 2: a fresh builder one band up; FAIL 3: the strongest model, only with the owner's approval in chat; after that the card is escalated and its chain blocks | orch | Can default |
| 8.7 | Usage regime: a subscription plan with usage windows or a metered API key? How many agents at once, may the build run unattended overnight, how much of the window may it use? | Plan: one agent at a time under the usage bands of `references/build-plan.md` section 10.2, raised when the owner says so; overnight only with a heartbeat the owner approved. API key: a daily cost cap. This changes often during a build; record each change as a DEC | orch, handoff | Pre-build |
| 8.8 | May the cheapest band (haiku, difficulty 1-5) build cards that change code? | Yes for well-specified cards with probes and a pattern to copy; never a security or privacy boundary; local models (Ollama) only for scripted difficulty 1-2 cards whose checks the orchestrator re-runs | orch, tasks | Can default |
| 8.10 | Who merges what? | With a remote: the orchestrator squash-merges card pull requests under the merge rules; a pull request that changes the spec, ADRs, RFCs, the decision log or `CLAUDE.md` carries the `needs-owner` label and only the owner merges it. A standing delegation ("merge everything this session") is a dated DEC; the tool may still ask the owner once per session before `gh pr merge` | orch, CLAUDE | Pre-build |
| 8.11 | Freeze the scope before a deadline? | Yes, from about five days before: fix at once only what stops the main journey, gives wrong or invented content or loses data; card the rest into a later phase held by a gate the owner opens | roadmap, orch | Can default |
| 8.12 | Test before the build that a fresh agent can build from the documents alone? | Yes: after G-01, a reviewer agent with no conversation context reads the set and lists what it would have to guess; each guess becomes a `Q-nn` or a document fix | orch, handoff | Can default |
| 8.9 | When does the owner try the running app? | A hands-on review with the demo seed as soon as the main workflow runs end to end (usually the end of P2), again before the last build phase; the changes become DEC-nn and cards | roadmap, handoff | Pre-build |

### 4.9 Sign-off

| Id | Question | Default | Lands in | Timing |
|---|---|---|---|---|
| 9.1 | Who reviews which documents (spec by the business, ADRs by IT, design by the brand owner)? | The product owner reviews all | orch gates, handoff | Pre-build |
| 9.2 | Date of the acceptance-gate review (`G-01`: docs accepted, build may start)? | Set at the end of the pre-build agenda | orch gates, handoff, roadmap | Pre-build |
| 9.3 | Which later gates need a date now (external access, pilot, go-live)? | None dated yet; each gate names its holder | orch gates, roadmap | Can default |

## 5. The pre-build agenda

Before the build plan is handed to an orchestrator, walk the user through three agenda items, one session
or one round each, in this order. Write the agenda into `handoff.md` as soon as it is agreed, so the next
session starts with these questions, not with work. Ask each item's questions first (with defaults), play
the answers back, then write.

### 5.1 Item 1: the full data model

Walk through every table before the first migration exists. Questions (defaults from the preset if any):
- New database, or reuse or extend an existing one? History imported or not (3.3)?
- Key strategy (integer identity or GUID), business keys as unique constraints.
- Grouping of tables into schemas or areas; naming rules for tables, columns and constraints.
- Enumerations: stored as readable names with a check constraint, never magic numbers or sentinel values.
- Audit columns, soft delete, optimistic concurrency, retention (3.4).
- Collation and text types when several languages are stored.
- Migration ownership: numbered, idempotent scripts; number ranges reserved per phase or module so parallel
  builders never collide.
- Database logins and grants per principal (least privilege).
- Test-database strategy (7.4).
- Mapping from the legacy data, when replacing a system.

Output: `docs/data-model.md` (every table, column rule, constraint that carries a business rule, grants,
migration ranges, test strategy), ADRs for the conventions and for the history decision, updated spec
requirements and task cards for the migrations.

### 5.2 Item 2: the design system

1. Ask 5.1 to 5.8.
2. Write `docs/design-system.md` v1 (tokens, layout and breakpoints, component inventory, patterns, print,
   accessibility, how a page is verified) and `docs/design-system-brief.md`: a self-contained brief for a
   design tool, saying what the product is, who uses it where, the draft tokens and components, and exactly
   what to return (token file, type and spacing scales, component specs, mockups of the key screens at the
   target sizes and themes).
3. The user runs the brief in the design tool and brings back the result.
4. Fold the result back as design system v2: copy the exported board into `docs/design/board/`, rewrite
   `docs/design-system.md` against it, and mark the brief "Superseded" with a pointer to v2 (the brief is
   kept for history, never deleted). Update the UI task cards and any requirement the design changed.

If the user skips the round trip, v1 stands and the brief stays for later; record that as a scope decision.

### 5.3 Item 3: other things to settle

One batch (numbered table with defaults) covering:
- environments and where each runs (6.1);
- secrets placement per environment (6.2);
- source control, system of record and continuous integration (0.9, 6.3);
- package baseline and the rule for adding a package (4.9);
- naming conventions: code, database objects, routes, permission codes, resource keys, branches and commits;
- error handling per layer and the user-facing error experience: what the user sees when a dependency is
  down, error codes, correlation ids (5.8, 2.4);
- printing or device output, if any (5.7);
- observability and alerting (6.5);
- release and versioning (6.4);
- legacy history and cutover, when replacing a system (3.3, 6.8);
- backup and restore (6.6);
- the review date for the acceptance gate (9.2).

Output: `docs/environments-and-delivery.md`, `docs/conventions.md`, the ADRs these decisions need, gate
definitions and dates in `docs/orchestration/README.md`, and new or changed task cards. Close the agenda in
`handoff.md` and list what is still owed by the user (access, dates, approvals) as gates or `Q-nn`.

## 6. From answers to documents

| What was collected | Where it goes |
|---|---|
| Scope-decisions rows | `DEC-nn` in `docs/decision-log.md`; the table in the RFC scope section and the README |
| Unanswered or deferred questions | `Q-nn` rows in the spec's open-question table, each with owner, needed by, default, status |
| Stack answers (preset or custom) | One ADR per decision that is hard to revert; `CLAUDE.md` hard rules; `docs/architecture.md`; `docs/conventions.md` |
| Workflows and actors | Spec actors and `RF-nnn` requirements (ranges reserved per module); `docs/process-flows.md` diagrams |
| Quality expectations (speed, availability, retention, accessibility) | `RNF-nnn` in the spec |
| Human approvals and accesses the build needs | `G-nn` gates in `docs/orchestration/README.md`, referenced by task cards |
| Pre-build agenda results | `docs/data-model.md`, `docs/design-system.md`, `docs/environments-and-delivery.md`, `docs/conventions.md` |

Every recorded answer names its source (`DEC-nn`, `Q-nn` default, or preset) so the review loop can later
check that each decision was applied everywhere it should be.
