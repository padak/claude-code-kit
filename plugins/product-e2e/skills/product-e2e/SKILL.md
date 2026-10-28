---
name: product-e2e
description: Use when Petr says "udělej mi E2E", "test plan", "testovací plán", "chci to otestovat", "převzetí", or when a feature built from a PRD (/product-proposal) reaches acceptance. Builds one hands-on E2E acceptance page as an Agnes Artifact on agnes.keboola.dev - header with PRD link and progress, what we test and what not, chapter 1 environment preparation, chapter 2 test cards (do this, correct when, watch out, OK / Bug / Unclear / Skipped + notes and pasted output), cleanup, results sent back as form responses that Claude reads with the agnes CLI - then writes the verdict into the PRD.
---

# Product E2E acceptance page

Petr accepts a feature by walking through one page "almost without thinking": every step is copyable, every expected result is visible on screen, nothing is forgotten, and his results come back to Claude as data. The PRD (`/product-proposal`) stays the single entry point; this page is its satellite for the acceptance run. Report to Petr in Czech; files on disk are English, the page text is Czech, commands and CLI output verbatim.

| What | Value |
|---|---|
| Page template | `assets/template.html` (data-driven: one JSON block, no external hosts) |
| Build | `python3 assets/build.py plan.json --html page.html --md page.md` (checks required fields, writes HTML + Markdown source) |
| Worked example | `assets/example-plan.json`, published as `geDVnnqJ5KjUojdkyR3JYpO4` v3 (TEAG-1023, artifacts as knowledge spaces) |
| Read results | `agnes artifact comments <id> --origin form`, full text `agnes artifact comments <id> --thread <comment-id>` |
| Environment | default https://agnes.keboola.dev (CLI `agnes`); production only when Petr says so |

## Inputs

1. **PRD:** `agnes artifact read <prd> --source --raw --all` and `agnes artifact knowledge <prd>`: phases in scope, acceptance examples, decisions, known defects (slice table), Linear id, keywords. A previous E2E artifact linked from the PRD: read it too and reuse its reviewed scenarios.
2. **Deployed build:** `agnes version` (server build) and the merged PRs it contains (`gh pr view`); a PR still OPEN is a known defect "until deployed", never a test that must pass.
3. **Switches:** `agnes admin config export --out cfg.yaml`, read only the switch lines you need (`grep -n <switch> cfg.yaml`), then `rm cfg.yaml` (the export can hold secrets).
4. **Real values:** concrete artifact ids, users, sizes and counts from the environment. Never "some artifact".

## The page (fixed structure, rendered by the template)

1. **Header:** feature name, PRD link, Linear id, environment + build, approver, plan version and date, time estimate, tester name field, sticky progress bar (done / total, OK / Bug / Unclear / Skipped, filter), the results-read command.
2. **What we test:** areas table (area, what it proves for a user, which tests), what we deliberately do not test (with why), known defects not to re-report (with the PR that fixes them and what to mark when the fix is visible), the pass rule with severities.
3. **Chapter 1, Environment preparation:** numbered steps with copyable commands and "what you will see"; CLI version (`agnes version`, `agnes self-upgrade`), sign-in (`agnes whoami`), switch proof, a work folder and shell variables, throwaway test objects created by exact commands, tokens kept only in a shell variable, agent/MCP setup (`claude mcp add-json --scope user agnes_server '{"type":"http","url":"https://agnes.keboola.dev/api/mcp/http","headersHelper":"agnes mcp headers"}'`), optional second account. Each step says how to undo anything risky.
4. **Chapter 2, Tests:** one card per test with ID (old ID as alias), area, priority, minutes, optional/security tags, "Do this" (numbered steps, copyable commands and prompts, concrete values), "Correct when" (observable, exact text where possible), "Watch out" (common confusions, what is not a bug), result buttons, note field, optional paste field, and a dry-run label. Story order: happy path first, then edge and failure cases (chains that depend on each other stay together and say so), access and security last, switch-off tests last of all.
5. **Chapter 3, Cleanup:** trash test objects (`agnes artifact trash <id>`, undo `agnes artifact restore <id>`), `unset` tokens, remove temporary MCP config if wanted, confirm switches are back.
6. **Results:** summary and bug list, **Send results** (`Agnes.respond` → stored as a form response on this artifact; splits into parts on `too_large`), **Download results** (.md) and copy-report fallback, a ready-to-paste message for Claude with the read command.

