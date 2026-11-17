# Agent Instructions — Human Writing Guard

Read [SKILL.md](SKILL.md) before drafting or editing any substantive prose where AI detection or plagiarism is prohibited (academic journals, school/university assignments, project descriptions, technical documentation, formal reviews, and emails).

## Quick Commands

1. Load the user's learned writing fingerprint:
   ```bash
   python scripts/style_learner.py show
   ```
2. Learn from a user-provided sample or edited draft:
   ```bash
   python scripts/style_learner.py learn --file <sample.txt> --domain <domain>
   ```
3. Audit your draft before returning it to the user:
   ```bash
   python scripts/analyze_text.py --file <draft.txt>
   ```

Do not apply these prose rules to casual conversation, shell commands, or pure code generation.
