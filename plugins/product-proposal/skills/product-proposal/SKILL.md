---
name: product-proposal
description: Use when Petr says "udělej mi produktový artefakt", "product proposal", "produktový návrh", "PRD", asks to propose, argue and document a product change for Agnes before it is built, or asks to update, reconcile or hand over an existing PRD during the build, acceptance or later ("aktualizuj PRD", "stav do PRD", "převzetí", "retro"). One bilingual (CZ/EN) Agnes Artifact per feature on agnes.keboola.dev in the "Product proposal" content and design system, the single entry point for the feature's whole life - status now, continue here, current behaviour, one slice table with a generated timeline, acceptance and feedback, one decision register with meeting-brief cards and forms, the full product design (research, competition, current state in code, C4 impact, surfaces matrix, alternatives), agentic retro, generated log, GPT Astra second opinion, glossary - linked both ways to a Linear TEAG feature and to satellite artifacts.
---

# Product proposal artifact

Petr reviews a feature as an Agnes Artifact before anything is built, and the same artifact then carries the feature through build, acceptance and later changes. It is the single entry point: anyone (Petr on a phone, a teammate arriving cold, an agent continuing the work) finds where it stands, what waits for whom, what was decided and why, and what happened. Report to Petr in Czech. Code, scripts and working notes on disk are English; the artifact's own sources (the bilingual Markdown and HTML, the Czech titles in `slices.json`) are Czech + English.

Fixed references (agnes.keboola.dev, CLI `agnes`):

| What | Value |
|---|---|
| Content system | `ef74c6ed49c241f490b6fb95ad65f84e@5` (Product proposal; private Store item). Variant `building` once the first PR is open |
| Design system | `ds_C-_CIyerl8dQ1ZzkXFE9zwrn@2` (slug `product-proposal`) |
| Page template | `assets/template.html` (components, language toggle, grouped TOC, overdue badge, decision forms) |
| Markdown skeleton | `assets/template.md` (`<!-- cs:<id> -->` markers, `<!-- lang:cs -->` / `<!-- lang:en -->` blocks) |
| Build-stage sections | `assets/building-sections.md` and `.html` (Continue here, What it does today, Acceptance and feedback, Retro, Log) |
| Plan and progress | `python3 assets/progress.py refresh slices.json` then `render slices.json --page P --md M --artifact ID --events events.json` |
| Checks | `python3 assets/check_proposal.py draft.md --page page.html --version vN` (content system per language + freshness and links) |
| Design system rebuild | `python3 assets/build_design_system.py` (keeps bundle and template CSS in sync) |
| Linear | team TEAG, `https://linear.app/keboola/issue/TEAG-<n>` |
| Worked example | Agentic workflows PRD, artifact `zoEtD4Xg2_AeQCCJ_QvdzJ4g` v37 (first PRD in this structure) |

Read `agnes content-system show ef74c6ed49c241f490b6fb95ad65f84e@5` before writing: it holds the section order, presence rules, voice and banned phrases. There are no word limits; the rule is no AI slop and no filler, and data the reader needs belongs in the document. Read `assets/template.html` before building a page.

## The document

Section order (fixed by the content system): What changed, Summary, Status now, Continue here, What it does today, Plan and progress, Acceptance and feedback, Decisions, Problem, Goals and non-goals, Principles, How we know it worked, Current state in Agnes, Research and competition, Proposal, Alternatives, Architecture impact, Retro, Log, Second opinion, Glossary, Sources, Appendix. The TOC groups them as Now / Proposal / Looking back and reference.

