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

If the download includes Municode's Supplement History Table, Code Comparative Table or
the ordinance that adopted the code, they are written to Tables/, and the latest supplement in the history table is saved to
tools/word-edition.txt and named in each file's current_through.
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
WORD_EDITION = os.path.join(ROOT, "tools", "word-edition.txt")
TABLES = os.path.join(ROOT, "Tables")
EDITION = ""  # e.g. "Supplement No. 101 (Ord. 26-049)", read from the Supplement History Table


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
        f"current_through: {EDITION + ', ' if EDITION else ''}Municode online edition as downloaded {retrieved}",
        f"retrieved: {retrieved}",
        "---",
        "",
        head,
        "",
        body,
    ]) + foot + "\n"


ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def roman(s):
    total = 0
    for i, c in enumerate(s):
        v = ROMAN[c]
        total += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return total


def split_schedules(ch):
    """Take the traffic schedules of 11-1-5 out of Chapter 11-1, one list of lines per schedule.

    The schedules run from the first "SCHEDULE I/..." line to the heading of 11-1-6. Part
    headings ("# Sch. IA: ...", "# Sch. VIIC-1: ...") belong to the schedule of their numeral.
    Their place in the chapter takes a list of links to the schedule files.
    """
    lines = ch["lines"]
    start = next((i for i, l in enumerate(lines) if re.match(r"^SCHEDULE I\s*/", l)), None)
    end = next((i for i, l in enumerate(lines) if re.match(r"^# 11-1-6:", l)), None)
    if start is None or end is None:
        return collections.OrderedDict(), {}
    names = {}
    for l in lines[:start]:
        m = re.match(r"^\|\s*(\S.*?)\s*\|\s*Schedule ([IVXL]+)\s*\|", l)
        if m:
            names[m.group(2)] = m.group(1)
    schedules, cur = collections.OrderedDict(), None
    for l in lines[start:end]:
        m = (re.match(r"^SCHEDULE ([IVXL]+)\s*/", l)
             or re.match(r"^# Sch\. ([IVXL]+?)(?:[A-H](?:-\d+)?)?:", l))
        if m and m.group(1) != cur:
            cur = m.group(1)
            schedules[cur] = []
        if re.match(r"^SCHEDULE [IVXL]+\s*/", l):
            continue  # the schedule's own title line; the file's heading says it
        schedules[cur].append(l)
    links = ["**Traffic schedules (Section 11-1-5).** Each schedule is kept in its own file:", ""]
    links += [f"- [Schedule {r}: {names.get(r, '')}](11-01-Schedules/Sch-{roman(r):02d}.md)".replace(": ]", "]")
              for r in schedules]
    ch["lines"] = lines[:start] + links + [""] + lines[end:]
    return schedules, names


def render_schedule(r, name, lines, notes, images, retrieved):
    ch = {"n": "1", "name": "", "extra": "", "lines": lines}
    text = render(11, ch, notes, images, retrieved)
    label = f"Schedule {r}" + (f": {name}" if name else "")
    text = text.replace("citation: Naperville Municipal Code 11-1\n", f"citation: Naperville Municipal Code 11-1-5, Schedule {r}\n", 1)
    return text.replace("\n# 11-1 \n", f"\n# 11-1-5 {label}\n", 1)


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
    if title == 11 and "1" in chapters:
        schedules, names = split_schedules(chapters["1"])
        sdir = os.path.join(folder, "11-01-Schedules")
        if schedules:
            os.makedirs(sdir, exist_ok=True)
            for old in glob.glob(os.path.join(sdir, "Sch-*.md")):
                os.remove(old)
        for r, ls in schedules.items():
            with open(os.path.join(sdir, f"Sch-{roman(r):02d}.md"), "w", encoding="utf-8") as fh:
                fh.write(render_schedule(r, names.get(r), ls, notes, images, retrieved))
        print(f"Title 11: {len(schedules)} traffic schedule files")
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


