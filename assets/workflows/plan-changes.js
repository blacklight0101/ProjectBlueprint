export const meta = {
  name: 'blueprint-plan-changes',
  description: 'Optional research and impact analyses, then one planner writes the canonical change plan (registry, per-file edits, coverage, groups), three critics check it and the planner revises; amend mode folds new decisions into an existing plan',
  whenToUse: 'Steps 4 and 5 of the project-blueprint review loop, after the owner answers are recorded in a decisions file',
  phases: [
    { title: 'Research', detail: 'read-only facts and impact analyses (optional)' },
    { title: 'Plan', detail: 'planner writes or amends the canonical change plan' },
    { title: 'Critique', detail: 'fidelity, cross-file consistency, completeness' },
    { title: 'Revise', detail: 'planner folds accepted critiques and records the resolution' },
  ],
}

// project-blueprint template: plan-changes.js (see references/workflows.md and references/review-loop.md)
// Keep this file pure ASCII with LF line endings.
//
// CONFIGURATION. Edit the constants below, or pass the same keys in the Workflow args object
// (args values win). Windows paths need doubled backslashes inside JS strings.
// Changing any constant that is interpolated into a prompt invalidates the resume cache from that agent on.
const CFG = (typeof args === 'object' && args) ? args : {}
const PROJECT = CFG.project || 'PROJECT_NAME'            // display name of the project
const REPO = CFG.repo || 'REPO_PATH'                     // absolute path of the repository (read-only in this workflow)
const SCRATCH = CFG.scratch || 'SCRATCH_PATH'            // absolute path of the session scratchpad
const DATE = CFG.date || 'YYYY-MM-DD'                    // date written on new notes, withdrawals and the plan header
const OWNER = CFG.owner || 'OWNER_NAME'                  // product owner whose decisions are binding
const CONTEXT = CFG.context || 'PROJECT_CONTEXT'          // 2-4 sentences: what the product is, stack, current release
const FINDINGS = CFG.findings || 'FINDINGS_FILE'          // review findings file, e.g. SCRATCH + '\\review-findings-YYYY-MM-DD.md'
const DECISIONS = CFG.decisions || ['DECISIONS_FILE']    // every decisions file that applies, oldest first
// MODE 'new' writes a fresh plan. MODE 'amend' folds the files in NEW_DECISIONS into the existing plan.
// A completed amend run rewrote the plan in place: never start it again as a fresh run for the same decisions.
const MODE = CFG.mode || 'new'
const NEW_DECISIONS = CFG.newDecisions || []             // amend mode only: the addendum file(s) to fold in
const AMEND_TITLE = CFG.amendTitle || ('Amendment ' + DATE)   // amend mode only: heading of the appended section
const PLAN = CFG.plan || (SCRATCH + (SCRATCH.includes('\\') ? '\\' : '/') + 'change-plan.md')
const CRITIQUE_AFTER_AMEND = CFG.critiqueAfterAmend !== undefined ? CFG.critiqueAfterAmend : true
// Optional read-only sources the research agents may read (legacy notes, vendor docs). Paths.
const SOURCES = CFG.sources || []
// Optional research agents. Each writes SCRATCH/research-<key>.md and returns a summary. Leave empty to skip.
// Example entries (uncomment and adapt):
//   { key: 'legacy', task: 'Extract the legacy facts the decisions depend on: ... Cite the legacy-sources.md scheme; never copy text.' },
//   { key: 'impact-offline', task: 'Impact analysis for DEC-10: proposed design, every document location (path:line + gist) that must change, remaining open questions.' },
const RESEARCH = CFG.research || []
// Proposed editor groups for the target layout. The planner may change them; every file in exactly one group.
const GROUP_HINT = CFG.groupHint || 'G1 docs/spec/requirements.md; G2 docs/rfc/, docs/roadmap.md, docs/process-flows.md, docs/legacy-sources.md, README.md, docs/README.md, docs/decision-log.md; G3 docs/architecture.md, docs/data-model.md, docs/conventions.md, docs/environments-and-delivery.md, CLAUDE.md; G4 docs/adr/ (existing notes, new ADRs, index); G5 docs/orchestration/, .claude/agents/, handoff.md; G6 docs/design-system.md, docs/design-system-brief.md and any design token files'
// ---- end of configuration ----

