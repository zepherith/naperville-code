#!/usr/bin/env python3
"""Split the Naperville Municipal Code into one Markdown file per chapter.

Input is the PDF of the whole code as printed by Municode (library.municode.com,
"Download" of the full code). Pass its path and the date it was downloaded:

  tools/municode_import.py "Naperville, IL Code of Ordinances.pdf" 2026-11-18

Needs pdftotext (poppler-utils). The script rewrites every chapter file, the
traffic schedule files of Chapter 11-1 and the README contents. Files whose text
didn't change are left alone.

What it does to the printed text:
- drops the front matter (supplement sheets, preface, history table, page
  checklist), each title's cover page, the Code Comparative Table and the Index;
- strips running page headers and footers;
- rejoins wrapped lines into paragraphs and words split by end-of-line hyphens;
- keeps tables and schedules in fixed-width blocks with their columns;
- closes up stray spaces the PDF puts before punctuation ("Council ," -> "Council,").
Words are never changed otherwise.
"""
import collections
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOURCE = "https://library.municode.com/il/naperville/codes/code_of_ordinances"
SMALL = {"and", "of", "the", "in", "for", "or", "to", "a", "an", "on"}

PAGE_ID = re.compile(r"\bCD\s?(\d+)\s?:\s?(\d+(?:\.\d+)?)")
LABEL = re.compile(r"^\(?(?:\d{1,3}(?:\.\d{1,3})*|[A-Za-z]{1,2}|[ivxlc]{1,5}|[IVXL]{1,5})[.)]\s+")
SECNUM = r"\d+\s?-\s?[\dSOl]+(?:\.\d+)?\s?[A-Z0-9]?\s?-\s?[\dOl]+(?:\s?[O\d])?[A-Z]?(?:\.\d+)?(?:-\d+)?"
# Letters and digits the OCR mixes up, each way round.
TO_LETTER = {"8": "B", "0": "D", "1": "I", "5": "S", "6": "G", "2": "Z"}
TO_DIGIT = {"S": "5", "O": "0", "l": "1", "I": "1", "B": "8", "D": "0"}
SECTION = re.compile(r"^(" + SECNUM + r")\s?:\s+(.*)$")
PAGES_SEEN = []  # (PDF page number, title, running header) of each page of the code, for reports
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}
MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"


# ---------------------------------------------------------------- helpers

def title_case(name):
    words = name.lower().split()
    return " ".join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")


def padded(chapter):
    """Pad the whole chapter number, keep decimals and letters: 2 -> 02, 0.5 -> 00.5."""
    m = re.fullmatch(r"(\d+)(\.\d+)?([A-Z]?)", chapter)
    return f"{int(m.group(1)):02d}{m.group(2) or ''}{m.group(3)}"


def roman(s):
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = ROMAN[a]
        total += -v if b != " " and ROMAN.get(b, 0) > v else v
    return total


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def secnum(s):
    return re.sub(r"\s", "", s)


def fix_spacing(s):
    """Close the stray spaces the PDF prints before punctuation."""
    s = re.sub(r"(\S) +([,;:])(?=\s|$)", r"\1\2", s)
    s = re.sub(r"([A-Za-z0-9)]) +\.(?=\s|$|,)", r"\1.", s)
    s = re.sub(r"(\d) \.(\d)", r"\1.\2", s)
    s = re.sub(r"(\d) ,(\d{3})\b", r"\1,\2", s)  # "$10 ,000.00"
    s = re.sub(r"(\d) %", r"\1%", s)
    s = re.sub(r"\b(\d+-\d+) ([A-Z]-\d)", r"\1\2", s)  # "8-1 C-6"  # "6-6A-3 .7.1", "$50,000 .00"
    s = re.sub(r"\b(\d{1,2}-\d{1,2}) -(\d{2,4})\b", r"\1-\2", s)  # "1-21 -1980"
    s = re.sub(r"\( +", "(", s)
    s = re.sub(r" +\)", ")", s)
    return s


