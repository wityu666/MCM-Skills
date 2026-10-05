"""Synthetic mechanics checks; supplied flags are not real paper or visual reviews."""
import json
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

from pypdf import PdfWriter

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from init_project import initialize
from freeze_artifacts import create, digest
from audit_delivery import audit as audit_english
from audit_bilingual_delivery import audit_bilingual, FLAGS


class BilingualDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        initialize(self.root, 2027, 'practice', 'B')
        self.review = self.root / 'verification/bilingual_review.json'

    def save_review(self, data):
        self.review.write_text(json.dumps(data), encoding='utf-8')

    def fixture(self):
        (self.root / 'results/answer.json').write_text('{"answer":2}', encoding='utf-8')
        create(self.root, 'results/run_manifest.json', 'F1', ['results/answer.json'])
        for language, count in [('zh', 2), ('en', 1)]:
            (self.root / f'paper/{language}/report.tex').write_text(
                r'\documentclass{article}\begin{document}' + language + r'\end{document}', encoding='utf-8')
            writer = PdfWriter()
            for _ in range(count):
                writer.add_blank_page(width=595, height=842)
            writer.write(self.root / f'paper/{language}/report.pdf')
        layout_path = self.root / 'verification/layout_review.json'
        layout = json.loads(layout_path.read_text())
        for key in layout:
            if key.endswith('_verified'):
                layout[key] = True
        layout.update(status='PASS', pdf_sha256=digest(self.root / 'paper/en/report.pdf'),
                      page_count=1, main_page_count=1, ai_used=False,
                      evidence=['SYNTHETIC TEST INPUT; not an actual visual review'])
        layout_path.write_text(json.dumps(layout), encoding='utf-8')
        (self.root / 'paper/zh/chapter.tex').write_text('SYNTHETIC Chinese chapter dependency', encoding='utf-8')
        create(self.root, 'paper/content_manifest.json', 'P1', [
            'paper/zh/report.tex', 'paper/en/report.tex', 'paper/zh/report.pdf', 'paper/en/report.pdf',
            'paper/zh/chapter.tex'])
        qa = json.loads(self.review.read_text())
        qa.update(status='PASS', freeze_id='F1',
                  result_manifest_sha256=digest(self.root / 'results/run_manifest.json'),
                  zh_page_count=2, zh_page_evidence=[
                      {'page': page, 'evidence': ['SYNTHETIC TEST INPUT']} for page in [1, 2]],
                  evidence=['SYNTHETIC TEST INPUT; not an actual language review'], unresolved=[])
        for name in FLAGS:
            qa[name] = True
        for name, relative in [('zh_source', 'paper/zh/report.tex'), ('en_source', 'paper/en/report.tex'),
                               ('zh_pdf', 'paper/zh/report.pdf'), ('en_pdf', 'paper/en/report.pdf'),
                               ('english_layout_review', 'verification/layout_review.json'),
                               ('paper_content_manifest', 'paper/content_manifest.json')]:
            qa[name] = {'path': relative, 'sha256': digest(self.root / relative)}
        self.save_review(qa)
        return qa

    def failed_checks(self):
        result = audit_bilingual(self.root)
        self.assertEqual(result['status'], 'FAIL')
        return {row['id'] for row in result['checks'] if row['status'] == 'FAIL'}

    def test_initializer_creates_two_empty_language_dirs_and_unreviewed_record(self):
        for language in ['zh', 'en']:
            self.assertEqual(list((self.root / 'paper' / language).iterdir()), [])
        qa = json.loads(self.review.read_text())
        self.assertEqual(qa['status'], 'INCOMPLETE')
        self.assertTrue(all(qa[name] is False for name in FLAGS))
        self.assertEqual(qa['zh_page_evidence'], [])
        self.assertIsNone(qa['zh_page_count'])
        self.assertEqual(json.loads((self.root / 'context.json').read_text())['paper_language'], 'en')

    def test_valid_fixture_gets_static_precheck_only(self):
        self.fixture()
        result = audit_bilingual(self.root)
        self.assertEqual(result['status'], 'PRECHECK_PASS')
        self.assertEqual(result['scope'], 'bilingual_static_preflight_only')
        self.assertEqual(result['official_submission'], 'NOT_SUBMITTED')
        self.assertIn('does not verify language equivalence', result['limitation'])

    def test_unfilled_template_cannot_pass_despite_valid_result_freeze(self):
        (self.root / 'results/x.json').write_text('{}')
        create(self.root, 'results/run_manifest.json', 'F1', ['results/x.json'])
        failed = self.failed_checks()
        self.assertIn('REVIEW_STATUS', failed)
        self.assertIn('TWO_VERSIONS_PRESENT', failed)

    def test_missing_chinese_does_not_invalidate_english_chain_but_blocks_dual_delivery(self):
        self.fixture()
        (self.root / 'paper/zh/report.pdf').unlink()
        self.assertEqual(audit_english(self.root, 'paper/en/report.pdf',
                                      'verification/layout_review.json')['status'], 'PRECHECK_PASS')
        self.assertIn('ZH_PDF_HASH', self.failed_checks())

    def test_chinese_reexport_invalidates_its_review_while_english_is_still_current(self):
        self.fixture()
        pdf = self.root / 'paper/zh/report.pdf'
        with pdf.open('ab') as stream:
            stream.write(b'\n% re-export\n')
        result = audit_bilingual(self.root)
        checks = {row['id']: row['status'] for row in result['checks']}
        self.assertEqual(checks['ZH_PDF_HASH'], 'FAIL')
        self.assertEqual(checks['ENGLISH_PREFLIGHT'], 'PASS')

    def test_changed_result_artifact_or_manifest_invalidates_bilingual_review(self):
        self.fixture()
        (self.root / 'results/answer.json').write_text('{"answer":3}')
        self.assertIn('RESULTS_STABLE', self.failed_checks())
        create(self.root, 'results/run_manifest.json', 'F2', ['results/answer.json'])
        self.assertIn('RESULT_BINDING', self.failed_checks())

    def test_changed_tex_dependency_and_refreeze_cannot_reuse_old_bilingual_record(self):
        self.fixture()
        (self.root / 'paper/zh/chapter.tex').write_text('Changed chapter', encoding='utf-8')
        self.assertIn('PAPER_CONTENT_STABLE', self.failed_checks())
        create(self.root, 'paper/content_manifest.json', 'P2', [
            'paper/zh/report.tex', 'paper/en/report.tex', 'paper/zh/report.pdf', 'paper/en/report.pdf',
            'paper/zh/chapter.tex'])
        self.assertIn('PAPER_CONTENT_MANIFEST_HASH', self.failed_checks())

    def test_unresolved_bilingual_review_cannot_pass(self):
        qa = self.fixture()
        qa['unresolved'] = ['A task is missing from the Chinese version']
        self.save_review(qa)
        self.assertIn('REVIEW_STATUS', self.failed_checks())

    def test_live_deadline_covers_tex_dependencies_even_after_refreeze(self):
        """Synthetic rule times and review flags verify mechanics, not contest compliance."""
        qa = self.fixture()
        stop = datetime.now(timezone.utc) + timedelta(days=1)
        context_path, rules_path = self.root / 'context.json', self.root / 'rules.json'
        context = json.loads(context_path.read_text())
        context.update(mode='live', team_control_number='1234567')
        context_path.write_text(json.dumps(context))
        rules = json.loads(rules_path.read_text())
        rules.update(verification='verified', problem_specific_requirements_status='verified')
        rules['claims']['stop_work_at']['value'] = stop.isoformat()
        rules['claims']['submit_by']['value'] = (stop + timedelta(days=1)).isoformat()
        rules_path.write_text(json.dumps(rules))
        old_pdf = self.root / 'paper/en/report.pdf'
        new_pdf = self.root / 'paper/en/1234567.pdf'
        old_pdf.rename(new_pdf)
        qa['en_pdf']['path'] = 'paper/en/1234567.pdf'
        files = ['paper/zh/report.tex', 'paper/en/report.tex', 'paper/zh/report.pdf',
                 'paper/en/1234567.pdf', 'paper/zh/chapter.tex']
        create(self.root, 'paper/content_manifest.json', 'LIVE-1', files)
        qa['paper_content_manifest']['sha256'] = digest(self.root / 'paper/content_manifest.json')
        self.save_review(qa)
        self.assertEqual(audit_bilingual(self.root, now=stop)['status'], 'PRECHECK_PASS')
        dependency = self.root / 'paper/zh/chapter.tex'
        dependency.write_text('Synthetic post-stop content change', encoding='utf-8')
        post_stop = (stop + timedelta(seconds=1)).timestamp()
        os.utime(dependency, (post_stop, post_stop))
        create(self.root, 'paper/content_manifest.json', 'LIVE-2', files)
        qa['paper_content_manifest']['sha256'] = digest(self.root / 'paper/content_manifest.json')
        self.save_review(qa)
        result = audit_bilingual(self.root, now=stop)
        checks = {row['id']: row['status'] for row in result['checks']}
        self.assertEqual(checks['PAPER_CONTENT_STABLE'], 'PASS')
        self.assertEqual(checks['ENGLISH_PREFLIGHT'], 'PASS')
        self.assertEqual(checks['BILINGUAL_EDIT_WINDOW'], 'FAIL')

    def test_manual_all_pages_flag_cannot_replace_actual_page_records(self):
        qa = self.fixture()
        qa['zh_page_evidence'] = []
        self.save_review(qa)
        self.assertIn('ZH_ALL_PAGE_RECORDS', self.failed_checks())
        qa['zh_page_evidence'] = [{'page': 1, 'evidence': ['synthetic']} for _ in range(2)]
        self.save_review(qa)
        self.assertIn('ZH_ALL_PAGE_RECORDS', self.failed_checks())
        qa['zh_page_count'] = True
        self.save_review(qa)
        self.assertIn('ZH_PAGE_COUNT', self.failed_checks())

    def test_sources_must_be_editable_not_pdf_or_pdf_renamed_to_tex(self):
        qa = self.fixture()
        for relative in ['paper/zh/report.pdf', 'paper/zh/disguised.tex']:
            if relative.endswith('.tex'):
                (self.root / relative).write_bytes((self.root / 'paper/zh/report.pdf').read_bytes())
            qa['zh_source'] = {'path': relative, 'sha256': digest(self.root / relative)}
            self.save_review(qa)
            self.assertIn('ZH_SOURCE_EDITABLE', self.failed_checks())

    def test_word_sources_work_and_pdf_renamed_to_docx_is_rejected(self):
        qa = self.fixture()
        for language in ['zh', 'en']:
            relative = f'paper/{language}/report.docx'
            with ZipFile(self.root / relative, 'w') as document:
                document.writestr('[Content_Types].xml',
                                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                                 '<Override PartName="/word/document.xml" '
                                 'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                                 '</Types>')
                document.writestr('word/document.xml',
                                 '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                                 f'<w:body><w:p><w:r><w:t>Synthetic {language} source</w:t></w:r></w:p></w:body></w:document>')
            qa[f'{language}_source'] = {'path': relative, 'sha256': digest(self.root / relative)}
        content_files = ['paper/zh/report.docx', 'paper/en/report.docx',
                         'paper/zh/report.pdf', 'paper/en/report.pdf']
        create(self.root, 'paper/content_manifest.json', 'WORD-1', content_files)
        qa['paper_content_manifest']['sha256'] = digest(self.root / 'paper/content_manifest.json')
        self.save_review(qa)
        self.assertEqual(audit_bilingual(self.root)['status'], 'PRECHECK_PASS')
        (self.root / 'paper/zh/report.docx').write_bytes((self.root / 'paper/zh/report.pdf').read_bytes())
        qa['zh_source']['sha256'] = digest(self.root / 'paper/zh/report.docx')
        create(self.root, 'paper/content_manifest.json', 'WORD-2', content_files)
        qa['paper_content_manifest']['sha256'] = digest(self.root / 'paper/content_manifest.json')
        self.save_review(qa)
        self.assertIn('ZH_SOURCE_EDITABLE', self.failed_checks())

    def test_copying_one_pdf_into_both_versions_cannot_pass(self):
        qa = self.fixture()
        (self.root / 'paper/zh/report.pdf').write_bytes((self.root / 'paper/en/report.pdf').read_bytes())
        qa['zh_pdf']['sha256'] = digest(self.root / 'paper/zh/report.pdf')
        qa.update(zh_page_count=1, zh_page_evidence=[{'page': 1, 'evidence': ['synthetic']}])
        self.save_review(qa)
        self.assertIn('DISTINCT_ARTIFACTS', self.failed_checks())

    def test_stale_english_layout_blocks_bilingual_precheck(self):
        qa = self.fixture()
        layout = self.root / 'verification/layout_review.json'
        layout_data = json.loads(layout.read_text())
        layout_data['pdf_sha256'] = '0' * 64
        layout.write_text(json.dumps(layout_data))
        qa['english_layout_review']['sha256'] = digest(layout)
        self.save_review(qa)
        self.assertIn('ENGLISH_PREFLIGHT', self.failed_checks())

    def test_cli_output_cannot_replace_chinese_input_or_its_hardlink(self):
        self.fixture()
        pdf = self.root / 'paper/zh/report.pdf'
        original = pdf.read_bytes()
        alias = self.root / 'verification/alias.json'
        os.link(pdf, alias)
        for output in ['paper/zh/report.pdf', 'verification/alias.json']:
            response = subprocess.run([sys.executable, str(SCRIPTS / 'audit_bilingual_delivery.py'),
                                       '--root', str(self.root), '--output', output], capture_output=True)
            self.assertEqual(response.returncode, 2)
            self.assertEqual(pdf.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