function unset(name, value, placeholder) {
  if (!value || value === placeholder || (Array.isArray(value) && (!value.length || value.indexOf(placeholder) >= 0)))
    throw new Error('Set ' + name + ' at the top of plan-changes.js or pass it in args')
}
unset('PROJECT', PROJECT, 'PROJECT_NAME'); unset('REPO', REPO, 'REPO_PATH'); unset('SCRATCH', SCRATCH, 'SCRATCH_PATH')
unset('DATE', DATE, 'YYYY-MM-DD'); unset('OWNER', OWNER, 'OWNER_NAME'); unset('CONTEXT', CONTEXT, 'PROJECT_CONTEXT')
unset('FINDINGS', FINDINGS, 'FINDINGS_FILE'); unset('DECISIONS', DECISIONS, 'DECISIONS_FILE')
if (MODE !== 'new' && MODE !== 'amend') throw new Error('MODE must be new or amend')
if (MODE === 'amend' && !NEW_DECISIONS.length) throw new Error('amend mode needs NEW_DECISIONS')
function join(dir, name) { return dir + (dir.includes('\\') ? '\\' : '/') + name }

const CTX = `Context: ${REPO} is the documentation repository of ${PROJECT}. ${CONTEXT} Product owner: ${OWNER}.
Binding decisions of ${OWNER} (read fully): ${DECISIONS.concat(NEW_DECISIONS).join('; ')}. Review findings: ${FINDINGS}.${SOURCES.length ? ' Read-only sources you may consult: ' + SOURCES.join('; ') + ' (cite them, never copy their text).' : ''}
Id schemes: RF-nnn, RNF-nnn (ranges reserved per module); Q-nn (columns Id | Question | Owner | Needed by | Default | Status; Status Open, Default applies, Answered (DEC-nn), Withdrawn); ADR-nnn in docs/adr/ADR-nnn-kebab-title.md (Status Proposed, Accepted, Superseded by ADR-nnn, Amended with a dated note); DEC-nn decisions in docs/decision-log.md (columns Id | Date | Decision | Answer to | Where applied); DEF-nn legacy defects; G-nn gates; phases P0..Pn; task cards P<phase>-nn (fields Builder, Size, Depends on, Gate, Status, Reads, Do, Delivers, Done when, Refs); RFC-nnn. Ids are never renumbered or reused; a withdrawn item keeps its id with "Withdrawn YYYY-MM-DD - see ...".
Plan-internal ids (never written into the repository): findings like A1 or B7, holes like H-A1, critic issues F/K/M plus a number, edit ids <FILEKEY>/nn such as REQ/07.
Never edit anything in ${REPO} and never run git commands that change state. No emojis. English.`

const ISSUES = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: {
  severity: { type: 'string', enum: ['high', 'medium', 'low'] }, where: { type: 'string' },
  issue: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'where', 'issue', 'fix'] } } }, required: ['issues'] }
const GROUP = { type: 'object', properties: { key: { type: 'string' }, sections: { type: 'string' },
  files: { type: 'array', items: { type: 'string' } }, edits: { type: 'number' } }, required: ['key', 'sections', 'files', 'edits'] }
const PLANNED = { type: 'object', properties: {
  summary: { type: 'string' },
  groups: { type: 'array', items: GROUP },
  keyChoices: { type: 'array', items: { type: 'string' } },
  surprisingFacts: { type: 'array', items: { type: 'string' } },
  openItems: { type: 'array', items: { type: 'string' } },
  staleTerms: { type: 'array', items: { type: 'string' } },
  accepted: { type: 'number' }, rejected: { type: 'number' },
}, required: ['summary', 'groups', 'keyChoices', 'surprisingFacts', 'openItems', 'staleTerms', 'accepted', 'rejected'] }

const PLAN_SHAPE = `Structure of the plan (keep these section numbers):
1. Principles (5-12 lines): the decisions win over existing text, research proposals and review suggestions; ADRs are never deleted or rewritten, a changed decision gets a new ADR that supersedes or amends and the old ADR gets a status change and a dated note; requirement ids are never renumbered, new ids go into free slots of the right module range, a retired requirement keeps its line as "Withdrawn ${DATE} - see ..."; one date (${DATE}) on every new note, withdrawal and header; decision dates stay as decided; each document keeps its style, headings and table formats; nothing is invented - anything undecided becomes a Q-nn with a default and Status "Default applies".
2. Registry: every identifier that crosses files, defined once, in tables: decisions DEC-nn with their homes; new, changed and withdrawn RF/RNF ids with exact titles, priority and phase; Q-nn status changes and new Q rows; ADR numbers with exact file names, titles, statuses and what they supersede or amend; and, where the decisions touch them, state names and transitions, tables and columns, migration numbers, permission codes and grants, settings with scope and default, design tokens, task cards (id, title, difficulty, size, depends on, gate) and gates; plus every count that documents state (ADRs by status, cards by phase and by band, requirements).
3. Per-file edits: one subsection per file, headed with its group (for example "3.1 G1 - docs/spec/requirements.md"). Numbered edits <FILEKEY>/nn, each "[decision and finding ids] anchor (section, approximate line, gist of the current text) -> new text or its exact intent". New files (new ADRs, new cards) get their full content or a complete outline. Principle: when a name changes, the editor changes every occurrence in that file.
4. Coverage table: every finding and every decision -> edit ids, or "no change - reason".
5. Items not decided: each with its Q-nn and default.
6. Groups and edit counts: table Group | Files | Edits. Every file in exactly one group; editors run in parallel and cannot talk to each other. Suggested grouping: ${GROUP_HINT}.`

