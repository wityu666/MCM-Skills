"""Behavior tests for the numeric-binding CLI with actual temporary source files."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_numeric_bindings.py"


class NumericBindingsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        (self.root / "values.csv").write_text("x,y\n1.5,4\n2.5,8\n", encoding="utf-8")
        (self.root / "values.json").write_text(
            json.dumps({"a": [{"b": 7.25}], "large": 9007199254740993}), encoding="utf-8"
        )

    def binding(self, **updates):
        item = {"id": "N-1", "file": "values.csv", "selector": {"row": 0, "column": "x"},
                "expected": 1.5, "abs_tol": 0, "rel_tol": 0, "unit": "kg"}
        item.update(updates)
        return item

    def run_registry(self, registry):
        path = self.root / "registry.json"
        path.write_text(registry if isinstance(registry, str) else json.dumps(registry),
                        encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), "--bindings", "registry.json",
             "--output", "review/report.json"], capture_output=True, text=True, check=False
        )
        self.assertNotIn("Traceback", result.stderr)
        report = json.loads((self.root / "review/report.json").read_text(encoding="utf-8"))
        return result, report

    def test_real_csv_json_and_source_hash_pass(self):
        items = [self.binding(), self.binding(id="N-2", selector={"row": 1, "column": "y"},
                                             expected=8, unit="USD"),
                 self.binding(id="N-3", file="values.json", selector={"keys": ["a", 0, "b"]},
                              expected=7.25, unit="1")]
        result, report = self.run_registry({"freeze_id": "F-1", "run_id": "R-1", "bindings": items})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["freeze_id"], "F-1")
        self.assertEqual(report["run_id"], "R-1")
        self.assertEqual([item["actual"] for item in report["results"]], [1.5, 8, 7.25])
        self.assertEqual([item["unit"] for item in report["results"]], ["kg", "USD", "1"])
        for item in report["results"]:
            source = self.root / item["source_path"]
            self.assertEqual(item["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertNotEqual(item["source_sha256"], report["registry_sha256"])

    def test_difference_fails_and_cli_is_nonzero(self):
        result, report = self.run_registry({"bindings": [self.binding(expected=1.6)]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["results"][0]["status"], "FAIL")

    def test_declared_relative_and_absolute_tolerance(self):
        result, report = self.run_registry({"bindings": [self.binding(expected=1.5001, abs_tol=.0002),
            self.binding(id="N-2", expected=1.51, rel_tol=.01)]})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["summary"]["PASS"], 2)

    def test_source_is_reread_after_change(self):
        registry = {"bindings": [self.binding()]}
        before, first = self.run_registry(registry)
        self.assertEqual(before.returncode, 0)
        (self.root / "values.csv").write_text("x,y\n9,4\n", encoding="utf-8")
        after, second = self.run_registry(registry)
        self.assertNotEqual(after.returncode, 0)
        self.assertEqual(second["results"][0]["actual"], 9)
        self.assertNotEqual(first["results"][0]["source_sha256"], second["results"][0]["source_sha256"])

    def test_path_traversal_and_absolute_outside_fail(self):
        outside = self.root.parent / "outside.csv"
        outside.write_text("x\n1.5\n", encoding="utf-8")
        for file in ("../outside.csv", str(outside)):
            with self.subTest(file=file):
                result, report = self.run_registry({"bindings": [self.binding(file=file)]})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["results"][0]["status"], "ERROR")
                self.assertIn("outside", report["results"][0]["message"])

    def test_symlink_outside_fails(self):
        outside = self.root.parent / "outside.csv"
        outside.write_text("x\n1.5\n", encoding="utf-8")
        (self.root / "linked.csv").symlink_to(outside)
        result, report = self.run_registry({"bindings": [self.binding(file="linked.csv")]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["status"], "ERROR")

    def test_nonfinite_expected_and_tolerances_fail(self):
        for changes in ({"expected": float("nan")}, {"expected": float("inf")},
                        {"abs_tol": -1}, {"rel_tol": -1}, {"abs_tol": float("nan")},
                        {"expected": True}, {"rel_tol": "0.1"}):
            with self.subTest(changes=changes):
                result, report = self.run_registry({"bindings": [self.binding(**changes)]})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["results"][0]["status"], "ERROR")
                self.assertEqual(report["results"][0]["source_sha256"],
                                 hashlib.sha256((self.root / "values.csv").read_bytes()).hexdigest())

    def test_nonfinite_source_fails(self):
        for file, contents, selector in (("nan.csv", "x\nNaN\n", {"row": 0, "column": "x"}),
                ("nan.json", '{"value":NaN}', {"keys": ["value"]})):
            with self.subTest(file=file):
                (self.root / file).write_text(contents, encoding="utf-8")
                result, report = self.run_registry({"bindings": [self.binding(file=file, selector=selector)]})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["results"][0]["status"], "ERROR")
                self.assertEqual(report["results"][0]["source_sha256"],
                                 hashlib.sha256((self.root / file).read_bytes()).hexdigest())

    def test_empty_missing_or_wrong_bindings_fail(self):
        for registry in ({"bindings": []}, {}, {"bindings": "bad"}, []):
            with self.subTest(registry=registry):
                result, report = self.run_registry(registry)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["status"], "ERROR")
                self.assertTrue(report["errors"])

    def test_duplicate_ids_both_error(self):
        result, report = self.run_registry({"bindings": [self.binding(), self.binding()]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([item["status"] for item in report["results"]], ["ERROR", "ERROR"])

    def test_every_missing_required_field_errors(self):
        for field in self.binding():
            with self.subTest(field=field):
                item = self.binding()
                del item[field]
                result, report = self.run_registry({"bindings": [item]})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("missing required", report["results"][0]["message"])

    def test_invalid_selectors_or_nonobject_item_error(self):
        for selector in ({"row": -1, "column": "x"}, {"row": True, "column": "x"},
                         {"row": 20, "column": "x"}, {"row": 0, "column": "absent"}, []):
            with self.subTest(selector=selector):
                result, report = self.run_registry({"bindings": [self.binding(selector=selector)]})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["results"][0]["status"], "ERROR")
        result, report = self.run_registry({"bindings": [None]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["status"], "ERROR")

    def test_exact_large_integer_comparison_does_not_round_to_pass(self):
        result, report = self.run_registry({"bindings": [self.binding(
            file="values.json", selector={"keys": ["large"]}, expected=9007199254740992)]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["status"], "FAIL")
        self.assertEqual(report["results"][0]["absolute_difference"], 1)

    def test_exponent_span_and_tiny_decimal_do_not_round_to_pass(self):
        for source, expected, abs_tol in (("1e50", -1, 1e50), ("1e-1000100", 0, 0)):
            with self.subTest(source=source):
                (self.root / "values.csv").write_text(f"x\n{source}\n", encoding="utf-8")
                result, report = self.run_registry({"bindings": [self.binding(
                    expected=expected, abs_tol=abs_tol)]})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["results"][0]["status"], "FAIL")
                self.assertNotEqual(report["results"][0]["absolute_difference"], 0)

    def test_json_float_precision_and_underflow_are_preserved(self):
        for value, expected in (("9007199254740993.0", 9007199254740992), ("1e-999", 0)):
            with self.subTest(value=value):
                (self.root / "values.json").write_text('{"value":' + value + '}', encoding="utf-8")
                result, report = self.run_registry({"bindings": [self.binding(
                    file="values.json", selector={"keys": ["value"]}, expected=expected)]})
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(report["results"][0]["status"], "FAIL")

    def test_registry_tiny_expected_is_preserved(self):
        (self.root / "values.csv").write_text("x\n0\n", encoding="utf-8")
        registry = json.dumps({"bindings": [self.binding(expected=0)]})
        result, report = self.run_registry(registry.replace('"expected": 0', '"expected": 1e-999'))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["status"], "FAIL")

    def test_malformed_csv_is_error(self):
        (self.root / "values.csv").write_text('x\n"1', encoding="utf-8")
        result, report = self.run_registry({"bindings": [self.binding(expected=1)]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["status"], "ERROR")

    def test_nul_source_path_keeps_error_report(self):
        result, report = self.run_registry({"bindings": [self.binding(file="bad\0.csv")]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["results"][0]["status"], "ERROR")

    def test_report_output_cannot_escape_root_or_overwrite_input(self):
        registry_path = self.root / "registry.json"
        registry_path.write_text(json.dumps({"bindings": [self.binding()]}), encoding="utf-8")
        original = (self.root / "values.csv").read_bytes()
        for output in ("../outside-report.json", str(self.root.parent / "absolute-report.json"),
                       "registry.json", "values.csv"):
            with self.subTest(output=output):
                result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                    "--bindings", "registry.json", "--output", output],
                    capture_output=True, text=True, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
        self.assertEqual((self.root / "values.csv").read_bytes(), original)
        self.assertFalse((self.root.parent / "outside-report.json").exists())
        self.assertFalse((self.root.parent / "absolute-report.json").exists())

    def test_output_hardlink_cannot_overwrite_source_or_registry(self):
        registry_path = self.root / "registry.json"
        registry_path.write_text(json.dumps({"bindings": [self.binding()]}), encoding="utf-8")
        output = self.root / "hard-report.json"
        for source in (self.root / "values.csv", registry_path):
            with self.subTest(source=source.name):
                original = source.read_bytes()
                output.hardlink_to(source)
                result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                    "--bindings", "registry.json", "--output", "hard-report.json"],
                    capture_output=True, text=True, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(source.read_bytes(), original)
                self.assertEqual(output.read_bytes(), original)
                output.unlink()

    def test_duplicate_json_keys_in_source_are_ambiguous(self):
        (self.root / "values.json").write_text('{"value":99,"value":7.25}', encoding="utf-8")
        result, report = self.run_registry({"bindings": [self.binding(
            file="values.json", selector={"keys": ["value"]}, expected=7.25)]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report["status"], "ERROR")

    def test_duplicate_registry_keys_are_not_last_wins(self):
        text=json.dumps({"bindings":[self.binding()]}).replace('"expected": 1.5','"expected":99,"expected":1.5')
        result,report=self.run_registry(text)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(report["status"],"ERROR")

    def test_ragged_csv_row_is_not_a_valid_record(self):
        for content in ["x,y\n1.5,4,extra\n", "x,y\n1.5\n"]:
            with self.subTest(content=content):
                (self.root/"values.csv").write_text(content,encoding="utf-8")
                result,report=self.run_registry({"bindings":[self.binding()]})
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(report["status"],"ERROR")

    def test_invalid_declared_version_or_freeze_identifiers_error(self):
        for metadata in [{"schema_version":True},{"schema_version":2},{"freeze_id":[]},
                         {"freeze_id":" "},{"run_id":False}]:
            with self.subTest(metadata=metadata):
                result,report=self.run_registry(dict(metadata,bindings=[self.binding()]))
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(report["status"],"ERROR")

    def test_nonfinite_unselected_json_and_registry_metadata_error(self):
        (self.root/"values.json").write_text('{"value":7.25,"bad":Infinity}',encoding="utf-8")
        result,report=self.run_registry({"bindings":[self.binding(file="values.json",
            selector={"keys":["value"]},expected=7.25)]})
        self.assertNotEqual(result.returncode,0)
        result,report=self.run_registry({"metadata":float("nan"),"bindings":[self.binding()]})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(report["status"],"ERROR")

    def test_bad_registry_does_not_overwrite_unrelated_existing_data(self):
        registry=self.root/"registry.json";registry.write_text('{"bindings":[]}',encoding="utf-8")
        source=self.root/"values.json";before=source.read_bytes()
        result=subprocess.run([sys.executable,str(SCRIPT),"--root",str(self.root),"--bindings","registry.json",
            "--output","values.json"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertNotIn("Traceback",result.stderr)
        self.assertEqual(source.read_bytes(),before)

    def test_bad_registry_cannot_replace_existing_hardlink(self):
        registry=self.root/"registry.json";registry.write_text('{"bindings":[]}',encoding="utf-8")
        output=self.root/"alias.json";output.hardlink_to(self.root/"values.csv")
        before=output.read_bytes()
        result=subprocess.run([sys.executable,str(SCRIPT),"--root",str(self.root),"--bindings","registry.json",
            "--output","alias.json"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(output.read_bytes(),before)

    def test_unbounded_precision_request_is_controlled_error(self):
        (self.root/"values.json").write_text('{"value":1e2000000000}',encoding="utf-8")
        result,report=self.run_registry({"bindings":[self.binding(file="values.json",
            selector={"keys":["value"]},expected=1)]})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(report['status'],'ERROR')
        self.assertIn('resource budget',report['results'][0]['message'])


if __name__ == "__main__":
    unittest.main()
