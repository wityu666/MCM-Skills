"""Behavior tests for stale evidence, yearly rules, originals, and PDF page limits."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfWriter

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from init_project import initialize
from freeze_artifacts import create, verify, digest
from audit_delivery import audit


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'project'
        initialize(self.root, 2027, 'practice', 'B')

    def test_review_templates_share_schema_and_do_not_assume_ai_usage(self):
        skills = SCRIPTS.parents[1]
        entry = json.loads((skills / 'mcm-suite/assets/layout-review.json').read_text())
        layout = json.loads((skills / 'mcm-layout-verifier/assets/layout-review.json').read_text())
        self.assertEqual(set(entry), set(layout))
        for template in [entry, layout]:
            self.assertIsNone(template['ai_used'])
            self.assertNotEqual('PASS', template['status'])
            self.assertTrue(all(value is False for key, value in template.items() if key.endswith('_verified')))

    def test_originals_untouched_and_overwrite_refused(self):
        original = self.base / 'original.csv'
        original.write_text('x\n3\n')
        before = original.stat().st_mode
        second = self.base / 'second'
        initialize(second, 2027, 'practice', 'B', [original])
        self.assertEqual(before, original.stat().st_mode)
        self.assertEqual(original.read_bytes(), (second / 'inputs' / original.name).read_bytes())
        self.assertEqual(0, (second / 'inputs' / original.name).stat().st_mode & 0o222)
        with self.assertRaises(ValueError):
            initialize(second, 2027, 'practice')

    def test_unknown_year_remains_unresolved(self):
        other = self.base / 'other'
        initialize(other, 2026, 'reproduce', 'C')
        rules = json.loads((other / 'rules.json').read_text())
        self.assertEqual(2026, rules['year'])
        self.assertEqual('unresolved', rules['verification'])
        self.assertEqual({}, rules['claims'])

    def test_changed_and_missing_artifacts_invalidate_freeze(self):
        result = self.root / 'results' / 'answer.json'
        result.write_text('{"cost":20}')
        create(self.root, 'results/run_manifest.json', 'test-1', ['results/answer.json'])
        self.assertEqual('PASS', verify(self.root, 'results/run_manifest.json')['status'])
        result.write_text('{"cost":21}')
        self.assertEqual('FAIL', verify(self.root, 'results/run_manifest.json')['status'])
        result.unlink()
        self.assertEqual('MISSING', verify(self.root, 'results/run_manifest.json')['checks'][0]['status'])

    def test_freeze_blocks_escape_self_reference_and_duplicate(self):
        outside = self.base / 'outside.txt'
        outside.write_text('secret')
        for files in [['../outside.txt'], ['results/run_manifest.json']]:
            with self.assertRaises(ValueError):
                create(self.root, 'results/run_manifest.json', 'test', files)
        (self.root / 'inside.txt').write_text('data')
        with self.assertRaises(ValueError):
            create(self.root, 'results/run_manifest.json', 'test', ['inside.txt', 'inside.txt'])

    def make_pdf_fixture(self, pages=25, main=None, ai=False):
        """Synthetic blanks test mechanics only; flags are test inputs, not real visual QA."""
        context = json.loads((self.root / 'context.json').read_text())
        context['team_control_number'] = '1234567'
        (self.root / 'context.json').write_text(json.dumps(context))
        writer = PdfWriter()
        for _ in range(pages):
            writer.add_blank_page(width=595, height=842)
        pdf = self.root / 'paper' / '1234567.pdf'
        writer.write(pdf)
        qa = json.loads((self.root / 'verification' / 'layout_review.json').read_text())
        for key, value in qa.items():
            if type(value) is bool:
                qa[key] = True
        main = pages if main is None else main
        qa.update(status='PASS', pdf_sha256=digest(pdf), page_count=pages, main_page_count=main,
                  ai_report_start_page=main + 1 if main < pages else None, ai_used=ai,
                  evidence=['SYNTHETIC TEST INPUT, NOT A REAL REVIEW'])
        review = self.root / 'verification' / 'layout_review.json'
        review.write_text(json.dumps(qa))
        return pdf, review

    def test_25_main_pages_pass_precheck_26_fail(self):
        pdf, review = self.make_pdf_fixture(25)
        self.assertEqual('PRECHECK_PASS', audit(self.root, str(pdf), str(review))['status'])
        pdf, review = self.make_pdf_fixture(26)
        self.assertEqual('FAIL', audit(self.root, str(pdf), str(review))['status'])

    def test_ai_report_exclusion_and_missing_report(self):
        pdf, review = self.make_pdf_fixture(27, main=25, ai=True)
        self.assertEqual('PRECHECK_PASS', audit(self.root, str(pdf), str(review))['status'])
        pdf, review = self.make_pdf_fixture(25, ai=True)
        self.assertEqual('FAIL', audit(self.root, str(pdf), str(review))['status'])

    def test_reexport_invalidates_review(self):
        pdf, review = self.make_pdf_fixture()
        with pdf.open('ab') as f:
            f.write(b'\n% re-exported\n')
        report = audit(self.root, str(pdf), str(review))
        self.assertEqual('FAIL', report['status'])
        self.assertEqual('FAIL', next(x for x in report['checks'] if x['id'] == 'PDF_REVIEW_HASH')['status'])

    def test_unreviewed_template_cannot_pass(self):
        pdf, review = self.make_pdf_fixture()
        qa = json.loads(review.read_text())
        qa['visual_all_pages_verified'] = False
        review.write_text(json.dumps(qa))
        self.assertEqual('FAIL', audit(self.root, str(pdf), str(review))['status'])

    def test_rule_year_mismatch_cannot_pass(self):
        pdf, review = self.make_pdf_fixture()
        rules = json.loads((self.root / 'rules.json').read_text())
        rules['year'] = 2026
        (self.root / 'rules.json').write_text(json.dumps(rules))
        self.assertEqual('FAIL', audit(self.root, str(pdf), str(review))['status'])

    def test_training_does_not_require_inventing_team_number(self):
        pdf, review = self.make_pdf_fixture()
        context = json.loads((self.root / 'context.json').read_text())
        context['team_control_number'] = None
        (self.root / 'context.json').write_text(json.dumps(context))
        renamed = pdf.with_name('practice.pdf')
        pdf.rename(renamed)
        qa = json.loads(review.read_text())
        qa['control_number_each_page_verified'] = False
        review.write_text(json.dumps(qa))
        self.assertEqual('PRECHECK_PASS', audit(self.root, str(renamed), str(review))['status'])

    def test_live_cannot_use_copied_rules_or_unpublished_problem(self):
        pdf, review = self.make_pdf_fixture()
        context = json.loads((self.root / 'context.json').read_text())
        context['mode'] = 'live'
        (self.root / 'context.json').write_text(json.dumps(context))
        report = audit(self.root, str(pdf), str(review))
        self.assertEqual('FAIL', report['status'])
        failures = {x['id'] for x in report['checks'] if x['status'] == 'FAIL'}
        self.assertIn('RULE_REFRESH', failures)
        self.assertIn('PROBLEM_RULES', failures)

    def test_unverified_rule_is_not_silently_assumed(self):
        pdf, review = self.make_pdf_fixture()
        rules = json.loads((self.root / 'rules.json').read_text())
        rules['claims']['max_main_pages']['status'] = 'unresolved'
        (self.root / 'rules.json').write_text(json.dumps(rules))
        with self.assertRaises(ValueError):
            audit(self.root, str(pdf), str(review))


if __name__ == '__main__':
    unittest.main()