def fix_table_spacing(s):
    """The same fix inside fixed-width rows, keeping every column where it was."""
    s = re.sub(r"([A-Za-z0-9)]) \.( |$)", r"\1. \2", s)
    s = re.sub(r"([A-Za-z0-9)]) ,( |$)", r"\1, \2", s)
    return s.rstrip()


def md_escape(s):
    s = s.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").replace("<", "\\<").replace("`", "\\`")
    s = re.sub(r"^(\d+)\.(\s|$)", r"\1\\.\2", s)
    s = re.sub(r"^([-+#>|=])", r"\\\1", s)
    return s


# "CODE:        The Municipal Code of ..." -- a defined term and its definition set in two columns
DEFINITION = re.compile(r"^\s*([A-Z][A-Z0-9 ,'’/()&.\-]{1,60}):\s{3,}(\S.*)$")
LEADERS = re.compile(r"(?:\s?\.){5,}\s*")


def tabular(line):
    """A line laid out in columns (runs of 3+ spaces between words)."""
    rest = LABEL.sub("", line.strip())
    return bool(re.search(r"\S {3,}\S", rest))


# ---------------------------------------------------------------- reading the PDF

def read_pages(pdf):
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return text.replace("\xa0", " ").split("\f")


def front_matter(pages):
    first = "\n".join(pages[:2])
    sup = re.search(r"SUPPLEMENT NO\. (\d+)\s*\n\s*(\w+ \d{4})", first)
    ords = re.search(r"Ordinance No\. (\S+), adopted (" + MONTH + r" \d+, \d{4})", first)
    titles = {}
    for p in pages[:400]:
        if "TABLE OF CONTENTS" in p or re.search(r"^\s+Title\s+Page\s*$", p, re.M):
            for m in re.finditer(r"^\s{5,12}(\d+)\. ([A-Z][A-Za-z ,'&-]+?)[ .]{3,}\s*CD\d+:1\s*$", p, re.M):
                titles[int(m.group(1))] = title_case(m.group(2).strip())
    return {
        "supplement": sup.group(1), "supplement_date": sup.group(2),
        "ordinance": ords.group(1), "adopted": ords.group(2), "titles": titles,
    }


FOOTNOTE = re.compile(r"^\s*(\*{1,3}|†{1,2}|‡|t{1,2}(?= See\b))\s?(\S.*)$")


def pull_footnotes(lines):
    """Take the footnotes printed at the foot of a page out of its text.

    They start with *, ** or a dagger (the OCR often reads a dagger as "t") and sit
    below the last line of text. Returns them and removes them from `lines`.
    """
    nonblank = [i for i, l in enumerate(lines) if l.strip()]
    start = None
    for i in reversed(nonblank[-6:]):
        if FOOTNOTE.match(lines[i]):
            start = i
        elif start is None:
            # a wrapped footnote line below its marker line
            continue
    if start is None:
        return []
    block = lines[start:]
    if not all(FOOTNOTE.match(l) or not l.strip() or len(l.strip()) < 120 for l in block):
        return []
    notes = []
    for l in block:
        if not l.strip():
            continue
        if FOOTNOTE.match(l) or not notes:
            notes.append(squash(l))
        else:
            notes[-1] += " " + squash(l)
    del lines[start:]
    return [re.sub(r"^t{1,2}(?= See)", lambda m: "†" * len(m.group(0)), n) for n in notes]