const RETURN_SHAPE = `Return: a summary (at most 20 lines); groups (key, the plan sections the group executes, its files relative to the repository, its edit count); keyChoices = the design choices the plan makes that the owner did not state literally (new states, tables, merged rules, defaults applied, new ADRs and cards with the new counts); surprisingFacts = facts from research or the repository the owner should know before editing; openItems = the Q-nn left open with their defaults; staleTerms = grep terms built from the OLD design (removed or renamed names, old counts, withdrawn rules) for the stale-text sweep; accepted and rejected critique counts (0 if none yet).`

let research = []
if (RESEARCH.length && MODE === 'new') {
  phase('Research')
  const done = await parallel(RESEARCH.map(r => () => agent(`${CTX}
Exception: you write exactly one file, ${join(SCRATCH, 'research-' + r.key + '.md')}.

You are a RESEARCHER (${r.key}). Task: ${r.task}
Write your answer to ${join(SCRATCH, 'research-' + r.key + '.md')}: structured, every fact with its source (path:line or citation), "not documented" where the sources are silent, and an exhaustive list of repository locations (path:line + gist) the topic touches. Return a summary of at most 12 lines.`, { label: 'research:' + r.key, phase: 'Research', effort: 'high' })
    .then(s => ({ key: r.key, file: join(SCRATCH, 'research-' + r.key + '.md'), summary: s }))))
  research = done.filter(Boolean)
  log('research done: ' + research.map(r => r.key).join(', '))
}
const RESEARCH_FILES = research.map(r => r.file)

phase('Plan')
let planned
if (MODE === 'new') {
  planned = await agent(`${CTX}
Exception: you write ${PLAN} (and nothing else).

You are the PLANNER. Read fully: the decisions files, the findings file${RESEARCH_FILES.length ? ', the research files ' + RESEARCH_FILES.join(', ') : ''}. Read the repository documents as needed to be exact (CLAUDE.md, docs/README.md, docs/adr/README.md, docs/adr/_template.md, id ranges in docs/spec/requirements.md, docs/decision-log.md, card format in docs/orchestration/tasks.md).
Write the CANONICAL CHANGE PLAN to ${PLAN}: header "# ${PROJECT} change plan - ${DATE}", an inputs paragraph (files, repository, HEAD commit from git -C ${REPO} log -1 --format=%h, and "line numbers are approximate; anchor on the quoted text"), a notation paragraph, then the sections below. The plan is executed by parallel editors who cannot talk to each other, so every cross-file identifier must be fixed in section 2 and every edit must use only those identifiers.
${PLAN_SHAPE}
Every finding and every decision must appear in section 4. Be exhaustive and precise.
${RETURN_SHAPE}`, { label: 'planner', phase: 'Plan', effort: 'xhigh', schema: PLANNED })
} else {
  planned = await agent(`${CTX}
Exception: you write ${PLAN} and one backup copy of it (nothing else).

You are the PLANNER. ${PLAN} is the current canonical change plan (read it fully, including earlier amendment sections). ${OWNER} has new decisions or corrections in ${NEW_DECISIONS.join('; ')} (read fully).
First copy ${PLAN} to the next free backup name ${join(SCRATCH, 'change-plan.vN.bak.md')} (N = 1, 2, ...; never overwrite a backup). Then amend ${PLAN} IN PLACE so it stays the single consistent source of truth:
- section 2 registry: add or change every identifier the new decisions touch (decisions with homes, requirement ids, Q statuses, ADRs, states, tables, settings, permissions, cards and every count);
- section 3: update the text of every affected edit and add new edits (new edit ids continue each file's numbering; ids are never reused); keep every file in exactly one group;
- sections 4, 5 and 6: coverage, items not decided, groups and edit counts;
- append "## <next number>. ${AMEND_TITLE}" that lists every changed, added and removed edit id per group with a one-line reason, and names the older statements it supersedes. Do not rewrite older amendment or critique sections.
Afterwards grep the plan for every term the new decisions make stale and resolve each hit.
${RETURN_SHAPE}`, { label: 'planner:amend', phase: 'Plan', effort: 'xhigh', schema: PLANNED })
}
if (!planned) throw new Error('the planner returned nothing; inspect the journal before re-running')
log('plan written: ' + planned.groups.length + ' groups, ' + planned.groups.reduce((n, g) => n + (g.edits || 0), 0) + ' edits')

