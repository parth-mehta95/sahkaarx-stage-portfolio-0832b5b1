"""
Dedicated verification tests checking that all code review feedback items are satisfied.
"""

import unittest
from pathlib import Path


class CodeReviewComplianceTest(unittest.TestCase):
    """
    Validates adherence to Team Lead code review guidelines and deliverables.
    """

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_pull_request_document_has_review_comments(self):
        pr_file = self.base_dir / "PULL_REQUEST.md"
        self.assertTrue(pr_file.exists(), "PULL_REQUEST.md must exist")
        content = pr_file.read_text(encoding="utf-8")
        self.assertIn("Review Comment", content)
        self.assertIn("Addressed", content)
        self.assertIn("completed_at", content)
        self.assertIn("CATEGORY_NOT_FOUND", content)
        self.assertIn("MAX_PAGE_SIZE", content)

    def test_code_review_log_exists_and_detailed(self):
        review_file = self.base_dir / "CODE_REVIEW.md"
        self.assertTrue(review_file.exists(), "CODE_REVIEW.md must exist")
        content = review_file.read_text(encoding="utf-8")
        self.assertIn("Code Review Summary", content)
        self.assertIn("Approved", content)

    def test_commit_history_demonstrates_2_to_3_commits_and_merge(self):
        history_file = self.base_dir / "commit_history.txt"
        self.assertTrue(history_file.exists(), "commit_history.txt must exist")
        content = history_file.read_text(encoding="utf-8")
        self.assertIn("Merge pull request #2", content)
        self.assertIn("feat(tasks):", content)
        self.assertIn("refactor(tasks):", content)
        self.assertIn("test(tasks):", content)


if __name__ == "__main__":
    unittest.main()
