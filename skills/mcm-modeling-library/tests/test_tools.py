"""Real JSON/CLI fixtures for lookup and structural contract boundaries."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


query = load('query_review', 'query_models.py')
contract_tool = load('contract_review', 'validate_model_contract.py')


def card(identifier='ml-svm', name='Support vector classification'):
    return dict(id=identifier, name=name, family='machine-learning', kind='model',
                aliases=['SVM'], assumptions=['Declared labels'], purpose='Classification',
                knowledge_level='INDEXED_ONLY')


def frozen():
    result = json.loads((ROOT / 'assets/model-contract.json').read_text())
    result.update(status='FROZEN', freeze_id='TEST-F',
                  task=dict(request='Find feasible allocation', outputs=['plan'], acceptance=['capacity']),
                  problem_evidence=['Supplied task'],
                  allowed_data=dict(model_inputs=['capacity'], background_only=['context'], excluded=['future']),
                  variables=[dict(name='x', meaning='quantity', unit='items', domain='integer', source='capacity')],
                  models=[dict(model_id='M', baseline='known feasible plan', core='Ax<=b', outputs=['plan'], input_sources=['capacity'])],
                  validation_plan=[dict(check='capacity residual', method='independent arithmetic', expected=0)])
    return result


class ToolsTest(unittest.TestCase):
    def cli(self, filename, text, *args):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fixture.json'
            path.write_text(text)
            command = [sys.executable, '-B', str(ROOT / 'scripts' / filename)]
            command += ['--catalog', str(path)] if filename == 'query_models.py' else [str(path)]
            proc = subprocess.run(command + list(args), capture_output=True, text=True)
            self.assertNotIn('Traceback', proc.stderr)
            return proc.returncode, json.loads(proc.stdout)

    def test_alias_and_full_catalog_keep_candidate_scope(self):
        self.assertEqual(query.search([card()], 'SVM')[0]['id'], 'ml-svm')
        code, result = self.cli('query_models.py', (ROOT / 'assets/catalog.json').read_text(), '--id', 'opt-milp', '--full')
        self.assertEqual(code, 0)
        self.assertEqual(result['results'][0]['knowledge_level'], 'THEORY_GUIDE_REVIEWED')
        self.assertIn('not a suitability', result['note'])

    def test_bad_card_types_and_duplicates_are_controlled(self):
        for cards in ([card(name=7)], [card(), card()], [None], [dict(card(), aliases='SVM')],
                      [dict(card(), assumptions=[None])], [dict(card(), knowledge_level='PASS')]):
            with self.subTest(cards=cards), self.assertRaises(ValueError):
                query.search(cards, 'SVM')
        code, result = self.cli('query_models.py', json.dumps({'cards': [card(name=7)]}), '--query', 'SVM')
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'ERROR')

    def test_lookup_missing_id_and_invalid_api_limit(self):
        with self.assertRaises(ValueError): query.search([card()], identifier='missing')
        with self.assertRaises(ValueError): query.search([card()], limit=-1)

    def test_duplicate_json_keys_and_nonfinite_catalog_fail(self):
        for text in ('{"cards":[],"cards":[]}', json.dumps({'cards': [dict(card(), metadata=float('nan'))]}),
                     json.dumps({'cards': [dict(card(), metadata=1)]}).replace('"metadata": 1', '"metadata": 1e999')):
            with self.subTest(text=text):
                self.assertNotEqual(self.cli('query_models.py', text)[0], 0)
    def test_excessively_nested_json_fails_without_traceback(self):
        text='['*2000+'0'+']'*2000
        for script in ('query_models.py','validate_model_contract.py'):
            self.assertNotEqual(self.cli(script,text)[0],0)

    def test_frozen_contract_and_zero_expected_value(self):
        report = contract_tool.validate(frozen())
        self.assertEqual(report['status'], 'CONTRACT_PRECHECK_PASS')
        self.assertIn('Structural', report['scope'])

    def test_draft_template_remains_valid_but_wrong_types_do_not(self):
        draft = json.loads((ROOT / 'assets/model-contract.json').read_text())
        self.assertEqual(contract_tool.validate(draft)['status'], 'CONTRACT_PRECHECK_PASS')
        for key, value in [('variables', {}), ('validation_plan', None), ('models', 'model'),
                           ('task', []), ('schema_version', 99), ('allowed_data', [])]:
            with self.subTest(key=key):
                self.assertEqual(contract_tool.validate(dict(draft, **{key: value}))['status'], 'FAIL')

    def test_source_roles_are_enforced_even_with_valid_structure(self):
        data = frozen()
        data['models'][0]['input_sources'] = ['future']
        self.assertEqual(contract_tool.validate(data)['status'], 'FAIL')
        data = frozen()
        data['allowed_data']['background_only'].append('capacity')
        self.assertEqual(contract_tool.validate(data)['status'], 'FAIL')

    def test_truthy_wrong_frozen_model_or_unit_types_do_not_pass(self):
        for key, value in [('model_id', 7), ('core', True), ('outputs', True)]:
            data = frozen()
            data['models'][0][key] = value
            with self.subTest(key=key): self.assertEqual(contract_tool.validate(data)['status'], 'FAIL')
        data = frozen()
        data['variables'][0]['unit'] = 7
        self.assertEqual(contract_tool.validate(data)['status'], 'FAIL')

    def test_nonfinite_and_duplicate_key_contracts_fail_cli(self):
        data = frozen()
        data['uncertainty'] = [{'value': float('nan')}]
        self.assertEqual(contract_tool.validate(data)['status'], 'FAIL')
        for text in (json.dumps(data), '{"schema_version":1,"schema_version":2}',
                     json.dumps(dict(frozen(), uncertainty=[1])).replace('"uncertainty": [1]', '"uncertainty": [1e999]')):
            with self.subTest(text=text):
                self.assertNotEqual(self.cli('validate_model_contract.py', text)[0], 0)


if __name__ == '__main__': unittest.main()
