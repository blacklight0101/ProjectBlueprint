# {{PROJECT}} - Requirements (Release 1)

| | |
|---|---|
| **Status** | Proposed (becomes Accepted after the review that opens gate G-01) |
| **Date** | {{DATE}} |
| **Owner** | {{OWNER}} |
| **Reviewers** | <!-- FILL: the people or teams who accept these requirements --> |
| **Related** | [RFC-001](../rfc/RFC-001-{{PROJECT_SLUG}}.md) - [ADRs](../adr/README.md) - [Decision log](../decision-log.md) - [Architecture](../architecture.md) - [Roadmap](../roadmap.md) |

<!-- FILL: Add "- [Legacy sources](../legacy-sources.md)" to Related when a system is replaced. -->

## 1. Introduction

### 1.1 Scope

<!-- FILL: What release 1 (R1) must do, for whom, and where (sites, tenants, platforms), in three to six lines.
Later releases appear only in section 7 as reserved ranges with one line of intent each. -->

### 1.2 How to read an id

- `RF-nnn` functional requirement, `RNF-nnn` non-functional requirement, `Q-nn` open question (section 4),
  `DEC-nn` a decision by the product owner in [decision-log.md](../decision-log.md) (a requirement cites it as
  `Decision DEC-nn`), `ADR-nnn` an architecture decision record.
- `DEF-nn` a defect of the system being replaced, from [legacy-sources.md](../legacy-sources.md), that the
  requirement closes (`Closes DEF-nn`). <!-- FILL: remove this bullet when nothing is replaced. -->
- Ids are **never renumbered or reused**. A dropped requirement keeps its id and reads
  `Withdrawn YYYY-MM-DD - see <id>`.
- **Release** says when it ships. **MoSCoW** (Must, Should, Could, Won't) says how negotiable it is inside that
  release.
- **Source** says where the behaviour comes from: a legacy citation, a decision, an interview, a regulation.
- A **deferred requirement** (section 7) is a reserved range and an intent, not a commitment, until it is promoted
  into section 5 with acceptance criteria.

### 1.3 Id ranges

Each module owns a range of a hundred functional ids; inside a range, ids are grouped in tens by topic. A new module
takes the next free range. This table is the canonical list of ranges.

| Range | Module | Release |
|---|---|---|
| RF-001..RF-099 | <!-- FILL: module A, e.g. "Sign-in and session" --> | R1 |
| RF-100..RF-199 | <!-- FILL: module B --> | R1 |
| RNF-001..RNF-099 | Non-functional requirements, grouped in tens by quality (see section 6) | all |

### 1.4 Acceptance criteria

Acceptance criteria are written Given / When / Then. `Must` requirements carry full scenarios (the happy path and
every failure the requirement names), `Should` at least one scenario, `Could` a one-line criterion. Every
requirement ends with a `Verification:` line that names the test level or manual check that proves it.

## 2. Actors

<!-- FILL: Every person role and every external or internal system that acts in release 1. Kind is "person",
"system" or "system (ours)" for a background service of this project. Role in R1 names what they do, with RF ids
where useful. -->

| Actor | Kind | Role in R1 |
|---|---|---|
| <!-- FILL: e.g. Operator --> | person | <!-- FILL: e.g. signs in, records work, reviews results (RF-001..RF-010) --> |
| <!-- FILL: e.g. External order system --> | system | <!-- FILL: what it provides or receives --> |

## 3. Glossary

<!-- FILL: Every domain term a builder could misread, with the exact meaning in this project (formats, lengths, which
entity owns it). This is the canonical definition of each term; other documents use the terms as defined here. -->

| Term | Meaning |
|---|---|
| <!-- FILL: term --> | <!-- FILL: meaning --> |

## 4. Open questions

Answers are recorded in the Status column. A question never blocks work silently: it has an owner, the phase or card
that needs the answer, and a default that applies until it is answered. Status is one of `Open`,
`Default applies`, `Answered (DEC-nn)` or `Withdrawn`. An answered question keeps its row; the answer itself lives in
the decision log.

| Id | Question | Owner | Needed by | Default | Status |
|---|---|---|---|---|---|
| Q-01 | <!-- FILL: e.g. "Which roles may approve a submitted record?" --> | <!-- FILL: e.g. business lead --> | <!-- FILL: e.g. P1 or P1-04 --> | <!-- FILL: e.g. "Supervisor and Admin only" --> | Default applies |

## 5. Functional requirements (R1)

<!-- FILL: One subsection per module, in id order, with its range in the heading. Inside, one block per requirement
in the format below. Keep each requirement to one behaviour; split rather than stack "and". The example block is
generic and must be replaced. -->

### 5.1 <!-- FILL: Module A --> (RF-001..RF-099)

**RF-001 <!-- FILL: title in the imperative, e.g. "Sign in and resolve the user's role from data" -->** - R1 - Must - Source <!-- FILL: citation, DEC-nn or "interview YYYY-MM-DD" --> - <!-- FILL: ADR-nnn -->
As a <!-- FILL: actor --> I want <!-- FILL: capability --> so that <!-- FILL: benefit -->.
- Given <!-- FILL: e.g. an operator listed with role Operator -->, when <!-- FILL: e.g. they open the application -->, then <!-- FILL: e.g. every screen shows only the actions that role permits -->.
- Given <!-- FILL: e.g. a user who is not listed -->, when <!-- FILL: e.g. they open the application -->, then <!-- FILL: e.g. they see an access-denied page and no data -->.
Verification: <!-- FILL: e.g. integration tests with a test authentication handler; manual check with two accounts -->.

### 5.2 <!-- FILL: Module B --> (RF-100..RF-199)

## 6. Non-functional requirements

<!-- FILL: One row per quality requirement, grouped in tens by quality (for example RNF-001..009 reliability and
idempotency, RNF-010..019 security, RNF-020..029 testability and observability, RNF-030..039 data and operations,
RNF-040.. usability and accessibility). Each states a measurable threshold and how it is verified. -->

| Id | Requirement | Verification |
|---|---|---|
| RNF-001 | <!-- FILL: e.g. "**Availability**: a restart of the background worker loses no queued work" --> | <!-- FILL: e.g. restart test --> |

## 7. Deferred requirements (reserved ids, not commitments)

<!-- FILL: One row per later module or release: its reserved range and one line of intent. Promote a range into
section 5, with acceptance criteria, when its release starts. -->

| Range | Release | Intent |
|---|---|---|
| <!-- FILL: e.g. RF-300..RF-399 --> | <!-- FILL: e.g. R2 --> | <!-- FILL: one line --> |

## 8. Traceability matrix

Each requirement group traces to where its behaviour comes from, the ADRs that shape it, the phase that delivers it
and the task cards that build it. The cards column is filled when the build plan is written and kept current when
cards are added. A requirement with no card, or a card with no requirement, is a finding in review.

| Requirement group | Source | ADR | Phase | Cards |
|---|---|---|---|---|
| RF-001..RF-009 | <!-- FILL: legacy citation, DEC-nn or "- (new)" --> | <!-- FILL: ADR-nnn --> | <!-- FILL: P1 --> | <!-- FILL: P1-03, P1-04 --> |
| RNF-001..RNF-009 | <!-- FILL --> | <!-- FILL --> | all | <!-- FILL --> |
| [Decision log](../decision-log.md) (all DEC ids) | - (product owner's decisions) | <!-- FILL: ADRs written from decisions --> | all | - |
