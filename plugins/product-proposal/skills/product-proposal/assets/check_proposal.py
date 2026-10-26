"""Check a bilingual proposal Markdown against the Product proposal content system.

The content-system checker counts every word under a section and refuses a
repeated marker, so a bilingual draft is split into one draft per language
(text between `<!-- lang:cs -->`, `<!-- lang:en -->` and `<!-- /lang -->`;
headings `Czech · English` keep the matching half) and each is checked alone.

Usage: python3 check_proposal.py PROPOSAL.md [--ref REF] [--earlier-version]
"""
import argparse
import pathlib
import re
import subprocess
import tempfile

REF = "ef74c6ed49c241f490b6fb95ad65f84e@4"
LANGS = ("cs", "en")
LANG_RE = re.compile(r"^<!--\s*(?:lang:(cs|en)|/lang)\s*-->\s*$")


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown", type=pathlib.Path)
    ap.add_argument("--ref", default=REF)
    ap.add_argument("--earlier-version", action="store_true")
    args = ap.parse_args()
    source = args.markdown.read_text()
    status = 0
    with tempfile.TemporaryDirectory() as tmp:
        for lang in LANGS:
            path = pathlib.Path(tmp) / f"{args.markdown.stem}.{lang}.md"
            path.write_text(split(source, lang))
            cmd = ["agnes", "content-system", "check", args.ref, "--markdown", str(path),
                   "--earlier-version" if args.earlier_version else "--no-earlier-version"]
            print(f"== {lang} ==", flush=True)
            status |= subprocess.run(cmd).returncode
    return status


if __name__ == "__main__":
    raise SystemExit(main())