def body_pages(pages):
    """Yield (title, page id, header, lines) for each page of the code itself.

    Many pages are scans with an OCR text layer, so the printed page label ("CD3:333")
    is often misread ("C03:333", "CDS:229"). Pages are therefore recognized by the
    "Municipal Code" footer, and the title is read from the section numbers in the
    running header, falling back to the previous page.
    """
    started, title = False, None
    for number, p in enumerate(pages, 1):
        lines = p.rstrip("\n").split("\n")
        nonblank = [i for i, l in enumerate(lines) if l.strip()]
        if not nonblank:
            continue
        tail = " ".join(lines[i] for i in nonblank[-3:])
        if "MunicipalCode" not in re.sub(r"\s", "", tail):
            continue  # supplement instruction sheets
        foot = " ".join(lines[i] for i in nonblank[-2:])
        if re.search(r"\b(CCT|C[DO0]i)\s?:\s?\d", foot):
            if started:
                break  # Code Comparative Table, then the Index: the code itself has ended
            continue
        cut = len(lines)
        for i in reversed(nonblank[-3:]):
            l, d = lines[i], re.sub(r"\s", "", lines[i])
            if (re.search(r"C\s?[DO0]\s?\S{0,3}\s?:", l) or "MunicipalCode" in d or "CityofNapervill" in d
                    or re.match(r"^(SupplementNo|" + MONTH + r")", d) or "[Thenextpageis" in d):
                cut = i
            else:
                break
        lines = lines[:cut]
        header = ""
        first = next((i for i, l in enumerate(lines) if l.strip()), None)
        if first is not None and re.match(r"^\s*\d+\s?-\s?\d", lines[first]) and re.search(r"\S\s{8,}\d+\s?-\s?\d", lines[first]):
            header = squash(re.split(r"\s{8,}", lines[first].strip())[0])
            lines = lines[first + 1:]
        body = "\n".join(lines)
        if re.search(r"^\s*Subject\s+Chapter\s*$", body, re.M):
            continue  # a title's cover page, listing its chapters
        hm = re.match(r"(\d+)\s?-", header)
        fm = PAGE_ID.search(tail)
        # Titles only move forward one at a time; an OCR misreading of the header
        # ("3-13-1" on a 6-13 page) is overruled by the page label when that reads well.
        cands = [int(x.group(1)) for x in (hm, fm) if x]
        ok = [c for c in cands if title is None or c in (title, title + 1)]
        if not started and not re.match(r"1\s?-\s?1\s?-", header):
            continue  # front matter, until the first page of Chapter 1-1
        if ok:
            title, started = (ok[-1] if fm and int(fm.group(1)) in ok else ok[0]), True
        elif not started:
            continue  # preface, adopting ordinance, supplement history, checklist
        lines = lines + [("note", n) for n in pull_footnotes(lines)]
        pid = PAGE_ID.search(tail)
        PAGES_SEEN.append((number, title, header))
        yield title, pid.group(2) if pid else "?", header, lines


# ---------------------------------------------------------------- splitting into chapters

