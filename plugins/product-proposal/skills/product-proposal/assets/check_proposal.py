"""Check a bilingual proposal against the Product proposal content system.

Two parts:

1. Structure. The content-system checker refuses a repeated marker, so a
   bilingual draft is split into one draft per language (text between
   `<!-- lang:cs -->`, `<!-- lang:en -->` and `<!-- /lang -->`; headings
   `Czech · English` keep the matching half) and each is checked alone. The
   draft is building once it has `<!-- cs:handoff -->` or `<!-- cs:log -->`,
   or when `--variant building` is passed: Continue here, What it does today,
   Acceptance and Log become required. The earlier-version rule applies when
   the version this publish creates is above v1 (`--no-earlier-version`
   overrides it).

2. Freshness and links, checked locally:
   - the draft and page headers show the version this publish creates;
   - every PR mentioned ("PR 123", "PRs 123/124", "PR #123", or a number in a
     link text) has a real Markdown link to https://github.com/OWNER/REPO/pull/N;
   - every generated region present occurs exactly once, opened before it is
     closed; a building draft needs gen:slices, gen:log and gen:data, and its
     page gen:slices, gen:timeline and gen:log;
   - the status card's next check (`data-next-check`) is an offset-aware
     ISO 8601 time in the future; a building page must have one;
   - every decision card in the page has a row in the decision register.

Usage: python3 check_proposal.py DRAFT.md --page PAGE.html --version vN
                                 [--variant building] [--no-earlier-version] [--ref REF]
Exit code 0 only when both parts pass.
"""
import argparse
import pathlib
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from html.parser import HTMLParser

REF = "ef74c6ed49c241f490b6fb95ad65f84e@5"
LANGS = ("cs", "en")
LANG_RE = re.compile(r"^<!--\s*(?:lang:(cs|en)|/lang)\s*-->\s*$")
BUILDING_MARKERS = ("<!-- cs:handoff -->", "<!-- cs:log -->")
MD_REGIONS = ("slices", "log", "data")
PAGE_REGIONS = ("slices", "timeline", "log")
PR_LINK = re.compile(r"\[([^\]]*)\]\(<?https://github\.com/[\w.-]+/[\w.-]+/pull/(\d+)(?:[/?#][^)\s>]*)?>?(?:\s+\"[^\"]*\")?\)")
AUTOLINK = re.compile(r"<https://github\.com/[\w.-]+/[\w.-]+/pull/(\d+)(?:[/?#][^>\s]*)?>")
MD_LINK_TEXT = re.compile(r"\[([^\]]*)\]\([^)]*\)")
PR_MENTION = re.compile(r"\bPRs? #?(\d+(?:\s*(?:/|,|and|&)\s*#?\d+)*)")


def split(markdown: str, lang: str) -> str:
    out: list[str] = []
    current: str | None = None
    index = LANGS.index(lang)
    for line in markdown.splitlines():
        m = LANG_RE.match(line)
        if m:
            current = m.group(1)
            continue
        if current is not None and current != lang:
            continue
        if re.match(r"^#{1,6} ", line) and " · " in line:
            hashes, text = line.split(" ", 1)
            parts = text.split(" · ")
            line = f"{hashes} {parts[index] if index < len(parts) else parts[0]}"
        out.append(line)
    return "\n".join(out) + "\n"


def is_building(md: str, variant: str | None) -> bool:
    return variant == "building" or any(m in md for m in BUILDING_MARKERS)


def earlier_version(version: str) -> bool:
    m = re.fullmatch(r"v(\d+)", version)
    return bool(m) and int(m.group(1)) > 1


def region_findings(text: str, names: tuple[str, ...], where: str, required: bool) -> list[str]:
    found = []
    for name in names:
        op, cl = f"<!-- gen:{name} -->", f"<!-- /gen:{name} -->"
        no, nc = text.count(op), text.count(cl)
        if no == 0 and nc == 0:
            if required:
                found.append(f"{where} lacks the generated region gen:{name} (run progress.py render)")
        elif no != 1 or nc != 1:
            found.append(f"{where}: region gen:{name} needs exactly one {op} and one {cl}, found {no} and {nc}")
        elif text.index(op) > text.index(cl):
            found.append(f"{where}: region gen:{name} closes before it opens")
    return found


def parse_time(value: str) -> tuple[datetime | None, str | None]:
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None, "is not an ISO 8601 time"
    if t.tzinfo is None or t.utcoffset() is None:
        return None, "has no offset; add Z or +HH:MM"
    return t, None


