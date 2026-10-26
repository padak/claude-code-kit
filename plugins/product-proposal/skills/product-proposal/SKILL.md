---
name: product-proposal
description: Use when Petr says "udělej mi produktový artefakt", "product proposal", "produktový návrh", "PRD", or asks to propose, argue and document a product change for Agnes before it is built. Produces one bilingual (CZ/EN) Agnes Artifact on agnes.keboola.dev in the "Product proposal" content and design system - research, competition, current state in code, C4 impact, surfaces matrix, argued proposal with alternatives, decisions with inline feedback forms, delivery plan, GPT Astra second opinion, glossary - linked both ways to a Linear TEAG feature.
---

# Product proposal artifact

Petr reviews a proposal as an Agnes Artifact before anything is built and comments in it. The artifact is the deliverable: factual, argued, complete, not padded. Report to Petr in Czech; everything written to disk is English, the artifact itself is Czech + English.

Fixed references (agnes.keboola.dev, CLI `agnes`):

| What | Value |
|---|---|
| Content system | `ef74c6ed49c241f490b6fb95ad65f84e@4` (Product proposal; private Store item) |
| Design system | `ds_C-_CIyerl8dQ1ZzkXFE9zwrn@2` (slug `product-proposal`) |
| Page template | `assets/template.html` (components, language toggle, TOC, decision forms) |
| Markdown skeleton | `assets/template.md` (`<!-- cs:<id> -->` markers, `<!-- lang:cs -->` / `<!-- lang:en -->` blocks) |
| Structure check | `python3 assets/check_proposal.py <draft.md>` (checks CZ and EN separately) |
| Design system rebuild | `python3 assets/build_design_system.py` (keeps bundle and template CSS in sync) |
| Linear | team TEAG, `https://linear.app/keboola/issue/TEAG-<n>` |

Read `agnes content-system show ef74c6ed49c241f490b6fb95ad65f84e@4` before writing: it holds the section order, word limits, voice and banned phrases. Read `assets/template.html` before building the page.

## Workflow

### 1. Frame and Linear
- Restate the ask in one sentence and name the decision Petr has to make.
- Find the Linear feature in TEAG (`list_issues` with team TEAG and a query). If several match, ask which one. If none exists, ask Petr whether to create it, then create it (`save_issue`, team TEAG, title = the feature, short description).
- An update of an existing proposal is a new version of the same artifact, never a new artifact (`agnes artifact update <id> --base-version N`).

