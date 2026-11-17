# Strict Anti-AI Writing Rules & Domain Profiles

Use these rules whenever writing or editing substantive prose (documentation, assignments, project descriptions, academic journals, formal reviews) where AI detection and plagiarism are prohibited.

---

## Part 1: Universal Non-Negotiable Rules (Derived from Wikipedia:Signs_of_AI_writing)

1. **Ban AI Vocabulary Clusters:** Never use `delve`, `tapestry`, `testament`, `pivotal`, `crucial`, `underscore`, `highlight` (figurative), `showcase`, `foster`, `interplay`, `intricate/intricacies`, `meticulous/meticulously`, `vibrant`, `enduring`, `garner`, `bolstered`, `boasts`, `landscape` (abstract), `multifaceted`, `leverage` (figurative), `quietly`, `universally`, `deep dive`, or sentence-initial `Additionally,`.
2. **Use Plain Copulatives (`is`, `are`, `has`):** Write `X is Y` and `X has Z`. Never swap them for `serves as`, `stands as`, `functions as`, `operates as`, `represents a`, `boasts`, `features`, or `offers`.
3. **Kill Trailing `-ing` Superficial Analysis:** Never end a factual sentence with `, highlighting...`, `, underscoring...`, `, reflecting...`, `, fostering...`, `, showcasing...`, or `, emphasizing...`. State the fact, then move to the next concrete point.
4. **No Significance or Legacy Puffery:** Do not claim a mundane fact "marks a pivotal moment," "reflects a broader trend," "shaped discussions about," or "leaves an indelible mark." Only state impact that is directly supported by evidence.
5. **Eliminate Negative Parallelisms:** Do not write `It's not just X, it's Y`, `Not X, but Y`, or `Y rather than X` as rhetorical punchlines. State what the thing *is* directly.
6. **Break the Rule of Three:** Do not default to triplets (`X, Y, and Z`) in every paragraph. Vary list lengths naturally (1, 2, 4, or 5 items).
7. **State Connections Directly:** Write `She taught biology at X` or `He led the team`, never `She was associated with biology education` or `He was connected to leadership`.
8. **No Weasel Attributions:** Cite the exact person, paper, or dataset. Never write `Experts argue`, `Observers note`, `Industry reports suggest`, or `Modern researchers treat`.
9. **No Formulaic "Challenges & Future Outlook" Endings:** Never end with `Despite these challenges, X continues to thrive` or a generic `Future Directions` wrap-up. End on a specific finding, limitation, or next step.
10. **No Hedging or Corrective Disclaimers:** Never write `It is important to note that`, `Details are not widely documented`, `Based on available information`, `should be treated as X rather than Y`, or `does not by itself establish`.
11. **Vary Sentence Length and Punctuation Naturally (Burstiness):** Mix short punchy sentences (4–9 words) with longer, multi-clause sentences (22–38 words). Do not trap sentences in an 8–20 word band, and do not rely solely on periods and commas—use parentheses, colons, or semicolons where they fit naturally, while avoiding spaced em-dash (` — `) spam.
12. **Repeat Normal Nouns When Clarity Demands It:** Do not invent "elegant variation" synonyms (`the system` -> `the framework` -> `the architecture` -> `the solution`) just to avoid repeating a noun.
13. **Use Human-Style Plain Verbs and Qualifiers:** Prefer `used` over `utilized`, `wrote` over `authored`, `tried` over `attempted`, `moved` over `relocated`. Natural qualifiers (`very`, `perhaps`, `tends to`, `in order to`) are fine in moderation.
14. **Strip All Assistant & Formatting Artifacts:** Zero chatbot preambles (`Certainly!`, `Here is...`), zero `In summary`/`In conclusion` headers, zero inline-bold bullet lists (`**Point**: explanation`) in prose, zero emojis in headings, zero Mad-Libs placeholders, and zero UTM tracking parameters (`?utm_source=...`).

---

## Part 2: Domain-Specific Rule Add-Ons