def next_check_findings(page: str, building: bool) -> list[str]:
    found = []
    checks = re.findall(r"""data-next-check\s*=\s*(?:"([^"]*)"|'([^']*)')""", page)
    values = [a or b for a, b in checks]
    if building and not values:
        found.append("status card has no data-next-check")
    now = datetime.now(timezone.utc)
    for c in values:
        due, error = parse_time(c)
        if error:
            found.append(f"data-next-check {c!r} {error}")
        elif due <= now:
            found.append(f"next check {c} is already past; set a new one")
    return found


class _Cards(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.unnamed = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "article":
            return
        a = {k: v or "" for k, v in attrs}
        if "pp-decision" in a.get("class", "").split():
            if a.get("data-decision"):
                self.ids.append(a["data-decision"].strip())
            else:
                self.unnamed += 1


def decision_cards(page: str) -> tuple[list[str], int]:
    p = _Cards()
    p.feed(page)
    p.close()
    return p.ids, p.unnamed


def table_cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def register_rows(md: str) -> set[str] | None:
    if "<!-- cs:decisions -->" not in md:
        return None
    section = md.split("<!-- cs:decisions -->", 1)[1].split("<!-- cs:", 1)[0]
    rows: set[str] = set()
    table: list[str] = []
    for line in section.splitlines():
        if line.strip().startswith("|"):
            table.append(line)
        elif table:
            break
    for line in table[2:]:
        first = table_cells(line)[0] if table_cells(line) else ""
        if re.fullmatch(r"[A-Z][A-Z0-9-]*", first):
            rows.add(first)
    return rows


def pr_findings(md: str) -> list[str]:
    linked = {m.group(2) for m in PR_LINK.finditer(md)} | set(AUTOLINK.findall(md))
    mentioned: set[str] = set()
    for m in PR_MENTION.finditer(md):
        mentioned |= set(re.findall(r"\d+", m.group(1)))
    for m in MD_LINK_TEXT.finditer(md):
        mentioned |= set(re.findall(r"(?<![\w&])#(\d+)\b", m.group(1)))
    loose = sorted(mentioned - linked, key=int)
    return ["PR numbers without a real link to the PR: " + ", ".join(loose)] if loose else []


def local_findings(md: str, page: str, version: str, building: bool) -> list[str]:
    found: list[str] = []
    if not re.fullmatch(r"v\d+", version):
        found.append(f"--version {version!r} is not of the form vN")
    head = md.split("<!-- cs:", 1)[0]
    labels = set(re.findall(r"· (v\d+) ·", head))
    if labels != {version}:
        found.append(f"draft header shows {sorted(labels) or 'no version'}, this publish creates {version}")
    badges = set(re.findall(r"""<span\b[^>]*\bclass\s*=\s*["'][^"']*\bpp-badge\b[^"']*["'][^>]*>\s*(v\d+)\s*</span>""", page))
    badges |= set(re.findall(r"<dd>\s*(v\d+)\s*</dd>", page))
    if badges != {version}:
        found.append(f"page header shows {sorted(badges) or 'no version'}, this publish creates {version}")
    found += pr_findings(md)
    found += region_findings(md, MD_REGIONS, "draft", building)
    found += region_findings(page, PAGE_REGIONS, "page", building)
    found += next_check_findings(page, building)
    cards, unnamed = decision_cards(page)
    if unnamed:
        found.append(f"{unnamed} decision card(s) without data-decision")
    rows = register_rows(md)
    if cards and rows is None:
        found.append("page has decision cards but the draft has no <!-- cs:decisions --> register")
    elif cards:
        missing = sorted(c for c in cards if c not in rows and c.split("-")[-1] not in rows)
        if missing:
            found.append("decision cards without a register row: " + ", ".join(missing))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown", type=pathlib.Path)
    ap.add_argument("--page", type=pathlib.Path, required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--variant")
    ap.add_argument("--ref", default=REF)
    ap.add_argument("--no-earlier-version", action="store_true")
    args = ap.parse_args()
    source = args.markdown.read_text()
    page = args.page.read_text()
    building = is_building(source, args.variant)
    variant = "building" if building else args.variant
    earlier = earlier_version(args.version) and not args.no_earlier_version
    status = 0
    with tempfile.TemporaryDirectory() as tmp:
        for lang in LANGS:
            path = pathlib.Path(tmp) / f"{args.markdown.stem}.{lang}.md"
            path.write_text(split(source, lang))
            cmd = ["agnes", "content-system", "check", args.ref, "--markdown", str(path),
                   "--earlier-version" if earlier else "--no-earlier-version"]
            if variant:
                cmd += ["--variant", variant]
            print(f"== {lang} ==", flush=True)
            status |= subprocess.run(cmd).returncode
    print("== freshness and links ==")
    findings = local_findings(source, page, args.version, building)
    for f in findings:
        print(f"- {f}")
    if not findings:
        print("0 findings")
    return status | (1 if findings else 0)


if __name__ == "__main__":
    raise SystemExit(main())
