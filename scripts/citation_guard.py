#!/usr/bin/env python3
"""Research and citation helper modeled on the Purdue OWL Research and Citation guides.

Subcommands
-----------
format  Build reference-list entries and in-text citations for APA 7, MLA 9,
        Chicago 18 (notes-bibliography and author-date), IEEE, AMA 11, and ASA 7.
check   Audit a draft for citation integrity: uncited quotations, unsupported
        statistics, mixed citation systems, missing or mismatched reference
        lists, orphan citations, placeholder citations, and (with --source)
        unquoted copying / patchwriting against an original source text.
styles  Print the supported styles and their core conventions.

Standard library only (Python 3.10+).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STYLES: dict[str, dict] = {
    "apa": {
        "name": "APA 7th edition", "fields": "Psychology, education, social sciences",
        "in_text": "(Smith, 2020, p. 4)", "family": "author-date-comma",
        "heading": "References", "order": "alpha", "block_quote_words": 40,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/apa_style/index.html",
    },
    "mla": {
        "name": "MLA 9th edition", "fields": "Literature, languages, humanities",
        "in_text": "(Smith 4)", "family": "author-page",
        "heading": "Works Cited", "order": "alpha", "block_quote_words": 50,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/mla_style/index.html",
    },
    "chicago-nb": {
        "name": "Chicago 18th edition, notes and bibliography", "fields": "History, arts, humanities",
        "in_text": "footnote marker [^1] or superscript 1", "family": "notes",
        "heading": "Bibliography", "order": "alpha", "block_quote_words": 100,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/chicago_manual_18th_edition/index.html",
    },
    "chicago-ad": {
        "name": "Chicago 18th edition, author-date", "fields": "Natural and social sciences",
        "in_text": "(Smith 2020, 4)", "family": "author-date",
        "heading": "References", "order": "alpha", "block_quote_words": 100,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/chicago_manual_18th_edition/index.html",
    },
    "ieee": {
        "name": "IEEE", "fields": "Engineering, computer science",
        "in_text": "[1]", "family": "numeric",
        "heading": "References", "order": "cited", "block_quote_words": 40,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/ieee_style/index.html",
    },
    "ama": {
        "name": "AMA 11th edition", "fields": "Medicine, health sciences",
        "in_text": "superscript number after the cited text", "family": "notes",
        "heading": "References", "order": "cited", "block_quote_words": 50,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/ama_style/index.html",
    },
    "asa": {
        "name": "ASA 7th edition", "fields": "Sociology",
        "in_text": "(Smith 2020:4)", "family": "author-date",
        "heading": "References", "order": "alpha", "block_quote_words": 50,
        "owl": "https://owl.purdue.edu/owl/research_and_citation/asa_style/index.html",
    },
}

STYLE_ALIASES = {
    "apa7": "apa", "mla9": "mla", "chicago": "chicago-nb", "cmos": "chicago-nb",
    "chicago-notes": "chicago-nb", "turabian": "chicago-nb", "chicago-author-date": "chicago-ad",
    "ama11": "ama", "asa7": "asa",
}

FAMILY_LABELS = {
    "author-date-comma": "author-date with comma (APA)",
    "author-date": "author-date without comma (Chicago author-date / ASA)",
    "author-page": "author-page (MLA)",
    "numeric": "bracketed numbers (IEEE)",
    "notes": "superscript or footnote markers (AMA / Chicago notes)",
}

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MLA_MONTHS = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.",
              "Sept.", "Oct.", "Nov.", "Dec."]
IEEE_MONTHS = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.",
               "Sept.", "Oct.", "Nov.", "Dec."]
MINOR_WORDS = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at",
    "by", "in", "of", "off", "on", "per", "to", "up", "via", "from", "into", "with",
}
SUPERSCRIPTS = str.maketrans("0123456789", "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079")
UNSUPERSCRIPTS = str.maketrans("\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079", "0123456789")


def resolve_style(style: str | None) -> str | None:
    if not style:
        return None
    key = STYLE_ALIASES.get(style.strip().lower(), style.strip().lower())
    if key not in STYLES:
        raise ValueError(f"Unknown style '{style}'. Choose from: {', '.join(STYLES)}")
    return key


# ----------------------------------------------------------------- helpers

def end(text: str, punct: str = ".") -> str:
    """Add closing punctuation unless the text (ignoring markdown *) already ends with it."""
    text = (text or "").rstrip()
    if not text:
        return text
    core = text.rstrip("*")
    return text if core and core[-1] in ".?!" else text + punct


def ital(text: str, md: bool) -> str:
    text = (text or "").strip()
    return f"*{text}*" if (md and text) else text


def pages_fmt(pages, dash: str = "\u2013") -> str:
    return re.sub(r"\s*[-\u2013\u2014]+\s*", dash, str(pages).strip())


def is_range(pages) -> bool:
    return bool(re.search(r"[-\u2013\u2014,]", str(pages)))


def bare_doi(doi: str) -> str:
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi.strip(), flags=re.I)


def doi_url(doi: str) -> str:
    return f"https://doi.org/{bare_doi(doi)}"


def strip_protocol(url: str) -> str:
    return re.sub(r"^https?://", "", url.strip())


def ordinal(value) -> str:
    text = str(value).strip()
    if not text.isdigit():
        return text
    n = int(text)
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def title_case(title: str) -> str:
    """Headline-style capitalization for MLA, Chicago, and ASA. Words with capitals are kept."""
    words = title.split(" ")
    out, after_colon = [], True
    for i, word in enumerate(words):
        bare = re.sub(r"^\W+|\W+$", "", word)
        last = i == len(words) - 1
        if bare and bare.lower() == bare and (after_colon or last or bare not in MINOR_WORDS):
            idx = word.find(bare[0])
            word = word[:idx] + word[idx].upper() + word[idx + 1:]
        out.append(word)
        after_colon = word.endswith((":", "?", "!"))
    return " ".join(out)


def short_title(title: str, max_words: int = 4) -> str:
    main = re.split(r"[:?!]", title, maxsplit=1)[0].strip()
    words = main.split()
    return " ".join(words[:max_words]) if len(words) > max_words else main


def month_index(month) -> int | None:
    if month in (None, ""):
        return None
    text = str(month).strip()
    if text.isdigit():
        return int(text) if 1 <= int(text) <= 12 else None
    for i, name in enumerate(MONTHS):
        if name.lower().startswith(text.lower()[:3]):
            return i + 1
    return None


def parse_iso(date) -> tuple:
    m = re.match(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?$", str(date or "").strip())
    if not m:
        return None, None, None
    return m.group(1), (int(m.group(2)) if m.group(2) else None), (int(m.group(3)) if m.group(3) else None)


def long_date(year, month, day) -> str:
    if not year:
        return ""
    if month and day:
        return f"{MONTHS[month - 1]} {day}, {year}"
    return f"{MONTHS[month - 1]} {year}" if month else str(year)


# ----------------------------------------------------------------- source model

def parse_author(raw) -> dict:
    if isinstance(raw, dict):
        if raw.get("literal"):
            return {"literal": str(raw["literal"]).strip()}
        return {"family": str(raw.get("family", "")).strip(), "given": str(raw.get("given", "")).strip()}
    text = str(raw).strip()
    if "," in text:
        fam, giv = text.split(",", 1)
        return {"family": fam.strip(), "given": giv.strip()}
    parts = text.split()
    if len(parts) == 1:
        return {"literal": text}
    return {"family": parts[-1], "given": " ".join(parts[:-1])}


def normalize_source(src: dict) -> tuple[dict, list[str]]:
    s = dict(src)
    s["_authors"] = [parse_author(a) for a in (s.get("authors") or [])]
    if s.get("organization") and not s["_authors"]:
        s["_authors"] = [{"literal": s["organization"]}]
    typ = (s.get("type") or "").lower()
    if typ not in {"journal", "book", "web"}:
        if s.get("volume") or s.get("issue") or (s.get("doi") and s.get("container")):
            typ = "journal"
        elif s.get("publisher") and not s.get("url"):
            typ = "book"
        else:
            typ = "web"
    s["type"] = typ
    s["_month"] = month_index(s.get("month"))
    s["_day"] = int(s["day"]) if str(s.get("day", "")).strip().isdigit() else None
    s["_accessed"] = parse_iso(s.get("accessed"))

    warnings = []
    if not s.get("title"):
        warnings.append("missing title")
    if not s["_authors"]:
        warnings.append("no author: entry will start with the title")
    if not s.get("year"):
        warnings.append("missing year: 'n.d.' will be used where the style allows it")
    if typ == "journal" and not s.get("container"):
        warnings.append("journal article without journal name ('container')")
    if typ == "book" and not s.get("publisher"):
        warnings.append("book without publisher")
    if typ == "web" and not s.get("url"):
        warnings.append("web source without URL")
    return s, warnings


def family(a: dict) -> str:
    return a.get("literal") or a.get("family", "")


def inverted(a: dict) -> str:
    if a.get("literal"):
        return a["literal"]
    return f"{a['family']}, {a['given']}" if a.get("given") else a["family"]


def natural(a: dict) -> str:
    if a.get("literal"):
        return a["literal"]
    return f"{a['given']} {a['family']}".strip()


def initials(given: str, dots: bool = True) -> str:
    out = []
    for part in given.replace(".", " ").split():
        pieces = [p for p in part.split("-") if p]
        marks = [p[0].upper() + ("." if dots else "") for p in pieces]
        out.append("-".join(marks))
    return " ".join(out) if dots else "".join(out)


def link_for(s: dict) -> str:
    if s.get("doi"):
        return doi_url(s["doi"])
    return s.get("url", "") or ""


# ----------------------------------------------------------------- formatters

def apa_name(a: dict) -> str:
    if a.get("literal"):
        return a["literal"]
    return f"{a['family']}, {initials(a['given'])}" if a.get("given") else a["family"]


def apa_authors(auths: list[dict]) -> str:
    names = [apa_name(a) for a in auths]
    if len(names) == 1:
        return names[0]
    if len(names) <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:19]) + ", . . . " + names[-1]


def fmt_apa(s: dict, md: bool) -> str:
    auths, title, typ = s["_authors"], (s.get("title") or "").strip(), s["type"]
    year = s.get("year") or "n.d."
    date = str(year)
    if typ == "web" and s["_month"] and s.get("year"):
        date += f", {MONTHS[s['_month'] - 1]}" + (f" {s['_day']}" if s["_day"] else "")
    src_part = ""
    if typ == "journal":
        title_part = end(title)
        src_part = ital(s.get("container", ""), md)
        if s.get("volume"):
            src_part += ", " + ital(str(s["volume"]), md) + (f"({s['issue']})" if s.get("issue") else "")
        if s.get("pages"):
            src_part += ", " + pages_fmt(s["pages"])
        elif s.get("article"):
            src_part += f", Article {s['article']}"
        src_part = end(src_part)
    elif typ == "book":
        t = ital(title, md) + (f" ({ordinal(s['edition'])} ed.)" if s.get("edition") else "")
        title_part = end(t)
        src_part = end(s.get("publisher", "")) if s.get("publisher") else ""
    else:
        title_part = end(ital(title, md))
        site = s.get("container", "")
        if site and not (auths and auths[0].get("literal") == site):
            src_part = end(site)
    parts = [end(apa_authors(auths)) + f" ({date}).", title_part] if auths else [title_part, f"({date})."]
    parts += [src_part, link_for(s)]
    return " ".join(p for p in parts if p)


def mla_authors(auths: list[dict]) -> str:
    if not auths:
        return ""
    first = inverted(auths[0])
    if len(auths) == 1:
        return first
    if len(auths) == 2:
        return f"{first}, and {natural(auths[1])}"
    return f"{first}, et al."


def mla_date(s: dict) -> str:
    if not s.get("year"):
        return ""
    if s["_month"]:
        d = f"{s['_day']} " if s["_day"] else ""
        return f"{d}{MLA_MONTHS[s['_month'] - 1]} {s['year']}"
    return str(s["year"])


def fmt_mla(s: dict, md: bool) -> str:
    auths, typ = s["_authors"], s["type"]
    title = title_case((s.get("title") or "").strip())
    head = end(mla_authors(auths)) if auths else ""
    link = doi_url(s["doi"]) if s.get("doi") else (strip_protocol(s["url"]) if s.get("url") else "")
    if typ == "journal":
        elems = [ital(title_case(s.get("container", "")), md)]
        if s.get("volume"):
            elems.append(f"vol. {s['volume']}")
        if s.get("issue"):
            elems.append(f"no. {s['issue']}")
        elems.append(mla_date(s))
        if s.get("pages"):
            elems.append(("pp. " if is_range(s["pages"]) else "p. ") + pages_fmt(s["pages"], "-"))
        elems.append(link)
        body = f'"{end(title)}" ' + end(", ".join(e for e in elems if e))
    elif typ == "book":
        elems = [f"{ordinal(s['edition'])} ed." if s.get("edition") else "", s.get("publisher", ""), str(s.get("year", ""))]
        body = end(ital(title, md)) + " " + end(", ".join(e for e in elems if e))
    else:
        elems = [ital(s.get("container", ""), md), mla_date(s), link]
        body = f'"{end(title)}" ' + end(", ".join(e for e in elems if e))
        y, m, d = s["_accessed"]
        if not s.get("year") and y:
            acc = " ".join(x for x in [str(d) if d else "", MLA_MONTHS[m - 1] if m else "", y] if x)
            body += f" Accessed {acc}."
    return " ".join(p for p in [head, body] if p)


def chicago_names(auths: list[dict], max_all: int = 6) -> str:
    if not auths:
        return ""
    names = [inverted(auths[0])] + [natural(a) for a in auths[1:]]
    if len(names) > max_all:
        return f"{names[0]}, {names[1]}, {names[2]}, et al."
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + ", and " + names[-1]


def fmt_chicago_nb(s: dict, md: bool) -> str:
    auths, typ = s["_authors"], s["type"]
    title = title_case((s.get("title") or "").strip())
    head = end(chicago_names(auths)) if auths else ""
    link = end(link_for(s)) if link_for(s) else ""
    if typ == "journal":
        core = ital(title_case(s.get("container", "")), md)
        if s.get("volume"):
            core += f" {s['volume']}"
        if s.get("issue"):
            core += f", no. {s['issue']}"
        core += f" ({long_date(s.get('year'), s['_month'], None) or 'n.d.'})"
        if s.get("pages"):
            core += f": {pages_fmt(s['pages'])}"
        body = f'"{end(title)}" {end(core)}'
    elif typ == "book":
        ed = f"{ordinal(s['edition'])} ed. " if s.get("edition") else ""
        pub = ", ".join(x for x in [s.get("publisher", ""), str(s.get("year") or "n.d.")] if x)
        body = f"{end(ital(title, md))} {ed}{end(pub)}"
    else:
        site = end(s.get("container", "")) + " " if s.get("container") else ""
        date = long_date(s.get("year"), s["_month"], s["_day"])
        if not date:
            y, m, d = s["_accessed"]
            date = f"Accessed {long_date(y, m, d)}" if y else ""
        body = f'"{end(title)}" {site}{end(date) if date else ""}'.rstrip()
    return " ".join(p for p in [head, body, link] if p)


def fmt_chicago_ad(s: dict, md: bool) -> str:
    auths, typ = s["_authors"], s["type"]
    title = title_case((s.get("title") or "").strip())
    year = s.get("year") or "n.d."
    link = end(link_for(s)) if link_for(s) else ""
    head = f"{end(chicago_names(auths))} {year}." if auths else ""
    if typ == "journal":
        core = ital(title_case(s.get("container", "")), md)
        if s.get("volume"):
            core += f" {s['volume']}"
        if s.get("issue"):
            core += f" ({s['issue']})"
        if s.get("pages"):
            core += f": {pages_fmt(s['pages'])}"
        body = f'"{end(title)}" {end(core)}'
    elif typ == "book":
        ed = f"{ordinal(s['edition'])} ed. " if s.get("edition") else ""
        body = f"{end(ital(title, md))} {ed}{end(s.get('publisher', ''))}".rstrip()
    else:
        tail = ", ".join(x for x in [s.get("container", ""), long_date(s.get("year"), s["_month"], s["_day"])] if x)
        body = f'"{end(title)}" {end(tail)}'.rstrip()
    if not auths:
        body = f"{body} {year}." if typ != "web" else body
    return " ".join(p for p in [head, body, link] if p)


def ieee_name(a: dict) -> str:
    if a.get("literal"):
        return a["literal"]
    return f"{initials(a['given'])} {a['family']}".strip() if a.get("given") else a["family"]


def ieee_authors(auths: list[dict]) -> str:
    names = [ieee_name(a) for a in auths]
    if not names:
        return ""
    if len(names) > 6:
        return f"{names[0]} et al."
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def fmt_ieee(s: dict, md: bool) -> str:
    auths, typ = s["_authors"], s["type"]
    title = (s.get("title") or "").strip().rstrip(".")
    who = ieee_authors(auths)
    lead = f"{who}, " if who else ""
    if typ == "journal":
        parts = [f'{lead}"{title}," {ital(s.get("container", ""), md)}']
        if s.get("volume"):
            parts.append(f"vol. {s['volume']}")
        if s.get("issue"):
            parts.append(f"no. {s['issue']}")
        if s.get("pages"):
            parts.append(("pp. " if is_range(s["pages"]) else "p. ") + pages_fmt(s["pages"]))
        date = (f"{IEEE_MONTHS[s['_month'] - 1]} " if s["_month"] else "") + str(s.get("year", ""))
        if date.strip():
            parts.append(date.strip())
        text = ", ".join(parts)
        return f"{text}, doi: {bare_doi(s['doi'])}." if s.get("doi") else end(text)
    if typ == "book":
        ed = f", {ordinal(s['edition'])} ed." if s.get("edition") else "."
        place = f"{s['city']}: " if s.get("city") else ""
        return f"{lead}{ital(title, md)}{ed} {place}{s.get('publisher', '')}, {s.get('year', 'n.d.')}."
    text = f'{lead}"{title},"'
    if s.get("container"):
        text += f" {end(s['container'])}"
    y, m, d = s["_accessed"]
    if y:
        acc = (f"{IEEE_MONTHS[m - 1]} " if m else "") + (f"{d}, " if d else "") + y
        text += f" Accessed: {acc}."
    if s.get("url"):
        text += f" [Online]. Available: {s['url']}"
    return text


def ama_authors(auths: list[dict]) -> str:
    names = []
    for a in auths:
        names.append(a["literal"] if a.get("literal") else
                     (f"{a['family']} {initials(a['given'], dots=False)}" if a.get("given") else a["family"]))
    if len(names) > 6:
        return ", ".join(names[:3]) + ", et al"
    return ", ".join(names)


def fmt_ama(s: dict, md: bool) -> str:
    auths, typ = s["_authors"], s["type"]
    title = (s.get("title") or "").strip()
    head = end(ama_authors(auths)) if auths else ""
    if typ == "journal":
        data = str(s.get("year", ""))
        if s.get("volume"):
            data += f";{s['volume']}"
        if s.get("issue"):
            data += f"({s['issue']})"
        if s.get("pages"):
            data += f":{pages_fmt(s['pages'], '-')}"
        body = f"{end(title)} {end(ital(s.get('container', ''), md))} {end(data)}"
        if s.get("doi"):
            body += f" doi:{bare_doi(s['doi'])}"
    elif typ == "book":
        ed = f"{ordinal(s['edition'])} ed. " if s.get("edition") else ""
        body = f"{end(ital(title, md))} {ed}{s.get('publisher', '')}; {s.get('year', '')}."
    else:
        body = end(title)
        if s.get("container"):
            body += f" {end(s['container'])}"
        pub = long_date(s.get("year"), s["_month"], s["_day"])
        if pub:
            body += f" Published {pub}."
        y, m, d = s["_accessed"]
        if y:
            body += f" Accessed {long_date(y, m, d)}."
        if s.get("url"):
            body += f" {s['url']}"
    return " ".join(p for p in [head, body] if p)


def asa_authors(auths: list[dict]) -> str:
    if not auths:
        return ""
    names = [inverted(auths[0])] + [natural(a) for a in auths[1:]]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + ", and " + names[-1]


def fmt_asa(s: dict, md: bool) -> str:
    auths, typ = s["_authors"], s["type"]
    title = title_case((s.get("title") or "").strip())
    year = s.get("year") or "n.d."
    head = f"{end(asa_authors(auths))} {year}." if auths else ""
    if typ == "journal":
        core = ital(title_case(s.get("container", "")), md)
        if s.get("volume"):
            core += f" {s['volume']}"
        if s.get("issue"):
            core += f"({s['issue']})"
        if s.get("pages"):
            core += f":{pages_fmt(s['pages'])}"
        body = f'"{end(title)}" {end(core)}'
        if s.get("doi"):
            body += f" {doi_url(s['doi'])}."
    elif typ == "book":
        place = f"{s['city']}: " if s.get("city") else ""
        body = f"{end(ital(title, md))} {place}{end(s.get('publisher', ''))}".rstrip()
    else:
        body = f'"{end(title)}"'
        if s.get("container"):
            body += f" {end(s['container'])}"
        y, m, d = s["_accessed"]
        if y and s.get("url"):
            body += f" Retrieved {long_date(y, m, d)} ({s['url']})."
        elif s.get("url"):
            body += f" {s['url']}."
    if not auths:
        body = f"{body} {year}." if typ != "web" else body
    return " ".join(p for p in [head, body] if p)


FORMATTERS = {
    "apa": fmt_apa, "mla": fmt_mla, "chicago-nb": fmt_chicago_nb, "chicago-ad": fmt_chicago_ad,
    "ieee": fmt_ieee, "ama": fmt_ama, "asa": fmt_asa,
}


def in_text(s: dict, style: str, page=None, index: int | None = None, narrative: bool = False, md: bool = True) -> str:
    """Return an in-text citation (or short note for Chicago notes-bibliography)."""
    fams = [family(a) for a in s["_authors"]]
    year = str(s.get("year") or "n.d.")
    title = (s.get("title") or "").strip()
    st = short_title(title_case(title) if style != "apa" else title)
    no_author = f'"{st}"' if s["type"] != "book" else ital(st, md)

    if style == "ieee":
        return f"[{index or 1}]"
    if style == "ama":
        return str(index or 1).translate(SUPERSCRIPTS)

    def who(conj: str, et_al_from: int = 3) -> str:
        if not fams:
            return no_author
        if len(fams) >= et_al_from:
            return f"{fams[0]} et al."
        if len(fams) == 2:
            return f"{fams[0]} {conj} {fams[1]}"
        if len(fams) == 3:
            return f"{fams[0]}, {fams[1]}, and {fams[2]}"
        return fams[0]

    if style == "apa":
        loc = f", {'pp.' if is_range(page) else 'p.'} {pages_fmt(page)}" if page else ""
        return f"{who('and')} ({year}{loc})" if narrative else f"({who('&')}, {year}{loc})"
    if style == "mla":
        loc = f" {pages_fmt(page, '-')}" if page else ""
        if narrative:
            return f"{who('and')} ({pages_fmt(page, '-')})" if page else who("and")
        return f"({who('and')}{loc})"
    if style == "chicago-ad":
        loc = f", {pages_fmt(page)}" if page else ""
        return f"{who('and')} ({year}{loc})" if narrative else f"({who('and')} {year}{loc})"
    if style == "asa":
        loc = f":{pages_fmt(page)}" if page else ""
        name = who("and", et_al_from=4)
        return f"{name} ({year}{loc})" if narrative else f"({name} {year}{loc})"
    st_fmt = ital(st, md) if s["type"] == "book" else f'"{st}"'
    parts = [who("and")] if fams else []
    parts.append(st_fmt)
    if page:
        parts.append(pages_fmt(page))
    return end(", ".join(parts))


def sort_key(s: dict) -> str:
    auths = s["_authors"]
    key = family(auths[0]) if auths else re.sub(r"^(?:the|a|an)\s+", "", (s.get("title") or ""), flags=re.I)
    return key.lower()


def build_bibliography(sources: list[dict], style: str, md: bool = True, page=None) -> dict:
    normalized = [normalize_source(src) for src in sources]
    if STYLES[style]["order"] == "alpha":
        normalized.sort(key=lambda pair: sort_key(pair[0]))
    entries = []
    for i, (s, warns) in enumerate(normalized, start=1):
        text = FORMATTERS[style](s, md)
        if style == "ieee":
            text = f"[{i}] {text}"
        elif style == "ama":
            text = f"{i}. {text}"
        entries.append({
            "reference": text,
            "in_text": in_text(s, style, page=page, index=i, md=md),
            "narrative": in_text(s, style, page=page, index=i, narrative=True, md=md)
            if style not in {"ieee", "ama", "chicago-nb"} else None,
            "warnings": warns,
        })
    return {"style": style, "style_name": STYLES[style]["name"], "heading": STYLES[style]["heading"], "entries": entries}


# ----------------------------------------------------------------- integrity checker

NAME = r"[A-Z][A-Za-z'\u2019\-]+"
YEAR = r"(?:1[5-9]\d\d|20\d\d)[a-z]?|n\.d\."
REF_HEADING = re.compile(
    r"^[ \t]{0,3}(?:#{1,6}[ \t]*)?(?:\*\*)?(references|reference list|works cited|works consulted|bibliography|sources|notes)"
    r"(?:\*\*)?[ \t]*:?[ \t]*$", re.I | re.M)
PAREN = re.compile(r"\(([^()]{2,200})\)")
PREFIX = r"(?:(?:e\.g\.,?|see(?:\s+also)?|cf\.)\s+)?"
APA_ITEM = re.compile(
    rf"^{PREFIX}({NAME}(?:(?:,\s*{NAME})*,?\s+(?:&|and)\s+{NAME}|\s+et\s+al\.?)?),\s+({YEAR})"
    r"(?:,\s*(?:pp?\.|para\.|chap\.|sec\.)\s*[\w\-\u2013]+)?$")
AD_ITEM = re.compile(
    rf"^{PREFIX}({NAME}(?:(?:,\s*{NAME})*,?\s+and\s+{NAME}|\s+et\s+al\.?)?)\s+({YEAR})"
    r"(?:(?:,\s*|:)[\d\-\u2013]+)?$")
MLA_ITEM = re.compile(rf"^{PREFIX}({NAME}(?:\s+and\s+{NAME}|\s+et\s+al\.?)?)\s+(\d{{1,4}}(?:[\-\u2013]\d+)?)$")
LOCATOR_ONLY = re.compile(r"\((?:(?:pp?\.|para\.)\s*)?\d{1,4}(?:[\-\u2013]\d+)?\)")
NARRATIVE = re.compile(
    rf"\b({NAME}(?:\s+(?:and|&)\s+{NAME}|\s+et\s+al\.)?)\s+\(({YEAR})(?:(?:,\s*(?:pp?\.)?\s*|:)[\d\-\u2013]+)?\)")
NUMERIC = re.compile(r"\[(\d{1,3}(?:\s*[\-\u2013,]\s*\d{1,3})*)\](?!\()")
SUPER = re.compile(r"(?<=[A-Za-z.,;:!?\"')\]])([\u00b9\u00b2\u00b3\u2070\u2074-\u2079]+|<sup>\s*[\d,\-\u2013 ]+\s*</sup>)")
FOOTNOTE_REF = re.compile(r"\[\^([\w\-]+)\](?!:)")
FOOTNOTE_DEF = re.compile(r"^\[\^([\w\-]+)\]:", re.M)
QUOTE = re.compile(r'"([^"\n]{1,1500})"|\u201c([^\u201d]{1,1500})\u201d')
PLACEHOLDER = re.compile(
    r"\[(?:citation needed|citation|source|ref|cite|\?+)\]|\((?:Author|Source|Citation),?\s*(?:Year|n\.d\.|20XX)?\)"
    r"|\b(?:Author|Smith),?\s+20[Xx]{2}\b|\[CITATION[^\]]*\]|\bINSERT[_ ](?:CITATION|SOURCE|REFERENCE)\b", re.I)
STAT = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:%|percent\b|per\s+cent\b)"
    r"|\b\d[\d,]*(?:\.\d+)?\s+(?:million|billion|trillion)\b"
    r"|\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:in|out\s+of)\s+(?:\d+|ten|five|four|three|a\s+hundred)\b"
    r"|\b(?:doubled|tripled|quadrupled|halved)\b", re.I)
OWN_DATA = re.compile(
    r"\b(?:Table|Figure|Fig\.)\s*\d|\b(?:we|our)\s+(?:found|measured|observed|recorded|surveyed|results|data|sample|survey)\b"
    r"|\bin\s+this\s+(?:study|survey|experiment|sample)\b", re.I)
ABBREVIATIONS = re.compile(r"\b(?:et al|e\.g|i\.e|Dr|Mr|Mrs|Ms|Prof|vs|cf|Fig|No|Vol|pp|p|ed|eds)\.")
SEVERITY_POINTS = {"high": 15, "medium": 8, "low": 3}


def _split_body_refs(text: str) -> tuple[str, str, str | None]:
    first = REF_HEADING.search(text)
    if not first:
        return text, "", None
    last = first
    for last in REF_HEADING.finditer(text):
        pass
    return text[:first.start()], text[first.end():], last.group(1)


def _expand_numbers(spec: str) -> list[int]:
    nums = []
    for part in re.split(r"\s*,\s*", spec.strip()):
        rng = re.split(r"\s*[\-\u2013]\s*", part)
        if len(rng) == 2 and rng[0].isdigit() and rng[1].isdigit() and int(rng[1]) >= int(rng[0]):
            nums.extend(range(int(rng[0]), int(rng[1]) + 1))
        elif part.isdigit():
            nums.append(int(part))
    return nums


def _surnames(group: str) -> list[str]:
    group = re.sub(r"\s+et\s+al\.?", "", group)
    return [n for n in re.findall(NAME, group) if n not in {"See", "Cf"}]


def find_citations(body: str) -> list[dict]:
    cites: list[dict] = []
    for m in PAREN.finditer(body):
        for item in m.group(1).split(";"):
            item = item.strip()
            for fam, rx in (("author-date-comma", APA_ITEM), ("author-date", AD_ITEM), ("author-page", MLA_ITEM)):
                im = rx.match(item)
                if im:
                    if fam == "author-page" and re.fullmatch(YEAR, im.group(2)):
                        continue
                    cites.append({"family": fam, "raw": f"({item})", "surnames": _surnames(im.group(1)),
                                  "start": m.start(), "end": m.end()})
                    break
    for m in NARRATIVE.finditer(body):
        cites.append({"family": "narrative", "raw": m.group(0), "surnames": _surnames(m.group(1)),
                      "start": m.start(), "end": m.end()})
    for m in NUMERIC.finditer(body):
        cites.append({"family": "numeric", "raw": m.group(0), "numbers": _expand_numbers(m.group(1)),
                      "start": m.start(), "end": m.end()})
    for m in SUPER.finditer(body):
        raw = m.group(1)
        digits = re.sub(r"</?sup>", "", raw).translate(UNSUPERSCRIPTS)
        cites.append({"family": "notes", "raw": raw, "numbers": _expand_numbers(digits.replace(" ", "")),
                      "start": m.start(), "end": m.end()})
    for m in FOOTNOTE_REF.finditer(body):
        cites.append({"family": "notes", "raw": m.group(0), "footnote": m.group(1),
                      "start": m.start(), "end": m.end()})
    for m in LOCATOR_ONLY.finditer(body):
        cites.append({"family": "locator", "raw": m.group(0), "start": m.start(), "end": m.end()})
    cites.sort(key=lambda c: c["start"])
    return cites


def _sentences(body: str) -> list[tuple[int, int, str]]:
    protected = ABBREVIATIONS.sub(lambda m: m.group(0)[:-1] + "\u2024", body)
    spans, start = [], 0
    for m in re.finditer(r"(?<=[.!?])[\"'\u201d)\]]*\s+(?=[A-Z\"\u201c(\[])|\n\s*\n", protected):
        spans.append((start, m.start()))
        start = m.end()
    spans.append((start, len(body)))
    return [(a, b, body[a:b]) for a, b in spans if body[a:b].strip()]


def _has_cite(cites: list[dict], lo: int, hi: int) -> bool:
    return any(lo <= c["start"] <= hi for c in cites)


def _ref_entries(refs: str) -> list[dict]:
    entries = []
    for line in refs.splitlines():
        raw = line.strip()
        if not raw or REF_HEADING.match(raw):
            continue
        num = None
        m = re.match(r"^(?:[-*]\s+)?(?:\[(\d+)\]|(\d+)\.)\s*", raw)
        if m:
            num = int(m.group(1) or m.group(2))
            raw = raw[m.end():]
        raw = re.sub(r"^[-*]\s+", "", raw)
        first = re.match(NAME, raw)
        entries.append({"number": num, "surname": first.group(0) if first else None, "text": raw})
    return entries


def _tokens(text: str) -> list[tuple[str, int, int]]:
    return [(m.group(0).lower(), m.start(), m.end()) for m in re.finditer(r"[A-Za-z0-9']+", text)]


def patchwriting(draft: str, source: str, n: int = 6) -> dict:
    """Detect unquoted n-gram overlap (copied or lightly edited spans) against a source text."""
    quoted = [(m.start(), m.end()) for m in QUOTE.finditer(draft)]
    quoted += [(m.start(), m.end()) for m in re.finditer(r"(?m)^>.*$", draft)]
    dtoks = _tokens(draft)
    stoks = [t for t, _, _ in _tokens(source)]
    if len(dtoks) < n or len(stoks) < n:
        return {"overlap_pct": 0.0, "spans": []}
    sgrams = {tuple(stoks[i:i + n]) for i in range(len(stoks) - n + 1)}
    hit_ranges: list[tuple[int, int]] = []
    matched_idx: set[int] = set()
    for i in range(len(dtoks) - n + 1):
        gram = tuple(dtoks[j][0] for j in range(i, i + n))
        if gram not in sgrams:
            continue
        lo, hi = dtoks[i][1], dtoks[i + n - 1][2]
        if any(ql <= lo and hi <= qr for ql, qr in quoted):
            continue
        matched_idx.update(range(i, i + n))
        if hit_ranges and lo <= hit_ranges[-1][1] + 25:
            hit_ranges[-1] = (hit_ranges[-1][0], hi)
        else:
            hit_ranges.append((lo, hi))
    spans = [re.sub(r"\s+", " ", draft[lo:hi].strip()) for lo, hi in hit_ranges[:10]]
    pct = round(100 * len(matched_idx) / len(dtoks), 1)
    return {"overlap_pct": pct, "spans": spans}


def check_text(text: str, style: str | None = None, source_text: str | None = None) -> dict:
    style = resolve_style(style)
    body, refs_raw, heading = _split_body_refs(text)
    cites = find_citations(body)
    sentences = _sentences(body)
    findings: list[dict] = []

    def add(code: str, severity: str, message: str, hits: list[str]) -> None:
        if hits:
            findings.append({"code": code, "severity": severity, "message": message, "hits": hits[:10]})

    # 1. Placeholder citations
    add("placeholder_citation", "high",
        "Placeholder or unfinished citation marker found",
        [m.group(0) for m in PLACEHOLDER.finditer(text)])

    # 2. Uncited direct quotations + block quote formatting hints
    uncited_q, long_inline_q = [], []
    block_limit = STYLES[style]["block_quote_words"] if style else 40
    for m in QUOTE.finditer(body):
        qtext = (m.group(1) or m.group(2) or "").strip()
        words = qtext.split()
        if len(words) < 5:  # skip scare quotes around single terms
            continue
        if len(words) >= block_limit:
            long_inline_q.append(f"{len(words)}w quote starting '{' '.join(words[:5])}...'")
        sent = next(((a, b) for a, b, _ in sentences if a <= m.start() <= b), (m.start(), m.end()))
        if not _has_cite(cites, sent[0], min(len(body), sent[1] + 15)):
            uncited_q.append(f'"{" ".join(words[:7])}..."')
    add("uncited_quote", "high", "Direct quotation without an in-text citation in the same sentence", uncited_q)
    add("block_quote_length", "low",
        f"Inline quotation is {block_limit}+ words; consider formatting as an indented block quote", long_inline_q)

    # 3. Statistics without nearby citation
    uncited_stats = []
    for a, b, s in sentences:
        s_clean = re.sub(r"https?://\S+", "", s)
        if STAT.search(s_clean) and not OWN_DATA.search(s_clean) and not _has_cite(cites, a, min(len(body), b + 1)):
            uncited_stats.append(re.sub(r"\s+", " ", s.strip())[:110])
    add("unsupported_statistic", "medium",
        "Statistic or quantitative claim without a source citation", uncited_stats)

    # 4. Mixed citation systems or mismatch with --style
    fams = {c["family"] for c in cites if c["family"] not in {"narrative", "locator"}}
    if len(fams) > 1:
        add("mixed_citation_styles", "high",
            "Draft mixes multiple in-text citation systems",
            [FAMILY_LABELS.get(f, f) for f in sorted(fams)])
    if style and fams:
        expected = STYLES[style]["family"]
        wrong = [FAMILY_LABELS.get(f, f) for f in sorted(fams) if f != expected]
        add("style_mismatch", "medium",
            f"In-text citations do not match {STYLES[style]['name']} ({STYLES[style]['in_text']})", wrong)

    # 5. Reference list presence, heading, order, and cross-check
    entries = _ref_entries(refs_raw)
    fn_defs = set(FOOTNOTE_DEF.findall(text))
    if cites and not entries and not fn_defs:
        add("missing_reference_list", "high",
            "Draft has in-text citations but no reference list / bibliography section",
            [c["raw"] for c in cites[:5]])
    if style and heading:
        want = STYLES[style]["heading"]
        if want.lower() not in heading.lower() and not (want == "References" and "reference list" in heading.lower()):
            add("heading_mismatch", "low",
                f"{STYLES[style]['name']} expects the section heading '{want}' (found '{heading}')", [heading])
    if style and entries and STYLES[style]["order"] == "alpha":
        surnames = [e["surname"].lower() for e in entries if e["surname"]]
        if len(surnames) >= 2 and surnames != sorted(surnames):
            add("unsorted_references", "low",
                f"{STYLES[style]['name']} reference list should be alphabetical by first author",
                [e["surname"] for e in entries if e["surname"]])

    if entries or fn_defs:
        ref_surnames = {e["surname"].lower() for e in entries if e["surname"]}
        ref_numbers = {e["number"] for e in entries if e["number"] is not None}
        orphan_cites = []
        for c in cites:
            lead = c.get("surnames", [])[:1]
            for s in lead:
                if ref_surnames and s.lower() not in ref_surnames:
                    orphan_cites.append(f"{s} in {c['raw']}")
            for num in c.get("numbers", []):
                if ref_numbers and num not in ref_numbers:
                    orphan_cites.append(f"[{num}]")
            if "footnote" in c and c["footnote"] not in fn_defs:
                orphan_cites.append(c["raw"])
        add("orphan_in_text_citation", "high",
            "In-text citation has no matching entry in the reference list", orphan_cites)

        cited_surnames = {s.lower() for c in cites for s in c.get("surnames", [])}
        cited_nums = {n for c in cites for n in c.get("numbers", [])}
        uncited_refs = []
        for e in entries:
            if e["number"] is not None and cited_nums and e["number"] not in cited_nums:
                uncited_refs.append(f"[{e['number']}] {e['text'][:60]}")
            elif e["surname"] and cited_surnames and e["surname"].lower() not in cited_surnames:
                uncited_refs.append(f"{e['surname']} ({e['text'][:55]})")
        if uncited_refs and not (style == "chicago-nb" and fn_defs):
            add("uncited_reference_entry", "low",
                "Reference-list entry is never cited in the body text", uncited_refs)

    # 6. Optional patchwriting / unquoted copying check against --source
    pw = None
    if source_text:
        pw = patchwriting(body, source_text)
        if pw["spans"]:
            sev = "high" if pw["overlap_pct"] >= 10 else "medium"
            add("unquoted_source_overlap", sev,
                f"Unquoted {pw['overlap_pct']}% word-sequence overlap with source (quote or paraphrase fully)",
                pw["spans"])

    score = min(100, sum(SEVERITY_POINTS[f["severity"]] * max(1, min(3, len(f["hits"]))) for f in findings))
    verdict = "CLEAN" if score == 0 else ("LOW" if score < 15 else ("MODERATE" if score < 35 else "HIGH"))
    return {
        "citation_risk_score": score, "verdict": verdict, "style": style,
        "citations_found": len(cites), "references_found": len(entries) + len(fn_defs),
        "patchwriting": pw, "findings": findings,
    }


# ----------------------------------------------------------------- CLI

def _read_input(file_arg: str | None, text_arg: str | None) -> str:
    if file_arg:
        return Path(file_arg).read_text(encoding="utf-8")
    return text_arg if text_arg is not None else sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Purdue OWL research and citation helper.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_styles = sub.add_parser("styles", help="List supported citation styles.")
    p_styles.add_argument("--json", action="store_true")

    p_fmt = sub.add_parser("format", help="Format a source or JSON array of sources.")
    p_fmt.add_argument("--style", required=True, help="apa, mla, chicago-nb, chicago-ad, ieee, ama, asa")
    p_fmt.add_argument("--source", help="Path to a JSON file (one source object or a list).")
    p_fmt.add_argument("--source-json", help="Inline JSON string (one source object or a list).")
    p_fmt.add_argument("--page", help="Page number or range for the in-text citation.")
    p_fmt.add_argument("--plain", action="store_true", help="Plain text output without markdown *italics*.")
    p_fmt.add_argument("--json", action="store_true")

    p_chk = sub.add_parser("check", help="Audit a draft for citation integrity and patchwriting.")
    p_chk.add_argument("--file", help="Path to draft file.")
    p_chk.add_argument("--text", help="Inline draft text.")
    p_chk.add_argument("--style", help="Expected citation style (apa, mla, chicago-nb, chicago-ad, ieee, ama, asa).")
    p_chk.add_argument("--source", help="Optional original source text file to check for unquoted copying.")
    p_chk.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.cmd == "styles":
        if args.json:
            print(json.dumps(STYLES, indent=2))
        else:
            for key, info in STYLES.items():
                print(f"{key:11} | {info['name']:44} | {info['in_text']}")
        return 0

    if args.cmd == "format":
        style = resolve_style(args.style)
        raw = Path(args.source).read_text(encoding="utf-8") if args.source else (args.source_json or sys.stdin.read())
        data = json.loads(raw)
        sources = data if isinstance(data, list) else [data]
        res = build_bibliography(sources, style, md=not args.plain, page=args.page)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return 0
        print(f"Style: {res['style_name']}")
        print(f"Section Heading: {res['heading']}\n")
        for i, item in enumerate(res["entries"], start=1):
            print(f"{i}. {item['reference']}")
            print(f"   In-text:   {item['in_text']}")
            if item["narrative"]:
                print(f"   Narrative: {item['narrative']}")
            if item["warnings"]:
                print(f"   Warnings:  {'; '.join(item['warnings'])}")
        return 0

    style = resolve_style(args.style) if args.style else None
    draft = _read_input(args.file, args.text)
    src_text = Path(args.source).read_text(encoding="utf-8") if args.source else None
    res = check_text(draft, style=style, source_text=src_text)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    print(f"Citation Integrity Risk: {res['citation_risk_score']}/100 ({res['verdict']})")
    print(f"Detected: {res['citations_found']} in-text citations | {res['references_found']} reference entries")
    if res["findings"]:
        print("\nFindings:")
        for f in res["findings"]:
            print(f"  - [{f['severity'].upper()}] {f['message']}: {f['hits']}")
    else:
        print("\nNo citation integrity issues detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
