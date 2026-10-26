# project-blueprint

A [Claude Code](https://claude.com/claude-code) skill that turns a project idea into a complete, consistent,
build-ready documentation repository, and then into a plan that coding agents can build card by card.

It interviews you first (every question comes with a default, so "defaults except 4 and 9" is a full answer), then
writes the set: README, `CLAUDE.md`, `AGENTS.md`, handoff, RFC, requirements with Given/When/Then, ADRs,
architecture, data model, conventions, environments and delivery, threat model, design system, roadmap, process
flows, a decision log and an agent build plan. Later it reviews the set, asks you the open questions and applies
each answer everywhere it lands.

## What the build plan gives you

- **Task cards** rated by difficulty 1-10. Each band maps to a model: haiku builds 1-5, sonnet 6-8 and opus 9-10.
  The strongest model is used only as an escalation that you approve.
- **An independent verifier** for every card. It runs the gates itself and checks that the tests were written first
  and fail without the code (red and mutation checks). It also checks requirement coverage, drift, new packages and
  security.
- **A retry ladder.** After a failed check, the same builder fixes it; after a second, a fresh builder one band up;
  after a third, escalation.
- **Merge rules** for local or pull-request repositories. Changes to the spec, ADRs, decision log or `CLAUDE.md`
  carry a `needs-owner` label.
- **A usage throttle** for subscription plans.
- **Human gates**, and a verification matrix that closes each phase.

## Install

Clone into your Claude Code skills folder:

```bash
git clone https://github.com/blacklight0101/ProjectBlueprint.git ~/.claude/skills/project-blueprint
```

Then ask Claude Code to start, plan or document a new project; the skill triggers on its own, or ask for it by name.
The scripts need Python 3.10 or later. `scripts/flows_pdf.py` (optional) uses Microsoft Edge to print the process
flows to PDF.

## Layout

| Path | What it is |
|---|---|
| `SKILL.md` | the skill: when it triggers, the steps, the principles |
| `references/` | the interview bank, the documentation-set catalogue, the build plan, the review loop, the verification matrix, stack presets |
| `assets/templates/` | the target repository layout, with `{{PLACEHOLDERS}}` and `<!-- FILL -->` comments |
| `assets/workflows/` | optional multi-agent review and apply scripts |
| `scripts/scaffold.py` | copies the templates into a new repository (`--without legacy,design,flows,orchestration,agents,security,context`) |
| `scripts/check_docs.py` | a consistency linter: ids, links, tables, placeholders, the ADR index, card dependencies, open questions and size budgets |

## Worked example

[Rosetta](https://github.com/blacklight0101/Rosetta) was planned and built with this skill: 404 cards run through
pull requests, DEC-01..DEC-174, a threat model with an AI section, and verification matrices per phase.

## License

[MIT](LICENSE)
