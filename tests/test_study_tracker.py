"""Tests for the Security+ study progress tracker."""
import tempfile
import unittest
from pathlib import Path

from study_tracker import load_progress, render_progress, set_note, set_status


class StudyTrackerTests(unittest.TestCase):
    def test_status_and_note_persist(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "progress.json"
            set_status("1", "reviewed", path)
            set_note("1", "Review CIA triad and control types.", path)
            data = load_progress(path)
            self.assertEqual(data["domains"]["1"]["status"], "reviewed")
            self.assertIn("CIA triad", data["domains"]["1"]["note"])
            self.assertIn("1/5", render_progress(path))

    def test_invalid_domain_and_long_note_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "progress.json"
            with self.assertRaises(ValueError):
                set_status("6", "reviewed", path)
            with self.assertRaises(ValueError):
                set_note("2", "x" * 501, path)


if __name__ == "__main__":
    unittest.main()