def split_chapters(pages):
    chapters, cur, cur_title = [], None, None
    for title, pid, header, lines in pages:
        if title != cur_title:
            cur, cur_title = None, title  # each title opens with a cover page listing its chapters
        sch = re.search(r"Sch\s?\.", header)
        tag = None
        if sch and cur and cur["n"] == "1" and title == 11:
            # IA, IB, VIIC-1 ... are parts of Schedules I and VII. Part letters run A to H, so they
            # never collide with a Roman numeral. One page prints "11B" for "IIB".
            sm = re.search(r"Sch\s?\.\s?([IVXL1]+?)([A-H](?:-\d+)?)?$", header)
            tag = sm.group(1).replace("1", "I")
        i = 0
        while i < len(lines):
            l = lines[i]
            if isinstance(l, tuple):  # a footnote from the foot of the page
                if cur is not None:
                    (cur["schedules"].setdefault(tag, []) if tag else cur["lines"]).append(l)
                i += 1
                continue
            m = re.match(r"^\s*CHAPTER ?(\d+(?:\.\d+)?)([A-Z]?)\s*$", l)
            if m:
                n, part = m.group(1), m.group(2)
                j, name = i + 1, []
                while j < len(lines) and not lines[j].strip():
                    j += 1
                while j < len(lines) and lines[j].strip() and not re.match(r"^\s*(ARTICLE [A-Z]|SECTION\s?:)", lines[j]):
                    name.append(lines[j].strip())
                    j += 1
                if cur is None or cur["title"] != title or cur["n"] != n:
                    cur = {"title": title, "n": n, "name": squash(" ".join(name)), "lines": [], "schedules": collections.OrderedDict()}
                    chapters.append(cur)
                if part:  # "CHAPTER 6A": printed as its own chapter, listed as part of Chapter 6
                    cur["lines"].append(("part", f"CHAPTER {n}{part}. {squash(' '.join(name))}"))
                i = j
                continue
            if tag and re.match(r"^\s*11\s?-\s?1\s?-\s?([6-9]|\d\d)\s?:\s+[A-Z]{3}", l):
                tag = None  # Section 11-1-6 begins on the last schedule page
            if tag:
                sw = re.match(r"^\s*(?:SCHEDULE ([IVXL]+)\s?/|Sch\s?\.\s?([IVXL]+?)[A-H]?(?:-\d+)?\s?:)", l)
                if sw and (sw.group(1) or sw.group(2)) != tag:
                    tag = sw.group(1) or sw.group(2)  # a new schedule starts partway down the page
            if cur is not None:
                if tag:
                    cur["schedules"].setdefault(tag, []).append(("page", pid))
                    cur["schedules"][tag].append(l)
                else:
                    cur["lines"].append(l)
            i += 1
        if cur is not None and not tag:
            cur["lines"].append(("page", pid))
    return chapters


# ---------------------------------------------------------------- rendering

class Words:
    """Decides whether "applica-" + "tion" was a soft hyphen, from the code's own vocabulary."""

    def __init__(self, text):
        self.plain = collections.Counter(w.lower() for w in re.findall(r"[A-Za-z]+", text))
        self.hyph = collections.Counter(w.lower() for w in re.findall(r"[A-Za-z]+-[A-Za-z]+", text))

    def join(self, left, right):
        a = re.search(r"([A-Za-z]+)-$", left).group(1)
        b = re.match(r"([A-Za-z]+)", right)
        if not b:
            return left + right
        b = b.group(1)
        joined, hyph = (a + b).lower(), f"{a}-{b}".lower()
        if self.hyph[hyph] > self.plain[joined]:
            return left + right
        return left[:-1] + right


def clean_lines(raw):
    """Drop page markers and the blank runs around page breaks; mark breaks as soft."""
    out = []
    for l in raw:
        if isinstance(l, tuple) and l[0] == "note":
            out.append(l)
            continue
        if isinstance(l, tuple):
            while out and out[-1] == "":
                out.pop()
            out.append(None)  # soft break: a paragraph may continue on the next page
            continue
        if l.strip() == "":
            if out and out[-1] is None:
                continue
            out.append("")
        else:
            out.append(l.rstrip())
    return out


def label_line(s):
    return bool(LABEL.match(s.strip())) or bool(re.match(r"^\s*\(?[a-z0-9]{1,3}\)\s", s))


