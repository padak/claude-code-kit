"""Build design-system.json (the `agnes design-system register|version` input).

Tokens, roles and guidance live here; component CSS is cut from template.html
between `/* @component <name> */` markers, so the template and the registered
bundle never drift apart. Run: python3 build_design_system.py
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent


def c(v):
    return {"$value": v}


TOKENS = {
    "color": {
        "$type": "color",
        "bg": {"page": c("#ffffff"), "surface": c("#f7f7f8"), "subtle": c("#efeff1")},
        "text": {"primary": c("#18181b"), "secondary": c("#55555f"), "faint": c("#8b8b95")},
        "border": {"default": c("#e2e2e6"), "strong": c("#c4c4cc")},
        "accent": {
            "default": {"$value": "#2f55d4", "$description": "The single accent colour: links, recommended option, changed parts, current phase."},
            "on": c("#ffffff"),
            "soft": c("#edf1fd"),
        },
        "status": {"ok": c("#1f7a4d"), "warn": c("#9a5b00"), "danger": c("#b42318")},
        "chart": {"1": c("#2f55d4"), "2": c("#3f3f46"), "3": c("#8b8b95"), "4": c("#9db1ee"), "5": c("#c4c4cc")},
    },
    "font": {
        "family": {
            "$type": "fontFamily",
            "body": c(["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"]),
            "heading": c(["Source Serif 4", "Georgia", "serif"]),
            "mono": c(["JetBrains Mono", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"]),
        },
        "weight": {"$type": "fontWeight", "regular": c(400), "medium": c(500), "semibold": c(600)},
    },
    "size": {
        "$type": "dimension",
        "small": c("0.8125rem"),
        "body": c("1rem"),
        "lead": c("1.1875rem"),
        "h3": c("1.1875rem"),
        "h2": c("1.625rem"),
        "h1": c("2.25rem"),
    },
    "line": {"$type": "number", "tight": c(1.25), "body": c(1.65)},
    "space": {"$type": "dimension", "xs": c("0.375rem"), "sm": c("0.75rem"), "md": c("1.25rem"), "lg": c("2.25rem"), "xl": c("3.5rem")},
    "radius": {"$type": "dimension", "sm": c("4px"), "md": c("6px"), "lg": c("10px")},
    "layout": {"$type": "dimension", "measure": c("42rem"), "wide": c("58rem"), "toc": c("14rem")},
}

DARK = {
    "color": {
        "bg": {"page": c("#121214"), "surface": c("#1a1a1e"), "subtle": c("#232328")},
        "text": {"primary": c("#ececef"), "secondary": c("#a8a8b3"), "faint": c("#76767f")},
        "border": {"default": c("#2c2c32"), "strong": c("#45454d")},
        "accent": {"default": c("#8eaaff"), "on": c("#0d1530"), "soft": c("#1b2340")},
        "status": {"ok": c("#5cc08f"), "warn": c("#e0a43c"), "danger": c("#f07a6e")},
        "chart": {"1": c("#8eaaff"), "2": c("#d4d4d8"), "3": c("#8b8b95"), "4": c("#4a5f9e"), "5": c("#45454d")},
    }
}
for group in DARK["color"].values():
    for tok in group.values():
        tok["$type"] = "color"

ROLES = {
    "background": "{color.bg.page}",
    "surface": "{color.bg.surface}",
    "text": "{color.text.primary}",
    "muted": "{color.text.secondary}",
    "border": "{color.border.default}",
    "accent": "{color.accent.default}",
    "on_accent": "{color.accent.on}",
    "font_body": "{font.family.body}",
    "font_heading": "{font.family.heading}",
    "font_mono": "{font.family.mono}",
    "radius": "{radius.lg}",
    "chart_palette": [f"{{color.chart.{i}}}" for i in range(1, 6)],
}

GUIDANCE = """# Product proposal

A restrained look for product proposals that a product owner reads closely,
comments on and decides from. The page must stay calm with 17 sections, two
languages and several decision forms on it.

## Principles

1. **Neutral first, one accent.** Greys carry the page. The accent
   (`--color-accent-default`) marks only what asks for attention: links, the
   recommended option, what changes in a diagram, the current phase, the
   active table-of-contents entry. Never use it as decoration or as a large
   fill; `--color-accent-soft` is the only tint.
