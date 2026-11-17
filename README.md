# Human Writing Guard

[![CI](https://github.com/deprofessorie/human-writing-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/deprofessorie/human-writing-guard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Universal-black.svg)](SKILL.md)

An adaptive, agent-agnostic **AI writing detection, Purdue OWL research & citation compliance, and personal style-matching skill**. It combines the [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) taxonomy with the [Purdue OWL Research and Citation Resources](https://owl.purdue.edu/owl/research_and_citation/index.html) to audit drafts deterministically and learn your writing fingerprint over time.

Built for **Claude Code, Gemini CLI, Antigravity, Codex, and Cursor**—with zero external Python dependencies.

---

## Why This Exists

Most "humanizer" prompts fail because they only ban three or four cliché words while leaving the underlying statistical tells intact: uniform 8–20 word sentences, trailing `-ing` commentary clauses, copulative avoidance (`serves as` instead of `is`), negative parallelisms (`not just X, but also Y`), and formulaic `Challenges / Future Outlook` endings. Academic drafts also fail when citations mix styles, leave quotes or statistics unsupported, or slip into patchwriting.

**Human Writing Guard** solves this in three ways:
1. **Strict Scope Gate:** Activates *only* when you write substantive prose where AI detection or plagiarism is prohibited—academic journals, school/university assignments, project descriptions, technical documentation, formal reviews, and emails. Casual chat and pure code generation stay untouched.
2. **Adaptive Style Learning:** `style_learner.py` measures your own writing samples (sentence length variance, contraction rate, punctuation mix, and natural transitions) and steers drafts toward your real cadence.
3. **Purdue OWL Research & Citation Compliance:** `citation_guard.py` formats references across all 7 major Purdue OWL styles (APA 7, MLA 9, Chicago 18 Notes & Bibliography / Author-Date, IEEE, AMA 11, ASA 7) and audits drafts for uncited quotes, unsupported statistics, mixed citation systems, orphan references, and patchwriting.

---

## Architecture

```
User Request (Academic / Docs / Assignment / Review / Email)
   │
   ▼
[1. Scope Gate] ──► Skip for casual chat or pure code tasks
   │
   ▼
[2. Style Learner] ──► Reads references/user_style_profile.json
   │                    (sentence burstiness, contractions, punctuation, domain)
   ▼
[3. Strict Ruleset] ──► 14 anti-AI rules + Purdue OWL research & citation guide
   │
   ▼
[4. Deterministic Scanners]
   ├── python scripts/analyze_text.py     ──► AI vocab, parallelisms, -ing, burstiness
   └── python scripts/citation_guard.py   ──► Citation integrity, style match, patchwriting
   │
   ▼
Clean, Cited Human Prose (Both Risk Scores < 15 / LOW)
```

See [docs/architecture.md](docs/architecture.md) for the full design breakdown.

---

## Key Features

- **Complete Wikipedia Pattern Coverage (2022–2026+):** Covers content, grammar, formatting, citation, and historical indicators documented on `Wikipedia:Signs_of_AI_writing`, including GPT-4, GPT-4o, GPT-5, GPT-6, and Grok idiolects.
- **Purdue OWL Research & Citation Engine (`citation_guard.py`):**
  - **Format** bibliographies and in-text/narrative citations for **APA 7, MLA 9, Chicago 18 (Notes & Bibliography and Author-Date), IEEE, AMA 11, and ASA 7**.
  - **Audit** drafts for uncited direct quotes, long inline quotes needing block formatting, unsupported statistics, mixed citation systems, placeholder citations (`[citation needed]`, `(Author, 20XX)`), heading/alphabetical-order mismatches, and orphan in-text or reference-list entries.
  - **Detect patchwriting** against an original source file via unquoted 6-gram overlap analysis (`--source`).
- **Deterministic Risk Scoring (`0–100`):** Runs locally using Python's standard library—no API keys, no external packages, no data sent to third-party servers.
- **Personal Writing Fingerprint Learner:** Computes weighted averages for sentence length, standard deviation (burstiness), short/long sentence ratio, contraction frequency, and punctuation habits.
- **Universal Agent Compatibility:** Works natively with `SKILL.md`-compatible agents (Claude Code, Gemini, Antigravity) and `AGENTS.md`-compatible agents (Codex, Cursor).

---

## Quick Start

### 1. Install the Skill

Clone directly into your global skills directory (or project `.claude/skills` / `.gemini/config/skills`):

```bash
git clone https://github.com/deprofessorie/human-writing-guard.git ~/.gemini/config/skills/human-writing-guard
```

### 2. Teach It Your Writing Style

Feed one or more samples of your own writing so the skill learns your natural cadence:

```bash
python scripts/style_learner.py learn --file my_paper.txt --domain academic
python scripts/style_learner.py show
```

Supported `--domain` values: `academic`, `assignment`, `documentation`, `project_description`, `review`, `email`, `work_docs`, `social`, `general`.

### 3. Scan Any Draft for AI Tells

```bash
python scripts/analyze_text.py --file draft.txt
```

Example output on an unedited AI draft:

```text
AI-Tell Risk Score: 91/100 (HIGH)

Flagged Patterns:
  - Language: High-risk AI vocabulary words: ['enduring', 'intricate', 'interplay', 'tapestry', 'testament', 'vibrant', 'highlighting', 'Additionally, (sentence-initial)']
  - Content: Significance/legacy/trend puffery: ['serves as an', 'enduring legacy']
  - Grammar: Avoidance of basic is/are/has: ['serves as an']
  - Grammar: Negative parallelism: ['not just food, but also']
  - Content: Superficial trailing -ing participle analysis: [', highlighting']
  - Content: Formulaic challenges/future/summary ending: ['despite these challenges', 'continues to thrive']
```

Add `--json` for machine-readable output in CI pipelines or agent toolchains.

### 4. Format Citations & Audit Citation Integrity (Purdue OWL)

List all supported styles:

```bash
python scripts/citation_guard.py styles
```

Format a JSON source (or array of sources) in APA 7, MLA 9, Chicago 18, IEEE, AMA 11, or ASA 7:

```bash
python scripts/citation_guard.py format --style apa --source-json '{"type":"journal","authors":["Jane Smith","Alex Lee"],"year":2024,"title":"Adaptive prose evaluation","container":"Journal of Writing Analytics","volume":8,"issue":2,"pages":"14-29","doi":"10.1000/jwa.2024.02"}'
```

Audit a draft for uncited quotes, unsupported statistics, style consistency, reference-list cross-checks, and optional patchwriting against a source file:

```bash
python scripts/citation_guard.py check --file draft.txt --style apa
python scripts/citation_guard.py check --file draft.txt --style apa --source source.txt
```

---

## Repository Layout

```text
human-writing-guard/
├── SKILL.md                                    # Core skill instructions for AI agents
├── AGENTS.md                                   # Universal agent entry point (Codex / Cursor / Claude / Gemini)
├── README.md                                   # Project overview and quick start
├── LICENSE                                     # MIT License
├── docs/
│   └── architecture.md                         # System design and scoring models
├── references/
│   ├── wikipedia-signs.md                      # Full catalog of Wikipedia:Signs_of_AI_writing patterns
│   ├── writing-rules.md                        # 14 strict rules, domain add-ons, permanent prompt template
│   ├── purdue-owl-research-citation.md         # Purdue OWL research, paraphrasing, and 7-style citation guide
│   └── user_style_profile.json                 # Persistent learned style fingerprint
├── scripts/
│   ├── analyze_text.py                         # Deterministic AI-tell scanner
│   ├── citation_guard.py                       # Purdue OWL citation formatter, integrity checker & patchwriting detector
│   └── style_learner.py                        # Adaptive user writing-pattern learner
└── tests/
    └── test_skill.py                           # Automated unit tests
```

---

## Running Tests

```bash
python -m unittest discover -s tests -v
```

---

## Sources & References

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [Purdue OWL: Research and Citation Resources](https://owl.purdue.edu/owl/research_and_citation/index.html)

## License

MIT — see [LICENSE](LICENSE).
