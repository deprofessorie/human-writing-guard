import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_text  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
