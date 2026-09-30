"""
Verification tests confirming complete, clean resolution of merge conflicts.

Asserts:
1. Complete absence of Git conflict markers (<<<<<<<, =======, >>>>>>>) across all source files.
2. Syntactic validity of all Python files (compiles cleanly).
3. Presence of dual-feature integration in tasks/services.py (Alice notifications + Bob audit logs).
4. Full documentation in README.md, MERGE_CONFLICT_RESOLUTION.md, and commit_history.txt.
"""

import os
import py_compile
from pathlib import Path
import unittest


class MergeConflictResolutionVerificationTest(unittest.TestCase):
    """
    Validates adherence to Deliverables and Success Criteria:
    - Conflict markers completely removed.
    - Code is syntactically valid.
    - Resolution documented in commit message and repository docs.
    """

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_no_residual_git_conflict_markers_in_source_code(self):
        """Ensures all merge conflict markers are cleanly excised from active code."""
        conflict_tokens = [
            "<<<<<<<",
            "=======",
            ">>>>>>>",
        ]
        scanned_count = 0
        for py_path in self.base_dir.rglob("*.py"):
            scanned_count += 1
            content = py_path.read_text(encoding="utf-8")
            for line_no, line in enumerate(content.splitlines(), start=1):
                # Allow docstrings explicitly discussing conflict markers in services.py
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
        """Confirms that both Alice's notification feature and Bob's audit logging are integrated."""
        services_file = self.base_dir / "tasks" / "services.py"
        self.assertTrue(services_file.exists())
        code = services_file.read_text(encoding="utf-8")

        # Developer Alice's feature
        self.assertIn("dispatch_task_notifications", code)
        self.assertIn("NotificationLog", code)

        # Developer Bob's feature
        self.assertIn("record_task_activity_audit", code)
        self.assertIn("AuditLog", code)
        self.assertIn("generate_checksum", code)

        # Resolved coordinator
        self.assertIn("process_task_status_transition", code)

    def test_merge_conflict_resolution_documentation_exists(self):
        """Confirms detailed documentation of conflict analysis, resolution, and verification."""
        doc_file = self.base_dir / "MERGE_CONFLICT_RESOLUTION.md"
        self.assertTrue(doc_file.exists(), "MERGE_CONFLICT_RESOLUTION.md must exist")
        text = doc_file.read_text(encoding="utf-8")

        self.assertIn("feature/task-notifications", text)
        self.assertIn("feature/task-activity-audit", text)
        self.assertIn("Conflict Resolution Strategy", text)
        self.assertIn("Manual Resolution Steps", text)
        self.assertIn("Verification", text)

    def test_commit_history_records_resolution_message(self):
        """Confirms commit history documents the merge commit explaining resolution."""
        history_file = self.base_dir / "commit_history.txt"
        self.assertTrue(history_file.exists(), "commit_history.txt must exist")
        log_text = history_file.read_text(encoding="utf-8")

        self.assertIn("Merge branch 'feature/task-activity-audit'", log_text)
        self.assertIn("Resolve merge conflict", log_text)
        self.assertIn("feature/task-notifications", log_text)
        self.assertIn("feature/task-activity-audit", log_text)


if __name__ == '__main__':
    unittest.main()
