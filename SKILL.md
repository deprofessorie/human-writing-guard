---
name: human-writing-guard
description: Human-like writing, AI-tell detection, Purdue OWL research & citation compliance, and adaptive user style-matching skill. Activate ONLY when writing, editing, or reviewing substantive prose where plagiarism and AI detection are prohibited—such as documentation, academic assignments, journal articles, project descriptions, technical reports, or formal reviews. Do NOT activate for casual conversation, code-only tasks, or quick Q&A.
---

# Human Writing Guard

Ensure substantive prose sounds genuinely human, avoids all documented AI-writing tells, follows Purdue OWL research and citation standards, and adapts to the user's own writing fingerprint over time.

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

### 3. Apply Purdue OWL Research & Citation Rules (When Using Sources)

For academic papers, assignments, literature reviews, or cited reports, read [purdue-owl-research-citation.md](references/purdue-owl-research-citation.md):
- **Quoting vs. paraphrasing vs. summarizing:** Use exact quotes only when wording matters; otherwise paraphrase in fresh sentence structure and vocabulary (never patchwrite by swapping synonyms) or summarize main claims. Always cite non-common-knowledge facts and statistics.
- **Format citations deterministically** across APA 7, MLA 9, Chicago 18 (`chicago-nb` / `chicago-ad`), IEEE, AMA 11, or ASA 7:

```bash
python scripts/citation_guard.py format --style apa --source sources.json
```

### 4. Run the Deterministic Scanners

Before delivering any final prose, save the draft to a temporary file or pipe it into the AI-tell scanner:

```bash
python scripts/analyze_text.py --file <draft.txt>
```

Target a `risk_score < 15` (`LOW`) with zero flagged AI-vocabulary hits, zero negative parallelisms, zero superficial `-ing` endings, and healthy sentence-length variance (`std_dev >= 5.0`).

If the draft cites sources or statistics, also run the Purdue OWL citation and patchwriting audit:

```bash
python scripts/citation_guard.py check --file <draft.txt> --style apa
# Optional: check against an original source file for unquoted copying / patchwriting
python scripts/citation_guard.py check --file <draft.txt> --style apa --source <source.txt>
```

Target `citation_risk_score < 15` (`CLEAN` or `LOW`) with zero uncited quotes, zero unsupported statistics, zero placeholder citations, and matching in-text/reference-list entries. Rewrite any flagged lines and re-run until clean.

### 5. Continuous Learning Loop

Whenever the user pastes their own text, shares past assignments/papers, or edits an agent draft to sound more like them, run `scripts/style_learner.py learn` on their version so future drafts match their natural cadence automatically.
