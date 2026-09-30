"""
Verification tests confirming complete, clean resolution of merge conflicts for Week 03.

Asserts:
1. Complete absence of Git conflict markers (<<<<<<<, =======, >>>>>>>) across all source files.
2. Syntactic validity of all Python files (compiles cleanly).
3. Presence of dual-feature integration in tasks/services.py (Claire's rate limiting + Dave's retry policy).
4. Documentation in CONTRIBUTING.md covering 3+ real-world conflict scenarios.
5. Commit history in commit_history.txt recording clean resolution message.
"""

from pathlib import Path
import py_compile
import unittest


class Week03MergeConflictResolutionVerificationTest(unittest.TestCase):
    """
    Validates adherence to Deliverables and Success Criteria:
    - Conflict resolved without errors.
    - Conflict markers completely removed.
    - Best practices document covers 3+ scenarios.
    - All changes committed with clear messages.
    """

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_no_residual_git_conflict_markers_in_source_code(self):
        """Ensures all merge conflict markers are cleanly excised from active code."""
        scanned_count = 0
        for py_path in self.base_dir.rglob("*.py"):
            scanned_count += 1
            if py_path.name == "test_conflict_resolution.py":
                continue
            content = py_path.read_text(encoding="utf-8")
            for line_no, line in enumerate(content.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("<<<<<<<") or stripped.startswith(">>>>>>>") or stripped == "=======":
                    self.fail(
                        f"Residual conflict marker found in {py_path.name} at line {line_no}: '{stripped}'"
                    )

        self.assertGreater(scanned_count, 5, "Should scan multiple Python source files")

    def test_python_source_code_syntactically_valid(self):
        """Ensures every Python source file compiles without SyntaxError."""
        for py_path in self.base_dir.rglob("*.py"):
            try:
                py_compile.compile(str(py_path), doraise=True)
            except py_compile.PyCompileError as err:
                self.fail(f"Syntax error found in {py_path.relative_to(self.base_dir)}: {err}")

    def test_tasks_services_implements_both_branches(self):
        """Confirms that both Claire's rate limiting feature and Dave's retry policy are integrated."""
        services_file = self.base_dir / "tasks" / "services.py"
        self.assertTrue(services_file.exists())
        code = services_file.read_text(encoding="utf-8")

        # Developer Claire's feature
        self.assertIn("check_rate_limit", code)
        self.assertIn("RateLimitLog", code)

        # Developer Dave's feature
        self.assertIn("execute_with_retry_policy", code)
        self.assertIn("calculate_exponential_backoff", code)
        self.assertIn("RetryPolicyLog", code)

        # Resolved coordinator
        self.assertIn("execute_task_pipeline", code)

    def test_contributing_best_practices_document_covers_three_plus_scenarios(self):
        """Confirms CONTRIBUTING.md exists and covers 3+ conflict scenarios."""
        contributing_file = self.base_dir / "CONTRIBUTING.md"
        self.assertTrue(contributing_file.exists(), "CONTRIBUTING.md must exist")
        text = contributing_file.read_text(encoding="utf-8")

        # Must cover multiple realistic scenarios
        self.assertIn("Scenario 1", text)
        self.assertIn("Scenario 2", text)
        self.assertIn("Scenario 3", text)

        # Must cover branching workflows and git practices
        self.assertIn("Conventional Commits", text)
        self.assertIn("Pull Request", text)
        self.assertIn("git merge", text)

    def test_commit_history_records_resolution_message(self):
        """Confirms commit history documents the merge commit explaining resolution."""
        history_file = self.base_dir / "commit_history.txt"
        self.assertTrue(history_file.exists(), "commit_history.txt must exist")
        log_text = history_file.read_text(encoding="utf-8")

        self.assertIn("Merge branch 'feature/task-retry-policy'", log_text)
        self.assertIn("Resolve merge conflict", log_text)
        self.assertIn("feature/task-rate-limiting", log_text)
        self.assertIn("feature/task-retry-policy", log_text)


if __name__ == '__main__':
    unittest.main()