- **One order for every stage** (Petr, 2026-10-28): the server enforces a single section order, so before the build too the product design follows Decisions. The decision cards are self-contained meeting briefs, which is what Petr reads first before the build.
- **Before the build** (no variant): Summary, Status now (stage Proposal, decisions needed by when), Plan and progress (phases, planned slices), Decisions (register + open cards) and the full product design. The product design is the bulk of the page and is never shortened: what and why, the problem with a real example, how it works today with a code map, competition, the proposal, alternatives, where we touch the architecture.
- **Once the first PR is open** (variant `building`): add the sections from `assets/building-sections.*`. Current state becomes "Baseline before the build" with its commit and date; metrics keep "Before the build" as the baseline and get a measured value.
- **Status now** always shows four separate states (code merged, deployed where, enabled which switches where, accepted by whom), each with how it was verified; three times (last work event, last reconciled with sources, next check as `<span data-next-check="<UTC ISO>">`, which the page flags "update overdue" after it passes); waiting for you; waiting for others; a links row (Linear, GitHub PRs, satellite artifacts, user docs).
- **One slice table** in `slices.json` is the single source of plan and progress: permanent IDs (W01...), aliases for older names, phase, Czech and English title, PR, state, note. The table, the timeline and the log are generated into `<!-- gen:slices -->`, `<!-- gen:timeline -->` and `<!-- gen:log -->` regions; never draw or edit them by hand. A slice with no PR keeps its state (planned, not started, postponed, dropped). Phase 3 or later ideas are slices with state "not started" and a note "not committed".
- **One decision register** in Decisions holds every decision, also small ones (simplifications, process rules, a poll winner): ID, question, decision, when, who, state (open, decided, deferred, amended by X, superseded by X), source. Open cards follow in full. Decided cards, the original rationale and the baseline are frozen records: collapsed, never rewritten, only annotated ("amended by S2", "deferred by S3", a dated note). A later decision that changes an earlier one is a new row, and every **current** statement of the old behaviour (Summary, Status now, What it does today, Plan, examples meant to be copied, Glossary) is updated in the same version.
- **Satellite artifacts** only when they have their own audience or interaction (a poll, the E2E acceptance plan, content system `agnes/e2e-test-plan@1`). Link both ways (`agnes artifact link add`) and in the Status links row, and record the outcome here (poll winner = register row, E2E run = verdict in Acceptance). A satellite never holds the only copy of a decision.
- **Retro** (optional to the checker, required by this skill) after each phase and after acceptance: what worked, what did not (stalls, repeated failures, review loops, usage limits, manual rescues), each backed by the Log or a named source; then changes to skills, hooks, checks, rules or templates with state (proposed, in place) and a link.

## Modes

### Propose (new feature)

1. **Frame and Linear.** Restate the ask in one sentence and name the decision Petr has to make. Find the Linear feature in TEAG (`list_issues`, team TEAG, a query). If several match, ask which one; if none exists, ask Petr whether to create it, then create it (`save_issue`, team TEAG, short description).
2. **Evidence** (parallel sub-agents, each returns facts with sources):
   - **Current state in Agnes:** how it works for users today, the code map (file:line), docs (`docs/`, `app/user_docs/`), switches, tests. Read-only Explore agent on a fresh `origin/main`.
   - **Architecture:** C4 containers and components that change (`docs/c4/MODEL.md`); the surfaces matrix (Tests, Docs, Frontend, API, CLI, MCP, external services), each yes/no and why; the CONTRIBUTING sync-map rows that apply.
   - **Research and competition:** 3-5 competitors via Perplexity (`perplexity_ask`; `perplexity_reason` for comparisons; `perplexity_research` only when Petr asks for deep research). Per competitor: approach, source link, date checked. Agnes before and after each phase.
   - **Screenshots** of today from agnes.keboola.dev via Claude in Chrome, embedded as data: URIs, annotated with the template's SVG overlay (numbered callouts). **Concepts** via Nano Banana only with the "Concept" badge.
