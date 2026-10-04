"""Regressions for malformed metadata and input-preserving writes."""
import importlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from init_project import initialize
from freeze_artifacts import create, verify
from audit_delivery import audit
workflow_spec = importlib.util.spec_from_file_location('mcm_workflow_fixture', Path(__file__).with_name('test_workflow.py'))
workflow = importlib.util.module_from_spec(workflow_spec)
workflow_spec.loader.exec_module(workflow)


class FreezeSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        (self.root / 'a.txt').write_bytes(b'x')

    def test_manifest_hardlink_to_input_never_overwrites_it(self):
        alias = self.root / 'run_manifest.json'
        os.link(self.root / 'a.txt', alias)
        with self.assertRaises(ValueError):
            create(self.root, 'run_manifest.json', 'F1', ['a.txt'])
        self.assertEqual((self.root / 'a.txt').read_bytes(), b'x')

    def test_existing_unrelated_manifest_target_is_preserved(self):
        target = self.root / 'existing.json'
        target.write_bytes(b'{"important":1}')
        with self.assertRaises(ValueError):
            create(self.root, target.name, 'F1', ['a.txt'])
        self.assertEqual(target.read_bytes(), b'{"important":1}')

    def test_created_manifest_can_be_refreshed_without_touching_inputs(self):
        create(self.root, 'run_manifest.json', 'F1', ['a.txt'])
        create(self.root, 'run_manifest.json', 'F2', ['a.txt'])
        self.assertEqual(verify(self.root, 'run_manifest.json')['freeze_id'], 'F2')
        self.assertEqual((self.root / 'a.txt').read_bytes(), b'x')

    def test_manifest_structure_and_nonfinite_metadata_are_rejected(self):
        original = create(self.root, 'run_manifest.json', 'F1', ['a.txt'])
        cases = [dict(original, schema_version=True), dict(original, freeze_id=3),
                 dict(original, files=True), dict(original, metadata=float('nan'))]
        for value in (True, 1.0, -1, float('inf')):
            cases.append(dict(original, files=[dict(original['files'][0], bytes=value)]))
        for value in cases:
            with self.subTest(value=value):
                (self.root/'run_manifest.json').write_text(json.dumps(value))
                with self.assertRaises((ValueError, TypeError)):
                    verify(self.root, 'run_manifest.json')

    def test_duplicate_json_keys_are_not_silently_last_wins(self):
        data = create(self.root, 'run_manifest.json', 'F1', ['a.txt'])
        text = json.dumps(data).replace('"freeze_id": "F1"', '"freeze_id":"bad", "freeze_id":"F1"')
        (self.root/'run_manifest.json').write_text(text)
        with self.assertRaises(ValueError):
            verify(self.root, 'run_manifest.json')

    def test_absolute_manifest_entry_is_not_a_project_relative_record(self):
        data = create(self.root, 'run_manifest.json', 'F1', ['a.txt'])
        data['files'][0]['path'] = str(self.root/'a.txt')
        (self.root/'run_manifest.json').write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            verify(self.root, 'run_manifest.json')

    def test_file_iterators_keep_compatibility_but_empty_ones_fail(self):
        create(self.root,'run_manifest.json','F1',iter(['a.txt']))
        self.assertEqual(verify(self.root,'run_manifest.json')['status'],'PASS')
        with self.assertRaises(ValueError):
            create(self.root,'empty.json','F2',iter([]))
        self.assertFalse((self.root/'empty.json').exists())


class InitializeSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def test_invalid_programmatic_context_is_rejected_before_writes(self):
        cases = [(2027.0,'practice','B','python'),(2027,'bogus','B','python'),
                 (2027,'practice','D','python'),(2027,'practice','B','javascript')]
        for i, args in enumerate(cases):
            root = self.base/f'case-{i}'
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    initialize(root, args[0], args[1], args[2], implementation=args[3])
                self.assertFalse(root.exists())

    def test_bad_asset_does_not_leave_half_initialized_project(self):
        package = self.base/'package'
        (package/'assets').mkdir(parents=True)
        (package/'scripts').mkdir()
        (package/'assets/rules-2027.json').write_text('[]')
        (package/'assets/layout-review.json').write_text('{"status":"INCOMPLETE"}')
        root = self.base/'project'
        module = importlib.import_module('init_project')
        with patch.object(module, '__file__', str(package/'scripts/init_project.py')):
            with self.assertRaises((ValueError, TypeError)):
                initialize(root,2027,'practice','B')
        self.assertFalse(root.exists())

    def test_existing_empty_symlink_root_is_not_initialized_through_alias(self):
        target = self.base/'target';target.mkdir()
        alias = self.base/'alias';alias.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            initialize(alias,2027,'practice','B')
        self.assertEqual(list(target.iterdir()),[])

    def test_new_contents_created_during_initialization_are_preserved(self):
        root=self.base/'project';original=self.base/'source.txt';original.write_text('source')
        real_copy=__import__('shutil').copyfile
        def concurrent_write(source,target):
            result=real_copy(source,target)
            root.mkdir()
            (root/'user-note.txt').write_text('keep')
            return result
        with patch('init_project.shutil.copyfile',side_effect=concurrent_write):
            with self.assertRaises(ValueError):
                initialize(root,2027,'practice','B',[original])
        self.assertEqual((root/'user-note.txt').read_text(),'keep')
        self.assertEqual(list(root.iterdir()),[root/'user-note.txt'])
        self.assertFalse(list(self.base.glob('.mcm-init-*')))


