# Stack presets

A **preset** is a named bundle of stack defaults and house rules that the interview can offer in one click.
It answers most of the stack questions (bank phase 4) and many of the conventions, environment and testing
questions at once, and it says exactly what to write into which document. A preset never contains business
content: it is the same for every project that uses the stack.

| Preset | File | Offer it when |
|---|---|---|
| .NET house preset | [dotnet-house.md](dotnet-house.md) | Intranet or line-of-business web app on Windows servers: .NET, Blazor Server, Dapper, SQL Server, IIS with Windows authentication |

For other kinds of project there are question checklists (section 5), not full presets. A checklist becomes
a preset once the same answers have been given on two projects.

## 1. What a preset contains

Every preset file has these sections, in this order, so Claude can apply any preset the same way:

1. **When to offer it** - the project kinds and signals (bank 0.12, 4.x) that make it the recommended option.
2. **Answers it fills** - a table `Bank id | Answer` for the interview questions it settles.
3. **Stack** - runtime, UI, data access, database, hosting, authentication, testing, principles.
4. **Solution layout** - projects or folders, what lives where, the dependency rule.
5. **Coding conventions** - names, file rules, error handling per layer, UI rules, and the authentication and
   authorization wiring when the stack decides it (a subsection, not a section of its own).
6. **Database conventions** (if the stack has a database) - schemas, keys, types, migrations, logins, test database.
7. **Testing** - frameworks, levels, fixtures, what "done" runs.
8. **ADRs this preset implies** - title and one-line decision for each, in creation order.
9. **CLAUDE.md hard rules block** - a block to paste into the project's `CLAUDE.md`.
10. **Environments and delivery defaults** - environments, secrets, CI, packaging, deployment, rollback.
11. **Known gotchas** - traps met on earlier projects with this stack, with the rule that avoids each.
12. **Questions the preset leaves open** - what must still be asked even when the preset is taken.

## 2. How Claude applies a preset

1. **Offer.** In the framing batch, next to the project-kind question (bank 0.12 decides which preset fits),
   offer the matching preset as the first option labelled `(Recommended)`, with "Another stack I will describe"
   as the alternative. Offering it before the deeper rounds means the bank rows it answers are never asked. Offer
   it only when the project kind fits; never push a web-server preset onto a game.
2. **Play back.** When the user accepts, show the preset's "Answers it fills" as one "What I recorded" table
   (same columns as in `references/interview.md` 2.5, with "preset" in the "What you said" column), right after
   the framing answers and before the deeper rounds. The user may override single rows; each override is recorded
   as its own scope decision ("Chosen: X, Instead of: preset default Y"). The deeper rounds then skip every bank
   row the preset answers.
3. **Record.** Add one scope-decisions row "Stack: `<preset name>` preset" and, at scaffold time, the
   matching `DEC-nn`. Rows of the preset that the user did not override are not separate decisions; the ADRs
   carry them.
4. **Ask what is left.** Put the preset's "Questions the preset leaves open" into the next numbered batch, with
   the defaults the preset suggests.
5. **Write.** Apply the preset to the documents:

   | Document | What the preset writes there |
   |---|---|
   | `docs/architecture.md` | the layers and dependency rule, the solution layout, where ports, services, repositories and pages live, authentication pipeline, testing approach summary |
   | `docs/conventions.md` | code and file names, routes, permission and resource keys, SQL embedding rules, error handling per layer, user-facing error behaviour, test naming, branch and commit names |
   | `docs/data-model.md` | the conventions section (schemas, keys, types, audit columns, enums, constraints), the migrations section (file names, number ranges, runner, schema-version table) and the test-database strategy; the tables themselves come from the interview |
   | `docs/environments-and-delivery.md` | environments table, secrets placement, source control and CI, package baseline, versioning, deployment and rollback procedure, observability defaults |
   | `CLAUDE.md` | the hard rules block, the prohibitions, the planned solution layout, the build and test commands |
   | `docs/adr/` | one ADR per entry in "ADRs this preset implies", numbered from the next free id after `ADR-001`, Status `Accepted` when the user took the preset, `Proposed` for entries the preset marks as needing confirmation |
   | `docs/spec/requirements.md` | the quality requirements the preset guarantees (`RNF-nnn`: test pyramid, secrets, accessibility baseline) and any `Q-nn` it leaves open |
   | `docs/orchestration/` | the verify commands the verifier runs and the checks the preset adds to its checklist |

