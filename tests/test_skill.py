import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_text  # noqa: E402
import citation_guard  # noqa: E402
import style_learner  # noqa: E402


class TestAnalyzeText(unittest.TestCase):
    def test_flags_heavy_ai_text(self) -> None:
        sample = (
            "Somali cuisine serves as an intricate tapestry of vibrant flavors, "
            "highlighting its enduring legacy. It is not just food, but also a "
            "testament to cultural interplay. Additionally, observers argue that "
            "despite these challenges, it continues to thrive."
        )
        result = analyze_text.analyze(sample)
        self.assertEqual(result["verdict"], "HIGH")
        self.assertGreaterEqual(result["risk_score"], 60)
        categories = {f["category"] for f in result["findings"]}
        self.assertIn("ai_vocabulary", categories)
        self.assertIn("negative_parallelism", categories)
        self.assertIn("superficial_ing", categories)
        self.assertIn("outline_conclusion", categories)

    def test_passes_natural_human_text(self) -> None:
        sample = (
            "We tested three caching layers on a 12-node cluster last Tuesday. "
            "Latency dropped by 40% under read-heavy load, though writes stalled "
            "whenever the queue filled up. That wasn't expected. Still, the trade-off "
            "makes sense for our workload because reads outnumber writes ten to one, "
            "and the memory overhead stayed under 200 MB across all replicas."
        )
        result = analyze_text.analyze(sample)
        self.assertEqual(result["verdict"], "LOW")
        self.assertLess(result["risk_score"], 15)


class TestStyleLearner(unittest.TestCase):
    def test_extract_features_metrics(self) -> None:
        sample = (
            "Short sentence here. Then we wrote a much longer sentence that explains "
            "exactly why the experiment failed after the third trial, even though the "
            "initial calibration looked promising. Didn't expect that!"
        )
        feats = style_learner.extract_features(sample)
        self.assertGreater(feats["word_count"], 25)
        self.assertGreater(feats["sentence_length_std"], 5.0)
        self.assertGreater(feats["contraction_rate_per_1k_words"], 0.0)
        self.assertGreater(feats["punctuation_per_1k_chars"]["exclamation"], 0.0)


class TestCitationGuard(unittest.TestCase):
    SAMPLE_JOURNAL = {
        "type": "journal",
        "authors": ["Jane Smith", "Alex Lee"],
        "year": 2024,
        "month": "May",
        "title": "Adaptive prose evaluation in classrooms",
        "container": "Journal of Writing Analytics",
        "volume": 8,
        "issue": 2,
        "pages": "14-29",
        "doi": "10.1000/jwa.2024.02",
    }

    def test_formats_all_seven_styles(self) -> None:
        for style in citation_guard.STYLES:
            res = citation_guard.build_bibliography([self.SAMPLE_JOURNAL], style, page="18")
            entry = res["entries"][0]
            self.assertEqual(entry["warnings"], [])
            self.assertIn("Smith", entry["reference"])
            self.assertTrue(entry["in_text"])

        apa = citation_guard.build_bibliography([self.SAMPLE_JOURNAL], "apa", page="18")["entries"][0]
        self.assertEqual(apa["in_text"], "(Smith & Lee, 2024, p. 18)")
        self.assertEqual(apa["narrative"], "Smith and Lee (2024, p. 18)")

        asa = citation_guard.build_bibliography([self.SAMPLE_JOURNAL], "asa", page="18")["entries"][0]
        self.assertEqual(asa["in_text"], "(Smith and Lee 2024:18)")

    def test_clean_cited_draft_passes(self) -> None:
        draft = (
            'Writing instruction improves when feedback targets structure rather than surface rules (Smith & Lee, 2024). '
            'As Smith and Lee (2024) noted, "students revised twice as many thesis statements after rubric modeling" (p. 18). '
            'In their sample, revision rates rose by 42% over six weeks (Smith & Lee, 2024).\n\n'
            "## References\n"
            "Smith, J., & Lee, A. (2024). Adaptive prose evaluation in classrooms. *Journal of Writing Analytics*, *8*(2), 14–29.\n"
        )
        res = citation_guard.check_text(draft, style="apa")
        self.assertEqual(res["verdict"], "CLEAN")
        self.assertEqual(res["citation_risk_score"], 0)

    def test_flags_uncited_quote_stats_mixed_styles_and_orphans(self) -> None:
        draft = (
            'The study argued that "students often copy sentence skeletons when paraphrasing under time pressure." '
            "Nearly 68% of respondents reported difficulty citing online sources. "
            "Prior work confirmed this trend (Doe 2021) and (Smith, 2020) [citation needed].\n\n"
            "## Works Cited\n"
            "Zimmer, T. (2019). Unused entry.\n"
            "Adams, B. (2020). Another entry.\n"
        )
        res = citation_guard.check_text(draft, style="apa")
        codes = {f["code"] for f in res["findings"]}
        self.assertEqual(res["verdict"], "HIGH")
        self.assertIn("placeholder_citation", codes)
        self.assertIn("uncited_quote", codes)
        self.assertIn("unsupported_statistic", codes)
        self.assertIn("mixed_citation_styles", codes)
        self.assertIn("orphan_in_text_citation", codes)
        self.assertIn("unsorted_references", codes)
        self.assertIn("heading_mismatch", codes)

    def test_detects_patchwriting_against_source(self) -> None:
        source = (
            "Undergraduate writers frequently rely on patchwriting when synthesizing unfamiliar "
            "disciplinary literature because they lack domain vocabulary to reframe technical claims."
        )
        draft_copied = (
            "Many students frequently rely on patchwriting when synthesizing unfamiliar "
            "disciplinary literature because they lack domain vocabulary (Smith, 2024).\n\n"
            "References\nSmith, J. (2024). Writing study.\n"
        )
        res = citation_guard.check_text(draft_copied, style="apa", source_text=source)
        codes = {f["code"] for f in res["findings"]}
        self.assertIn("unquoted_source_overlap", codes)
        self.assertGreater(res["patchwriting"]["overlap_pct"], 25.0)


if __name__ == "__main__":
    unittest.main()