def render_body(lines, words):
    """Markdown for the text between headings: paragraphs rejoined, tables kept in code blocks."""
    raw, lines, notes_at = clean_lines(lines), [], {}
    for l in raw:
        if isinstance(l, tuple):
            notes_at.setdefault(len(lines), []).append(l[1])
            lines.append(None)  # the note sat at a page foot: treat it as a page break
        else:
            lines.append(l)
    out, para, pending = [], [], []

    def flush_notes():
        if pending:
            out.append("\n".join("> " + md_escape(fix_spacing(n)) for n in pending))
            pending.clear()

    def end_para():
        if para:
            text = para[0]
            for nxt in para[1:]:
                if re.search(r"[A-Za-z]-$", text) and re.match(r"[a-z]", nxt):
                    text = words.join(text, nxt)
                else:
                    text += " " + nxt
            text = fix_spacing(squash(text))
            out.append(md_escape(text))
            para.clear()
            flush_notes()

    real = [l for l in lines if l]
    special = [bool(l) and (DEFINITION.match(l) is not None or LEADERS.search(l) is not None) for l in lines]
    indent = min((len(l) - len(l.lstrip()) for l in real), default=0)
    tab = [bool(l) and not special[k] and tabular(l) for k, l in enumerate(lines)]
    in_table = list(tab)
    idx = [i for i, t in enumerate(tab) if t]
    for a, b in zip(idx, idx[1:]):
        gap = lines[a + 1:b]
        if b - a <= 4 and all(g is None or g == "" or (g.startswith(" ") and not label_line(g)) for g in gap):
            for k in range(a, b + 1):
                in_table[k] = True
    i = 0
    while i < len(lines):
        l = lines[i]
        if i in notes_at:
            pending.extend(notes_at[i])
            if not para:
                flush_notes()
        if in_table[i]:
            end_para()
            j = i
            block = []
            while j < len(lines) and (in_table[j] or lines[j] is None):
                if lines[j] is not None:
                    block.append(fix_table_spacing(lines[j][indent:] if lines[j] else ""))
                j += 1
            while block and not block[-1]:
                block.pop()
            out.append("```text\n" + "\n".join(block) + "\n```")
            i = j
            continue
        if l is None:
            # Page break: keep the paragraph going unless the last line closed a sentence
            # and the next one starts a new labeled item or a capitalized sentence.
            nxt = next((x for x in lines[i + 1:] if x), "")
            if para and (label_line(nxt) or (re.search(r"[.:;]$", para[-1]) and not re.match(r"\s*[a-z]", nxt))):
                end_para()
        elif l == "":
            end_para()
        elif special[i] and LEADERS.search(l):
            # a fee or schedule line with dot leaders: one line each
            end_para()
            para.append(LEADERS.sub(" . . . ", l.strip()))
            end_para()
        else:
            dm = DEFINITION.match(l)
            if para and (label_line(l) or dm):
                end_para()
            para.append(f"{dm.group(1)}: {dm.group(2)}" if dm else l.strip())
        i += 1
    end_para()
    flush_notes()
    return "\n\n".join(out)


def fix_number(raw, title, chapter, part):
    """Correct an OCR-misread section number from the chapter it sits in.

    In Chapter 8-2, Article B, "8-28-15" can only be 8-2B-15; "3-SA-7" in Chapter 3-5,
    Article A is 3-5A-7; "1-9-1O" is 1-9-10. A number that can't be matched this way
    is left as printed.
    """
    raw = secnum(raw)
    want = f"{title}-{chapter}{part}-"
    if raw.startswith(want) or (not part and re.match(re.escape(f"{title}-{chapter}") + r"[A-Z]-", raw)):
        head, rest = raw[:len(want)], raw[len(want):]
        if raw.startswith(want):
            return head + "".join(TO_DIGIT.get(c, c) if c in "Ol" else c for c in rest)
        return raw
    pre = raw.split("-")
    if len(pre) < 3:
        return raw
    t, ca, rest = pre[0], pre[1], "-".join(pre[2:])
    exp = f"{chapter}{part}"
    if t == str(title) and len(ca) == len(exp) and all(
            a == b or TO_DIGIT.get(a) == b or TO_LETTER.get(a) == b for a, b in zip(ca, exp)):
        return f"{title}-{exp}-" + "".join(TO_DIGIT.get(c, c) if c in "Ol" else c for c in rest)
    return raw


CAPTION = re.compile(
    "^([A-Z0-9\"“\\[][A-Z0-9\"“” ,;'’&()/.\\-\\[\\]]*?[A-Z)\\]\"”])\\s?[:.](?:\\s+|$)(.*)$")


