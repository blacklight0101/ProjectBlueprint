# Threat model

| | |
|---|---|
| **Status** | Proposed ({{DATE}}) <!-- FILL: Accepted once the owner has reviewed it; add "revised YYYY-MM-DD for DEC-nn" on every later change --> |
| **Scope** | what is worth protecting, who could attack it and how, the controls that answer each threat, and the risks the owner accepted |
| **Related** | [architecture](../architecture.md) (security section), [environments and delivery](../environments-and-delivery.md) section 4 (secrets), [decision log](../decision-log.md) (accepted risks), [requirements](../spec/requirements.md) (security RNFs) |

Every threat has a control with a test or a check, or a residual-risk row the owner accepted with a DEC-nn. A decision
that accepts a risk adds its row here in the same change. The first milestone's verification matrix reviews this
document.

<!-- FILL: Fill every table with the project's own rows. Write "Not applicable: <reason>" for a section that does not
apply (section 5 when no AI model is called). Keep rows short: one threat, one control, one check. -->

## 1. Assets

| Asset | Why it matters | Where it lives |
|---|---|---|
| <!-- FILL: example row, replace --> User accounts and permissions | wrong access exposes every other asset | database, identity provider |
| <!-- FILL: example row, replace --> Secrets (connection strings, API keys) | full access to a system | secret store per environment |

## 2. Trust boundaries

<!-- FILL: one line per boundary where data or control crosses from less trusted to more trusted: browser to server,
server to database, server to an external API, an uploaded file or repository read by the system, a model's output
used by the system, a CI runner with secrets. -->

- <!-- FILL: boundary - what crosses it - what is trusted on each side -->

## 3. Threats and controls

| Id | Threat | Boundary | Control | Check (test or grep) | Requirement |
|---|---|---|---|---|---|
| <!-- FILL: example row, replace --> T-01 | a user reaches a page without the permission | browser to server | one policy per permission code, checked server-side | integration test per policy; grep for anonymous routes | RNF-nnn |
| <!-- FILL: example row, replace --> T-02 | a secret is committed | developer to repository | secret scan in the pre-commit hook and in CI | CI secret-scan step | RNF-nnn |
| <!-- FILL: example row, replace --> T-03 | shell injection in CI | pull request to CI runner | values through `env:`, never `${{ }}` inside `run:` | hard-rule grep | RNF-nnn |

## 4. Supply chain

- Exact versions and a committed lock file; new versions only after the cooldown in
  [environments and delivery](../environments-and-delivery.md) section 7.
- Install scripts off for agents and CI; a new package exists in the registry under that exact name and has an ADR.
- The dependency audit fails on high and critical findings; exceptions expire.

## 5. AI-specific threats

<!-- FILL: only when the system calls an AI model or feeds untrusted content to one; otherwise "Not applicable: no
model is called". -->

| Id | Threat | Control | Check |
|---|---|---|---|
| <!-- FILL: example row, replace --> T-20 | prompt injection in untrusted input changes the model's task | input is delimited and labelled as data; the model's output is validated against a schema; no tool or command runs from model output | evaluation cases with injected instructions |
| <!-- FILL: example row, replace --> T-21 | model output rendered as HTML runs a script | output rendered as text only | unit test with markup in the output |
| <!-- FILL: example row, replace --> T-22 | a secret or personal data reaches the provider | secrets never in prompts; personal data redacted before the call | grep of the prompt builder; unit test |
| <!-- FILL: example row, replace --> T-23 | runaway cost | cost caps per run and per day enforced in code | unit test of the cap |
| <!-- FILL: example row, replace --> T-24 | the model invents a package or an API | generated code is never installed or run without review | process rule in CLAUDE.md |

## 6. Residual risks

Risks the owner accepted. Each row names its decision; a row is never deleted, only marked `Closed YYYY-MM-DD` with
the card or DEC that closed it.

| Id | Risk | Why it is accepted | Decision | Review by |
|---|---|---|---|---|
| <!-- FILL: example row, replace, or write "None yet." --> R-01 | | | DEC-nn | <!-- FILL: date or phase --> |