### 2. Evidence (parallel sub-agents, each returns facts with sources)
- **Current state in Agnes:** how it works for users today, where it lives in the code (file:line), relevant docs (`docs/`, `app/user_docs/`), switches, existing tests. Read-only Explore agent on a fresh `origin/main`.
- **Architecture:** which C4 containers and components change (`docs/c4/MODEL.md`, `docs/c4/`); fill the surfaces matrix: Tests, Docs, Frontend, API, CLI, MCP, external services (agent sandbox, LLM provider, object store) - each yes/no and why; check the CONTRIBUTING sync-map rows that apply.
- **Research and competition:** 3-5 relevant competitors via Perplexity (`perplexity_ask`; `perplexity_reason` for comparisons; `perplexity_research` only when Petr asks for deep research). For each: how they address it, a source link, the date checked. Where Agnes is now vs after each phase.
- **Screenshots of the current state:** from agnes.keboola.dev via Claude in Chrome (Petr's signed-in session), saved to disk, embedded as data: URIs (resize to stay small). Annotate with the template's SVG overlay (numbered callouts), never by repainting the image.
- **Concepts:** mockups of the proposed state may be generated or edited with the Nano Banana MCP; always show them with the "Concept" badge and never present them as the current product.

### 3. Proposal
- Problem with one real example and its source; goals and non-goals; principles; outcome metrics with baseline, target and date, plus guardrails.
- The proposed solution: user journey and behaviour; then at least two real alternatives with why this one wins (cost, risk, fit with Agnes principles: on-prem parity, rollout switch, Postgres app-state, no comments in code, coupled surfaces).
- Every open choice becomes a **decision**, prepared like a brief for a decision meeting: Petr has not read the code and decides from the card alone. Per card, in order: **What it is about** (today's situation for a person, what changes, why it must be decided now; no file paths, config keys or internal names); **What it looks like**: one concrete example carried through every option (the same workflow written both ways side by side, a scenario walkthrough, or a situation table), never only option names; an **options table** with the rows Pros, Cons (effort, money, who is affected, risk), Change later (how hard to reverse, what breaks) and Who does this (competitors, with sources); then the **recommendation and the one reason that decides it**, and the template's decision card with a feedback form. Title the decision as a plain question ("Comments inside the text, or in a list beside it"), not a technical label. Before publishing, reread each card as Petr: if it needs another section to make sense, put that on the card. Worked example: the D1-D7 cards of the Agentic workflows proposal (artifact `zoEtD4Xg2_AeQCCJ_QvdzJ4g`, version 2).
- Delivery plan: phases with ambitious, realistic dates at AI-agent build speed (days, not months; a core phase is typically 3 days), never a phase that waits for decisions (Petr answers them in the review the same day), each phase says what works for users when done; owner = Petr unless he names someone; rollout switch (`purpose="rollout"`, default off - unless Petr decides otherwise), dependencies, risks, acceptance examples (given/when/then).
- Plain language: explain every number, unit and term on first use (what "180 s" measures, what a "turn" is); no slogans or abstract policy wording; principles get short names and are referred to by name, never "principle 2".
- Glossary for every new or redefined term (check `GLOSSARY.md`).

### 4. Second opinion (mandatory)
- Use the `second-opinion` skill: GPT Astra (`gpt-6-astra`, effort high) on the full draft, run from the Agnes repo root at fresh `origin/main` so it checks claims against the code.
- Incorporate or explicitly rebut every finding. The "Second opinion" section lists each finding and what was done.

### 5. Build the page
- Write the Markdown source from `assets/template.md` (both languages in every section, one marker per section).
- Run `python3 assets/check_proposal.py draft.md` until both languages report 0 findings.
- Build the HTML from `assets/template.html`: replace all sample content, keep the components and scripts; diagrams as inline SVG styled by design tokens (preferred over Mermaid for precise layout); position chart and comparison table filled with real data. No external hosts, no storage APIs.
- Self-review against the content system checklist: every Agnes claim has a path or link, every competitor claim a source, verified/inferred/unverified labels where needed, no filler, both languages say the same.

### 6. Publish
- New: `agnes artifact create --html page.html --markdown-source draft.md --title "<title>" --visibility instance --audience everyone --design-system ds_C-_CIyerl8dQ1ZzkXFE9zwrn@2 --content-system ef74c6ed49c241f490b6fb95ad65f84e@4 --summary "<1-2 sentences>" --keywords teag-<n>,<topic words>`.
- The page header shows a hardcoded version label (`vN` in the metadata line of `draft.md`): before every build set it to the version this publish will create (current head + 1), or the page shows a stale version.
- Update: `agnes artifact update <id> --base-version <head> --html ... --markdown-source ... --note "<what changed>" --summary ... --keywords ...` (summary and keywords every time).
- Settings: `agnes artifact settings <id> --form-responses` (comments stay visible to everyone; everyone with access may answer).
- Keywords are the public tags: always `teag-<n>` plus 2-5 topic words. Petr's private label: `agnes artifact tag <id> --add <topic>`.
- Link back: add the artifact URL to the Linear issue (`save_issue` with `links`).
- Open the published page in Claude in Chrome: no CSP errors, language toggle, TOC, decision form, dark mode, phone width.

### 7. Report to Petr
In Czech, outcome first: the link, version, who can open it, the decisions he is asked to make (one line each), what Astra changed, what is unverified. No code in chat.

## Rules
- Facts before claims: verify numbers, paths and competitor statements against the source; label anything not verified.
- No AI slop: no filler, hype or generic statements; numbers over adjectives; short sentences.
- Never publish secrets, customer-specific data or anything with visibility `public`.
- Do not edit `assets/` during a normal run; improvements to the template or systems are a separate, explicit change (republish the content or design system version and update the table above).