2. **Status colours are semantic only.** `--color-status-ok|warn|danger` for
   approved, concept/unverified and rejected/risk. Never rely on colour
   alone: every mark has a word or a shape (filled, half, empty circle).
3. **Reading width.** Prose stops at `--layout-measure` (42rem, about 75
   characters of Inter at 16px). Tables, figures and diagrams may use
   `--layout-wide` (58rem). The table of contents is `--layout-toc` wide.

## Typography

- **Inter** for the body and every piece of UI (top bar, badges, table of
  contents, tables, forms): it is the most legible bundled sans at small
  sizes and has tabular figures for numbers.
- **Source Serif 4** only for the document title (`--size-h1`) and section
  headings (`--size-h2`). A proposal has 17 sections; a serif heading marks
  each break without heavy weight or colour, and tells the reader this is a
  document to read, not an app screen. Sub-headings (h3, h4) stay in Inter
  semibold. For an all-sans variant, point `font_heading` at the body
  family; nothing else changes.
- **JetBrains Mono** for code, repo paths, IDs (TEAG-123, D1) and section
  numbers.
- Body 1rem / 1.65; lead 1.1875rem. Do not shrink text to fit more.

## Layout

Sticky top bar (title, Linear badge, status, version, CZ/EN toggle at the
right), then a two-column grid: a sticky table of contents on the left and
the document on the right. At 960px and below the grid becomes one column
and the table of contents folds into a collapsible box above the text.
Sections are separated by a hairline rule and `--space-lg`.

## Bilingual pages

Both languages are in the page. Every piece of text exists twice, as
sibling elements with `lang="cs"` and `lang="en"`; the root element's
`data-lang` hides the other language. Czech is the default; the choice is
kept only in the URL hash (`#cs`, `#en`) because the artifact sandbox has
no storage.

## Components

Use the components below; build nothing that duplicates them. Every figure
has a caption whose first sentence is the takeaway (bold) and a text
equivalent (notes list, table or hidden list). Generated images and
mockups always use the concept variant with the "Concept" badge.

## Dark mode and print

