#!/usr/bin/env python3
"""Scan prose for Wikipedia:Signs_of_AI_writing patterns and compare against learned user style."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = SKILL_DIR / "references" / "user_style_profile.json"

AI_VOCAB_BY_ERA = {
    "2023-2024": [
        "boasts", "bolstered", "crucial", "delve", "delves", "delving", "delved",
        "emphasizing", "enduring", "garner", "garnered", "intricate", "intricacies",
        "interplay", "landscape", "meticulous", "meticulously", "pivotal",
        "underscore", "underscores", "underscored", "tapestry", "testament",
        "valuable", "vibrant",
    ],
    "2024-2025": [
        "align with", "aligns with", "enhance", "enhancing", "fostering",
        "highlighting", "showcasing",
    ],
    "2026+": [
        "clearer", "dependable", "echoed", "foster", "leverage", "leveraging",
        "multifaceted", "prioritize", "quietly", "universally", "deep dive",
    ],
    "grok": [
        "causal", "empirical", "correlate", "correlates",
    ],
}

REGEX_RULES = [
    ("significance_puffery", "Content: Significance/legacy/trend puffery", 8, [
        r"\b(?:stands|serves)\s+as\s+(?:a|an)\b",
        r"\bis\s+a\s+(?:testament|reminder)\s+to\b",
        r"\b(?:marking|marked|marks)\s+a\s+(?:pivotal|significant|key)\s+(?:moment|shift|turning point)\b",
        r"\bbroader\s+(?:movement|trend|context|history|landscape|discussions?)\b",
        r"\b(?:indelible\s+mark|evolving\s+landscape|enduring\s+legacy|setting\s+the\s+stage\s+for)\b",
        r"\b(?:has|have)\s+shaped\s+(?:conversations|discussions|debate)\s+about\b",
    ]),
    ("copulative_avoidance", "Grammar: Avoidance of basic is/are/has", 6, [
        r"\b(?:serves|stands|functions|operates)\s+as\s+(?:a|an|the)\b",
        r"\bholds\s+the\s+distinction\s+of\s+being\b",
        r"\b(?:boasts|features|offers)\s+(?:a|an|several|numerous|multiple)\b",
    ]),
    ("negative_parallelism", "Grammar: Negative parallelism (not just X / not X but Y / Y rather than X)", 8, [
        r"\bnot\s+(?:just|only)\b[^.!?\n]{1,80}\bbut\s+(?:also\b)?",
        r"\bis\s+not\s+[^.!?\n]{1,50},\s*(?:but|it's|it\s+is)\b",
        r"\brather\s+than\s+(?:merely|simply|just|a\s+replacement)\b",
    ]),
    ("superficial_ing", "Content: Superficial trailing -ing participle analysis", 7, [
        r",\s*(?:highlighting|underscoring|emphasizing|reflecting|symbolizing|fostering|cultivating|showcasing|ensuring|contributing\s+to)\s+",
    ]),
    ("vague_connection", "Content: Vague connection or association phrasing", 5, [
        r"\bin\s+(?:connection|association)\s+with\b",
        r"\b(?:is|are|was|were|became)\s+(?:closely\s+|widely\s+)?(?:associated|connected)\s+with\b",
    ]),
    ("weasel_attribution", "Content: Vague attribution / weasel wording", 7, [
        r"\b(?:industry\s+reports|observers\s+(?:have\s+)?cited|experts\s+argue|some\s+critics\s+argue|modern\s+researchers\s+treat|described\s+in\s+scholarship)\b",
        r"\b(?:sources|records|databases|listings|filings)\s+(?:identify|list|describe)\b",
    ]),
    ("hedging_disclaimer", "Communication: Hedging or corrective disclaimer", 8, [
        r"\bit\s+is\s+(?:important|crucial)\s+to\s+(?:note|remember|differentiate)\b",
        r"\b(?:not\s+widely\s+documented|limited\s+in\s+the\s+provided|based\s+on\s+available\s+information)\b",
        r"\bshould\s+be\s+(?:treated|viewed|presented)\s+as\b[^.!?\n]{1,60}\brather\s+than\b",
        r"\bdoes\s+not\s+(?:by\s+itself\s+)?establish\b",
    ]),
    ("outline_conclusion", "Content: Formulaic challenges/future/summary ending", 8, [
        r"\bdespite\s+(?:its|these)\s+(?:challenges|success|promising)\b",
        r"\bfaces\s+(?:several|numerous|new)\s+challenges\b",
        r"\bcontinues\s+to\s+thrive\b",
        r"^(?:In\s+summary|In\s+conclusion|Overall),",
    ]),
    ("assistant_artifact", "Artifact: Leaked chatbot preamble, placeholder, or UTM tag", 15, [
        r"\b(?:Certainly!|Of course!|I hope this helps|You're absolutely right!|As an AI(?: language model)?)\b",
        r"utm_source=(?:chatgpt\.com|openai|copilot\.com)|referrer=grok\.com",
        r"contentReference\[oaicite:\d+\]",
        r"\b20\d\d-[Xx]{2}-[Xx]{2}\b|INSERT_SOURCE_URL|PASTE_[A-Z_]+_HERE|example\.com/source",
    ]),
]


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", cleaned)
    return [p.strip() for p in parts if re.search(r"[A-Za-z0-9]", p)]


def analyze(text: str) -> dict:
    findings = []
    risk = 0
    text_lower = text.lower()

    # 1. AI Vocabulary scan
    vocab_hits = []
    for era, words in AI_VOCAB_BY_ERA.items():
        for w in words:
            matches = re.findall(rf"\b{re.escape(w)}\b", text_lower)
            if matches:
                vocab_hits.append({"word": w, "era": era, "count": len(matches)})
    # Sentence-initial "Additionally,"
    add_hits = len(re.findall(r"(?:^|[.!?]\s+|\n)Additionally,", text))
    if add_hits:
        vocab_hits.append({"word": "Additionally, (sentence-initial)", "era": "2023-2024", "count": add_hits})

    if vocab_hits:
        total_vocab = sum(v["count"] for v in vocab_hits)
        risk += min(30, total_vocab * 4)
        findings.append({
            "category": "ai_vocabulary",
            "label": "Language: High-risk AI vocabulary words",
            "hits": vocab_hits,
        })

    # 2. Regex pattern rules
    for rule_id, label, weight, patterns in REGEX_RULES:
        matched_snippets = []
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.IGNORECASE | re.MULTILINE):
                matched_snippets.append(m.group(0).strip())
        if matched_snippets:
            risk += min(20, len(matched_snippets) * weight)
            findings.append({
                "category": rule_id,
                "label": label,
                "hits": matched_snippets[:10],
            })

    # 3. Formatting & punctuation tells
    bold_bullets = len(re.findall(r"^\s*[-*]\s+\*\*[^*\n]{2,60}\*\*:", text, flags=re.MULTILINE))
    spaced_em_dashes = len(re.findall(r"\s—\s", text))
    curly_quotes = len(re.findall(r"[“”’]", text))
    if bold_bullets >= 2:
        risk += 10
        findings.append({
            "category": "inline_bold_lists",
            "label": "Style: Inline-header bold bullet lists",
            "hits": [f"{bold_bullets} bold-header bullets"],
        })
    if spaced_em_dashes >= 3:
        risk += 8
        findings.append({
            "category": "em_dash_spam",
            "label": "Style: Frequent spaced em-dashes ( — )",
            "hits": [f"{spaced_em_dashes} spaced em-dashes"],
        })
    if curly_quotes >= 4:
        risk += 3
        findings.append({
            "category": "curly_quotes",
            "label": "Style: Typographic curly quotes/apostrophes",
            "hits": [f"{curly_quotes} curly quote characters"],
        })

    # 4. Sentence length & burstiness check
    sentences = split_sentences(text)
    sent_lengths = [len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", s)) for s in sentences]
    sent_lengths = [l for l in sent_lengths if l > 0]
    burstiness = {}
    if len(sent_lengths) >= 4:
        mean_len = sum(sent_lengths) / len(sent_lengths)
        std_len = math.sqrt(sum((l - mean_len) ** 2 for l in sent_lengths) / len(sent_lengths))
        band_8_20 = sum(1 for l in sent_lengths if 8 <= l <= 20) / len(sent_lengths)
        burstiness = {
            "sentence_count": len(sent_lengths),
            "mean_length": round(mean_len, 2),
            "std_dev": round(std_len, 2),
            "pct_in_8_to_20_band": round(band_8_20 * 100, 1),
        }
        if std_len < 4.5 or band_8_20 > 0.85:
            risk += 12
            findings.append({
                "category": "low_burstiness",
                "label": "Syntax: Uniform sentence length (low burstiness / 8-20 word trap)",
                "hits": [f"std_dev={std_len:.2f}, {band_8_20*100:.1f}% in 8-20 word band"],
            })

    # 5. Compare with user style profile if learned
    style_drift = []
    if PROFILE_PATH.exists():
        profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        if profile.get("samples_learned", 0) > 0 and burstiness:
            target_mean = profile["metrics"]["avg_sentence_length"]
            if target_mean and abs(burstiness["mean_length"] - target_mean) > 6:
                style_drift.append(
                    f"Draft mean sentence length ({burstiness['mean_length']}w) differs from your baseline ({target_mean}w)."
                )

    risk = min(100, risk)
    verdict = "LOW" if risk < 20 else ("MODERATE" if risk < 45 else "HIGH")
    return {
        "risk_score": risk,
        "verdict": verdict,
        "burstiness": burstiness,
        "findings": findings,
        "style_drift": style_drift,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze text for Wikipedia:Signs_of_AI_writing tells.")
    parser.add_argument("--file", help="Path to text file to analyze.")
    parser.add_argument("--text", help="Inline text to analyze.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON.")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    result = analyze(text)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"AI-Tell Risk Score: {result['risk_score']}/100 ({result['verdict']})")
    if result["burstiness"]:
        b = result["burstiness"]
        print(
            f"Burstiness: {b['sentence_count']} sentences | mean={b['mean_length']}w | "
            f"std_dev={b['std_dev']} | 8-20w band={b['pct_in_8_to_20_band']}%"
        )
    if result["findings"]:
        print("\nFlagged Patterns:")
        for f in result["findings"]:
            print(f"  - {f['label']}: {f['hits']}")
    else:
        print("\nNo AI-tell patterns detected.")
    if result["style_drift"]:
        print("\nStyle Drift vs. Learned Profile:")
        for d in result["style_drift"]:
            print(f"  - {d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
