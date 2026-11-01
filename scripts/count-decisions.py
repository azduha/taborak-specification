#!/usr/bin/env python3
"""The decision count, measured instead of remembered.

This repository states the size of its own decision log in prose, and nothing
else checks a sentence that stands beside a heading: the row for `D-192` was
added to the index while the sentence above it went on saying the log held one
fewer decision than it did. `check-registries.py` reads permission codes,
selectors, scope types and actor labels, and a total is not one of the things it
knows about.

Three numbers, and they must agree:

1. `## D-NNN` headings across the round files — the entries that exist;
2. rows of the index table — the entries that are reachable;
3. every total the prose states about the decision log.

A miss is printed, never fixed here: this script has no authority over wording,
and a word it rewrites is a word it did not read. History pages — anything named
`round-NN.md` — are excluded, because a wrong figure there is a true report of a
wrong belief, which is what those pages are for.

Scanning is per paragraph rather than per line on purpose. Prose in these
documents wraps, and the sentence this script was written to catch was stale at a
line break: "…this page indexes all" / "191 of them…". A line scanner reads the
second line as a number with no noun beside it and says nothing.

Exit code 1 means at least one mismatch. Run it as part of closing a round, the
way `check-registries.py` is run.
"""

import re
import sys
import pathlib

DOC_ROOT = pathlib.Path(__file__).resolve().parent.parent / "docs"
ROUND_DIR = DOC_ROOT / "decisions"
INDEX = ROUND_DIR / "index.md"

# Pages that record what a round believed at the time. A wrong figure there is a
# true report of a wrong belief, so it is history and not a defect.
HISTORY = re.compile(r"round-\d+[a-z]?\.md$")

HEADING = re.compile(r"^#{1,6} (D-\d+) ")
INDEX_ROW = re.compile(r"^\| \[(D-\d+)\]")

# A total is a bare number next to the words it counts. Everything read has
# already had markdown link targets and inline code taken out of it, because
# `[D-190](decisions/round-23.md)` is a reference and not a claim about how many
# decisions there are; the `-` in front of `190` is also what refuses `round-23`
# and `05d`. The gap stops at a full stop, so a number cannot borrow the word
# "decision" from the next sentence.
COUNT_WORDS = r"(?:decisions?|of them|entries)"
AFTER = re.compile(r"(?<![\w-])(\d{2,3})\b[^.]{0,30}?\b" + COUNT_WORDS + r"\b")
BEFORE = re.compile(r"\b" + COUNT_WORDS + r"\b[^.]{0,15}?\b(\d{2,3})(?![\w-])")

LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
CODE = re.compile(r"`[^`]*`")
MARKER = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+|^\s*>\s?")


def prose_of(line: str) -> str:
    """Strip what a reader is shown somewhere else; keep what this page asserts."""
    out = LINK.sub(lambda m: m.group(1), line)
    out = CODE.sub(" ", out)
    return MARKER.sub("", out)


def decisions_exist() -> list[str]:
    out = []
    for path in sorted(ROUND_DIR.glob("round-*.md")):
        for line in path.read_text(encoding="utf-8").split("\n"):
            m = re.match(r"^## (D-\d+) ", line)
            if m:
                out.append(m.group(1))
    return out


def index_rows() -> list[str]:
    out = []
    for line in INDEX.read_text(encoding="utf-8").split("\n"):
        m = INDEX_ROW.match(line)
        if m:
            out.append(m.group(1))
    return out


def paragraphs(text: str):
    """Yield (joined_prose, starts) per blank-line block.

    `starts` is a list of `(offset_in_joined, file_line_number)` for the prose
    lines that went into the block, so a match found across a wrapped line is
    still reported against a line a reader can open.
    """
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        parts, starts, at = [], [], 0
        while i < len(lines) and lines[i].strip():
            line = lines[i]
            i += 1
            if INDEX_ROW.match(line) or HEADING.match(line) or line.lstrip().startswith("|"):
                # a table row and a heading are not prose: the heading is the entry
                # itself, and a row is what the second measure counts
                continue
            text_of_line = prose_of(line)
            starts.append((at, i))  # i was incremented, so it is this line's 1-based number
            parts.append(text_of_line)
            at += len(text_of_line) + 1
        if parts:
            yield " ".join(parts), starts


def line_of(starts, offset: int) -> int:
    """The file line this offset falls in — the last part that begins at or before it."""
    found = starts[0][1]
    for at, lineno in starts:
        if at <= offset:
            found = lineno
    return found


def stated_totals() -> list[tuple[pathlib.Path, int, str]]:
    found = []
    for path in sorted(DOC_ROOT.rglob("*.md")):
        if HISTORY.search(str(path)):
            continue
        for joined, starts in paragraphs(path.read_text(encoding="utf-8")):
            for pat in (AFTER, BEFORE):
                for m in pat.finditer(joined):
                    said = m.group(0)
                    before = joined[max(0, m.start() - 16): m.start()]
                    # a number beside `round 20`, or beside a `D-089` that happens
                    # to sit nearby, is not a claim about the size of the log
                    context = said + " " + before
                    if re.search(r"\bround\b|D-\d", context, re.I):
                        continue
                    # `05d §11, the registry diff, the decisions` is a list item whose
                    # number has nothing to do with a noun three clauses away, and a
                    # comma inside the span is what makes it a list item
                    if re.search(r"§\s*$", before) or "," in said:
                        continue
                    if "of them" in said:
                        back = joined[max(0, m.start() - 70): m.start()]
                        if not re.search(r"decision|\blog\b|index", back, re.I):
                            continue
                    found.append((path, line_of(starts, m.start()), said.strip()))
    return found


def main() -> int:
    entries = decisions_exist()
    rows = index_rows()
    true_total = len(entries)

    problems = []
    if len(rows) != true_total:
        problems.append(f"index rows {len(rows)} != entries {true_total}")
    for missing in sorted(set(entries) - set(rows)):
        problems.append(f"no index row for {missing}")
    for extra in sorted(set(rows) - set(entries)):
        problems.append(f"index row {extra} has no entry")

    hits = stated_totals()
    stale = []
    for path, lineno, snippet in hits:
        number = int(re.search(r"\d{2,3}", snippet).group(0))
        if number != true_total:
            rel = path.relative_to(DOC_ROOT.parent)
            stale.append(f"{rel}:{lineno}: {number} where the log holds {true_total} — “{snippet}”")

    print(f"entries:       {true_total}  (## D- headings in {ROUND_DIR.name}/)")
    print(f"index rows:    {len(rows)}")
    print(f"stated totals: {len(hits)} sentences outside the history pages")
    for line in problems:
        print(f"MISMATCH {line}")
    for line in stale:
        print(f"STALE    {line}")
    if not problems and not stale:
        print("ok")
    return 1 if (problems or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
