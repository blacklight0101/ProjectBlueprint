export const meta = {
  name: 'blueprint-review',
  description: 'Consistency review of a project documentation set: parallel read-only reviewers by slice, an adversarial check of each slice high findings, and one merged findings file with owner questions and defaults',
  whenToUse: 'Step 1 of the project-blueprint review loop, after the step 0 preflight (repository shape, check_docs.py)',
  phases: [
    { title: 'Review', detail: 'one read-only reviewer per slice' },
    { title: 'Verify', detail: 'try to refute each high finding of the slice' },
    { title: 'Merge', detail: 'dedup, number and write the findings file' },
  ],
}

// project-blueprint template: review.js (see references/workflows.md and references/review-loop.md)
// Keep this file pure ASCII with LF line endings.
//
// CONFIGURATION. Edit the constants below, or pass the same keys in the Workflow args object
// (args values win). Windows paths need doubled backslashes inside JS strings.
// Changing any constant that is interpolated into a prompt invalidates the resume cache from that agent on.
const CFG = (typeof args === 'object' && args) ? args : {}
const PROJECT = CFG.project || 'PROJECT_NAME'            // display name of the project
const REPO = CFG.repo || 'REPO_PATH'                     // absolute path of the repository to review
const SCRATCH = CFG.scratch || 'SCRATCH_PATH'            // absolute path of the session scratchpad (outputs go here)
const DATE = CFG.date || 'YYYY-MM-DD'                    // today; scripts cannot read the clock
const OWNER = CFG.owner || 'OWNER_NAME'                  // product owner who answers the questions
const CONTEXT = CFG.context || 'PROJECT_CONTEXT'          // 2-4 sentences: what the product is, stack, current release
const CHECK_DOCS_OUT = CFG.checkDocsOut || ''            // optional: path of the saved check_docs.py output; its issues are skipped
const VERIFY_HIGH = CFG.verifyHigh !== undefined ? CFG.verifyHigh : true   // adversarial check of high findings
// Slices: one reviewer each. Adjust the file lists to the repository (paths relative to REPO).
const SLICES = CFG.slices || [
  { key: 'A', title: 'Product: spec, RFC, roadmap, flows, legacy',
    files: ['docs/spec/requirements.md', 'docs/rfc/', 'docs/roadmap.md', 'docs/process-flows.md', 'docs/legacy-sources.md', 'docs/decision-log.md', 'README.md', 'docs/README.md'],
    focus: 'requirements that contradict each other or a project rule; Given/When/Then scenarios vs the rule text; priorities vs roadmap phases and requirements in no phase; non-goals vs requirements; the open-question table (every Q-nn has owner, needed by, default and a valid Status); process flows vs the spec; defect register (DEF-nn) claims vs the requirements that close them; traceability gaps; stated counts.' },
  { key: 'B', title: 'Technical: ADRs, architecture, data model, conventions, environments',
    files: ['docs/adr/', 'docs/architecture.md', 'docs/data-model.md', 'docs/conventions.md', 'docs/environments-and-delivery.md', 'CLAUDE.md'],
    focus: 'ADRs vs architecture text; ADR index vs ADR files and statuses; data constraints (keys, check constraints, unique indexes) vs the flows that write them; permissions and grants vs the actions each role or login performs; migration or version numbering overlaps; enum lists vs constraints; configuration and secrets rules; package baseline vs ADRs; folder layout rules vs architecture.' },
  { key: 'C', title: 'Delivery: orchestration, tasks, agents, handoff, design system',
    files: ['docs/orchestration/README.md', 'docs/orchestration/tasks.md', '.claude/agents/', 'handoff.md', 'docs/design-system.md', 'docs/design-system-brief.md'],
    focus: 'task card dependency cycles; a component, table or file used by a card before the card that builds it; circular or unreachable gates (G-nn); card counts per phase and per difficulty band vs every place that states them; card fields complete (Difficulty, Size, Depends on, Gate, Status, Reads, Do, Delivers, Done when, Refs); verifier tools vs the checks it must run; stale facts in handoff.md; design tokens vs pages and components; superseded briefs not marked.' },
]
// ---- end of configuration ----

