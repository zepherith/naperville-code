#!/usr/bin/env python3
"""Replace titles' chapter files with the text of Municode's Word download.

Municode's online code is born-digital, so its Word export avoids the OCR errors of
the scanned pages in the PDF. Download one or more titles as Word from library.municode.com
and run:

  tools/municode_word_import.py "TITLE 6 - ZONING REGULATIONS.docx" 2026-11-18

Needs pandoc. The script writes the title's chapter files (and any figures, into the
title's images/ folder) and adds the title to tools/word-titles.txt, so that later
runs of tools/municode_import.py leave those chapters alone. Re-run this script with
a fresh download to update the title.
"""
import collections
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from municode_import import ROOT, SOURCE, padded, slug, squash, title_case  # noqa: E402

WORD_TITLES = os.path.join(ROOT, "tools", "word-titles.txt")


def convert(docx, media):
    md = subprocess.run(
        ["pandoc", "-f", "docx", "-t", "gfm", "--wrap=none", f"--extract-media={media}", docx],
        capture_output=True, text=True, check=True).stdout
    return md.replace("\xa0", " ")


def tidy_tables(md):
    """Pandoc writes complex tables as HTML; turn their inline footnotes into plain notes."""
    def one(m):
        table = m.group(0)
        notes = []
        for a in re.finditer(r'<aside id="footnotes".*?</aside>', table, re.S):
            for li in re.finditer(r'<li id="fn(\d+)"><p>(.*?)<a href="#fnref\d+"[^>]*>.*?</a></p></li>', a.group(0), re.S):
                notes.append(f"<sup>{li.group(1)}</sup> {squash(li.group(2))}")
        table = re.sub(r'<aside id="footnotes".*?</aside>', "", table, flags=re.S)
        table = re.sub(r'<a href="#fn(\d+)"[^>]*><sup>\d+</sup></a>', r"<sup>\1</sup>", table)
        return table + ("\n\n" + "\\\n".join(notes) if notes else "")
    return re.sub(r"<table>.*?</table>", one, md, flags=re.S)


def split(md, title):
    """Chapters keyed by number, each a list of lines; plus the footnote definitions."""
    notes = dict(re.findall(r"(?m)^\[\^(\w+)\]:\s*(.*)$", md))
    md = re.sub(r"(?m)^\[\^\w+\]:.*$", "", md)
    chapters, cur = collections.OrderedDict(), None
    for line in md.split("\n"):
        # The name is usually bold ("## CHAPTER 1 **OFFICIAL MUNICIPAL CODE**"), but not always.
        m = re.match(r"^## CHAPTER (\d+(?:\.\d+)?)\s+(?:\*\*(.+?)\*\*|(.+?))((?:\[\^\w+\])*)\s*$", line)
        if m:
            cur = {"n": m.group(1), "name": squash(m.group(2) or m.group(3)), "extra": m.group(4).strip(), "lines": []}
            chapters[cur["n"]] = cur
            continue
        if cur is not None:
            cur["lines"].append(line)
    return chapters, notes


def render(title, ch, notes, images, retrieved):
    num = f"{title}-{ch['n']}"
    out = []
    for line in ch["lines"]:
        m = re.match(r"^# (\d+-[\w.]+-[\w.-]+):\s*(.*?):?\s*$", line)
        if m:
            line = f"### {m.group(1)}: {m.group(2).rstrip(':')}"
        elif re.match(r"^### ARTICLE ", line):
            line = "## " + line[4:].strip()
        elif re.match(r"^# ", line):
            line = "### " + line[2:]
        out.append(line)
    body = "\n".join(out)
    for old, new in images.items():
        body = body.replace(old, new)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    used = sorted(set(re.findall(r"\[\^(\w+)\]", ch["extra"] + body)), key=lambda x: int(x) if x.isdigit() else x)
    head = f"# {num} {ch['name']}" + (ch["extra"] and f"{ch['extra']}")
    foot = "\n\n" + "\n\n".join(f"[^{u}]: {notes[u]}" for u in used if u in notes) if used else ""
    return "\n".join([
        "---",
        f"citation: Naperville Municipal Code {num}",
        f"source: {SOURCE}",
        f"current_through: Municode online edition as downloaded {retrieved}",
        f"retrieved: {retrieved}",
        "---",
        "",
        head,
        "",
        body,
    ]) + foot + "\n"


def import_title(title, tname, md, notes, retrieved):
    folder = os.path.join(ROOT, f"Title-{title:02d}-{slug(tname)}")
    os.makedirs(folder, exist_ok=True)
    # Figures: name each one by the label Municode gave it (alt text), e.g. 6-2-33.png.
    images = {}
    imgdir = os.path.join(folder, "images")
    for m in re.finditer(r'<img src="([^"]+)"[^>]*alt="([^"]+)"', md):
        src, alt = m.group(1), m.group(2)
        name = re.sub(r"[^A-Za-z0-9.-]+", "-", alt)
        os.makedirs(imgdir, exist_ok=True)
        shutil.copyfile(src, os.path.join(imgdir, name))
        images[src] = f"images/{name}"
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", md):
        src = m.group(2)
        if src not in images:
            name = os.path.basename(src)
            os.makedirs(imgdir, exist_ok=True)
            shutil.copyfile(src, os.path.join(imgdir, name))
            images[src] = f"images/{name}"
    chapters, _ = split(md, title)
    written, skipped = 0, []
    for n, ch in chapters.items():
        if not any(re.match(r"^# \d", l) for l in ch["lines"]):
            skipped.append(f"{title}-{n}")
            continue
        path = os.path.join(folder, f"{title}-{padded(n)}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render(title, ch, notes, images, retrieved))
        written += 1
    print(f"Title {title} {tname}: {written} chapter files written, {len(images)} figures"
          + (f"; no sections in {', '.join(skipped)}" if skipped else ""))


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    docx, retrieved = argv
    done = []
    with tempfile.TemporaryDirectory() as tmp:
        md = tidy_tables(convert(docx, tmp))
        # Footnote numbers run through the whole download, so read them once.
        notes = dict(re.findall(r"(?m)^\[\^(\w+)\]:\s*(.*)$", md))
        # A download can hold one title or several, each opening with "# TITLE n  NAME".
        parts = re.split(r"(?m)^(?=# TITLE \d+\s)", md)
        for part in parts:
            tm = re.match(r"# TITLE (\d+)\s+(.+)$", part, re.M)
            if not tm:
                continue
            title, tname = int(tm.group(1)), title_case(squash(tm.group(2)))
            import_title(title, tname, part, notes, retrieved)
            done.append(title)
    titles = set()
    if os.path.exists(WORD_TITLES):
        titles = {int(x) for x in open(WORD_TITLES).read().split() if x.strip().isdigit()}
    titles.update(done)
    with open(WORD_TITLES, "w") as fh:
        fh.write("# Titles whose chapter files come from Municode's Word download (tools/municode_word_import.py).\n")
        fh.write("# tools/municode_import.py leaves these titles' chapter files alone.\n")
        fh.write("\n".join(str(t) for t in sorted(titles)) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