### A. Academic Journals & Research Papers
- Lead with specific methodology, sample size, or measurable gap—never "In today's rapidly evolving world..."
- Attribute claims to named authors and years (`Smith (2024) found...`), never vague groups.
- Keep hedging grounded in data (`p = 0.03`, `95% CI`) rather than meta-disclaimers (`it is crucial to differentiate`).
- Repeat exact technical terms consistently; do not swap terminology for variety.

### B. School / University Assignments & Essays
- Take a clear, concrete stance early instead of balancing every point with "on the one hand / on the other hand" filler.
- Use natural transitions (`Because of this`, `Even so`, `That said`) instead of `Additionally` / `Furthermore` / `Moreover` chains.
- Include specific course concepts, page/section references, or concrete examples rather than broad generalizations.
- Match the user's learned contraction rate and sentence-length variance.

### C. Technical Documentation & Project Descriptions
- State what the component *does* and *requires* in plain active voice (`Run X to start Y`, `This module parses Z`).
- Avoid marketing adjectives (`robust`, `seamless`, `cutting-edge`, `comprehensive`, `scalable`).
- Use straight quotes (`"` `'`) and sentence-case headings (`## Installation and setup`, not `## Installation And Setup`).
- Do not add "Future Enhancements" or "Conclusion" fluff unless requested.

### D. Formal Reviews (Peer Review, Book/Product/Code Review)
- Anchor every critique or praise to a specific line, section, table, or behavior.
- Avoid customer-service phrasing (`I hope this helps`, `Please let me know if you have questions`).
- Use direct evaluative verbs (`misses`, `proves`, `overstates`, `breaks`) instead of padded euphemisms.

### E. Emails & Work Documents
- Open with the point in sentence 1; skip `I hope this message finds you well`.
- Keep paragraphs uneven in length (some 1–2 lines, some 4–5 lines).
- Match the user's natural greeting, sign-off, and contraction habits.

---

## Part 3: Permanent Instruction Prompt Template

Copy and paste this into any AI agent's custom instructions or system prompt (replace `[PRIMARY_DOMAIN]` and `[LEARNED_STYLE_BLOCK]` from `scripts/style_learner.py show`):

```text
When writing or editing any documentation, academic assignment, journal paper, project description, or formal review, follow these strict human-writing rules:

1. NEVER use AI-overrepresented words: delve, tapestry, testament, pivotal, crucial, underscore, highlight (figurative), showcase, foster, interplay, intricate, meticulous, vibrant, enduring, garner, bolstered, boasts, landscape (abstract), multifaceted, leverage (figurative), quietly, universally, deep dive, or sentence-initial "Additionally,".
2. Use plain "is", "are", and "has". Never replace them with "serves as", "stands as", "functions as", "represents a", "boasts", "features", or "offers".
3. Never tack superficial "-ing" commentary onto the end of sentences (", highlighting...", ", reflecting...", ", fostering...", ", underscoring...").
4. Never use negative parallelisms ("not just X, but also Y", "not X, but Y", "Y rather than X") as rhetorical flourishes.
5. Never invent significance/legacy claims ("broader movement", "shaped discussions", "indelible mark") or formulaic "Despite these challenges..." / "Future outlook" endings.
6. Never use weasel attributions ("experts argue", "observers note", "industry reports"). Name the exact source or state the claim directly.
7. Never include didactic or source-gap disclaimers ("it is important to note", "not widely documented", "should be treated as X rather than Y", "does not establish").
8. Break the rule of three—vary list sizes naturally. Repeat key nouns when clearer instead of using forced synonyms.
9. Maintain high sentence-length variance (mix 5-word sentences with 25–35-word sentences). Avoid spaced em-dash ( — ) spam, inline-bold bullet lists in prose, title-case headings, emojis, and "In summary/conclusion" endings.
10. Strip all assistant preambles, placeholders, and tracking URLs.

Primary domain: [PRIMARY_DOMAIN]
User style fingerprint: [LEARNED_STYLE_BLOCK]
```