let final = planned
let issues = []
if (MODE === 'new' || CRITIQUE_AFTER_AMEND) {
  phase('Critique')
  const scope = MODE === 'new' ? 'the whole plan' : 'the new amendment section and every registry entry and edit it changed'
  const LENSES = [
    { key: 'fidelity', tag: 'F', text: `FIDELITY to the decisions: for every DEC-nn, check that the plan implements exactly what ${OWNER} decided (no more, no less); flag anything invented (it must become a Q-nn with a default instead), anything that contradicts the words of a decision, any decision silently dropped, and any item the owner left open that the plan closes.` },
    { key: 'consistency', tag: 'K', text: 'CROSS-FILE CONSISTENCY: the registry is complete and unambiguous (every identifier an editor needs is defined once); per-file edits use only registry identifiers; no two edits contradict; state transitions, rules and permissions are coherent; numbering ranges do not overlap; card dependencies have no cycles and every builder of a component precedes its users; every count adds up; every file is in exactly one group. Spot-check against the repository files.' },
    { key: 'completeness', tag: 'M', text: 'COMPLETENESS: every finding and every decision is mapped to a concrete edit or explicitly waived with a reason; grep the repository for every concept the decisions change (old names, old rules, old counts) and list every location the plan misses, with path:line.' },
  ]
  const crit = await parallel(LENSES.map(l => () => agent(`${CTX}

You are a CRITIC of the change plan at ${PLAN} (read it fully, and the decisions, findings and research files). Scope: ${scope}. Lens: ${l.text}
Be concrete and adversarial; do not praise. Output issues only; where = plan section or edit id, plus repository path:line when relevant.`, { label: 'critic:' + l.key, phase: 'Critique', effort: 'high', schema: ISSUES })
    .then(r => ({ tag: l.tag, lens: l.key, issues: r ? r.issues : [] }))))
  for (const c of crit.filter(Boolean)) c.issues.forEach((i, n) => issues.push(Object.assign({ id: c.tag + (n + 1), lens: c.lens }, i)))
  log(`critique: ${issues.length} issues (${issues.filter(i => i.severity === 'high').length} high)`)

  if (issues.length) {
    phase('Revise')
    const revised = await agent(`${CTX}
Exception: you write ${PLAN} and one backup copy of it (nothing else).

You are the PLANNER again. The plan is ${PLAN}. Critics raised these issues (JSON): ${JSON.stringify(issues)}
First copy ${PLAN} to the next free backup name ${join(SCRATCH, 'change-plan.vN.bak.md')} (never overwrite a backup). For each issue: verify it against the plan, the decisions and the repository; accept and fix the plan in place, or reject it with a one-line reason (only when the critic is wrong). Keep the section structure. Then ${MODE === 'new' ? 'append "## 7. Critique resolution"' : 'append a critique-resolution subsection to the amendment section you are reviewing'}: a table | Issue | Lens and severity | Issue (short) | Resolution | Fix and where applied | with every issue id.
${RETURN_SHAPE}`, { label: 'planner:revise', phase: 'Revise', effort: 'xhigh', schema: PLANNED })
    if (revised) final = revised
  }
}

log('groups for apply-changes.js: ' + JSON.stringify(final.groups.map(g => ({ key: g.key, sections: g.sections, files: g.files }))))
return { mode: MODE, plan: PLAN, research: research.map(r => ({ key: r.key, summary: r.summary })), critiqueIssues: issues.length,
  summary: final.summary, groups: final.groups, keyChoices: final.keyChoices, surprisingFacts: final.surprisingFacts,
  openItems: final.openItems, staleTerms: final.staleTerms, accepted: final.accepted, rejected: final.rejected }
