#!/usr/bin/env python3
"""Learn and persist a user's natural writing style fingerprint from their own text samples."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = SKILL_DIR / "references" / "user_style_profile.json"

CONTRACTIONS = {
    "aren't", "can't", "couldn't", "didn't", "doesn't", "don't", "hadn't",
    "hasn't", "haven't", "he'd", "he'll", "he's", "i'd", "i'll", "i'm",
    "i've", "isn't", "it'd", "it'll", "it's", "let's", "mightn't", "mustn't",
    "shan't", "she'd", "she'll", "she's", "shouldn't", "that's", "there's",
    "they'd", "they'll", "they're", "they've", "wasn't", "we'd", "we'll",
    "we're", "we've", "weren't", "what's", "where's", "who's", "won't",
    "wouldn't", "you'd", "you'll", "you're", "you've",
}

TRANSITION_PHRASES = [
    "however", "therefore", "moreover", "furthermore", "additionally",
    "consequently", "meanwhile", "nevertheless", "nonetheless", "that said",
    "even so", "in fact", "actually", "still", "yet", "so", "because of this",
    "for example", "for instance", "on the other hand", "instead",
]

VALID_DOMAINS = [
    "academic", "assignment", "documentation", "project_description",
    "review", "email", "work_docs", "social", "general",
]


def default_profile() -> dict:
    return {
        "primary_domain": "general",
        "samples_learned": 0,
        "total_words_analyzed": 0,
        "last_updated": None,
        "metrics": {
            "avg_sentence_length": None,
            "sentence_length_std": None,
            "short_sentence_ratio": None,
            "long_sentence_ratio": None,
            "avg_word_length": None,
            "type_token_ratio": None,
            "contraction_rate_per_1k_words": None,
            "first_person_rate_per_1k_words": None,
            "punctuation_per_1k_chars": {
                "comma": None,
                "semicolon": None,
                "colon": None,
                "em_dash": None,
                "parentheses": None,
                "exclamation": None,
            },
        },
        "preferred_transitions": {},
        "avoided_ai_words_verified_absent": True,
    }


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", cleaned)
    return [p.strip() for p in parts if re.search(r"[A-Za-z0-9]", p)]


def extract_features(text: str) -> dict:
    sentences = split_sentences(text)
    words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", text)
    words_lower = [w.lower() for w in words]
    word_count = len(words)

    if word_count == 0 or not sentences:
        raise ValueError("Sample text has too few words or sentences to learn from.")

    sent_lengths = [len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", s)) for s in sentences]
    sent_lengths = [l for l in sent_lengths if l > 0]
    mean_len = sum(sent_lengths) / len(sent_lengths)
    variance = sum((l - mean_len) ** 2 for l in sent_lengths) / len(sent_lengths)
    std_len = math.sqrt(variance)

    short_ratio = sum(1 for l in sent_lengths if l <= 10) / len(sent_lengths)
    long_ratio = sum(1 for l in sent_lengths if l >= 22) / len(sent_lengths)
    avg_word_len = sum(len(w) for w in words) / word_count
    ttr = len(set(words_lower)) / word_count

    contraction_count = sum(1 for w in words_lower if w in CONTRACTIONS)
    first_person_count = sum(1 for w in words_lower if w in {"i", "me", "my", "mine", "we", "us", "our", "ours"})

    char_count = max(len(text), 1)
    scale_chars = 1000.0 / char_count
    scale_words = 1000.0 / word_count

    punct = {
        "comma": round(text.count(",") * scale_chars, 2),
        "semicolon": round(text.count(";") * scale_chars, 2),
        "colon": round(text.count(":") * scale_chars, 2),
        "em_dash": round((text.count("—") + text.count("--")) * scale_chars, 2),
        "parentheses": round(text.count("(") * scale_chars, 2),
        "exclamation": round(text.count("!") * scale_chars, 2),
    }

    text_lower = text.lower()
    transitions = Counter()
    for phrase in TRANSITION_PHRASES:
        hits = len(re.findall(rf"\b{re.escape(phrase)}\b", text_lower))
        if hits > 0:
            transitions[phrase] = hits

    return {
        "word_count": word_count,
        "avg_sentence_length": round(mean_len, 2),
        "sentence_length_std": round(std_len, 2),
        "short_sentence_ratio": round(short_ratio, 3),
        "long_sentence_ratio": round(long_ratio, 3),
        "avg_word_length": round(avg_word_len, 2),
        "type_token_ratio": round(ttr, 3),
        "contraction_rate_per_1k_words": round(contraction_count * scale_words, 2),
        "first_person_rate_per_1k_words": round(first_person_count * scale_words, 2),
        "punctuation_per_1k_chars": punct,
        "transitions": dict(transitions),
    }


def weighted_avg(old: float | None, new: float, old_w: int, new_w: int) -> float:
    if old is None or old_w <= 0:
        return round(new, 3)
    return round((old * old_w + new * new_w) / (old_w + new_w), 3)


def load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return default_profile()


def save_profile(profile: dict) -> None:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")


def format_style_summary(profile: dict) -> str:
    if profile["samples_learned"] == 0:
        return (
            f"Primary domain: {profile['primary_domain']}. "
            "No personal writing samples learned yet; using universal anti-AI human baseline."
        )
    m = profile["metrics"]
    p = m["punctuation_per_1k_chars"]
    top_trans = sorted(profile["preferred_transitions"].items(), key=lambda x: -x[1])[:5]
    trans_str = ", ".join(k for k, _ in top_trans) if top_trans else "minimal explicit transitions"
    return (
        f"Domain: {profile['primary_domain']} (learned from {profile['samples_learned']} sample(s), "
        f"{profile['total_words_analyzed']} words). "
        f"Target sentence length: ~{m['avg_sentence_length']} words (std dev ~{m['sentence_length_std']}; "
        f"{int(round(m['short_sentence_ratio'] * 100))}% short <=10w, "
        f"{int(round(m['long_sentence_ratio'] * 100))}% long >=22w). "
        f"Contractions: {m['contraction_rate_per_1k_words']}/1k words. "
        f"First-person: {m['first_person_rate_per_1k_words']}/1k words. "
        f"Punctuation/1k chars: commas={p['comma']}, semicolons={p['semicolon']}, "
        f"colons={p['colon']}, em-dashes={p['em_dash']}, parens={p['parentheses']}. "
        f"Natural transitions used: {trans_str}."
    )


def cmd_learn(args: argparse.Namespace) -> int:
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    feats = extract_features(text)
    profile = load_profile()
    old_w = profile["total_words_analyzed"]
    new_w = feats["word_count"]

    if args.domain:
        profile["primary_domain"] = args.domain

    m = profile["metrics"]
    for key in [
        "avg_sentence_length", "sentence_length_std", "short_sentence_ratio",
        "long_sentence_ratio", "avg_word_length", "type_token_ratio",
        "contraction_rate_per_1k_words", "first_person_rate_per_1k_words",
    ]:
        m[key] = weighted_avg(m[key], feats[key], old_w, new_w)

    for pkey, pval in feats["punctuation_per_1k_chars"].items():
        m["punctuation_per_1k_chars"][pkey] = weighted_avg(
            m["punctuation_per_1k_chars"][pkey], pval, old_w, new_w
        )

    for tkey, tcount in feats["transitions"].items():
        profile["preferred_transitions"][tkey] = profile["preferred_transitions"].get(tkey, 0) + tcount

    profile["samples_learned"] += 1
    profile["total_words_analyzed"] += new_w
    profile["last_updated"] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_profile(profile)

    print("Style profile updated.")
    print(format_style_summary(profile))
    return 0


def cmd_show(_args: argparse.Namespace) -> int:
    profile = load_profile()
    print(json.dumps(profile, indent=2))
    print("\n--- Prompt Style Block ---")
    print(format_style_summary(profile))
    return 0


def cmd_set_domain(args: argparse.Namespace) -> int:
    profile = load_profile()
    profile["primary_domain"] = args.domain
    profile["last_updated"] = dt.datetime.now(dt.timezone.utc).isoformat()
    save_profile(profile)
    print(f"Primary domain set to: {args.domain}")
    return 0


def cmd_reset(_args: argparse.Namespace) -> int:
    profile = default_profile()
    save_profile(profile)
    print("User style profile reset to defaults.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Learn and inspect user writing style fingerprint.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_learn = sub.add_parser("learn", help="Learn writing patterns from a human-written sample.")
    p_learn.add_argument("--file", help="Path to text file.")
    p_learn.add_argument("--text", help="Inline text sample.")
    p_learn.add_argument("--domain", choices=VALID_DOMAINS, help="Optional domain label.")
    p_learn.set_defaults(func=cmd_learn)

    p_show = sub.add_parser("show", help="Show the current learned style profile.")
    p_show.set_defaults(func=cmd_show)

    p_dom = sub.add_parser("set-domain", help="Set the user's primary writing domain.")
    p_dom.add_argument("--domain", required=True, choices=VALID_DOMAINS)
    p_dom.set_defaults(func=cmd_set_domain)

    p_reset = sub.add_parser("reset", help="Reset learned style profile.")
    p_reset.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
