---
name: human-writing-guard
description: Human-like writing, AI-tell detection, and adaptive user style-matching skill. Activate ONLY when writing, editing, or reviewing substantive prose where plagiarism and AI detection are prohibited—such as documentation, academic assignments, journal articles, project descriptions, technical reports, or formal reviews. Do NOT activate for casual conversation, code-only tasks, or quick Q&A.
---

# Human Writing Guard

Ensure substantive prose sounds genuinely human, avoids all documented AI-writing tells, and adapts to the user's own writing fingerprint over time.

## Activation Scope

Apply this skill **only** when drafting, rewriting, or auditing prose where AI detection or plagiarism is prohibited:
- Documentation and project descriptions
- Academic assignments, essays, and journal articles
- Formal reviews, reports, and proposals

Skip this skill for casual chat, pure code generation, shell commands, or short direct answers.

## Core Workflow

### 1. Load the User's Learned Style Profile

Run the style learner to inspect the user's current writing fingerprint and primary domain:

```bash
python scripts/style_learner.py show
```

- If `samples_learned` is `> 0`, adopt the reported target sentence length, variance (short/long mix), contraction rate, first-person frequency, punctuation profile, and natural transitions.
- If the user provides a sample of their own writing (or corrects a draft), immediately learn from it:

```bash
python scripts/style_learner.py learn --file <path-to-sample.txt> --domain <domain>
```

Available domains: `academic`, `assignment`, `documentation`, `project_description`, `review`, `email`, `work_docs`, `social`, `general`.

### 2. Draft Using Strict Anti-AI Rules

Read [writing-rules.md](references/writing-rules.md) before drafting. Apply all 14 universal rules plus the matching domain add-on:
- Ban AI vocabulary clusters (`delve`, `tapestry`, `testament`, `pivotal`, `crucial`, figurative `underscore`/`highlight`/`showcase`/`leverage`, `multifaceted`, sentence-initial `Additionally,`, etc.).
- Use plain `is`, `are`, and `has` instead of `serves as`, `stands as`, `boasts`, `features`, or `offers`.
- Remove trailing `-ing` commentary clauses (`, highlighting...`, `, reflecting...`, `, fostering...`).
- Remove negative parallelisms (`not just X, but also Y`, `not X, but Y`, `Y rather than X`).
- Remove significance/legacy puffery, weasel attributions (`experts argue`, `observers note`), hedging disclaimers (`it is important to note`, `should be treated as X rather than Y`), and formulaic `Challenges / Future Outlook / In summary` endings.
- Maintain natural sentence-length burstiness (mix 5-word sentences with 25–35-word sentences; avoid trapping every sentence in an 8–20 word band).
- Use plain human verbs (`used`, `wrote`, `tried`, `moved`) and repeat normal nouns instead of inventing forced synonyms.

For the full catalog of patterns and real-world examples from Wikipedia, consult [wikipedia-signs.md](references/wikipedia-signs.md).

### 3. Run the Deterministic AI-Tell Scanner

Before delivering any final prose, save the draft to a temporary file or pipe it into the scanner:

```bash
python scripts/analyze_text.py --file <draft.txt>
```

Target a `risk_score < 15` (`LOW`) with zero flagged AI-vocabulary hits, zero negative parallelisms, zero superficial `-ing` endings, and healthy sentence-length variance (`std_dev >= 5.0`). Rewrite any flagged lines and re-run until clean.

### 4. Continuous Learning Loop

Whenever the user pastes their own text, shares past assignments/papers, or edits an agent draft to sound more like them, run `scripts/style_learner.py learn` on their version so future drafts match their natural cadence automatically.
