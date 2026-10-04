"""Isolated evidence files, declared scope, and real output protection checks."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts/check_claims.py'
spec = importlib.util.spec_from_file_location('claims_review', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClaimsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'root'
        self.root.mkdir()
        self.proof = self.root / 'evidence.txt'
        self.proof.write_text('Synthetic evidence; labels alone do not establish mathematical truth.\n')
        self.ledger_path = self.root / 'ledger.json'
        self.ledger = dict(freeze_id='F', evidence=[dict(id='E', file='evidence.txt',
            sha256=hashlib.sha256(self.proof.read_bytes()).hexdigest(), type='hypothesis_test', status='PASS', freeze_id='F')],
            claims=[dict(id='C', statement='Declared synthetic result', location='p1', strength='significant',
            scope='synthetic fixture only', evidence_ids=['E'], test_method='declared test',
            effect_size=0, threshold=.05, sample_scope='synthetic sample')])

    def tearDown(self): self.tmp.cleanup()

    def cli(self, ledger=None, output=None, raw=None):
        self.ledger_path.write_text(raw if raw is not None else json.dumps(self.ledger if ledger is None else ledger))
        command = [sys.executable, '-B', str(SCRIPT), '--root', str(self.root), '--ledger', 'ledger.json']
        if output is not None: command += ['--output', str(output)]
        proc = subprocess.run(command, capture_output=True, text=True)
        self.assertNotIn('Traceback', proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def test_valid_zero_effect_and_real_output_readback(self):
        code, result = self.cli(output='reports/check.json')
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'CLAIM_PRECHECK_PASS')
        self.assertIn('Evidence contents', result['scope'])
        self.assertEqual(json.loads((self.root / 'reports/check.json').read_text()), result)

    def test_nan_inf_and_duplicate_json_key_fail(self):
        for number in (float('nan'), float('inf')):
            ledger = copy.deepcopy(self.ledger)
            ledger['claims'][0]['effect_size'] = number
            self.assertEqual(module.check(self.root, ledger)['status'], 'FAIL')
            self.assertNotEqual(self.cli(ledger)[0], 0)
        self.assertNotEqual(self.cli(raw='{"freeze_id":"F","freeze_id":"G","claims":[],"evidence":[]}')[0], 0)
        raw = json.dumps(self.ledger).replace('"effect_size": 0', '"effect_size": 1e999')
        self.assertNotEqual(self.cli(raw=raw)[0], 0)

    def test_blank_and_duplicate_ids_fail(self):
        for ledger in (dict(self.ledger, claims=[dict(self.ledger['claims'][0], id=' ')]),
                       dict(self.ledger, claims=self.ledger['claims'] * 2),
                       dict(self.ledger, evidence=self.ledger['evidence'] * 2)):
            with self.subTest(ledger=ledger): self.assertNotEqual(self.cli(ledger)[0], 0)
    def test_empty_or_boolean_significance_declarations_do_not_replace_zero(self):
        for value in ([], {}, True, False, ' '):
            ledger = copy.deepcopy(self.ledger)
            ledger['claims'][0]['effect_size'] = value
            with self.subTest(value=value): self.assertNotEqual(self.cli(ledger)[0], 0)

    def test_referenced_failed_stale_missing_changed_or_wrong_type_fails(self):
        for key, value in [('status', 'FAIL'), ('freeze_id', 'OLD'), ('file', 'missing.txt'),
                           ('sha256', '0'*64), ('type', 'in_sample')]:
            ledger = copy.deepcopy(self.ledger)
            ledger['evidence'][0][key] = value
            with self.subTest(key=key): self.assertNotEqual(self.cli(ledger)[0], 0)

    def test_unused_stale_evidence_does_not_validate_or_block_report(self):
        ledger = copy.deepcopy(self.ledger)
        ledger['evidence'].append(dict(ledger['evidence'][0], id='UNUSED', file='missing.txt', freeze_id='OLD'))
        self.assertEqual(self.cli(ledger)[0], 0)
        ledger['evidence'][-1]['sha256'] = 'malformed'
        self.assertNotEqual(self.cli(ledger)[0], 0)

    def test_output_cannot_escape_or_overwrite_source_and_evidence(self):
        original_proof = self.proof.read_bytes()
        for output in ('../outside.json', 'ledger.json', 'evidence.txt'):
            with self.subTest(output=output): self.assertNotEqual(self.cli(output=output)[0], 0)
        self.assertFalse((self.root.parent / 'outside.json').exists())
        self.assertEqual(self.proof.read_bytes(), original_proof)
        self.assertEqual(json.loads(self.ledger_path.read_text()), self.ledger)

    def test_hardlink_and_symlink_output_do_not_damage_inputs(self):
        hard = self.root / 'hard.json'
        os.link(self.proof, hard)
        self.assertNotEqual(self.cli(output='hard.json')[0], 0)
        linked = self.root / 'linked.json'
        linked.symlink_to(self.proof)
        self.assertNotEqual(self.cli(output='linked.json')[0], 0)
        self.assertEqual(hashlib.sha256(self.proof.read_bytes()).hexdigest(), self.ledger['evidence'][0]['sha256'])

    def test_evidence_path_traversal_and_bad_structure_fail_without_crash(self):
        for ledger in ([], dict(self.ledger, evidence=[None]),
                       dict(self.ledger, evidence=[dict(self.ledger['evidence'][0], file='../outside.txt')])):
            with self.subTest(ledger=ledger): self.assertNotEqual(self.cli(ledger)[0], 0)
        self.assertNotEqual(self.cli(raw='['*2000+'0'+']'*2000)[0],0)

    def test_unreported_hypothesis_can_continue_without_result_evidence(self):
        ledger = dict(freeze_id='F', evidence=[], claims=[dict(self.ledger['claims'][0],
                      reported=False, strength='hypothesis', evidence_ids=[])])
        self.assertEqual(self.cli(ledger)[0], 0)


if __name__ == '__main__': unittest.main()
