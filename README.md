# Human Writing Guard

[![CI](https://github.com/deprofessorie/human-writing-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/deprofessorie/human-writing-guard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Universal-black.svg)](SKILL.md)

An adaptive, agent-agnostic **AI writing detection and human-style skill** built from the complete [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) taxonomy. It runs a deterministic AI-tell scanner on drafts and learns your personal writing fingerprint over time from your own samples.

Built for **Claude Code, Gemini CLI, Antigravity, Codex, and Cursor**—with zero external Python dependencies.

---

## Why This Exists

Most "humanizer" prompts fail because they only ban three or four cliché words while leaving the underlying statistical tells intact: uniform 8–20 word sentences, trailing `-ing` commentary clauses, copulative avoidance (`serves as` instead of `is`), negative parallelisms (`not just X, but also Y`), and formulaic `Challenges / Future Outlook` endings.

**Human Writing Guard** solves this in two ways:
1. **Strict Scope Gate:** It activates *only* when you write substantive prose where AI detection or plagiarism is prohibited—academic journals, school/university assignments, project descriptions, technical documentation, formal reviews, and emails. Casual chat and pure code generation stay untouched.
2. **Adaptive Style Learning:** Instead of forcing a generic "human" voice, `style_learner.py` measures your own writing samples (sentence length variance, contraction rate, punctuation mix, and natural transitions) and steers every draft toward your real cadence.

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
[3. Strict Ruleset] ──► Applies 14 anti-AI rules + domain add-ons
   │                     (from Wikipedia:Signs_of_AI_writing)
   ▼
[4. Deterministic Scanner] ──► python scripts/analyze_text.py
   │                            Flags AI vocab (2023–2026), parallelisms,
   │                            trailing -ing, puffery, low burstiness
   ▼
Clean Human Prose (Risk Score < 15 / LOW)
```

See [docs/architecture.md](docs/architecture.md) for the full design breakdown.

---

## Key Features

- **Complete Wikipedia Pattern Coverage (2022–2026+):** Covers every content, grammar, formatting, citation, and historical indicator documented on `Wikipedia:Signs_of_AI_writing`, including GPT-4, GPT-4o, GPT-5, GPT-6, and Grok idiolects.
- **Deterministic Risk Scoring (`0–100`):** Scans drafts locally using Python's standard library—no API keys, no external packages, no data sent to third-party servers.
- **Personal Writing Fingerprint Learner:** Ingests your past papers, docs, or emails to compute weighted averages for sentence length, standard deviation (burstiness), short/long sentence ratio, contraction frequency, and punctuation habits.
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

---

## Repository Layout

```text
human-writing-guard/
├── SKILL.md                          # Core skill instructions for AI agents
├── AGENTS.md                         # Universal agent entry point (Codex / Cursor / Claude / Gemini)
├── README.md                         # Project overview and quick start
├── LICENSE                           # MIT License
├── docs/
│   └── architecture.md               # System design and scoring model
├── references/
│   ├── wikipedia-signs.md            # Full catalog of Wikipedia:Signs_of_AI_writing patterns
│   ├── writing-rules.md              # 14 strict rules, domain add-ons, permanent prompt template
│   └── user_style_profile.json       # Persistent learned style fingerprint
├── scripts/
│   ├── analyze_text.py               # Deterministic AI-tell scanner
│   └── style_learner.py              # Adaptive user writing-pattern learner
└── tests/
    └── test_skill.py                 # Automated unit tests
```

---

## Running Tests

```bash
python -m unittest discover -s tests -v
```

---

## License

MIT — see [LICENSE](LICENSE).
