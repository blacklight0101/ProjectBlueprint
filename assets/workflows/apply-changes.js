export const meta = {
  name: 'blueprint-apply-changes',
  description: 'Apply the canonical change plan with one editor per file group, a verifier per group that diffs against the plan and a fix, then cross-file check lenses in rounds with issues routed to the owning groups',
  whenToUse: 'Step 6 and the first part of step 7 of the project-blueprint review loop, with a clean git tree and an approved plan',
  phases: [
    { title: 'Preflight', detail: 'the working tree must be clean' },
    { title: 'Edit', detail: 'one editor per group, disjoint files' },
    { title: 'Verify', detail: 'per-group verifier against the plan, then fix' },
    { title: 'Cross-check', detail: 'repository-wide lenses' },
    { title: 'Fix', detail: 'issues routed back to the owning groups' },
  ],
}

// project-blueprint template: apply-changes.js (see references/workflows.md and references/review-loop.md)
// Keep this file pure ASCII with LF line endings.
// This workflow never rewrites the plan. Amendments are a separate plan-changes.js run in amend mode.
// If new decisions arrive while it runs: stop it (TaskStop), revert the partial edits, amend the plan, restart.
//
// CONFIGURATION. Edit the constants below, or pass the same keys in the Workflow args object
// (args values win). Windows paths need doubled backslashes inside JS strings.
// Changing any constant that is interpolated into a prompt invalidates the resume cache from that agent on.
const CFG = (typeof args === 'object' && args) ? args : {}
const PROJECT = CFG.project || 'PROJECT_NAME'            // display name of the project
const REPO = CFG.repo || 'REPO_PATH'                     // absolute path of the repository to edit
const SCRATCH = CFG.scratch || 'SCRATCH_PATH'            // absolute path of the session scratchpad
const DATE = CFG.date || 'YYYY-MM-DD'                    // date for new notes, withdrawals and headers
const OWNER = CFG.owner || 'OWNER_NAME'                  // product owner whose decisions are binding
const CONTEXT = CFG.context || 'PROJECT_CONTEXT'          // 2-4 sentences: what the product is, stack, current release
const PLAN = CFG.plan || 'PLAN_FILE'                     // the canonical change plan, e.g. SCRATCH + '\\change-plan.md'
const DECISIONS = CFG.decisions || ['DECISIONS_FILE']    // every decisions file (and addendum) the plan applies
const AMENDMENTS = CFG.amendments || ''                  // e.g. 'sections 8 (Amendment ...) and 9 (Amendment ...)'; '' if none
const ALLOW_DIRTY = CFG.allowDirty || false               // true only if the owner accepted editing on a dirty tree
const MAX_ROUNDS = CFG.maxRounds || 3                     // cross-check rounds; the rest goes to final-pass.js
// Groups: copy them from section 6 of the plan (plan-changes.js returns them). Every file in exactly one group.
// files: paths relative to REPO; a trailing slash means a folder; '*' matches within one path segment.
const GROUPS = CFG.groups || [
  { key: 'G1', sections: 'section 3.1', files: ['docs/spec/requirements.md'] },
  { key: 'G2', sections: 'the section 3 subsections headed G2', files: ['docs/rfc/', 'docs/roadmap.md', 'docs/process-flows.md', 'docs/legacy-sources.md', 'README.md', 'docs/README.md', 'docs/decision-log.md'] },
  { key: 'G3', sections: 'the section 3 subsections headed G3', files: ['docs/architecture.md', 'docs/data-model.md', 'docs/conventions.md', 'docs/environments-and-delivery.md', 'CLAUDE.md'] },
  { key: 'G4', sections: 'the section 3 subsections headed G4', files: ['docs/adr/'] },
  { key: 'G5', sections: 'the section 3 subsections headed G5', files: ['docs/orchestration/', '.claude/agents/', 'handoff.md'] },
  { key: 'G6', sections: 'the section 3 subsections headed G6', files: ['docs/design-system.md', 'docs/design-system-brief.md', 'docs/design/'] },
]
// Stale-text sweep: terms of the OLD design (plan-changes.js returns staleTerms). Regex fragments are fine.
const STALE_TERMS = CFG.staleTerms || []
// Paths the checkers skip (generated files, mockups, PDFs).
const EXCLUDE = CFG.exclude || ['*.pdf', 'docs/design/**/*.html']
// Optional path of scripts/check_docs.py of the project-blueprint skill; the structure lens runs it when set.
const CHECK_DOCS = CFG.checkDocs || ''
// ---- end of configuration ----