def section_heading(l):
    """('1-1-1', 'TITLE', 'rest of line') for a section's first line, else None."""
    m = SECTION.match(l.strip())
    if not m:
        return None
    num, rest = secnum(m.group(1)), m.group(2).strip()
    hm = re.match(CAPTION, rest)
    if hm and hm.group(1) == hm.group(1).upper() and re.search(r"[A-Z]{2}", hm.group(1)):
        return num, squash(hm.group(1)), hm.group(2)
    if rest and rest == rest.upper() and re.search(r"[A-Z]{3}", rest) and not re.search(r"[a-z]", rest):
        return num, squash(rest.rstrip(":.")), ""
    return None


def render_chapter(ch, meta, retrieved, schedule_links=None):
    num = f"{ch['title']}-{ch['n']}"
    out, body = [], []
    words = meta["words"]

    def flush():
        if body:
            r = render_body(body, words)
            if r:
                out.append(r)
            body.clear()

    lines, i = ch["lines"], 0
    part = ""
    while i < len(lines):
        l = lines[i]
        if isinstance(l, tuple) and l[0] == "part":
            part = re.match(r"CHAPTER [\d.]+([A-Z])", l[1]).group(1)
            flush()
            out.append("## " + l[1])
            i += 1
            continue
        if isinstance(l, tuple):
            body.append(l)
            i += 1
            continue
        s = l.strip()
        am = re.match(r"^ARTICLE ([A-Z])\.\s*(.*)$", s)
        if am and s == s.upper():
            part = am.group(1)
            flush()
            name = [am.group(2)]
            while i + 1 < len(lines) and isinstance(lines[i + 1], str) and lines[i + 1].strip() and lines[i + 1].strip() == lines[i + 1].strip().upper() and not re.match(r"^\s*SECTION", lines[i + 1]):
                i += 1
                name.append(lines[i].strip())
            out.append(f"## ARTICLE {am.group(1)}. {squash(' '.join(name))}")
            i += 1
            continue
        if re.match(r"^SECTION\s?:$", s):
            flush()
            entries, j = [], i + 1
            while j < len(lines):
                x = lines[j]
                if isinstance(x, tuple) or not x.strip():
                    j += 1
                    continue
                m = SECTION.match(x.strip())
                if m and not section_heading(x):
                    entries.append(f"{fix_number(m.group(1), ch['title'], ch['n'], part)}: {fix_spacing(squash(m.group(2)))}")
                    j += 1
                    continue
                if entries and x.startswith(" ") and not SECTION.match(x.strip()) and not section_heading(x) and x.strip() != x.strip().upper():
                    entries[-1] += " " + squash(x)  # a wrapped entry
                    j += 1
                    continue
                break
            out.append("SECTION:\\\n" + "\\\n".join(md_escape(e) for e in entries))
            i = j
            continue
        h = section_heading(l)
        fixed = h and fix_number(h[0], ch["title"], ch["n"], part)
        if h and (fixed.startswith(f"{num}-") or re.match(re.escape(num) + r"[A-Z]-", fixed)):
            flush()
            out.append(f"### {fixed}: {fix_spacing(h[1])}")
            if h[2]:
                body.append(" " * (len(l) - len(l.lstrip())) + h[2])
            i += 1
            continue
        body.append(l)
        i += 1
    flush()
    if schedule_links:
        out.append("**Traffic schedules (Section 11-1-5).** Each schedule is kept in its own file:\n\n" + "\n".join(schedule_links))
    return header(f"Naperville Municipal Code {num}", meta, retrieved) + f"# {num} {ch['name']}\n\n" + "\n\n".join(out) + "\n"


def header(citation, meta, retrieved):
    return "\n".join([
        "---",
        f"citation: {citation}",
        f"source: {SOURCE}",
        f"current_through: Supplement No. {meta['supplement']} (Ord. {meta['ordinance']})",
        f"retrieved: {retrieved}",
        "---",
        "",
        "",
    ])


