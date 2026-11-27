import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_lean.py"
spec = importlib.util.spec_from_file_location("verify_lean", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class AxiomTests(unittest.TestCase):
    def test_no_axioms(self):
        self.assertEqual(
            checker.parse_axioms("'Demo.ok' does not depend on any axioms\n", "Demo.ok"), []
        )

    def test_classical_axioms(self):
        self.assertEqual(
            checker.parse_axioms(
                "Demo.ok : True\n'Demo.ok' depends on axioms: [propext,\n Classical.choice, Quot.sound]\n",
                "Demo.ok"
            ),
            ["propext", "Classical.choice", "Quot.sound"]
        )

    def test_forbidden_axioms(self):
        for axiom in ["sorryAx", "Custom.bad", "Lean.trustCompiler", "Demo._native"]:
            with self.subTest(axiom=axiom), self.assertRaises(checker.CheckError):
                checker.parse_axioms(f"'Demo.ok' depends on axioms: [{axiom}]", "Demo.ok")

    def test_missing_or_duplicate_reports(self):
        valid = "'Demo.ok' does not depend on any axioms\n"
        for output in ["", "'Other' depends on axioms: []", valid + valid]:
            with self.subTest(output=output), self.assertRaises(checker.CheckError):
                checker.parse_axioms(output, "Demo.ok")

    def test_identifier_injection(self):
        for name in ["X\n#eval 1", "A; B", "A..B", "_root_.X", "../A"]:
            with self.subTest(name=name), self.assertRaises(Exception):
                checker.identifier(name)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        (self.project / "lakefile.toml").write_text('name = "Demo"\n')
        self.theorems = ["Demo.ok"]

    def test_missing_lake(self):
        with patch.object(checker.shutil, "which", return_value=None):
            result = checker.verify(self.project, "Demo", self.theorems, 10)
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("not found", result["error"])

    def test_workflow_pass_not_statement_validation(self):
        calls = []
        def fake_run(command, project, timeout):
            calls.append(command)
            if "--version" in command:
                return "Lean (version 4.x)"
            if "build" in command:
                return "Build completed successfully"
            audit = project / command[-1]
            self.assertIn("import Demo\n", audit.read_text())
            self.assertIn("#print axioms Demo.ok", audit.read_text())
            return "Demo.ok : True\n'Demo.ok' does not depend on any axioms\n"

        with patch.object(checker.shutil, "which", return_value="/fake/lake"), \
             patch.object(checker, "run", side_effect=fake_run):
            result = checker.verify(self.project, "Demo", self.theorems, 10)
        self.assertEqual(result["status"], "MECHANICAL_PASS")
        self.assertEqual(result["statement_review"], "REQUIRED")
        self.assertEqual(calls[1][-1], "+Demo")
        self.assertEqual(list(self.project.glob("Lean4Audit_*")), [])

    def test_build_failure_and_sorry(self):
        for build in [checker.CheckError("build failed"), "warning: declaration uses 'sorry'"]:
            with self.subTest(build=build), \
                 patch.object(checker.shutil, "which", return_value="/fake/lake"), \
                 patch.object(checker, "run", side_effect=["Lean", build]):
                result = checker.verify(self.project, "Demo", self.theorems, 10)
            self.assertEqual(result["status"], "FAILED")

    def test_workflow_rejects_bad_axiom(self):
        with patch.object(checker.shutil, "which", return_value="/fake/lake"), \
             patch.object(checker, "run", side_effect=[
                 "Lean", "Build OK", "'Demo.ok' depends on axioms: [sorryAx]"
             ]):
            result = checker.verify(self.project, "Demo", self.theorems, 10)
        self.assertEqual(result["status"], "FAILED")

    def test_all_requested_theorems_must_pass(self):
        with patch.object(checker.shutil, "which", return_value="/fake/lake"), \
             patch.object(checker, "run", side_effect=[
                 "Lean", "Build OK", "'Demo.ok' does not depend on any axioms"
             ]):
            result = checker.verify(self.project, "Demo", ["Demo.ok", "Demo.missing"], 10)
        self.assertEqual(result["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
