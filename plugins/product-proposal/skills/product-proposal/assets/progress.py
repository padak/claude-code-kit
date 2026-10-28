"""Plan and progress for a product proposal, from one slice file.

The slice file (slices.json) is the single source of the plan: every slice has
a permanent id, an alias, a phase, a Czech and English title, an optional PR
number, a state, an optional delivery and a note. This script keeps it true
and renders it.

  refresh SLICES                 re-read every PR from GitHub (state, opened,
                                 merged, closed, review, auto-merge) and stamp
                                 the snapshot time; run before every publish.
                                 It never touches `delivery`.
  render SLICES --page P --md M  rewrite the generated regions in the page and
       --events E                the Markdown source: slice table, timeline,
       [--artifact ID]           log, and (Markdown only) the data region that
                                 holds slices.json and events.json. The log
                                 joins PR events, the artifact's version notes
                                 and the events file (E: a JSON list, may be
                                 empty). Both files are validated and rendered
                                 in memory first; neither is written unless
                                 both succeed.
  extract DRAFT.md --out DIR     recover slices.json and events.json from the
                                 draft's data region into DIR.

Generated regions are delimited by markers that stay in the files; each
required region occurs exactly once, opening marker before closing marker:
  <!-- gen:slices -->...<!-- /gen:slices -->       (page and Markdown)
  <!-- gen:timeline -->...<!-- /gen:timeline -->   (page only)
  <!-- gen:log -->...<!-- /gen:log -->             (page and Markdown)
  <!-- gen:data -->...<!-- /gen:data -->           (Markdown only)

slices.json:
  {"repo": "keboola/agnes-the-ai-analyst", "axis_start": "2026-10-26T20:00:00Z",
   "phases": {"1": ["Fáze 1", "Phase 1"], ...},
   "slices": [{"id": "W01", "alias": "T", "phase": "1", "cs": "...", "en": "...",
               "pr": 5672, "state": "merged", "delivery": "verified on dev",
               "note": ""}, ...]}
A slice without a PR keeps its state (planned, not started, postponed, dropped).
A PR closed without merging has state "closed" and a `closed` time. `delivery`
is free text set by hand (deployed to dev 27 Oct, verified on dev).
`axis_start` is optional; without it the timeline starts one hour before the
earliest opened PR.

events.json: a list of {"time", "type", "text", "link"?, "id"?, "resolved_by"?,
"count"?}. `resolved_by` is another event's id or a URL; `count` > 1 renders as
×N. An event whose type contains "failure" or "incident" (but not "fix") and has no
`resolved_by` is listed again under Open failures.

Every timestamp is ISO 8601 with an offset (2026-10-27T22:01:13Z or
+01:00); a naive or malformed value stops the script with the field named.
Times display as "%Y-%m-%d %H:%M %Z" in Europe/Prague.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Prague")
DISPLAY = "%Y-%m-%d %H:%M %Z"
STATE_LABEL = {"merged": "merged", "open": "PR open", "closed": "PR closed", "postponed": "postponed",
               "not started": "not started", "planned": "planned", "dropped": "dropped"}
PAGE_REGIONS = ("slices", "timeline", "log")
MD_REGIONS = ("slices", "log", "data")
DATA_HEADING = "Inputs of this page (slices.json, then events.json); recover them with `progress.py extract`."


class InputError(Exception):
    pass


def ts(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise InputError(f"{field}: expected an ISO 8601 timestamp with an offset, got {value!r}")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise InputError(f"{field}: malformed timestamp {value!r}") from None
    if t.tzinfo is None or t.utcoffset() is None:
        raise InputError(f"{field}: timestamp {value!r} has no offset; add Z or +HH:MM")
    return t


def opt_ts(obj: dict, key: str, field: str) -> datetime | None:
    return ts(obj[key], field) if obj.get(key) else None


def local(t: datetime, fmt: str = DISPLAY) -> str:
    return t.astimezone(TZ).strftime(fmt)


def gh_json(args: list[str]) -> dict | list:
    return json.loads(subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout)


def apply_pr(s: dict, pr: dict) -> None:
    sid = s.get("id", "?")
    for key in ("createdAt", "mergedAt", "closedAt"):
        if pr.get(key):
            ts(pr[key], f"gh pr {s['pr']}.{key}")
    state = {"MERGED": "merged", "OPEN": "open", "CLOSED": "closed"}.get(pr.get("state", ""))
    if state is None:
        raise InputError(f"slice {sid}: unknown PR state {pr.get('state')!r}")
    s["opened"] = pr.get("createdAt")
    s["merged"] = pr.get("mergedAt") if state == "merged" else None
    s["closed"] = pr.get("closedAt") if state == "closed" else None
    s["state"] = state
    s["gh"] = " ".join(x for x in (pr["state"], pr.get("reviewDecision") or "",
                                   "AUTO-MERGE ENABLED" if pr.get("autoMergeRequest") else "") if x)


def refresh_data(data: dict, fetch) -> dict:
    for s in data["slices"]:
        if s.get("pr"):
            apply_pr(s, fetch(s["pr"]))
    data["snapshot"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return data


def refresh(path: Path) -> None:
    data = json.loads(path.read_text())
    repo = data["repo"]
    fetch = lambda n: gh_json(["pr", "view", str(n), "--repo", repo, "--json",
                               "state,createdAt,mergedAt,closedAt,reviewDecision,autoMergeRequest,title"])
    refresh_data(data, fetch)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"refreshed {sum(1 for s in data['slices'] if s.get('pr'))} PRs, snapshot {data['snapshot']}")


def validate(data: dict, events: list) -> None:
    if not data.get("snapshot"):
        raise InputError("slices.snapshot missing; run refresh first")
    ts(data["snapshot"], "slices.snapshot")
    if data.get("axis_start"):
        ts(data["axis_start"], "slices.axis_start")
    for s in data["slices"]:
        for key in ("opened", "merged", "closed"):
            opt_ts(s, key, f"slices[{s.get('id', '?')}].{key}")
    if not isinstance(events, list):
        raise InputError("events: expected a JSON list")
    for i, e in enumerate(events):
        if not isinstance(e, dict) or not all(isinstance(e.get(k), str) for k in ("type", "text")):
            raise InputError(f"events[{i}]: needs string fields time, type and text")
        ts(e.get("time"), f"events[{i}].time")
        if "count" in e and (not isinstance(e["count"], int) or e["count"] < 1):
            raise InputError(f"events[{i}].count: expected a positive integer")


def safe_url(u: str | None) -> str | None:
    return u if u and re.match(r"https?://", u) else None


def md_cell(text: str) -> str:
    return re.sub(r"\s*[\r\n]+\s*", " ", text).replace("|", "\\|")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def pr_url(repo: str, n: int | None) -> str | None:
    return f"https://github.com/{repo}/pull/{n}" if n else None


def slice_rows(data: dict) -> tuple[str, list[str], list[list[tuple[str, str | None]]]]:
    snap = ts(data["snapshot"], "slices.snapshot")
    lead = f"Snapshot {local(snap)}, read from GitHub ({data['repo']})."
    head = ["ID", "Alias", "Phase", "What a user gets", "State", "Delivery", "PR", "PR opened", "PR merged", "Note"]
    rows = []
    for s in data["slices"]:
        sid = s["id"]
        state = s.get("gh") if s["state"] == "open" and s.get("gh") else STATE_LABEL.get(s["state"], s["state"])
        opened = opt_ts(s, "opened", f"slices[{sid}].opened")
        merged = opt_ts(s, "merged", f"slices[{sid}].merged")
        rows.append([(str(sid), None), (str(s.get("alias", "")), None), (str(s["phase"]), None), (str(s["en"]), None),
                     (str(state), None), (str(s.get("delivery") or "–"), None),
                     (str(s["pr"]) if s.get("pr") else "–", pr_url(data["repo"], s.get("pr"))),
                     (local(opened) if opened else "–", None), (local(merged) if merged else "–", None),
                     (str(s.get("note", "")), None)])
    return lead, head, rows


def slice_table_md(data: dict) -> str:
    lead, head, rows = slice_rows(data)

    def cell(c: tuple[str, str | None]) -> str:
        text, url = c
        return f"[{md_cell(text)}]({url})" if safe_url(url) else md_cell(text)

    out = [lead, "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def slice_table_html(data: dict) -> str:
    lead, head, rows = slice_rows(data)

    def cell(c: tuple[str, str | None]) -> str:
        text, url = c
        return f'<a href="{esc(url)}">{esc(text)}</a>' if safe_url(url) else esc(text)

    th = "".join(f"<th>{esc(h)}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<p>{esc(lead)}</p><div class="pp-table"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


TIMELINE_CSS = """<style>
.wf-tl{border:1px solid var(--ds-border);border-radius:var(--radius-md);padding:var(--space-sm);margin:var(--space-md) 0;background:var(--ds-surface);font-size:var(--size-small)}
.wf-tl__stamp{margin:0 0 var(--space-xs);color:var(--ds-muted)}
.wf-tl__axis,.wf-tl__row{display:grid;grid-template-columns:minmax(9rem,16rem) 1fr;gap:var(--space-xs);align-items:center}
.wf-tl__axis .wf-tl__track{height:1.4rem}
.wf-tl__track{position:relative;height:1.2rem;border-left:1px solid var(--ds-border)}
.wf-tl__body{position:relative}
.wf-tl__tick{position:absolute;top:0;transform:translateX(-50%);font-family:var(--ds-font-mono);color:var(--color-text-faint)}
.wf-tl__tick--day{color:var(--ds-text);font-weight:600}
.wf-tl__lab{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.wf-tl__id{font-family:var(--ds-font-mono);color:var(--ds-muted)}
.wf-tl__phase{font-weight:600;margin-top:var(--space-xs)}
.wf-tl__bar{position:absolute;top:.2rem;height:.8rem;border-radius:var(--radius-sm)}
.wf-tl__bar--done{background:var(--color-accent-default)}
.wf-tl__bar--open{background:var(--color-accent-soft);border:1px dashed var(--color-accent-default)}
.wf-tl__bar--closed{background:var(--color-text-faint);opacity:.45}
.wf-tl__bar--clipped{border-top-left-radius:0;border-bottom-left-radius:0}
.wf-tl__when{position:absolute;top:.05rem;font-family:var(--ds-font-mono);color:var(--ds-muted);white-space:nowrap}
.wf-tl__none{color:var(--color-text-faint);font-style:italic;padding-left:var(--space-xs)}
.wf-tl__nowlayer{position:absolute;top:0;bottom:0;left:calc(min(16rem,40%) + var(--space-xs));right:0;pointer-events:none}
.wf-tl__now{position:absolute;top:0;bottom:0;border-left:2px solid #b3261e}
.wf-tl__now span{position:absolute;top:-1.2rem;left:.2rem;color:#b3261e;font-family:var(--ds-font-mono);white-space:nowrap}
.wf-tl__scroll{overflow-x:auto}
.wf-tl__inner{min-width:44rem;position:relative;padding-top:1.2rem}
</style>"""


def axis_bounds(data: dict) -> tuple[datetime, datetime, datetime]:
    snap = ts(data["snapshot"], "slices.snapshot")
    if data.get("axis_start"):
        t0 = ts(data["axis_start"], "slices.axis_start")
    else:
        opened = [ts(s["opened"], f"slices[{s['id']}].opened") for s in data["slices"] if s.get("opened")]
        t0 = (min(opened) if opened else snap) - timedelta(hours=1)
    if t0 >= snap:
        raise InputError(f"slices.axis_start {local(t0)} is not before the snapshot {local(snap)}")
    return t0, snap + timedelta(hours=1), snap


def timeline_html(data: dict) -> str:
    t0, t1, snap = axis_bounds(data)
    span = (t1 - t0).total_seconds()

    def x(t: datetime) -> float:
        return max(0.0, min(100.0, (t - t0).total_seconds() / span * 100))

    step = max(1, round(span / 3600 / 16))
    ticks = []
    t = t0.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    if t < t0:
        t += timedelta(hours=1)
    while t <= t1:
        lt = t.astimezone(TZ)
        if lt.hour % step == 0:
            day = lt.hour == 0
            ticks.append('<span class="wf-tl__tick%s" style="left:%.2f%%">%s</span>' % (
                " wf-tl__tick--day" if day else "", x(t), lt.strftime("%d.%m.") if day else lt.strftime("%H")))
        t += timedelta(hours=1)
    rows, cur = [], None
    for s in data["slices"]:
        sid = str(s["id"])
        if s["phase"] != cur:
            cur = s["phase"]
            cs, en = data["phases"].get(cur, [cur, cur])
            rows.append(f'<div class="wf-tl__phase"><span lang="cs">{esc(str(cs))}</span><span lang="en">{esc(str(en))}</span></div>')
        label = '<span class="wf-tl__id">%s</span> <span lang="cs">%s</span><span lang="en">%s</span>' % (
            esc(sid), esc(str(s["cs"])), esc(str(s["en"])))
        if s.get("opened"):
            a = ts(s["opened"], f"slices[{sid}].opened")
            merged = opt_ts(s, "merged", f"slices[{sid}].merged")
            closed = opt_ts(s, "closed", f"slices[{sid}].closed")
            if s["state"] == "merged" and merged:
                cls, b, when = "done", merged, local(merged, "%H:%M")
            elif s["state"] == "closed":
                cls, b, when = "closed", closed or snap, "closed"
            else:
                cls, b, when = "open", snap, "open"
            clipped = a < t0
            title = f"{sid} {local(a)} → {local(b) if cls != 'open' else 'open'}"
            if clipped:
                title = "starts before the axis; " + title
                cls += " wf-tl__bar--clipped"
            bar = ('<span class="wf-tl__bar wf-tl__bar--%s" style="left:%.2f%%;width:%.2f%%" title="%s"></span>'
                   '<span class="wf-tl__when" style="left:%.2f%%">%s</span>') % (
                cls, x(a), max(0.6, x(b) - x(a)), esc(title), min(92.0, x(b) + 0.6), esc(when))
        else:
            bar = f'<span class="wf-tl__none">{esc(STATE_LABEL.get(s["state"], str(s["state"])))}</span>'
        rows.append(f'<div class="wf-tl__row"><div class="wf-tl__lab">{label}</div><div class="wf-tl__track">{bar}</div></div>')
    stamp = ('<p class="wf-tl__stamp"><span lang="cs">Generováno z tabulky slices, snímek %s. Pruh = PR otevřeno → sloučeno; '
             'čárkovaně otevřené PR; šedě PR zavřené bez sloučení.</span>'
             '<span lang="en">Generated from the slice table, snapshot %s. Bar = PR opened → merged; dashed = open PR; '
             'grey = PR closed unmerged.</span></p>') % (esc(local(snap)), esc(local(snap)))
    axis = '<div class="wf-tl__axis"><div></div><div class="wf-tl__track">%s</div></div>' % "".join(ticks)
    now = '<div class="wf-tl__nowlayer"><div class="wf-tl__now" style="left:%.2f%%"><span>%s</span></div></div>' % (
        x(snap), esc(local(snap, "%H:%M")))
    return (TIMELINE_CSS + '<div class="wf-tl">' + stamp + '<div class="wf-tl__scroll"><div class="wf-tl__inner">' + axis
            + '<div class="wf-tl__body">' + "".join(rows) + now + "</div></div></div></div>")


def log_events(data: dict, artifact: str | None, events: list) -> list[dict]:
    repo = data["repo"]
    ev: list[dict] = []
    for s in data["slices"]:
        if s.get("pr") and s.get("opened"):
            url = pr_url(repo, s["pr"])
            text = f"#{s['pr']} {s['id']} {s['en']}"
            ev.append({"t": ts(s["opened"], f"slices[{s['id']}].opened"), "type": "PR opened", "text": text, "link": url})
            if s.get("merged"):
                ev.append({"t": ts(s["merged"], f"slices[{s['id']}].merged"), "type": "merged", "text": text, "link": url})
            if s["state"] == "closed" and s.get("closed"):
                ev.append({"t": ts(s["closed"], f"slices[{s['id']}].closed"), "type": "PR closed", "text": text, "link": url})
    if artifact:
        out = subprocess.run(["agnes", "artifact", "versions", artifact, "--json"], check=True, capture_output=True, text=True).stdout
        for v in json.loads(out)["data"]:
            if v.get("note") and v.get("finalized_at"):
                ev.append({"t": ts(v["finalized_at"], f"artifact version v{v['number']}.finalized_at"),
                           "type": f"version v{v['number']}", "text": v["note"], "link": ""})
    for i, e in enumerate(events):
        ev.append({**e, "t": ts(e["time"], f"events[{i}].time")})
    ev.sort(key=lambda e: e["t"], reverse=True)
    return ev


def is_open_failure(e: dict) -> bool:
    kind = e["type"].lower()
    return ("failure" in kind or "incident" in kind) and "fix" not in kind and not e.get("resolved_by")


def log_line_md(e: dict) -> str:
    parts = [local(e["t"]), e["type"], md_cell(e["text"]) + (f" ×{e['count']}" if e.get("count", 1) > 1 else "")]
    if safe_url(e.get("link")):
        parts.append(f"[link]({e['link']})")
    if e.get("resolved_by"):
        r = e["resolved_by"]
        parts.append("→ fixed by " + (f"[{r}]({r})" if safe_url(r) else f"`{r}`"))
    if e.get("id"):
        parts.append(f"id `{e['id']}`")
    return "- " + " · ".join(parts)


def log_md(ev: list[dict]) -> str:
    if not ev:
        return "not recorded"
    out = []
    open_ = [e for e in ev if is_open_failure(e)]
    if open_:
        out += ["**Open failures**", ""] + [log_line_md(e) for e in open_] + ["", "**All entries**", ""]
    return "\n".join(out + [log_line_md(e) for e in ev])


def log_item_html(e: dict) -> str:
    s = "<li><code>%s</code> · <strong>%s</strong> · %s" % (esc(local(e["t"])), esc(e["type"]), esc(e["text"]))
    if e.get("count", 1) > 1:
        s += f" ×{e['count']}"
    if safe_url(e.get("link")):
        s += f' <a href="{esc(e["link"])}">link</a>'
    if e.get("resolved_by"):
        r = e["resolved_by"]
        s += " → fixed by " + (f'<a href="{esc(r)}">{esc(r)}</a>' if safe_url(r) else f"<code>{esc(r)}</code>")
    if e.get("id"):
        s += f" · id <code>{esc(e['id'])}</code>"
    return s + "</li>"


def log_html(ev: list[dict]) -> str:
    if not ev:
        return '<ul class="pp-log"><li>not recorded</li></ul>'
    out = ""
    open_ = [e for e in ev if is_open_failure(e)]
    if open_:
        out = ('<h4 class="pp-log__head">Open failures</h4><ul class="pp-log pp-log--open">'
               + "".join(log_item_html(e) for e in open_) + '</ul><h4 class="pp-log__head">All entries</h4>')
    return out + '<ul class="pp-log">' + "".join(log_item_html(e) for e in ev) + "</ul>"


def fenced_json(obj: object) -> str:
    body = json.dumps(obj, indent=1, ensure_ascii=False).replace("<", "\\u003c")
    longest = max((len(m) for m in re.findall(r"`+", body)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}json\n{body}\n{fence}"


def data_md(data: dict, events: list) -> str:
    return "\n\n".join([DATA_HEADING, fenced_json(data), fenced_json(events)])


def region_errors(text: str, names: tuple[str, ...], where: str) -> list[str]:
    errors = []
    for name in names:
        op, cl = f"<!-- gen:{name} -->", f"<!-- /gen:{name} -->"
        no, nc = text.count(op), text.count(cl)
        if no != 1 or nc != 1:
            errors.append(f"{where}: region gen:{name} needs exactly one {op} and one {cl}, found {no} and {nc}")
        elif text.index(op) > text.index(cl):
            errors.append(f"{where}: region gen:{name} closes before it opens")
    return errors


def inject(text: str, name: str, content: str) -> str:
    op, cl = f"<!-- gen:{name} -->", f"<!-- /gen:{name} -->"
    a = text.index(op) + len(op)
    b = text.index(cl)
    return text[:a] + "\n" + content + "\n" + text[b:]


def render_texts(data: dict, events: list, page_text: str, md_text: str, artifact: str | None) -> tuple[str, str, int]:
    errors = region_errors(page_text, PAGE_REGIONS, "page") + region_errors(md_text, MD_REGIONS, "markdown")
    if errors:
        raise InputError("; ".join(errors))
    validate(data, events)
    ev = log_events(data, artifact, events)
    p = inject(page_text, "slices", slice_table_html(data))
    p = inject(p, "timeline", timeline_html(data))
    p = inject(p, "log", log_html(ev))
    m = inject(md_text, "slices", slice_table_md(data))
    m = inject(m, "log", log_md(ev))
    m = inject(m, "data", data_md(data, events))
    return p, m, len(ev)


def write_together(pairs: list[tuple[Path, str]]) -> None:
    tmps = []
    try:
        for path, text in pairs:
            tmp = path.with_name(path.name + ".progress-tmp")
            tmp.write_text(text)
            tmps.append((tmp, path))
        for tmp, path in tmps:
            os.replace(tmp, path)
    finally:
        for tmp, _ in tmps:
            if tmp.exists():
                tmp.unlink()


def render(path: Path, page: Path, md: Path, artifact: str | None, events_path: Path) -> None:
    data = json.loads(path.read_text())
    events = json.loads(events_path.read_text())
    p, m, n = render_texts(data, events, page.read_text(), md.read_text(), artifact)
    write_together([(page, p), (md, m)])
    print(f"rendered {len(data['slices'])} slices, {n} log entries, snapshot {data['snapshot']}")


def extract_inputs(md_text: str) -> tuple[dict, list]:
    errors = region_errors(md_text, ("data",), "markdown")
    if errors:
        raise InputError(errors[0])
    region = md_text[md_text.index("<!-- gen:data -->"):md_text.index("<!-- /gen:data -->")]
    blocks = [b for _, b in re.findall(r"^(`{3,})json\n(.*?)\n\1[ \t]*$", region, re.S | re.M)]
    if len(blocks) != 2:
        raise InputError(f"markdown: region gen:data needs two json blocks, found {len(blocks)}")
    data, events = (json.loads(b) for b in blocks)
    if not isinstance(data, dict) or not isinstance(events, list):
        raise InputError("markdown: region gen:data holds slices (an object) then events (a list)")
    return data, events


def extract(md: Path, out: Path) -> None:
    data, events = extract_inputs(md.read_text())
    out.mkdir(parents=True, exist_ok=True)
    (out / "slices.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    (out / "events.json").write_text(json.dumps(events, indent=1, ensure_ascii=False) + "\n")
    print(f"extracted {len(data.get('slices', []))} slices and {len(events)} events to {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("refresh")
    r.add_argument("slices", type=Path)
    g = sub.add_parser("render")
    g.add_argument("slices", type=Path)
    g.add_argument("--page", type=Path, required=True)
    g.add_argument("--md", type=Path, required=True)
    g.add_argument("--events", type=Path, required=True)
    g.add_argument("--artifact")
    x = sub.add_parser("extract")
    x.add_argument("draft", type=Path)
    x.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    try:
        if a.cmd == "refresh":
            refresh(a.slices)
        elif a.cmd == "render":
            render(a.slices, a.page, a.md, a.artifact, a.events)
        else:
            extract(a.draft, a.out)
    except (InputError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