Every colour is a token with a dark value; never hard-code one. Print hides
the top bar, table of contents and forms, opens collapsed blocks and prints
source URLs.
"""

COMPONENT_META = {
    "base": ("Reset, body type, language switching, evidence chips.", "Always; it carries the bilingual hiding rule."),
    "topbar": ("Sticky bar: short title, Linear badge, status, version, CZ/EN toggle.", "Once, first element of the body."),
    "badge": ("Pills: Linear ID, status (draft, review, approved, rejected), version, Concept; evidence chips verified/inferred/unverified.", "Top bar, figure captions, next to a claim."),
    "layout": ("Two-column grid: table of contents and document; one column at 960px.", "Once, wraps the table of contents and main."),
    "header": ("Kicker, title, lead (max three sentences) and facts row (owner, decider, updated, evidence as of).", "Top of the document."),
    "toc": ("Sticky table of contents built from the sections; collapsible on a phone.", "Once, in the layout's first column."),
    "section": ("Numbered section with a serif heading and a callout box.", "One per content-system section; id = the cs marker id."),
    "table": ("Bordered, scrollable table; Agnes columns highlighted; yes/partial/no marks; yes/no pills for a surfaces matrix.", "Comparisons, metrics, alternatives, surfaces matrix, Astra findings."),
    "position-chart": ("SVG position chart drawn from inline JSON: competitors and Agnes now / after each phase, with a path.", "Research section, under the comparison table."),
    "figure": ("Annotated screenshot: image (data: URI) with an SVG overlay of numbered pins and rings, caption and notes; dashed concept variant with a badge.", "Current state (real screenshots) and proposal (concepts)."),
    "c4-diagram": ("C4-style SVG: boundary, boxes (changed, new, unchanged, external), arrows, legend.", "Architecture impact."),
    "decision-card": ("Question, option cards with the recommended one highlighted, reasoning, and a choice + comment form sent with Agnes.respond.", "Decisions section, one card per decision."),
    "timeline": ("Phase timeline: dates, name, exit criterion; current phase in the accent.", "Delivery plan."),
    "acceptance": ("Given / when / then cards.", "Delivery plan, acceptance examples."),
    "glossary": ("Two-column definition list.", "Glossary."),
    "sources": ("Numbered sources with anchors; superscript citation links.", "Sources section; cite with <a class=\"pp-cite\" href=\"#src-N\">[N]</a>."),
    "appendix": ("Collapsible blocks for technical detail.", "Appendix."),
    "print": ("Print rules.", "Always."),
}

COMPONENT_HTML = {
    "base": '<span class="pp-ev pp-ev--verified">verified</span> <span class="pp-ev pp-ev--inferred">inferred</span> <span class="pp-ev pp-ev--unverified">unverified</span>',
    "topbar": '<header class="pp-topbar"><div class="pp-topbar__inner"><div class="pp-topbar__title"><span lang="cs">Název</span><span lang="en">Title</span></div><div class="pp-topbar__meta"><a class="pp-badge pp-badge--linear" href="https://linear.app/keboola/issue/TEAG-123">TEAG-123</a><span class="pp-badge pp-status" data-status="review"><span lang="cs">Ke kontrole</span><span lang="en">In review</span></span><span class="pp-badge">v1</span></div><div class="pp-lang" role="group" aria-label="Jazyk / Language"><button type="button" data-set-lang="cs" aria-pressed="true">CZ</button><button type="button" data-set-lang="en" aria-pressed="false">EN</button></div></div></header>',
    "badge": '<span class="pp-badge pp-status" data-status="approved">Approved</span> <span class="pp-badge pp-badge--concept">Concept</span>',
    "layout": '<div class="pp-layout"><nav class="pp-toc">...</nav><main class="pp-main">...</main></div>',
    "header": '<header class="pp-header"><p class="pp-kicker">Product proposal</p><h1>Title</h1><p class="pp-lead">Lead.</p><dl class="pp-facts"><div><dt>Owner</dt><dd>Name</dd></div></dl></header>',
    "toc": '<nav class="pp-toc" aria-label="Obsah / Contents"><details open><summary><span lang="cs">Obsah</span><span lang="en">Contents</span></summary><ol data-toc></ol></details></nav>',
    "section": '<section class="pp-section" id="problem" data-cs="problem"><h2><span class="pp-section__num">02</span><span lang="cs">Problém</span><span lang="en">The problem</span></h2><p lang="cs">Text.</p><p lang="en">Text.</p></section>',
    "table": '<div class="pp-table"><table><thead><tr><th>Capability</th><th>Competitor A</th><th class="pp-col-agnes">Agnes now</th><th class="pp-col-agnes">After phase 1</th></tr></thead><tbody><tr><td>Save a set</td><td><span class="pp-mark pp-mark--yes">Yes</span></td><td class="pp-col-agnes"><span class="pp-mark pp-mark--no">No</span></td><td class="pp-col-agnes"><span class="pp-mark pp-mark--partial">Partly</span></td></tr></tbody></table></div>',
    "position-chart": '<figure class="pp-figure pp-position" data-position><script-json>{"x":{"cs":"Osa X","en":"X axis"},"y":{"cs":"Osa Y","en":"Y axis"},"points":[{"cs":"A","en":"A","x":0.3,"y":0.6},{"cs":"Agnes dnes","en":"Agnes now","x":0.5,"y":0.2,"agnes":"now"},{"cs":"Po fázi 1","en":"After phase 1","x":0.7,"y":0.7,"agnes":"phase"}]}</script-json><svg role="img" aria-labelledby="pos-cap"></svg><figcaption id="pos-cap">Takeaway.</figcaption></figure>',
    "figure": '<figure class="pp-figure pp-shot pp-shot--concept"><div class="pp-shot__frame"><span class="pp-badge pp-badge--concept">Concept</span><img src="data:image/png;base64,..." width="1200" height="720" alt="..."><svg class="pp-shot__overlay" viewBox="0 0 1200 720" aria-hidden="true"><rect class="pp-shot__ring" x="100" y="100" width="300" height="80" rx="10"/><g class="pp-shot__pin" transform="translate(100 100)"><circle r="18"/><text>1</text></g></svg></div><figcaption><strong>Takeaway.</strong><ol class="pp-shot__notes"><li>Note for pin 1.</li></ol></figcaption></figure>',
    "c4-diagram": '<figure class="pp-figure pp-c4"><svg viewBox="0 0 760 330" role="img"><rect class="c4-boundary" x="10" y="10" width="560" height="310" rx="10"/><rect class="c4-box c4-box--changed" x="30" y="56" width="220" height="86" rx="8"/><text class="c4-title" x="46" y="82">API</text><text class="c4-tech" x="46" y="100">FastAPI</text><path class="c4-edge c4-edge--changed" d="M250 99H322"/></svg><ul class="pp-legend"><li><i class="changed"></i>Changes</li><li><i class="new"></i>New</li><li><i></i>Unchanged</li><li><i class="external"></i>External</li></ul></figure>',
    "decision-card": '<article class="pp-decision" id="d1"><div class="pp-decision__head"><span class="pp-decision__id">D1</span><h3>Question?</h3></div><div class="pp-options"><div class="pp-option" data-option="A"><h4><span class="pp-option__key">A</span>Option</h4><p>Cost.</p></div><div class="pp-option pp-option--recommended" data-option="B"><span class="pp-option__flag">Recommended</span><h4><span class="pp-option__key">B</span>Option</h4><p>Cost.</p></div></div><p class="pp-reason"><strong>Why B:</strong> reason.</p><form class="pp-form" data-decision="D1" novalidate><fieldset><legend>Your choice</legend><div class="pp-form__choices"><label><input type="radio" name="choice" value="A"> A</label><label><input type="radio" name="choice" value="B"> B</label></div></fieldset><label class="pp-form__comment">Comment<textarea name="comment" rows="3"></textarea></label><button class="pp-button" type="submit">Send answer</button><p class="pp-form__note" role="status" hidden></p></form></article>',
    "timeline": '<ol class="pp-timeline"><li class="pp-phase pp-phase--current"><span class="pp-phase__when">2026-11 → 2026-12</span><h4>Phase 1</h4><p><strong>Done when:</strong> criterion.</p></li><li class="pp-phase"><span class="pp-phase__when">2027-01</span><h4>Phase 2</h4><p>...</p></li></ol>',
    "acceptance": '<div class="pp-gwt"><div class="pp-gwt__case"><h4>Case</h4><dl><dt>Given</dt><dd>state</dd><dt>When</dt><dd>action</dd><dt>Then</dt><dd>observable result</dd></dl></div></div>',
    "glossary": '<dl class="pp-glossary"><dt>Term</dt><dd>Definition.</dd></dl>',
    "sources": '<ol class="pp-sources"><li id="src-1">Title, date. <a href="https://example.com">example.com</a></li></ol>',
    "appendix": '<details class="pp-appendix"><summary>Data model</summary><div><pre>...</pre></div></details>',
    "print": '<!-- print rules apply to the whole page -->',
}


def main():
    html = (HERE / "template.html").read_text()
    style = re.search(r"<style>\n(.*?)</style>", html, re.S).group(1)
    parts = re.split(r"/\* @component ([a-z0-9-]+) \*/\n", style)
    css = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
    missing = set(COMPONENT_META) ^ set(css)
    if missing:
        raise SystemExit(f"component mismatch between template and builder: {sorted(missing)}")
    components = []
    for name, (description, when) in COMPONENT_META.items():
        components.append({
            "name": f"pp-{name}",
            "description": description,
            "when_to_use": when,
            "html": COMPONENT_HTML[name].replace("<script-json>", "<template data-json>").replace("</script-json>", "</template>"),
            "css": css[name],
        })
    out = {
        "slug": "product-proposal",
        "name": "Product proposal",
        "description": "Restrained neutral look for bilingual product proposals: Inter UI and body, Source Serif 4 headings, one blue accent, sticky table of contents, decision cards with feedback forms. Light and dark.",
        "bundle": {
            "tokens": TOKENS,
            "modes": {"dark": DARK},
            "roles": ROLES,
            "guidance": GUIDANCE,
            "components": components,
            "charts": {"library": "inline-svg", "notes": "Hand-drawn SVG styled by tokens: position chart, C4 diagram, annotated screenshots. Takeaway caption and a text equivalent for each."},
            "diagrams": {"library": "none", "notes": "C4-style inline SVG with the c4-* classes; no Mermaid, so it styles with the tokens in both modes."},
            "fonts": [{"href": "/_static/fonts/fonts.css"}],
        },
    }
    (HERE / "design-system.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("components:", len(components), "bytes:", len(json.dumps(out)))


if __name__ == "__main__":
    main()