6. **Keep it generic.** The preset text is copied with the project's names substituted; business rules never
   come from a preset.

When a preset rule and a user decision conflict, the user's decision wins and the ADR records the deviation
in its Context or Consequences.

## 3. How to add a new preset

1. Pick a kebab-case file name (`phaser-game.md`, `android-compose.md`) and create it next to this file with
   the twelve sections of section 1, in order.
2. Derive it from at least one real repository the user built with that stack: read its `CLAUDE.md`,
   project files, test setup and deployment notes, and take the conventions that are actually used. Where the
   repository and the intended rule differ, write the intended rule and note the difference.
3. Keep it generic: no product names, customer names, people, locations or business terms. Use `<Product>` for
   the solution or package name.
4. List every ADR with a title in imperative mood and a one-line decision; the project's ADRs are written from
   these at scaffold time.
5. Add a row to the table at the top of this file, and move the matching checklist out of section 5 if one
   existed.
6. Test it: run a dry interview for an invented project of that kind and check that every bank question is
   either answered by the preset, listed as left open, or not relevant.

## 4. When no preset fits

Ask bank phase 4 question by question and write one ADR per hard-to-revert choice (runtime, UI technology,
data access, database, hosting, authentication, test approach). Use the matching checklist below if there is
one; otherwise the bank alone is enough.

## 5. Question checklists for other project kinds

Each checklist lists what to ask in addition to the framing questions, with a sensible default and the
document it lands in. The full docs set still applies, but some documents stay short (noted per checklist).

### 5.1 Browser game: Phaser 3 + TypeScript + Vite

| Question | Default | Lands in |
|---|---|---|
| Genre, core loop and win or lose conditions in three sentences? | Must be answered | RFC, spec |
| Target platforms and input (keyboard and mouse, touch, gamepad)? | Desktop browsers, keyboard and mouse | spec RNF, design |
| Logical resolution, scaling mode, orientation? | 1280x720, fit to window, landscape | arch, design |
| Physics engine? | Arcade Physics | ADR, arch |
| Architecture: one game scene orchestrating systems, a parallel UI scene, events on an event bus, data-driven config for enemies, weapons, waves? | Yes | arch, conv |
| Object pooling for bullets, enemies, effects? | Yes, pool everything spawned more than once per second | arch, conv |
| TypeScript strict mode, path aliases, lint rules? | Strict on; no `any` without a comment | conv, CLAUDE |
| Unit tests with Vitest (and a DOM stub) for systems and pure logic; what is left to manual play-testing? | Vitest for systems, config validation and scoring; manual play-test checklist per phase | ADR, arch, tasks |
| Asset pipeline: sprite atlases, audio formats, who makes the art, licences? | Atlases built from source images; licences recorded per asset | design |
| Save data: none, local storage, or a server? | Local storage, versioned | data |
| Hosting and release: static hosting, itch.io, own site? | Static build published by hand | env |
| Performance budget (frame rate, draw calls, bundle size)? | 60 fps on a mid-range laptop; bundle under 5 MB | spec RNF |
| Audio and accessibility options (mute, volume, colour-blind safe palette, remappable keys)? | Mute and volume; remapping later | spec, design |

Short documents: `docs/data-model.md` covers save data and config files only; `docs/environments-and-delivery.md`
covers build and publish only; `docs/process-flows.md` shows the game state flow (menu, play, pause, game over)
and the level progression.

### 5.2 Unity 6 game

