#!/usr/bin/env python3
"""Build an E2E test plan page and its Markdown source from one plan JSON.

Usage: python3 build.py plan.json --html page.html --md page.md

The HTML is template.html with the plan injected; the Markdown is the same
plan as plain text, published as --markdown-source so agents can read it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIRED_META = ["feature", "prd_id", "prd_url", "env_url", "approver", "plan_version", "artifact_id", "results_cmd"]
REQUIRED_ITEM = {"prep": ["id", "title", "do", "see"], "tests": ["id", "title", "area", "prio", "do", "see"], "cleanup": ["id", "title", "do"]}


def check(plan):
    errors = []
    for k in REQUIRED_META:
        if not plan.get("meta", {}).get(k):
            errors.append(f"meta.{k} missing")
    seen = set()
    for group, keys in REQUIRED_ITEM.items():
        for it in plan.get(group, []):
            for k in keys:
                if not it.get(k):
                    errors.append(f"{group} {it.get('id', '?')}: {k} missing")
            if it.get("id") in seen:
                errors.append(f"duplicate id {it['id']}")
            seen.add(it.get("id"))
            if group == "tests" and not it.get("dry"):
                errors.append(f"tests {it.get('id')}: dry (dry-run label) missing")
            text = json.dumps(it, ensure_ascii=False)
            if re.search(r"\b(some|nějak[ýéá]|libovoln[ýéá]) (artifact|artefakt)", text, re.I):
                errors.append(f"{group} {it.get('id')}: vague value, name the exact artifact")
    if not plan.get("tests"):
        errors.append("no tests")
    return errors


def steps_md(steps, ordered=True):
    out = []
    for i, s in enumerate(steps or [], 1):
        bullet = f"{i}." if ordered else "-"
        if isinstance(s, str):
            out.append(f"{bullet} {s}")
        else:
            out.append(f"{bullet} {s.get('text', s.get('label', ''))}".rstrip())
            if s.get("cmd"):
                out.append("")
                out.append("   ```")
                out.extend("   " + line for line in s["cmd"].splitlines())
                out.append("   ```")
    return out


def item_md(it, test):
    head = f"### {it['id']} {it['title']}"
    tags = [x for x in [it.get("alias") and f"dříve {it['alias']}", it.get("area"), it.get("prio"), it.get("optional") and "volitelné", it.get("min") and f"~{it['min']} min"] if x]
    out = [head, ""]
    if tags:
        out += [" · ".join(tags), ""]
    if it.get("why"):
        out += [it["why"], ""]
    for key, label, ordered in [("do", "Udělej", True), ("see", "Správně, když" if test else "Uvidíš", False), ("watch", "Pozor", False), ("undo", "Vrácení", False)]:
        if it.get(key):
            out += [f"**{label}:**", ""] + steps_md(it[key], ordered) + [""]
    if it.get("dry"):
        out += [f"Nanečisto: {it['dry']}", ""]
    return out


def to_markdown(plan):
    m = plan["meta"]
    out = [f"# {plan['title']}", "", plan.get("lead", ""), "",
           f"- Feature: {m['feature']} {m.get('linear_id', '')} {m.get('linear_url', '')}".rstrip(),
           f"- PRD: {m.get('prd_title', m['prd_id'])} ({m['prd_url']})",
           f"- Prostředí: {m['env_url']}" + (f", build {m['build']}" if m.get("build") else ""),
           f"- Schvaluje: {m['approver']}", f"- Plán: {m['plan_version']}, napsáno {m.get('written', '')}",
           f"- Výsledky: `{m['results_cmd']}`", "", "## Co testujeme", "",
           "| Oblast | Co to dokazuje | Testy |", "|---|---|---|"]
    out += [f"| {a['area']} | {a['proves']} | {a['tests']} |" for a in plan.get("areas", [])]
    out += ["", "Záměrně netestujeme:", ""] + [f"- {x}" for x in plan.get("not_tested", [])]
    out += ["", "Známé vady, nehlásit znovu:", ""] + [f"- {x}" for x in plan.get("known", [])]
    out += ["", f"Kdy test projde: {plan.get('pass_rule', '')}", "", "## 1. Příprava prostředí", ""]
    for it in plan.get("prep", []):
        out += item_md(it, False)
    out += ["## 2. Testy", "", plan.get("tests_intro", ""), ""]
    for it in plan.get("tests", []):
        out += item_md(it, True)
    out += ["## 3. Úklid", ""]
    for it in plan.get("cleanup", []):
        out += item_md(it, False)
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--html", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    errors = check(plan)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    data = json.dumps(plan, ensure_ascii=False).replace("</", "<\\/")
    title = plan["title"].replace("&", "&amp;").replace("<", "&lt;")
    page = (HERE / "template.html").read_text(encoding="utf-8").replace("__TITLE__", title).replace("__PLAN_JSON__", data)
    Path(a.html).write_text(page, encoding="utf-8")
    Path(a.md).write_text(to_markdown(plan), encoding="utf-8")
    print(f"ok: {len(plan.get('prep', []))} prep, {len(plan['tests'])} tests, {len(plan.get('cleanup', []))} cleanup; {len(page)} bytes")


if __name__ == "__main__":
    main()
