export const meta = {
  name: 'blueprint-final-pass',
  description: 'Final repository-wide consistency pass: cross-file check lenses in rounds, each round followed by one sequential fixer that may edit any documentation file, until only low issues remain',
  whenToUse: 'End of step 7 of the project-blueprint review loop, after apply-changes.js, or alone after small edits',
  phases: [
    { title: 'Cross-check', detail: 'repository-wide lenses' },
    { title: 'Fix', detail: 'one fixer per round, any file' },
  ],
}

// project-blueprint template: final-pass.js (see references/workflows.md and references/review-loop.md)
// Keep this file pure ASCII with LF line endings.
// One fixer per round on purpose: group-restricted fixers skip issues that span files.
//
// CONFIGURATION. Edit the constants below, or pass the same keys in the Workflow args object
// (args values win). Windows paths need doubled backslashes inside JS strings.
// Changing any constant that is interpolated into a prompt invalidates the resume cache from that agent on.
const CFG = (typeof args === 'object' && args) ? args : {}
const PROJECT = CFG.project || 'PROJECT_NAME'            // display name of the project
const REPO = CFG.repo || 'REPO_PATH'                     // absolute path of the repository
const DATE = CFG.date || 'YYYY-MM-DD'                    // date for any note the fixer must add
const OWNER = CFG.owner || 'OWNER_NAME'                  // product owner whose decisions are binding
const CONTEXT = CFG.context || 'PROJECT_CONTEXT'          // 2-4 sentences: what the product is, stack, current release
const DECISIONS = CFG.decisions || ['DECISIONS_FILE']    // every decisions file the change applies (docs/decision-log.md is read too)
const PLAN = CFG.plan || ''                              // optional: the canonical change plan, reference for identifiers
const MAX_ROUNDS = CFG.maxRounds || 4                     // hard stop; remaining issues are reported
const FIX_LOW = CFG.fixLow !== undefined ? CFG.fixLow : true   // when only low issues remain: fix them once, then stop
// Issues carried over from apply-changes.js (unrouted or last-round issues), same shape as ISSUES items.
const SEED_ISSUES = CFG.seedIssues || []
// Stale-text sweep: terms of the OLD design. Regex fragments are fine.
const STALE_TERMS = CFG.staleTerms || []
// Paths the checkers skip (generated files, mockups, PDFs).
const EXCLUDE = CFG.exclude || ['*.pdf', 'docs/design/**/*.html']
// Files the fixer must never edit (in addition to anything outside REPO).
const PROTECTED = CFG.protected || []
// Optional path of scripts/check_docs.py of the project-blueprint skill; the structure lens runs it when set.
const CHECK_DOCS = CFG.checkDocs || ''
// Optional extra lens texts, e.g. { key: 'glossary', text: 'GLOSSARY: every term ... ' }.
const EXTRA_LENSES = CFG.extraLenses || []
// ---- end of configuration ----

function unset(name, value, placeholder) {
  if (!value || value === placeholder || (Array.isArray(value) && (!value.length || value.indexOf(placeholder) >= 0)))
    throw new Error('Set ' + name + ' at the top of final-pass.js or pass it in args')
}
unset('PROJECT', PROJECT, 'PROJECT_NAME'); unset('REPO', REPO, 'REPO_PATH'); unset('DATE', DATE, 'YYYY-MM-DD')
unset('OWNER', OWNER, 'OWNER_NAME'); unset('CONTEXT', CONTEXT, 'PROJECT_CONTEXT'); unset('DECISIONS', DECISIONS, 'DECISIONS_FILE')

const CTX = `Context: ${REPO} is the documentation repository of ${PROJECT}. ${CONTEXT} Product owner: ${OWNER}, whose decisions are binding: ${DECISIONS.join('; ')} and docs/decision-log.md.${PLAN ? ' The canonical change plan ' + PLAN + ' is the reference for identifiers; the decisions win when they conflict with it.' : ''}
Id schemes: RF-nnn, RNF-nnn; Q-nn (Status Open, Default applies, Answered (DEC-nn), Withdrawn); ADR-nnn (Proposed, Accepted, Superseded by ADR-nnn, Amended); DEC-nn; DEF-nn; G-nn; phases P0..Pn; cards P<phase>-nn; RFC-nnn. Ids are never renumbered or reused.
Rules: never run git commands that change state (git status, git diff, git log, git grep are fine). No emojis. English. Plan-internal ids (edit ids like REQ/07, findings like A1, critic issues like F3) never go into repository text.`

const ISSUES = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: {
  file: { type: 'string' }, where: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
  issue: { type: 'string' }, fix: { type: 'string' } }, required: ['file', 'where', 'severity', 'issue', 'fix'] } } }, required: ['issues'] }