def table_rows(html):
    """The cells of each row of the HTML tables in html, as plain text."""
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = [squash(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        rows.append([re.sub(r"(\d+)-\s+(\d+)-", r"\1-\2-", c).replace("|", "\\|") for c in cells])
    return rows


def write_table(name, title, md, retrieved):
    """Write one of Municode's back-matter tables as a Markdown table in Tables/."""
    intro = [squash(p) for p in re.split(r"\n\s*\n", md.split("<table", 1)[0]) if p.strip() and not p.startswith("#")]
    rows = [r for r in table_rows(md) if any(r)]
    head, body = rows[0], rows[1:]
    out = ["---", f"citation: Naperville Municipal Code, {title}", f"source: {SOURCE}",
           f"current_through: {EDITION + ', ' if EDITION else ''}Municode online edition as downloaded {retrieved}",
           f"retrieved: {retrieved}", "---", "", f"# {title}", ""]
    out += [p + "\n" for p in intro]
    out += ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)]
    out += ["| " + " | ".join(r + [""] * (len(head) - len(r))) + " |" for r in body]
    os.makedirs(TABLES, exist_ok=True)
    with open(os.path.join(TABLES, name), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"{title}: {len(body)} rows")
    return body


def write_ordinance(num, md, retrieved):
    """Write the ordinance that adopted the code (Ord. No. 85-10) to Tables/."""
    body = re.sub(r"\n{3,}", "\n\n", md).strip()
    out = ["---", f"citation: Naperville Ord. No. {num}", f"source: {SOURCE}",
           f"current_through: {EDITION + ', ' if EDITION else ''}Municode online edition as downloaded {retrieved}",
           f"retrieved: {retrieved}", "---", "", f"# Ordinance No. {num}", "", body]
    os.makedirs(TABLES, exist_ok=True)
    with open(os.path.join(TABLES, f"Adopting-Ordinance-{num}.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"Ordinance No. {num} written to Tables/")


def main(argv):
    global EDITION
    if len(argv) != 2:
        sys.exit(__doc__)
    docx, retrieved = argv
    done = []
    with tempfile.TemporaryDirectory() as tmp:
        md = tidy_tables(convert(docx, tmp))
        if os.path.exists(WORD_EDITION):
            EDITION = open(WORD_EDITION).read().strip()
        # A download may open with Municode's Supplement History Table. Its latest supplement
        # dates the online text, and the table is kept in Tables/.
        hist = re.search(r"(?ms)^#\s+SUPPLEMENT HISTORY TABLE\s*$(.*?)(?=^# )", md)
        if hist:
            rows = [r for r in table_rows(hist.group(1)) if len(r) == 4 and r[3].isdigit()]
            supp = max(int(r[3]) for r in rows)
            last = [r for r in rows if int(r[3]) == supp][-1]
            EDITION = f"Supplement No. {supp} (Ord. {last[0]})"
            with open(WORD_EDITION, "w") as fh:
                fh.write(EDITION + "\n")
            write_table("Supplement-History.md", "Supplement History Table", hist.group(1), retrieved)
            md = md[:hist.start()] + md[hist.end():]
        # The download of the code's front matter carries the ordinance that adopted the code.
        adopt = re.search(r"(?ms)^\*\*ORDINANCE NO\. ([\d-]+)\*\*\s*$(.*?AN ORDINANCE ADOPTING.*?)(?=^# |\Z)", md)
        if adopt:
            write_ordinance(adopt.group(1), adopt.group(2), retrieved)
        # Municode's back matter (Code Comparative Table, Index) follows the last title.
        md, *back = re.split(r"(?m)^(?=# (?:CODE COMPARATIVE TABLE|INDEX)\b)", md)
        for b in back:
            if b.startswith("# CODE COMPARATIVE TABLE"):
                write_table("Code-Comparative-Table.md", "Code Comparative Table", b.split("\n", 1)[1], retrieved)
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