function unset(name, value, placeholder) {
  if (!value || value === placeholder || (Array.isArray(value) && (!value.length || value.indexOf(placeholder) >= 0)))
    throw new Error('Set ' + name + ' at the top of apply-changes.js or pass it in args')
}
unset('PROJECT', PROJECT, 'PROJECT_NAME'); unset('REPO', REPO, 'REPO_PATH'); unset('SCRATCH', SCRATCH, 'SCRATCH_PATH')
unset('DATE', DATE, 'YYYY-MM-DD'); unset('OWNER', OWNER, 'OWNER_NAME'); unset('CONTEXT', CONTEXT, 'PROJECT_CONTEXT')
unset('PLAN', PLAN, 'PLAN_FILE'); unset('DECISIONS', DECISIONS, 'DECISIONS_FILE')

// Route a repository path to the group that owns it (first match wins; null when no group owns it).
function norm(p) { return String(p || '').replace(/\\/g, '/').replace(/^\.\//, '').replace(/\s*\(.*$/, '').trim().replace(/:\d+(?::\d+)?$/, '').toLowerCase() }
function toRegex(pattern) {
  const esc = pattern.replace(/[.+^${}()|[\]]/g, '\\$&').replace(/\*\*/g, '\u0000').replace(/\*/g, '[^/]*').replace(/\u0000/g, '.*')
  // Anchored at the repository root, so 'README.md' does not match docs/adr/README.md.
  return new RegExp('^' + esc + (pattern.endsWith('/') ? '' : '$'))
}
function groupOf(path) {
  const p = norm(path)
  const rel = p.startsWith(norm(REPO) + '/') ? p.slice(norm(REPO).length + 1) : p
  for (const g of GROUPS) for (const f of g.files) if (toRegex(norm(f)).test(rel)) return g.key
  return null
}

const CTX = `Context: ${REPO} is the documentation repository of ${PROJECT}. ${CONTEXT} Product owner: ${OWNER}, whose decisions are binding: ${DECISIONS.join('; ')}.
The canonical change plan (single source of truth for every identifier and edit) is ${PLAN}${AMENDMENTS ? '; it has been amended in ' + AMENDMENTS : ''}.
Rules: never run git commands that change state (git status, git diff, git log, git grep are fine). No emojis. English. Ids are never renumbered or reused. Plan-internal ids (edit ids like REQ/07, findings like A1, holes like H-A1, critic issues like F3, the words "change plan", "registry" or "critique") never go into repository text.`

const REPORT = { type: 'object', properties: {
  applied: { type: 'array', items: { type: 'string' } },
  skipped: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, reason: { type: 'string' } }, required: ['id', 'reason'] } },
  notes: { type: 'string' } }, required: ['applied', 'skipped', 'notes'] }
const ISSUES = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: {
  file: { type: 'string' }, where: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
  issue: { type: 'string' }, fix: { type: 'string' } }, required: ['file', 'where', 'severity', 'issue', 'fix'] } } }, required: ['issues'] }
const CLEAN = { type: 'object', properties: { clean: { type: 'boolean' }, head: { type: 'string' }, status: { type: 'string' } }, required: ['clean', 'head', 'status'] }

phase('Preflight')
const pre = await agent(`Run exactly these two read-only commands and report: git -C "${REPO}" status --porcelain ; git -C "${REPO}" log -1 --format=%h . clean = true only when the status output is empty. status = the status output (or empty). Do not run anything else.`, { label: 'preflight', phase: 'Preflight', effort: 'low', schema: CLEAN })
if (!pre) throw new Error('preflight failed; check the repository path')
if (!pre.clean && !ALLOW_DIRTY) throw new Error('the working tree of ' + REPO + ' is not clean; commit, stash or revert first: ' + pre.status)
log('preflight: HEAD ' + pre.head + (pre.clean ? ', tree clean' : ', tree DIRTY (allowed by ALLOW_DIRTY)'))