def render_schedule(tag, lines, meta, retrieved, name=None):
    """One traffic schedule; drops the heading lines repeated at the top of each page."""
    for l in lines:
        if name is None and isinstance(l, str):
            m = re.match(r"^\s*SCHEDULE ([IVXL]+)\s?/\s?(.+?)\s*$", l)
            if m:
                name = title_case(squash(m.group(2)))
                break
    seen, kept, page_start = set(), [], False
    for l in lines:
        if isinstance(l, tuple):
            kept.append(l)
            page_start = page_start or l[0] == "page"
            continue
        key = squash(l)
        if page_start:
            if not key:
                continue
            if key in seen:
                continue
            page_start = False
        if key and len(seen) < 400 and not re.search(r"\d{2}-\d{2,3}\s*$", key):
            seen.add(key)
        kept.append(l)
    body = render_body(kept, meta["words"])
    title = f"Schedule {tag}" + (f": {name}" if name else "")
    return header(f"Naperville Municipal Code 11-1-5, Schedule {tag}", meta, retrieved) + f"# 11-1-5 {title}\n\n" + body + "\n", name


# Titles whose pages in Municode's PDF (Supplement 100) are all digital text, none scanned.
DIGITAL_TITLES = {2}


def strip_dates(text):
    return re.sub(r"^(current_through|retrieved): .*$", "", text, flags=re.M)