Persistence follows the reader sandbox (no `allow-same-origin`, so storage APIs throw): state lives in the URL fragment (`#s=` base64url JSON), written with `history.replaceState`; send and download are explicit. Do not add `localStorage`.

Language: Czech only, no EN toggle. The page is Petr's working checklist with form state; a bilingual copy doubles every card and the results stay comparable only in one language. The team-facing outcome is the verdict in the bilingual PRD.

## Steps

1. **Collect** the inputs above. Map PRD acceptance examples and risks to tests; every P1 risk gets a test, every gap is listed under "not tested".
2. **Write `plan.json`** (shape: `assets/example-plan.json`). Inline markup in strings: `` `code` ``, `**bold**`, `[text](https://...)`. A step is a string or `{"text", "cmd", "label"}`; `cmd` gets a copy button. Use shell variables set in preparation (`$A`, `$P`) so commands paste unchanged.
3. **Dry-run** every read-only command yourself against the environment exactly as written (zsh), and fix the plan from what really prints (exact text, counts, stderr lines). Never run destructive or write steps on real artifacts and never flip production switches; write steps run only on throwaway objects or are labelled. Every test has `dry`: `ano, Claude <date> ...` with the observed values, `částečně: ...` or `ne: <why>`.
4. **Build:** `python3 assets/build.py plan.json --html page.html --md page.md`. Render check without opening the artifact: headless Chrome `--dump-dom file://.../page.html` (and once with a `#s=` state) shows every card and the summary.
5. **Second opinion** on the plan for exactness of expected outputs (GPT Astra via `second-opinion`, from the product repo at fresh `origin/main`) when the scenarios are new; reused scenarios already reviewed need it only for what changed.
6. **Publish:** new `agnes artifact create --html page.html --markdown-source page.md --title "<title>" --visibility instance --audience everyone --summary "<1-2 sentences>" --keywords teag-<n>,acceptance,e2e`; update `agnes artifact update <id> --base-version <head> --require-head --html page.html --markdown-source page.md --note "<what changed>" --summary ... --keywords ...`. An existing content system (`agnes/e2e-test-plan@1`) may stay; if it blocks the publish, use `--no-content-system` and say so. Then `agnes artifact settings <id> --form-responses`; `agnes artifact link add` both ways with the PRD (check with `agnes artifact connections <id>`); the link in the PRD's Status links row.
7. **Report to Petr** (Czech, outcome first): link, version, time estimate, what he needs before starting (second account, MCP setup), what was dry-run and what not, the read command.
8. **After Petr's run:** `agnes artifact comments <id> --origin form` (latest non-withdrawn response per person is current), `--thread <id>` for full text. Classify every Bug/Unclear (real defect, plan error, known defect), fix plan errors in a new version, and write the verdict (who, when, build, reservations), the "What was verified" table and the findings into the PRD's Acceptance section via `/product-proposal` Update mode.

## Rules

- Every expected result is something Petr sees on screen; no "works correctly".
- Concrete values everywhere; numbers that drift (versions, counts) are given "as of <date>" and the test compares with its own first step.
- No secrets on the page; tokens only via `agnes mcp headers` into a shell variable, never printed.
- No stubs: a test that cannot be run on this environment is listed under "not tested" with the reason, not faked.
- One feature, one E2E artifact: a re-run or revised plan is a new version of the same artifact.
- Do not edit `assets/` during a normal run; template changes are a separate change to this skill.