3. **Proposal.** Problem with one real example and its source; goals and non-goals; principles with short names; outcome metrics (baseline, target, date) and guardrails. The user journey and behaviour, then at least two real alternatives with why this one wins (cost, risk, fit with Agnes principles: on-prem parity, rollout switch, Postgres app-state, no comments in code, coupled surfaces).
4. **Decisions.** Every open choice is a register row and a card prepared like a brief for a decision meeting: Petr has not read the code and decides from the card alone. Per card: **What it is about** (today's situation for a person, what changes, why now; no file paths or internal names); **What it looks like** (one concrete example carried through every option); an **options table** (Pros; Cons: effort, money, who is affected, risk; Change later; Who does this, with sources); the **recommendation and the one reason that decides it**; the template's form. Title it as a plain question.
5. **Plan.** Phases with ambitious, realistic dates at AI-agent build speed (days; a core phase is typically 3 days), none waiting for decisions; planned slices in `slices.json`; what works for users after each phase; owner Petr unless he names someone; rollout switch (`purpose="rollout"`, default off unless Petr decides otherwise); dependencies; risks; given/when/then acceptance examples. Status now: stage Proposal, decisions needed by when, next check.
6. Plain language throughout: explain every number, unit and term on first use; glossary for every new or redefined term (check `GLOSSARY.md`).
7. **Second opinion, build, publish:** see the shared steps below.

### Update (during the build and after)

Run at the start and end of every work session on the feature, after every merge, decision, incident or re-plan, and whenever Petr asks for the state.

1. Read the current head of the artifact (`agnes artifact read <id> --source --raw --all`) and its comments; never update from memory.
2. **Recover the inputs** if this session does not have them: `python3 assets/progress.py extract draft.md --out .` (slices.json and events.json live in the draft's `gen:data` region, so every artifact version carries them).
3. **Reconcile with sources:** `python3 assets/progress.py refresh slices.json` (PR state, opened, merged, review, auto-merge); the release runs on main (`gh run list --workflow release.yml --branch main`); the switches on each instance (`agnes admin config export`, read only the switch lines, delete the file); the deploy and test state you rely on. Also re-read measured outcomes for the metrics, owed reviews (admin merges, Devin retro reviews, unresolved slice findings) and the before-production gate. Only now move "last reconciled".
4. Add extra events (incidents, deploys, decisions taken in chat, blockers) to `events.json`; a failure gets an `id`; its fix is an event with `resolved_by` pointing back, and repeats are one event with `count`.
5. Update by hand only what is not generated: Status now (focus, four states, three times, waiting lists), Continue here (active slice, branch, PR state as gh reports it, last verified result, next action, blockers, responsible), What it does today (steps and limits that changed), the decision register and anything a new decision invalidates, Acceptance and feedback, What changed (only this version against the previous one).
6. `python3 assets/progress.py render slices.json --page page.html --md draft.md --artifact <id> --events events.json` (also writes `gen:data`).
7. Check, publish (shared steps). When a phase completes, write the Retro.

### Accept (handover to Petr)

1. Create the E2E acceptance plan as a satellite artifact with content system `agnes/e2e-test-plan@1` (exit criteria fixed before the run), link it both ways and in the Status links row.
2. After each run: the "What was verified" table, the feedback register (item, from, when, state, link), known issues, and the verdict (who, when, on which deployment, with which reservations) in Acceptance; the accepted state in Status now.
3. Write the Retro of the whole build.

## Shared steps

### Second opinion (mandatory before every publish that changes the design or a decision, and on every larger update)
- Use the `second-opinion` skill: GPT Astra (`gpt-6-astra`, effort medium) on the full draft, run from the Agnes repo root at fresh `origin/main` so it checks claims against the code. Astra reads only Markdown; give it the English half when the draft is large.
- Ask it for contradictions between parts, statements in the top parts that are stale or unsupported, information lost in collapsed records, and Retro claims without evidence. Incorporate or explicitly rebut every finding; the Second opinion section lists each finding and what was done.

### Build
- Write the Markdown from `assets/template.md` (plus `building-sections.md` once building): both languages in every bilingual section, one marker per section; the slice table, registers and log are English only, outside the language blocks.
- Build the HTML from `assets/template.html` (plus `building-sections.html`): replace all sample content, keep the components and scripts; diagrams as inline SVG styled by design tokens; no external hosts, no storage APIs.
- The page header shows a hardcoded version label (`vN` in the draft's metadata line and in the page header): set it to the version this publish will create (current head + 1).
- Run `python3 assets/check_proposal.py draft.md --page page.html --version vN` (What changed becomes required from v2 on) until both languages report 0 findings and the freshness check reports 0 findings (version label, every PR number linked, generated regions present, next check in the future, every decision card in the register).
- Self-review against the content system checklist: every Agnes claim has a path or link, every competitor claim a source, verified/inferred/unverified labels where needed, no filler, both languages say the same.

### Publish
- New: `agnes artifact create --html page.html --markdown-source draft.md --title "<title>" --visibility instance --audience everyone --design-system ds_C-_CIyerl8dQ1ZzkXFE9zwrn@2 --content-system ef74c6ed49c241f490b6fb95ad65f84e@5 --summary "<1-2 sentences>" --keywords teag-<n>,<topic words>`.
- Update: `agnes artifact update <id> --base-version <head> --html ... --markdown-source ... --note "<what changed>" --summary ... --keywords ...` (summary and keywords every time). A conflict means someone published in between: read the new head, merge, rebuild.
- Settings: `agnes artifact settings <id> --form-responses` (comments stay visible to everyone; everyone with access may answer).
- Keywords are the public tags: always `teag-<n>` plus 2-5 topic words. Petr's private label: `agnes artifact tag <id> --add <topic>`.
- Link back: the artifact URL on the Linear issue (`save_issue` with `links`; keep the Linear description short); satellites with `agnes artifact link add`.
- Open the published page in Claude in Chrome: no CSP errors, language toggle, grouped TOC, timeline, decision forms, the overdue badge logic, dark mode, phone width.

### Report to Petr
In Czech, outcome first: the link, version, who can open it, where the feature stands (the four states), what waits for him (one line each), what Astra changed, what is unverified. Re-read every PR or CI state you mention right before answering. No code in chat.

## Rules
- Facts before claims: verify numbers, paths, states and competitor statements against the source; label anything not verified; missing history is "not recorded", never reconstructed.
- States literally as their tool reports them (OPEN, MERGED, AUTO-MERGE ENABLED) with the time read.
- No AI slop: no filler, hype or generic statements; numbers over adjectives; short sentences.
- One feature, one artifact: a revision, follow-up research or a status update is a new version, never a new artifact; satellites only for their own interaction.
- Never publish secrets, customer-specific data or anything with visibility `public`. Server config exports may hold secrets: read only the lines you need and delete the file.
- Do not edit `assets/` during a normal run; improvements to the templates, scripts or systems are a separate, explicit change (republish the content or design system version and update the table above).