function editorPrompt(g, extra) {
  return `${CTX}

You are EDITOR ${g.key}. Your files (edit ONLY these; paths relative to ${REPO}; a trailing slash means every file in that folder, including new files the plan creates there): ${g.files.join('; ')}.
Read ${PLAN}: section 1 (Principles), section 2 (Registry) and section 5 (Items not decided) fully${AMENDMENTS ? ', every amendment section (' + AMENDMENTS + ') fully' : ', and every amendment section at the end fully'}, then ${g.sections}, and the coverage rows and critique-resolution items that concern your files. Also read the decisions files.
${extra || `Apply EVERY numbered edit for your files exactly as specified. Rules: use only the identifiers of the registry (ids, names, numbers, permission codes, settings, card ids, ADR file names, counts); when a name changes, change every occurrence in your files, not only the listed line; match each document's existing style, headings, table formats and tone; new ADRs follow docs/adr/_template.md; new notes and withdrawals are dated ${DATE}; if an anchor has moved, find the equivalent place; if an edit is impossible or contradicts the registry, skip it and report why. Touch no other file. When done, re-read each of your files top to bottom and repair any markdown table, list or link you broke.`}
Return the report: applied edit ids, skipped (id and reason), notes.`
}

function verifierPrompt(g, rep) {
  return `${CTX}

You are the VERIFIER for editor group ${g.key}. Files: ${g.files.join('; ')} (relative to ${REPO}). Read ${PLAN} (sections 1, 2 and 5, the amendment sections, and ${g.sections}) and the decisions files. Run git -C "${REPO}" diff -- <path> for each existing file of the group and read new (untracked) files fully (git -C "${REPO}" status --porcelain lists them).
The editor reported (JSON): ${JSON.stringify(rep || {})}
Check adversarially: (1) every numbered edit for these files is applied and says what the plan says - nothing weaker, nothing invented; (2) identifiers match the registry exactly; (3) every skipped edit has a valid reason, otherwise it is an issue; (4) no collateral damage: unrelated text removed, broken tables, lists or links, duplicated paragraphs, leaked plan-internal ids; (5) the decisions are reflected wherever they concern these files. Report issues only, each with the file, the location and the exact fix.`
}

phase('Edit')
const results = await pipeline(GROUPS,
  g => agent(editorPrompt(g), { label: 'edit:' + g.key, phase: 'Edit', effort: 'high', schema: REPORT }),
  (rep, g) => agent(verifierPrompt(g, rep), { label: 'verify:' + g.key, phase: 'Verify', effort: 'high', schema: ISSUES })
    .then(v => ({ rep, issues: v ? v.issues : [] })),
  (r, g) => (r && r.issues.length)
    ? agent(editorPrompt(g, `A verifier found these issues in your files (JSON): ${JSON.stringify(r.issues)}. Verify each against the plan and the decisions, then fix every valid one; if an issue is wrong, leave the text and say why in notes.`), { label: 'fix:' + g.key, phase: 'Verify', effort: 'high', schema: REPORT })
        .then(f => ({ key: g.key, skipped: r.rep ? r.rep.skipped : [], verifierIssues: r.issues.length, fix: f }))
    : { key: g.key, skipped: r && r.rep ? r.rep.skipped : [], verifierIssues: 0, fix: null })
const groupResults = results.map((r, i) => r || { key: GROUPS[i].key, failed: true })
log('edit and verify done: ' + groupResults.map(r => r.key + (r.failed ? ':FAILED' : ':' + r.verifierIssues)).join(' '))

const LENSES = [
  { key: 'ids-counts', text: 'IDS AND COUNTS: every referenced id exists where it is defined (RF/RNF in the requirements, Q-nn in its table with a valid Status, ADR-nnn as a file, DEC-nn in docs/decision-log.md, DEF-nn in the legacy defect register, G-nn in the gates list, card ids in tasks.md); counts (ADRs by status, cards by phase and by difficulty band, requirements) are identical everywhere they are stated and match the registry of the plan; docs/adr/README.md lists every ADR file with the right title, status and file name; every Depends on names an existing card and there is no cycle; registry names (states, tables, permissions, settings, migrations) are used exactly.' },
  { key: 'decisions', text: 'DECISION FIDELITY: for every decision in the decisions files and docs/decision-log.md, every document that touches its topic says the same thing, with no leftover of the old design; nothing is presented as decided that the owner did not decide; undecided items are Q-nn rows with a default and Status "Default applies" or "Open".' },
  { key: 'stale', text: 'STALE TEXT SWEEP: grep the whole repository' + (EXCLUDE.length ? ' (skip ' + EXCLUDE.join(', ') + ')' : '') + ' for leftovers of the old design and judge each hit in context. Terms: ' + (STALE_TERMS.length ? STALE_TERMS.map(t => "'" + t + "'").join(', ') : 'build the list yourself from the names, rules and counts the plan removes or renames (section 2 and the per-file edits)') + '. Report only real leftovers.' },
  { key: 'structure', text: 'STRUCTURE AND LINKS: every markdown table in the changed files has a consistent column count; every relative link and every cited path or ADR file name resolves; section references between documents still point at existing headings; no leaked plan-internal ids; no duplicated sections; new ADRs follow docs/adr/_template.md and carry Date, Status and Deciders; docs/decision-log.md is well formed (Id | Date | Decision | Answer to | Where applied) and linked from docs/README.md and handoff.md.' + (CHECK_DOCS ? ' Run python "' + CHECK_DOCS + '" "' + REPO + '" and include its real findings.' : '') + ' Use git -C "' + REPO + '" diff --stat and status to see the changed files.' },
]

async function crossCheck(round) {
  const found = await parallel(LENSES.map(l => () => agent(`${CTX}

You are a CROSS-FILE CHECKER (round ${round}). The editors have applied the plan to ${REPO} (git -C "${REPO}" status and diff show the changes). Lens: ${l.text}
READ-ONLY. Be adversarial and concrete; verify every issue in the current files; report issues only, each with the exact path relative to the repository, the location, the severity and the fix. When one problem spans several files, report one issue per file. The plan is the reference for identifiers; the decisions win when the plan conflicts with them.`, { label: 'check:' + l.key + ':r' + round, phase: 'Cross-check', effort: 'high', schema: ISSUES })))
  return found.filter(Boolean).flatMap(f => f.issues)
}

const rounds = []
let remaining = []
let unrouted = []
for (let round = 1; round <= MAX_ROUNDS; round++) {
  phase('Cross-check')
  const issues = await crossCheck(round)
  const serious = issues.filter(i => i.severity !== 'low')
  log(`round ${round}: ${issues.length} cross-file issues (${serious.length} medium or high)`)
  rounds.push({ round, issues: issues.length, serious: serious.length })
  remaining = issues
  if (!serious.length) break
  phase('Fix')
  const byGroup = {}
  unrouted = []
  for (const i of serious) {
    const k = groupOf(i.file)
    if (k) (byGroup[k] = byGroup[k] || []).push(i)
    else unrouted.push(i)
  }
  if (unrouted.length) log(`round ${round}: ${unrouted.length} issues in files no group owns; left for final-pass.js`)
  const fixes = await parallel(Object.keys(byGroup).map(k => () => {
    const g = GROUPS.find(x => x.key === k)
    return agent(editorPrompt(g, `Cross-file checkers found these issues in your files (JSON): ${JSON.stringify(byGroup[k])}. Verify each against the files, the plan and the decisions, then fix every valid one in your files only. If fixing needs a change in a file outside your group, fix your side and describe the other side in notes. If an issue is wrong, leave the text and say why in notes.`), { label: 'xfix:' + k + ':r' + round, phase: 'Fix', effort: 'high', schema: REPORT })
      .then(f => ({ key: k, notes: f ? f.notes : 'no report' }))
  }))
  rounds[rounds.length - 1].fixNotes = fixes.filter(Boolean)
}

return { head: pre.head, groups: groupResults, rounds,
  lastRoundIssues: remaining.map(i => Object.assign({ group: groupOf(i.file) }, i)), unrouted,
  stoppedClean: rounds.length > 0 && rounds[rounds.length - 1].serious === 0,
  next: 'If stoppedClean is false or unrouted is not empty, run final-pass.js with SEED_ISSUES = unrouted (the lenses re-find the rest); then the own spot checks of step 8.' }