function unset(name, value, placeholder) {
  if (!value || value === placeholder) throw new Error('Set ' + name + ' at the top of review.js or pass it in args')
}
unset('PROJECT', PROJECT, 'PROJECT_NAME'); unset('REPO', REPO, 'REPO_PATH'); unset('SCRATCH', SCRATCH, 'SCRATCH_PATH')
unset('DATE', DATE, 'YYYY-MM-DD'); unset('OWNER', OWNER, 'OWNER_NAME'); unset('CONTEXT', CONTEXT, 'PROJECT_CONTEXT')
function join(dir, name) { return dir + (dir.includes('\\') ? '\\' : '/') + name }
const FINDINGS = join(SCRATCH, 'review-findings-' + DATE + '.md')

const CTX = `Context: ${REPO} is the documentation repository of ${PROJECT}. ${CONTEXT} Product owner: ${OWNER}.
Id schemes used by the documents: RF-nnn functional and RNF-nnn non-functional requirements; Q-nn open questions (columns Id | Question | Owner | Needed by | Default | Status; Status is Open, Default applies, Answered (DEC-nn) or Withdrawn); ADR-nnn in docs/adr (Status Proposed, Accepted, Superseded by ADR-nnn, Amended); DEC-nn owner decisions in docs/decision-log.md; DEF-nn legacy defects; G-nn human gates; phases P0..Pn; task cards P<phase>-nn; RFC-nnn. Ids are never renumbered; withdrawn items keep their id.
Rules for you: READ-ONLY. Do not edit, create or delete any file. Never run git commands that change state (git status, git diff, git log, git grep are fine). No emojis. English.` +
  (CHECK_DOCS_OUT ? `\nMechanical issues (placeholders, FILL comments, broken links, duplicate ids, table shapes) are already listed in ${CHECK_DOCS_OUT}; do not report them again.` : '')

const REVIEW = { type: 'object', properties: {
  counts: { type: 'string' },
  inconsistencies: { type: 'array', items: { type: 'object', properties: {
    severity: { type: 'string', enum: ['high', 'medium', 'low'] },
    title: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
    issue: { type: 'string' },
    proposal: { type: 'string' } }, required: ['severity', 'title', 'evidence', 'issue', 'proposal'] } },
  holes: { type: 'array', items: { type: 'object', properties: {
    theme: { type: 'string', enum: ['Business rules', 'Architecture', 'Orchestration and design', 'Still owed'] },
    question: { type: 'string' },
    owner: { type: 'string' },
    neededBy: { type: 'string' },
    default: { type: 'string' },
    why: { type: 'string' } }, required: ['theme', 'question', 'owner', 'neededBy', 'default', 'why'] } },
}, required: ['counts', 'inconsistencies', 'holes'] }

const VERDICTS = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
  index: { type: 'number' },
  holds: { type: 'boolean' },
  severity: { type: 'string', enum: ['high', 'medium', 'low'] },
  note: { type: 'string' } }, required: ['index', 'holds', 'severity', 'note'] } } }, required: ['verdicts'] }

const MERGED = { type: 'object', properties: {
  file: { type: 'string' },
  high: { type: 'number' }, medium: { type: 'number' }, low: { type: 'number' }, refuted: { type: 'number' },
  questions: { type: 'number' },
  highlights: { type: 'array', items: { type: 'string' } },
  notes: { type: 'string' } }, required: ['file', 'high', 'medium', 'low', 'refuted', 'questions', 'highlights', 'notes'] }

function reviewPrompt(s) {
  return `${CTX}

You are REVIEWER ${s.key} (${s.title}). Your slice (paths relative to ${REPO}; a trailing slash means every file in that folder): ${s.files.join('; ')}.
Read every file of your slice fully. You may read any other file of the repository to confirm a cross-file contradiction; report it here when at least one side is in your slice.
Look for: ${s.focus}
Return:
- counts: the counts you observed (for example ADRs by status, cards by phase and band, requirements by module) in one line each.
- inconsistencies: two documents (or two places) that cannot both be true, stale statements, ambiguous rules. Severity high = a builder would build the wrong thing or the two texts cannot both hold; medium = stale or ambiguous, a builder would have to guess; low = cosmetic or a count in a secondary place. evidence = one entry per side, each "path:line - short gist" (line numbers as of the current HEAD). proposal = the concrete fix.
- holes: things a builder needs that no document decides. question = the exact question for ${OWNER} in plain words (explain any jargon inside the question); owner = who can answer; neededBy = the phase; default = the answer you propose if nobody decides; why = which card or requirement needs it; theme = Business rules, Architecture, Orchestration and design, or Still owed (only an external party can answer).
Be adversarial and precise. Verify every claim in the files; report nothing merely stylistic; do not praise.`
}

