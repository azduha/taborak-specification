#!/usr/bin/env python3
"""Diff these documents against the registries they name.

Adopted by D-127 as the gate on a refinement round: while this script reports a
finding that is not in `scripts/registry-baseline.txt`, a round is not closed.

It reads markdown and nothing else. It has no dependency, and it never writes
except with `--update-baseline`.

    python3 scripts/check-registries.py            # exit 1 on an unbaselined finding
    python3 scripts/check-registries.py --verbose  # also list what it chose to ignore
    python3 scripts/check-registries.py --update-baseline

**The registries are the documents.** Not a list kept beside them. A second copy
of a registry is a second thing that can be wrong, which is the defect this script
exists to catch — the catalog's own §12 tells the story of a seeded table copied
from an evaluator's arm list. So each register below is a section of a page, and a
section that stops parsing is reported as `no-registry` rather than silently
yielding an empty set: an empty registry would make every token in the corpus a
finding and would look, for about one second, like a very good result.

**What a finding is.**

  code-shape        a code-shaped token in prose that no register carries
  unknown-action    a code-shaped token in a known namespace whose act no code uses
  selector          an operand spelled like a selector that is not seeded
  label             an actor label that is not on the vocabulary of 00-conventions §7a
  unnamed-row       a registered row that no page names except its own register
  no-registry       a vocabulary the corpus calls seeded and never lists

**Why "code-shaped" is a rule and not a guess.** Most dotted tokens in these files
are `table.column`, and treating every one of them as a permission code would
report hundreds of correct sentences. The catalog's own §1 grammar decides it
instead: a code's last segment is an act and its first segment names stored state.
Both halves are read from the catalog — the acts are the last segments of the
registered codes, the namespaces their first segments — so the classifier holds no
opinion of its own, and an invented act is caught by reading the registry's own
vocabulary back at the prose.

**What is not reported, and why each exemption is a page.** `decisions/` records
what was proposed before it was settled and is exempt outright.
`appendix/removed-concepts.md` is where a dead name is indexed, so a name listed
there is known-dead rather than news; the catalog's §9 and §10 register the
namespaces that are absent on purpose and the ones deferred to unbuilt modules. An
ALL-CAPS word counts as an operand only inside an expression, because in these
files the same shape also carries SQL keywords, column types and one group's name.

**Two directions, one limit.** A token in prose with no row is half the check; a
row that no prose names is the other half, and that half only ever says *nobody
reads this outside its own table* — which is a question to ask, not a defect. What
this script cannot see at all is a name that is nowhere: a word the prose never
uses cannot be missing from it.

**A `no-registry` finding is the loudest one here.** 00-conventions §10 promises
certain vocabularies ship as seed data; a vocabulary that promise names and no
page enumerates is one nothing can be checked against. The claim is read from §11
each run, so it appeared when `reason_code` was listed with no rows anywhere and
went away by itself when D-128 deleted that table.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

# --- where each register lives -------------------------------------------------

CATALOG_CODES = "appendix/permission-catalog-a-codes.md"
CATALOG_B = "appendix/permission-catalog-b-roles-and-open-issues.md"
REMOVED = "appendix/removed-concepts.md"
SELECTORS_PAGE = "data-model/05a-audience-and-grammar.md"
AUTHZ_PAGE = "data-model/05-authorization.md"
CONVENTIONS = "data-model/00-conventions.md"
BASELINE_DEFAULT = "scripts/registry-baseline.txt"

# Pages a finding is not raised in: a decision log records what was proposed, and
# the removed-concepts page exists to hold dead names. They still cannot *count*
# as a mention, so a row named only in history is still `unnamed-row`.
HISTORY = ("decisions/",)

# Which parsed register answers for which vocabulary 00-conventions §10 calls
# seeded. The *claim* is read out of §11, never listed here: what this table can
# say is "something answers for this name", never "these are the vocabularies".
# A claimed vocabulary with no row here is reported `no-registry` rather than
# skipped — that is how `reason_code` got reported while §11 still listed a table
# no page enumerated, and it is why the row is gone now that D-128 deleted it.
VOCABULARY_REGISTER = {
    "permission": "code",
    "selector_type": "selector",
    "grant_scope_type": "scope",
}
SEEDED_BULLET = re.compile(r"^- \*\*Seed data for vocabularies\*\*.*?(?=^- \*\*|\Z)", re.S | re.M)

# --- token shapes -------------------------------------------------------------

BACKTICK = re.compile(r"`([^`\n]+)`")
CODE_TOKEN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+$")
OPERAND_TOKEN = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")
LABEL_TOKEN = re.compile(r"^[a-z][a-z0-9_]*:[a-z0-9_<>.:-]+$")
WORD = re.compile(r"^[a-z][a-z0-9_]*$")

FIELDS_HEAD = re.compile(r"\*\*Fields\*\*\s*\(`([^`]+)`\)")
SEEDED_ROWS = re.compile(r"\*\*Seeded rows\*\*")

# An operand spelled as a word, or as a word with its argument; plus the acts the
# expression language itself spells in words.
OPERAND_CONTEXT = re.compile(r"[A-Z][A-Z0-9_]{2,}\s*\(|[*+]|\S\s+-\s+\S")

# ALL-CAPS words that are not operands and never will be. Each was found by
# reading a report this script produced, not by guessing in advance.
OPERAND_STOPWORDS = {
    "AND", "NOT", "THE", "OR", "NULL", "TRUE", "FALSE", "SQL", "ORM", "URL", "URI",
    "CSV", "PDF", "XML", "HTML", "JSON", "GDPR", "EU", "CZ", "US", "UK", "API",
    "DDL", "FK", "PK", "ID", "IDS", "ERD", "AGM", "SMS", "TLS", "HTTPS", "EUR",
    "OK", "TODO", "FIXME", "WIP", "XXX", "NB", "PS", "II", "III", "IV", "XI",
    "UUID", "DATE", "BIGINT", "INTEGER", "TEXT", "BOOLEAN", "CHECK", "UNIQUE",
    "INSERT", "UPDATE", "DELETE", "SELECT", "TABLE", "INDEX", "T12", "POZNAMKA",
}

LABEL_SCHEMES = {"app", "http", "https", "mailto", "urn", "file", "tel", "sms"}


def md_files(docs: pathlib.Path):
    return sorted(p for p in docs.rglob("*.md") if "site" not in p.parts)


def is_history(rel: str) -> bool:
    return rel.startswith(HISTORY)


def table_first_cells(text: str):
    """The first cell of every data row of every markdown table in a block: a
    table's header row and its `|---|` rule are not data rows, and reading them as
    such is how a column named `code` became a seeded value of a vocabulary."""
    header = False
    for line in text.splitlines():
        if not line.startswith("|"):
            header = False
            continue
        if set(line.replace("|", "").strip()) <= set("-: "):
            continue
        if not header:
            header = True
            continue
        cells = line.split("|")
        if len(cells) > 1:
            yield cells[1]


def section(text: str, head: str):
    """A `##` section of a page, from a heading containing `head` to the next one."""
    m = re.search(rf"^##[^\n]*{re.escape(head)}[^\n]*\n.*?(?=^## |\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


def next_label(text: str):
    """Text up to the next bolded label or `##` heading — one block of a page."""
    stops = [i for i in (text.find("\n**"), text.find("\n## ")) if i != -1]
    return text[: min(stops)] if stops else text


def block_after(text: str, pattern: re.Pattern):
    """What follows a marker, up to the next label."""
    m = pattern.search(text)
    return next_label(text[m.end():]) if m else ""


def codes_in(cells, pattern=CODE_TOKEN):
    out = set()
    for cell in cells:
        for tok in BACKTICK.findall(cell.replace("~~", "")):
            tok = tok.strip()
            if pattern.match(tok):
                out.add(tok)
    return out


# --- the registers, read out of the pages that hold them -----------------------

def read_registers(docs: pathlib.Path):
    reg = collections.defaultdict(set)

    catalog = docs / CATALOG_CODES
    if catalog.exists():
        for line in catalog.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = line.split("|")
            if len(cells) < 3:
                continue
            for tok in BACKTICK.findall(cells[1]):
                if CODE_TOKEN.match(tok.strip()):
                    reg["code"].add(tok.strip())

    catb = (docs / CATALOG_B).read_text(encoding="utf-8") if (docs / CATALOG_B).exists() else ""
    deferred = section(catb, "Deferred namespaces")
    if deferred:
        for line in deferred.splitlines():
            if not line.startswith("|"):
                continue
            cells = line.split("|")
            if len(cells) < 4:
                continue
            for tok in BACKTICK.findall(cells[2]):
                if CODE_TOKEN.match(tok.strip()):
                    reg["deferred"].add(tok.strip())
    # §9 declares a whole namespace absent by naming it in a heading.
    for m in re.finditer(r"^## \d+\.[^\n]*`([a-z_]+)\.\*`[^\n]*", catb, re.M):
        reg["absent-namespace"].add(m.group(1))

    dead = docs / REMOVED
    if dead.exists():
        reg["dead"] = codes_in(table_first_cells(dead.read_text(encoding="utf-8")))

    sel_page = (docs / SELECTORS_PAGE).read_text(encoding="utf-8") if (docs / SELECTORS_PAGE).exists() else ""
    registry_section = section(sel_page, "The selector registry")
    if registry_section:
        for cell in table_first_cells(registry_section):
            for tok in BACKTICK.findall(cell):
                tok = tok.strip()
                if OPERAND_TOKEN.match(tok) and tok not in OPERAND_STOPWORDS:
                    reg["selector"].add(tok)

    authz = (docs / AUTHZ_PAGE).read_text(encoding="utf-8") if (docs / AUTHZ_PAGE).exists() else ""
    scope_head = re.search(r"\*\*Fields\*\*\s*\(`grant_scope_type`\)", authz)
    if scope_head:
        for cell in table_first_cells(block_after(authz[scope_head.start():], SEEDED_ROWS)):
            for tok in BACKTICK.findall(cell):
                if WORD.match(tok.strip()):
                    reg["scope"].add(tok.strip())

    conv = (docs / CONVENTIONS).read_text(encoding="utf-8") if (docs / CONVENTIONS).exists() else ""
    label_block = re.search(r"^## 7a\..*?(?=^## |\Z)", conv, re.S | re.M)
    if label_block:
        reg["label"] = codes_in(table_first_cells(label_block.group(0)), LABEL_TOKEN)
    # What §11 *claims* is seeded, in its own words. A claim is a promise this
    # script can hold the corpus to only if it reads the promise from the page.
    seeded = SEEDED_BULLET.search(conv)
    if seeded:
        reg["claimed-vocabulary"] = {tok.strip() for tok in BACKTICK.findall(seeded.group(0))
                                     if WORD.match(tok.strip())}

    # Column names, so that `person.contact` is read as a column and not as a code.
    tables, columns, pairs = set(), set(), set()
    for f in md_files(docs):
        text = f.read_text(encoding="utf-8")
        for m in FIELDS_HEAD.finditer(text):
            table = m.group(1)
            if not WORD.match(table):
                continue
            tables.add(table)
            for cell in table_first_cells(next_label(text[m.end():])):
                for tok in BACKTICK.findall(cell):
                    tok = tok.strip().rstrip("*")
                    if WORD.match(tok):
                        columns.add(tok)
                        pairs.add(f"{table}.{tok}")
    return reg, (tables, columns, pairs)


# --- the check ----------------------------------------------------------------

Finding = collections.namedtuple("Finding", "kind token path note")


def scan(docs: pathlib.Path):
    reg, (tables, columns, pairs) = read_registers(docs)
    codes, deferred = reg["code"], reg["deferred"]
    selectors, labels, scopes = reg["selector"], reg["label"], reg["scope"]
    dead, absent = reg["dead"], reg["absent-namespace"]
    known = codes | deferred | dead
    actions = {c.rsplit(".", 1)[1] for c in codes}
    namespaces = {c.split(".", 1)[0] for c in codes}

    findings = []
    ignored = collections.Counter()
    mentions = collections.Counter()

    own_register = {"code": CATALOG_CODES, "selector": SELECTORS_PAGE, "label": CONVENTIONS}
    for kind, page in own_register.items():
        if not reg[kind]:
            findings.append(Finding("no-registry", kind, page, "the register did not parse"))
    for vocab in sorted(reg["claimed-vocabulary"]):
        key = VOCABULARY_REGISTER.get(vocab)
        if key is None or not reg.get(key):
            findings.append(Finding("no-registry", vocab, CONVENTIONS,
                                    "§10 calls it seeded; nothing in the corpus enumerates it"))

    for f in md_files(docs):
        rel = str(f.relative_to(docs))
        if rel == REMOVED:
            continue
        historic = is_history(rel)
        for lineno, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for raw in BACKTICK.findall(line):
                tok = raw.strip()

                if CODE_TOKEN.match(tok):
                    if tok in known:
                        if not historic and rel != own_register["code"]:
                            mentions[("code", tok)] += 1
                        continue
                    head, tail = tok.split(".", 1)[0], tok.rsplit(".", 1)[1]
                    if head in absent:
                        ignored[f"declared-absent {tok}"] += 1
                        continue
                    if tok in pairs or (tail in columns and (head in tables or head in columns)):
                        ignored[f"column {tok}"] += 1
                        continue
                    if tail in actions and head in namespaces:
                        kind = "code-shape"
                        note = "a catalog row is owed, or the prose names the wrong one"
                    elif tail in actions:
                        kind = "unknown-action"
                        note = f"act `{tail}` is registered, namespace `{head}` is not"
                    else:
                        ignored[f"unclassified {tok}"] += 1
                        continue
                    if not historic:
                        findings.append(Finding(kind, tok, f"{rel}:{lineno}", note))
                    continue

                if OPERAND_TOKEN.match(tok):
                    if tok in OPERAND_STOPWORDS:
                        continue
                    if tok in selectors:
                        if not historic:
                            mentions[("selector", tok)] += 1
                        continue
                    # An ALL-CAPS word is an operand only inside an expression.
                    spans = [s for s in BACKTICK.findall(line)
                             if re.search(rf"(^|\W){re.escape(tok)}(\W|$)", s)]
                    if not any(OPERAND_CONTEXT.search(s) for s in spans):
                        ignored[f"capitalised, not in an expression: {tok}"] += 1
                        continue
                    if not historic:
                        findings.append(Finding("selector", tok, f"{rel}:{lineno}",
                                                "spelled as an operand; not a seeded selector"))
                    continue

                if LABEL_TOKEN.match(tok):
                    head = tok.split(":", 1)[0]
                    if head in LABEL_SCHEMES:
                        continue
                    if any(tok == l for l in labels) or any(
                        l.endswith(":<id>") and tok.startswith(l.split(":")[0] + ":") for l in labels):
                        if not historic:
                            mentions[("label", tok)] += 1
                        continue
                    if not historic:
                        findings.append(Finding("label", tok, f"{rel}:{lineno}",
                                                "not on the vocabulary of 00-conventions §7a"))

    for kind in ("code", "selector", "label"):
        for row in sorted(reg[kind]):
            if mentions[(kind, row)] == 0:
                findings.append(Finding("unnamed-row", f"{kind}:{row}", "docs",
                                        "no page names this outside its own register"))

    return findings, ignored, reg


# --- the baseline -------------------------------------------------------------

def read_baseline(path: pathlib.Path):
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def fid(f: Finding) -> str:
    """A finding's identity, deliberately without a line number: moving a sentence
    must not re-open a finding that was read once."""
    return f"{f.kind} {f.token}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docs", default=None)
    ap.add_argument("--baseline", default=None)
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    root = pathlib.Path(__file__).resolve().parent.parent
    docs = pathlib.Path(args.docs) if args.docs else root / "docs"
    baseline_path = pathlib.Path(args.baseline) if args.baseline else root / BASELINE_DEFAULT

    findings, ignored, reg = scan(docs)
    print(f"registers: {len(reg['code'])} codes, {len(reg['deferred'])} deferred, "
          f"{len(reg['dead'])} dead names, {len(reg['selector'])} selectors, "
          f"{len(reg['scope'])} scope types, {len(reg['label'])} actor labels")

    if args.update_baseline:
        ids = sorted({fid(f) for f in findings})
        baseline_path.write_text(
            "# Every line here is a finding this repository has read and decided to keep.\n"
            "# Add to it in the round that decides, and say why after the `#`.\n"
            + "".join(f"{i}    # \n" for i in ids), encoding="utf-8")
        print(f"baseline rewritten: {len(ids)} findings")
        return 0

    baseline = read_baseline(baseline_path)
    fresh = sorted((f for f in findings if fid(f) not in baseline),
                   key=lambda f: (f.kind, f.token, f.path))
    waived = [f for f in findings if fid(f) in baseline]

    by_kind = collections.Counter(f.kind for f in findings)
    print("findings:   " + (", ".join(f"{k} {v}" for k, v in sorted(by_kind.items())) or "none"))
    print(f"read and kept: {len(waived)} in the baseline")
    print(f"outstanding:   {len(fresh)}")

    seen = set()
    for f in fresh:
        where = "" if fid(f) in seen else f"\n    at {f.path}"
        seen.add(fid(f))
        print(f"\n  {f.kind}  {f.token}{where}\n    {f.note}")

    if args.verbose:
        print("\nnot reported, by token:")
        for tok, n in ignored.most_common(50):
            print(f"  {n:>3}  {tok}")

    return 1 if fresh else 0


if __name__ == "__main__":
    sys.exit(main())