class AuditSafetyTests(unittest.TestCase):
    setUp = workflow.WorkflowTests.setUp
    make_pdf_fixture = workflow.WorkflowTests.make_pdf_fixture
    def rejects(self,pdf,review):
        try:
            return audit(self.root,str(pdf),str(review))['status'] != 'PRECHECK_PASS'
        except (ValueError,TypeError):
            return True

    def test_invalid_mode_does_not_take_training_shortcut(self):
        pdf,review=self.make_pdf_fixture()
        context=json.loads((self.root/'context.json').read_text());context['mode']='bogus'
        (self.root/'context.json').write_text(json.dumps(context))
        self.assertTrue(self.rejects(pdf,review))

    def test_infinite_file_size_limit_cannot_pass(self):
        pdf,review=self.make_pdf_fixture()
        rules=json.loads((self.root/'rules.json').read_text())
        rules['claims']['max_file_mb_exclusive']['value']=float('inf')
        (self.root/'rules.json').write_text(json.dumps(rules))
        self.assertTrue(self.rejects(pdf,review))

    def test_boolean_physical_page_count_cannot_pass_as_one(self):
        pdf,review=self.make_pdf_fixture(pages=1)
        qa=json.loads(review.read_text());qa['page_count']=True;review.write_text(json.dumps(qa))
        self.assertTrue(self.rejects(pdf,review))

    def test_boolean_year_and_schema_cannot_pass(self):
        pdf,review=self.make_pdf_fixture()
        context=json.loads((self.root/'context.json').read_text());rules=json.loads((self.root/'rules.json').read_text())
        context.update(year=True,schema_version=True);rules.update(year=True,schema_version=True)
        (self.root/'context.json').write_text(json.dumps(context));(self.root/'rules.json').write_text(json.dumps(rules))
        self.assertTrue(self.rejects(pdf,review))

    def test_output_hardlink_to_pdf_is_rejected_without_mutation(self):
        pdf,review=self.make_pdf_fixture()
        original=pdf.read_bytes();target=self.root/'verification/alias.json';os.link(pdf,target)
        result=subprocess.run([sys.executable,str(SCRIPTS/'audit_delivery.py'),'--root',str(self.root),
            '--pdf',str(pdf),'--review',str(review),'--output',str(target)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertNotIn('Traceback',result.stderr)
        self.assertEqual(pdf.read_bytes(),original)

    def test_error_run_replaces_previous_precheck_report_with_error(self):
        pdf,review=self.make_pdf_fixture();output=self.root/'verification/preflight.json'
        args=[sys.executable,str(SCRIPTS/'audit_delivery.py'),'--root',str(self.root),
              '--pdf',str(pdf),'--review',str(review),'--output',str(output)]
        self.assertEqual(subprocess.run(args,capture_output=True).returncode,0)
        context=json.loads((self.root/'context.json').read_text());context['mode']='bad'
        (self.root/'context.json').write_text(json.dumps(context))
        self.assertEqual(subprocess.run(args,capture_output=True).returncode,2)
        report=json.loads(output.read_text())
        self.assertEqual(report['status'],'ERROR')
        self.assertEqual(report['official_submission'],'NOT_SUBMITTED')

    def test_static_report_hashes_its_actual_metadata_inputs(self):
        from freeze_artifacts import digest
        pdf,review=self.make_pdf_fixture();result=audit(self.root,str(pdf),str(review))
        self.assertEqual(result['context_sha256'],digest(self.root/'context.json'))
        self.assertEqual(result['rules_sha256'],digest(self.root/'rules.json'))
        self.assertEqual(result['review_sha256'],digest(review))


if __name__=='__main__':
    unittest.main()
