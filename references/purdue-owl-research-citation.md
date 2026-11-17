# Purdue OWL Research and Citation Reference

Operational guide distilled from the [Purdue OWL Research and Citation Resources](https://owl.purdue.edu/owl/research_and_citation/index.html) for drafting, auditing, and formatting cited academic and technical prose.

Run `scripts/citation_guard.py` to format citations or audit drafts against these rules.

---

## 1. Conducting Research

### Primary vs. Secondary Research
- **Primary research** collects original data directly (interviews, surveys, observations, field notes, lab experiments, archival artifacts). State sample size, instruments, and collection dates explicitly.
- **Secondary research** synthesizes existing studies, reports, or historical records. Verify claims against the original primary study rather than chaining secondary summaries.

### Evaluating Sources
Apply four checks before citing any source:
1. **Authority and Expertise:** Identify the author's credentials, institutional affiliation, and whether the venue is peer-reviewed or editorially vetted.
2. **Evidence and Methodology:** Check whether claims are backed by primary data, reproducible methods, or cited primary records rather than assertions.
3. **Currency:** Match publication date to the domain (fast-moving technical/medical topics require recent literature; foundational historical/theoretical works do not).
4. **Bias and Purpose:** Distinguish empirical reporting from advocacy, sponsored white papers, or marketing copy; read laterally across independent sources when a claim is contested.

### Literature Reviews
- Organize by **themes, methods, or debates**, not a chronological "Author A said X; Author B said Y" list.
- Show how studies agree, conflict, or leave a specific gap that the current paper addresses.

---

## 2. Using Research: Quoting, Paraphrasing, Summarizing, and Plagiarism

### Choosing the Right Method
| Technique | When to Use | Rules |
|---|---|---|
| **Quoting** | Exact wording matters (definitions, legal/policy text, vivid phrasing, contested claims) | Reproduce word-for-word inside quotation marks (or block quote); introduce with a signal phrase and cite author, year/page. |
| **Paraphrasing** | Specific passage or data point from a source | Rewrite in **fresh sentence structure and vocabulary**, keeping the original meaning and level of detail; cite the source. |
| **Summarizing** | Main argument or findings of a whole section/paper | Condense to core claims in your own words, omitting minor examples; cite the source. |

### Preventing Plagiarism and Patchwriting
- **Patchwriting is plagiarism:** Swapping a few synonyms while keeping the source's clause order or sentence skeleton is not paraphrasing. Either quote the exact phrase in quotation marks or rebuild the sentence from your notes without looking at the original.
- **Common knowledge exception:** Widely established, undisputed facts found across many general references (e.g., water freezes at 0 °C, the UN was founded in 1945) do not need a citation. Specialized findings, statistics, interpretations, and non-obvious dates always need a citation.
- **Block quotes:** Use indented block quotes without surrounding quotation marks when a direct quote meets the style threshold (`40+` words in APA/IEEE, `>4` prose lines in MLA, `50+` words in AMA/ASA, `100+` words or `5+` lines in Chicago).
- **Responsible tool use:** Citation generators and paper checkers frequently misformat corporate authors, DOIs, capitalization, and secondary citations. Always verify generated entries against the official style rules below.

### Writing with Statistics
- Cite every statistic that did not originate from your own study.
- Report **raw counts alongside percentages** when sample sizes are small (`3 of 12 participants, 25%`), state the denominator or comparison group, and distinguish correlation from causation.
- Never extrapolate unprinted precision or invent rounded claims (`nearly doubled`) without the underlying figures.

---

## 3. Citation Style Quick Reference

Use `python scripts/citation_guard.py format --style <style> --source <sources.json>` to generate entries and in-text citations automatically.

### A. APA 7th Edition (Psychology, Education, Social Sciences)
- **Heading:** `References` (alphabetical by first author surname; hanging indent).
- **In-text:** Parenthetical `(Smith, 2020, p. 4)` or narrative `Smith (2020, p. 4)`. Two authors: `(Smith & Lee, 2020)` vs. `Smith and Lee (2020)`. Three or more: `(Smith et al., 2020)`.
- **Journal:** `Author, A. A., & Author, B. B. (2020). Title in sentence case. *Journal Name*, *12*(3), 45–67. https://doi.org/10.xxxx/xxxx`
- **Book:** `Author, A. A. (2020). *Book title in sentence case* (2nd ed.). Publisher.`
- **Webpage:** `Author, A. A. (2020, May 14). *Page title in sentence case*. Site Name. https://example.com`

### B. MLA 9th Edition (Literature, Languages, Humanities)
- **Heading:** `Works Cited` (alphabetical; title case for titles).
- **In-text:** `(Smith 4)` or narrative `Smith ... (4)`. Two authors: `(Smith and Lee 4)`. Three or more: `(Smith et al. 4)`.
- **Journal:** `Author, First, and Second Author. "Article Title in Title Case." *Journal Title*, vol. 12, no. 3, May 2020, pp. 45-67, https://doi.org/10.xxxx/xxxx.`
- **Book:** `Author, First. *Book Title in Title Case*. 2nd ed., Publisher, 2020.`
- **Webpage:** `Author, First. "Page Title in Title Case." *Site Name*, 14 May 2020, example.com.`

### C. Chicago 18th Edition — Notes and Bibliography (History, Arts, Humanities)
- **Heading:** `Bibliography` (alphabetical; title case).
- **In-text:** Superscript note number or markdown footnote `[^1]` leading to a full note on first reference and short note (`Smith, "Short Title," 4.`) thereafter.
- **Journal:** `Author, First. "Article Title in Title Case." *Journal Title* 12, no. 3 (May 2020): 45–67. https://doi.org/10.xxxx/xxxx.`
- **Book:** `Author, First. *Book Title in Title Case*. 2nd ed. Publisher, 2020.` (Chicago 18th drops publisher city for modern books.)
- **Webpage:** `Author, First. "Page Title in Title Case." Site Name. May 14, 2020. https://example.com.`

### D. Chicago 18th Edition — Author-Date (Physical, Natural, and Social Sciences)
- **Heading:** `References` (alphabetical; title case).
- **In-text:** `(Smith 2020, 4)` or `Smith (2020, 4)` — **no comma** between author and year.
- **Journal:** `Author, First. 2020. "Article Title in Title Case." *Journal Title* 12 (3): 45–67. https://doi.org/10.xxxx/xxxx.`
- **Book:** `Author, First. 2020. *Book Title in Title Case*. 2nd ed. Publisher.`

### E. IEEE (Engineering, Computer Science, Electronics)
- **Heading:** `References` (numbered `[1]`, `[2]` in **order of first appearance**, not alphabetical).
- **In-text:** `[1]` or `[1], [2]` inside punctuation (`...as shown in [1].`).
- **Journal:** `[1] A. Author and B. Author, "Article title in sentence case," *Journal Abbrev.*, vol. 12, no. 3, pp. 45–67, May 2020, doi: 10.xxxx/xxxx.`
- **Book:** `[1] A. Author, *Book Title*, 2nd ed. City: Publisher, 2020.`
- **Webpage:** `[1] A. Author, "Page title," Site Name. Accessed: May 14, 2020. [Online]. Available: https://example.com`

### F. AMA 11th Edition (Medicine, Health, Biological Sciences)
- **Heading:** `References` (numbered `1.`, `2.` in **order of first appearance**).
- **In-text:** Superscript Arabic numerals placed outside periods and commas (`...as reported earlier.¹`).
- **Journal:** `1. Author AA, Author BB. Article title in sentence case. *J Abbrev*. 2020;12(3):45-67. doi:10.xxxx/xxxx`
- **Book:** `1. Author AA. *Book Title*. 2nd ed. Publisher; 2020.`

### G. ASA 7th Edition (Sociology)
- **Heading:** `References` (alphabetical; title case).
- **In-text:** `(Smith 2020:4)` or `Smith (2020:4)` — **colon** before page numbers, no space.
- **Journal:** `Author, First, and Second Author. 2020. "Article Title in Title Case." *Journal Title* 12(3):45–67. https://doi.org/10.xxxx/xxxx.`
- **Book:** `Author, First. 2020. *Book Title in Title Case*. City: Publisher.`