| Question | Default | Lands in |
|---|---|---|
| Genre, core loop, win or lose conditions? | Must be answered | RFC, spec |
| Render pipeline (URP, HDRP, built-in)? | URP | ADR, arch |
| Target platforms and input system? | Windows desktop; the Input System package | spec RNF, ADR |
| Architecture: an event bus for decoupling, ScriptableObjects for data, a composition root or service locator? | Event bus plus ScriptableObject configuration; no singletons beyond the composition root | ADR, arch, conv |
| Project folder root and naming (`Assets/_Project/...`), assembly definitions per area? | `Assets/_Project/` with an assembly definition per area | arch, conv |
| Scene structure: bootstrap scene, additive level scenes? | Bootstrap scene plus additive levels | arch |
| Testing: Unity Test Framework edit-mode tests for logic, play-mode tests for key loops? | Edit-mode for all logic; play-mode for one smoke loop per level | ADR, tasks |
| Source control for large assets (Git LFS, `.gitattributes`, Smart Merge for scenes)? | Git with LFS for binaries and the Unity YAML merge tool | env, CLAUDE |
| Save system and data format? | JSON in the persistent data path, versioned | data |
| Performance budget and target hardware? | 60 fps on the target machine; profile each phase exit | spec RNF |
| Build and distribution (Steam, itch.io, internal)? | Local builds per phase exit | env |
| Which Unity packages are allowed, and is a new one an ADR? | Only packages already in the manifest; a new one needs an ADR | env, CLAUDE |

Short documents as for the browser game. Builders need a running Unity Editor for play-mode tests; record that
as a gate or a verifier limitation in `docs/orchestration/README.md`.

### 5.3 Android app

| Question | Default | Lands in |
|---|---|---|
| Kotlin with Jetpack Compose, or another toolkit (Flutter, React Native)? | Kotlin and Compose | ADR, arch |
| Minimum and target SDK, device classes (phone, tablet, rugged scanner)? | Minimum SDK 26, phones | spec RNF, design |
| Architecture: single activity, MVVM with a unidirectional state flow, repository layer, dependency injection (Hilt or manual)? | Single activity, MVVM, repositories, Hilt | ADR, arch, conv |
| Offline behaviour and local storage (Room, DataStore), sync with a server? | Offline-first with Room and a sync worker | arch, data, ADR |
| Backend: none, the team's own API, a cloud service? | The team's own API | arch, env |
| Authentication on device? | Company sign-on through the backend | arch, ADR |
| Permissions the app needs (camera, location, notifications) and why? | Only what a workflow needs, requested in context | spec, design |
| Brand system shared with a web product? | Reuse the same tokens and fonts | design |
| Tests: JVM unit tests for view models and repositories, instrumented tests for key journeys? | Unit for logic, one instrumented journey per main workflow | ADR, tasks |
| Distribution (Play Store, internal track, managed devices, side-load)? | Internal testing track first | env |
| Signing keys: who holds them, where are they stored? | Outside the repository, held by the product owner | env, ADR |
| Crash reporting and analytics? | Crash reporting only, no analytics without consent | env, spec RNF |

Builders need an emulator or a device for instrumented tests; record that in the orchestration protocol.

### 5.4 Plain web app (no preset stack)

| Question | Default | Lands in |
|---|---|---|
| Server-rendered, single-page app, or static site? | Server-rendered | ADR, arch |
| Language and framework? | What the user's other web projects use | ADR, arch |
| Hosting (own server, managed platform, container)? | A managed platform with a free or low tier | env, ADR |
| Database and data access style? | A relational database with parameterised SQL or a thin mapper | ADR, data |
| Authentication (none, own accounts, external provider)? | External provider through a standard protocol | ADR, arch |
| Public or internal? Search engine indexing, legal pages, cookie consent? | Internal, not indexed | spec RNF |
| Styling: own tokens and components, or a CSS framework? | Own tokens and a small component set | design, ADR |
| Tests: unit, integration against a test database, browser end-to-end with Playwright? | All three, pyramid 60 / 30 / 10 | ADR, spec RNF |
| Environments and secrets? | Dev and production; secrets in the platform's secret store | env |
| CI and deployment? | Pipeline on push to `main` runs tests and deploys | env |
| Observability (logs, uptime check, error tracking)? | Platform logs plus an uptime check | env |
| Accessibility and supported browsers? | WCAG 2.1 AA; current evergreen browsers | spec RNF, design |
