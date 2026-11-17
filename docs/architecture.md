# Architecture — Human Writing Guard

## Design Goals

1. **Zero dependencies:** Both scripts (`analyze_text.py` and `style_learner.py`) run on Python 3.10+ using only the standard library so any agent environment can execute them immediately.
2. **Scoped activation:** Prose constraints only trigger on substantive writing tasks (academic papers, assignments, project descriptions, technical documentation, formal reviews, and emails) so normal coding and Q&A stay fast.
3. **Closed-loop verification:** Agents do not guess whether a draft sounds human; they run `analyze_text.py` and revise until `risk_score < 15` (`LOW`).
4. **Privacy-preserving learning:** `style_learner.py` stores statistical metrics (sentence length mean/std, contraction rate, punctuation ratios, transition frequencies) in `references/user_style_profile.json` rather than storing raw personal documents.

## Pipeline

```mermaid
flowchart LR
    A[User Prompt] --> B{Substantive Prose?}
    B -- No --> C[Skip Skill]
    B -- Yes --> D[Load user_style_profile.json]
    D --> E[Draft with Strict Rules + Domain Add-on]
    E --> F[Run analyze_text.py]
    F --> G{Risk Score < 15?}
    G -- No --> E
    G -- Yes --> H[Deliver Prose]
    H --> I[User Edits or Supplies Sample]
    I --> J[Run style_learner.py learn]
    J --> D
```

## Scoring Model (`analyze_text.py`)

| Signal Category | Max Weight | What It Catches |
|---|---:|---|
| AI vocabulary by era | 30 | Overrepresented 2023–2026 LLM words and Grok-isms |
| Significance & legacy puffery | 20 | `serves as`, `pivotal moment`, `broader movement`, `shaped discussions` |
| Negative parallelisms | 20 | `not just X, but also Y`, `not X, but Y`, `Y rather than X` |
| Hedging & corrective disclaimers | 20 | `important to note`, `not widely documented`, `should be treated as... rather than` |
| Formulaic endings | 20 | `Despite these challenges`, `continues to thrive`, `In summary/conclusion` |
| Superficial `-ing` clauses | 20 | Trailing `, highlighting...`, `, reflecting...`, `, fostering...` |
| Copulative avoidance | 20 | `serves as`, `boasts`, `features`, `offers` replacing `is`/`are`/`has` |
| Leaked assistant artifacts | 20 | `Certainly!`, `utm_source=`, `oaicite`, date/URL placeholders |
| Low sentence burstiness | 12 | Uniform sentence length (`std_dev < 4.5` or `>85%` in 8–20 word band) |
| Style & punctuation tells | 21 | Inline-bold bullet lists, spaced em-dash spam (` — `), curly quotes |