const FIXREPORT = { type: 'object', properties: {
  applied: { type: 'array', items: { type: 'string' } },
  rejected: { type: 'array', items: { type: 'object', properties: { issue: { type: 'string' }, reason: { type: 'string' } }, required: ['issue', 'reason'] } },
  notes: { type: 'string' } }, required: ['applied', 'rejected', 'notes'] }

const LENSES = [
  { key: 'ids-counts', text: 'IDS AND COUNTS: every referenced id exists where it is defined (RF/RNF in the requirements, Q-nn in its table with a valid Status, ADR-nnn as a file, DEC-nn in docs/decision-log.md, DEF-nn in the legacy defect register, G-nn in the gates list, card ids in tasks.md); counts (ADRs by status, cards by phase and by difficulty band, requirements) are identical everywhere they are stated; docs/adr/README.md lists every ADR file with the right title, status and file name; every Depends on names an existing card and there is no cycle; the same concept has the same name in every document.' },
  { key: 'decisions', text: 'DECISION FIDELITY: for every decision in the decisions files and docs/decision-log.md, every document that touches its topic says the same thing, with no leftover of the old design; nothing is presented as decided that the owner did not decide; undecided items are Q-nn rows with a default and Status "Default applies" or "Open".' },
  { key: 'stale', text: 'STALE TEXT SWEEP: grep the whole repository' + (EXCLUDE.length ? ' (skip ' + EXCLUDE.join(', ') + ')' : '') + ' for leftovers of the old design and judge each hit in context. Terms: ' + (STALE_TERMS.length ? STALE_TERMS.map(t => "'" + t + "'").join(', ') : 'build the list yourself from what the decisions removed or renamed') + '. Report only real leftovers.' },
  { key: 'structure', text: 'STRUCTURE AND LINKS: every markdown table has a consistent column count; every relative link and every cited path or ADR file name resolves; section references between documents point at existing headings; no leaked plan-internal ids; no duplicated sections; ADRs follow docs/adr/_template.md and carry Date, Status and Deciders; docs/decision-log.md is well formed (Id | Date | Decision | Answer to | Where applied) and linked from docs/README.md and handoff.md; no leftover {{ placeholders or <!-- FILL comments.' + (CHECK_DOCS ? ' Run python "' + CHECK_DOCS + '" "' + REPO + '" and include its real findings.' : '') },
].concat(EXTRA_LENSES)

const rounds = []
let remaining = []
let seed = SEED_ISSUES
for (let round = 1; round <= MAX_ROUNDS; round++) {
  phase('Cross-check')
  const found = await parallel(LENSES.map(l => () => agent(`${CTX}

You are a CROSS-FILE CHECKER (final pass, round ${round}). The repository is ${REPO} (git -C "${REPO}" status and diff show uncommitted changes; new files are untracked). Lens: ${l.text}
READ-ONLY. Be adversarial but precise: report only real problems you verified in the current files, each with the exact path relative to the repository, the location, the severity and the exact fix. When several files must change for one problem, name all of them in the fix. Report nothing merely stylistic.`, { label: 'final:' + l.key + ':r' + round, phase: 'Cross-check', effort: 'high', schema: ISSUES })))
  const issues = seed.concat(found.filter(Boolean).flatMap(f => f.issues))
  seed = []
  const serious = issues.filter(i => i.severity !== 'low')
  rounds.push({ round, issues: issues.length, serious: serious.length })
  log(`final round ${round}: ${issues.length} issues (${serious.length} medium or high)`)
  remaining = issues
  if (!issues.length) break
  if (!serious.length && !FIX_LOW) break
  phase('Fix')
  const fix = await agent(`${CTX}

You are the FINAL FIXER (round ${round}). You may edit ANY documentation file in ${REPO} that an issue names${PROTECTED.length ? ', except ' + PROTECTED.join(', ') : ''}; nothing outside the repository, never git state. Checkers found these issues (JSON): ${JSON.stringify(issues)}
For each: verify it against the current files and the decisions; fix every valid one consistently in every file it affects (same words everywhere, dates ${DATE} on any new note); reject invalid ones with a reason. Keep each document's style; never renumber ids. Re-read the changed passages afterwards to make sure tables, lists and links are intact.`, { label: 'final:fix:r' + round, phase: 'Fix', effort: 'high', schema: FIXREPORT })
  rounds[rounds.length - 1].fix = fix ? { applied: fix.applied.length, rejected: fix.rejected, notes: fix.notes } : null
  if (!serious.length) { remaining = []; break }
}

const last = rounds[rounds.length - 1]
return { rounds,
  clean: !!last && (last.issues === 0 || (last.serious === 0 && !!last.fix)),
  lastRoundIssues: remaining,
  next: 'Own spot checks (check_docs.py, counts, stale grep), then docs/decision-log.md and handoff.md, then commit when the owner asks.' }