def write(path, text, stats):
    if os.path.exists(path) and strip_dates(open(path, encoding="utf-8").read()) == strip_dates(text):
        stats["unchanged"] += 1
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    stats["written"] += 1


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    pdf, retrieved = argv
    pages = read_pages(pdf)
    meta = front_matter(pages)
    chapters = split_chapters(body_pages(pages))
    alltext = "\n".join(l for c in chapters for l in c["lines"] if isinstance(l, str))
    meta["words"] = Words(alltext)
    stats = collections.Counter()
    toc, reserved = [], []
    word_file = os.path.join(ROOT, "tools", "word-titles.txt")
    word = set()
    if os.path.exists(word_file):
        word = {int(x) for x in open(word_file).read().split() if x.isdigit()}
    for t in sorted(meta["titles"]):
        tfolder = f"Title-{t:02d}-{slug(meta['titles'][t])}"
        if t in word:
            stats["word"] += 1
        toc += ["", f"### Title {t}: {meta['titles'][t]}", "", "| Chapter | Name |", "| --- | --- |"]
        for ch in [c for c in chapters if c["title"] == t]:
            num = f"{t}-{ch['n']}"
            has_text = any(isinstance(x, str) and section_heading(x) for x in ch["lines"])
            if not has_text:
                reserved.append(num)
                note = squash(" ".join(x for x in ch["lines"] if isinstance(x, str)))
                rep = re.search(r"\(Rep\. by Ord\. [^)]*\)", note)
                ed = re.search(r"Ord\. No\. (\S+), § \d+ ?, adopted (" + MONTH + r" \d+, \d{4})", note)
                why = (f"repealed {rep.group(0)[1:-1].replace('Rep. by', 'by')}" if rep
                       else f"reserved; former chapter repealed by Ord. {ed.group(1)}, {ed.group(2)}" if ed
                       else "reserved")
                name = title_case(ch["name"].rstrip("*"))
                toc.append(f"| {num} | {name} (no file{'' if why == 'reserved' else ': ' + why.replace('reserved; ', '')}) |")
                continue
            base = f"{t}-{padded(ch['n'])}"
            links = []
            if ch["schedules"]:
                names = {}
                for x in ch["lines"]:
                    if isinstance(x, str):
                        nm = re.match(r"^(\S.*?)\s{3,}Schedule ([IVXL]+)\s*$", x.strip())
                        if nm:
                            names[nm.group(2)] = squash(nm.group(1))
                for top, ls in ch["schedules"].items():
                    rel = f"{tfolder}/{base}-Schedules/Sch-{roman(top):02d}.md"
                    text, sname = render_schedule(top, ls, meta, retrieved, names.get(top))
                    if t not in word:
                        write(os.path.join(ROOT, rel), text, stats)
                    label = f"Schedule {top}" + (f": {sname}" if sname else "")
                    links.append(f"- [{label}]({base}-Schedules/Sch-{roman(top):02d}.md)")
                    toc.append(f"| [11-1-5 Sch. {top}]({rel}) | {sname or ''} |")
            rel = f"{tfolder}/{base}.md"
            if t not in word:  # titles taken from Municode's Word download are left alone
                write(os.path.join(ROOT, rel), render_chapter(ch, meta, retrieved, links), stats)
            toc.insert(len(toc) - len(links), f"| [{num}]({rel}) | {title_case(ch['name'])} |")
    pdf_titles = set(meta["titles"]) - word
    pdf_label = ("Title " if len(pdf_titles) == 1 else "Titles ") + ", ".join(str(t) for t in sorted(pdf_titles))
    readme = [
        "# Naperville Municipal Code",
        "",
        "An unofficial copy of the Municipal Code of the City of Naperville, Illinois, kept as one Markdown file per chapter so that changes can be tracked with Git.",
        "",
        f"**The official text controls.** This copy is for reference only. The official code is published by Municode at [library.municode.com]({SOURCE}).",
        "",
        f"- **Current through:** Supplement No. {meta['supplement']} ({meta['supplement_date']}), which includes ordinances through Ord. No. {meta['ordinance']}, adopted {meta['adopted']}.",
        "- **Layout:** one folder per title and one file per chapter. Chapter numbers are padded with zeros so files sort in order (`1-09.md` is Chapter 1-9, and `8-00.5.md` is Chapter 8-0.5). Lettered parts of a chapter (Article 6A, Chapter 9A and so on) are headings inside the chapter's file.",
        "- **Traffic schedules:** the 31 schedules of Section 11-1-5 are kept one per file in `Title-11-Motor-Vehicles-and-Traffic/11-01-Schedules/`, because together they run about 260 pages.",
        "- **Each file** starts with its citation, source, the supplement it reflects and the date the text was downloaded.",
        ("- **Word downloads:** Title" + ("s " if len(word) > 1 else " ") + ", ".join(str(w) for w in sorted(word))
         + " come" + ("" if len(word) > 1 else "s") + " from Municode's online text, downloaded as Word, which is born-digital, so it has no OCR errors. Its files say so in `current_through`, keep Municode's tables and footnotes, and show its figures from the title's `images/` folder. To update "
         + ("them" if len(word) > 1 else "it") + ", run `tools/municode_word_import.py <file> <date downloaded>` on a fresh download.") if word else None,
        "- **How the text was made:** " + (pdf_label + " " + ("was" if len(pdf_titles) == 1 else "were") if word else "it was") + " extracted from Municode's PDF of the code. Wrapped lines were rejoined into paragraphs, tables and schedules were kept in fixed-width blocks, footnotes from the foot of a page were moved below the paragraph they interrupt (shown as quoted notes), and running page headers and footers were removed, along with the supplement sheets, Code Comparative Table and Index. No wording was changed.",
        None if not pdf_titles - DIGITAL_TITLES else "- **Scanned pages:** many pages of Municode's PDF are scans of the 2010 printing with a machine-read (OCR) text layer, so some words in this copy may be misread. Where a passage matters, check it against the official code.",
        "- **Updating:** download the full code from Municode as a PDF and run `tools/municode_import.py <file> <date downloaded>` (needs `pdftotext`). It rewrites only the chapters whose text changed and this page.",
        "",
        "## Contents",
    ] + toc
    readme = [r for r in readme if r is not None]
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(readme) + "\n")
    print(f"Supplement {meta['supplement']}, through Ord. {meta['ordinance']} ({meta['adopted']})")
    print(f"{len(chapters)} chapters: {stats['written']} files written, {stats['unchanged']} unchanged; "
          f"{len(reserved)} reserved ({', '.join(reserved)})")


if __name__ == "__main__":
    main(sys.argv[1:])