function verifyPrompt(s, highs) {
  return `${CTX}

You are a SKEPTIC for slice ${s.key}. A reviewer reported these HIGH findings (JSON, index = position): ${JSON.stringify(highs)}
For each one, open every cited line in ${REPO} and try to REFUTE it: is the contradiction real in the current text, or is it resolved elsewhere (a later note, an amendment, a superseding ADR, a definition that makes both true)? Return one verdict per index: holds (true only if you confirmed both sides), the severity you would give it, and a one-line note with the evidence.`
}

phase('Review')
const slices = await pipeline(SLICES,
  s => agent(reviewPrompt(s), { label: 'review:' + s.key, phase: 'Review', effort: 'high', schema: REVIEW }),
  (r, s) => {
    const rev = r || { counts: '', inconsistencies: [], holes: [] }
    const highs = rev.inconsistencies.filter(i => i.severity === 'high')
    if (!VERIFY_HIGH || !highs.length) return { s, rev, verdicts: [] }
    return agent(verifyPrompt(s, highs), { label: 'verify:' + s.key, phase: 'Verify', effort: 'high', schema: VERDICTS })
      .then(v => ({ s, rev, highs, verdicts: v ? v.verdicts : [] }))
  })

// Number findings per slice (A1, A2, ...) and holes (H-A1, ...), apply verdicts. Plan-internal ids only.
const all = []
const holes = []
let refuted = 0
for (const x of slices.filter(Boolean)) {
  const highs = x.highs || []
  const judged = x.rev.inconsistencies.map(i => {
    const hi = highs.indexOf(i)
    const v = hi >= 0 ? x.verdicts.find(d => d.index === hi) : null
    if (v && !v.holds) { refuted++; return Object.assign({}, i, { refuted: true, verifierNote: v.note }) }
    if (v) return Object.assign({}, i, { severity: v.severity, verifierNote: v.note })
    return i
  })
  const order = { high: 0, medium: 1, low: 2 }
  judged.sort((a, b) => (a.refuted ? 3 : order[a.severity]) - (b.refuted ? 3 : order[b.severity]))
  judged.forEach((i, n) => all.push(Object.assign({ id: x.s.key + (n + 1), slice: x.s.key }, i)))
  x.rev.holes.forEach((h, n) => holes.push(Object.assign({ id: 'H-' + x.s.key + (n + 1), slice: x.s.key }, h)))
  log(`slice ${x.s.key}: ${judged.length} inconsistencies, ${x.rev.holes.length} holes`)
}
const counts = slices.filter(Boolean).map(x => ({ slice: x.s.key, counts: x.rev.counts }))
log(`review: ${all.length} inconsistencies (${refuted} refuted by the skeptics), ${holes.length} holes`)

phase('Merge')
const merged = await agent(`${CTX}
Exception to READ-ONLY: you write exactly one file, ${FINDINGS}.

You are the MERGER. Reviewer output (JSON): inconsistencies ${JSON.stringify(all)}; holes ${JSON.stringify(holes)}; observed counts ${JSON.stringify(counts)}.
Write ${FINDINGS} in English with this structure:
1. Title "# Consistency review findings - ${DATE}", one line naming the reviewers (slices), the HEAD commit (git -C ${REPO} log -1 --format=%h) and a key of short file names you use.
2. One section per slice with subsections High, Medium, Low. One bullet per finding: "- <id> [<severity>] <title>." then "Evidence: ..." and "Proposal: ...". Keep the ids given (they are plan-internal and never go into the repository). When two slices report the same problem, keep the lower id, drop the other and add "(also <id>)".
3. A section "Refuted by the skeptics" listing refuted findings with the note, so nothing silently disappears.
4. A section "Holes" and then "Questions for ${OWNER}": one numbered table | # | Theme | Question | Default | Owner | Needed by | Source | with every hole and every inconsistency that needs an owner decision, grouped by theme in this order: Business rules, Architecture, Orchestration and design, Still owed. Every row has a default. Merge duplicate questions.
5. A section "Observed counts" with the counts per slice and any disagreement between them.
Return the file path, the counts per severity (after dedup), refuted count, question count, up to eight one-line highlights (the high findings first) and notes.`, { label: 'merge', phase: 'Merge', effort: 'medium', schema: MERGED })

return { findingsFile: FINDINGS, merged, inconsistencies: all.length, refuted, holes: holes.length,
  high: all.filter(i => i.severity === 'high' && !i.refuted).map(i => ({ id: i.id, title: i.title, evidence: i.evidence })) }
