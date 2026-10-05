"""Regression checks for bilingual discovery and accidental acronym matches."""
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location('query_matching_review', ROOT / 'scripts/query_models.py')
query = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(query)
CATALOG = json.loads((ROOT / 'assets/catalog.json').read_text())['cards']


def fixture(identifier, alias, family='simulation'):
    return dict(id=identifier, name=alias, aliases=[alias], family=family,
                purpose='Declared model', assumptions=['Declared inputs'],
                kind='model', knowledge_level='THEORY_GUIDE_REVIEWED')


def ids(text, **kwargs):
    return [card['id'] for card in query.search(CATALOG, text, **kwargs)]


class BilingualMatchingTest(unittest.TestCase):
    def test_short_alias_does_not_match_inside_english_words(self):
        # Neutral family avoids an intentional allocation -> optimization hint;
        # this fixture isolates aliases rather than suitability or card ranking.
        cards = [fixture('cellular', 'CA'), fixture('alias-ip', 'IP'), fixture('alias-lp', 'LP')]
        for text in ('forecast', 'forecasting', 'allocation', 'shipping', 'helpful'):
            with self.subTest(text=text):
                self.assertEqual(query.search(cards, text), [])

    def test_short_alias_can_be_used_as_an_actual_token(self):
        cards = [fixture('cellular', 'CA'), fixture('svm-model', 'SVM', 'machine-learning')]
        for text, expected in (('CA', 'cellular'), ('compare (CA) models', 'cellular'),
                               ('SVM', 'svm-model'), ('fit SVM now', 'svm-model'),
                               ('SVM分类', 'svm-model')):
            with self.subTest(text=text):
                self.assertEqual(query.search(cards, text)[0]['id'], expected)

    def test_english_forecasting_discovers_baseline_without_cellular_alias(self):
        for text in ('forecast', 'forecasting', 'time series forecasting', 'time-series forecast'):
            with self.subTest(text=text):
                found = ids(text)
                self.assertIn('ts-naive', found)
                self.assertNotIn('sim-cellular', found)

    def test_integer_resource_allocation_discovers_integer_model(self):
        found = ids('integer resource allocation')
        self.assertIn('opt-milp', found)
        self.assertNotIn('sim-cellular', found)
        self.assertEqual(found[0], 'opt-milp')

    def test_family_filter_retains_relevant_english_candidates(self):
        found = query.search(CATALOG, 'integer resource allocation', family='optimization')
        self.assertIn('opt-milp', [card['id'] for card in found])
        self.assertTrue(all(card['family'] == 'optimization' for card in found))

    def test_actual_acronyms_and_chinese_substrings_remain_searchable(self):
        for text, expected in (('ARIMA', 'ts-arima'), ('MILP', 'opt-milp'),
                               ('整数规划', 'opt-milp'), ('朴素预测', 'ts-naive'),
                               ('可识别', 'inverse-identifiability')):
            with self.subTest(text=text):
                self.assertIn(expected, ids(text))

    def test_svm_family_name_finds_support_vector_models_before_incidental_rbf_mention(self):
        for text in ('SVM', 'support vector machine'):
            with self.subTest(text=text):
                found = ids(text)
                self.assertIn('ml-svc', found)
                self.assertIn('ml-svr', found)
                if 'ml-rbf-network' in found:
                    self.assertLess(found.index('ml-svc'), found.index('ml-rbf-network'))
                    self.assertLess(found.index('ml-svr'), found.index('ml-rbf-network'))

    def test_unrelated_unknown_word_does_not_gain_acronym_matches(self):
        self.assertEqual(ids('zxqvunknown'), [])


if __name__ == '__main__':
    unittest.main()
