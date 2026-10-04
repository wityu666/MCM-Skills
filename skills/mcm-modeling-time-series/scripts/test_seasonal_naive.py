"""Hand-derived predictions and split failures, with no source-material execution."""
import unittest
try: import numpy as np
except ImportError: np = None
from seasonal_naive import seasonal_naive, check_temporal_split


class NaiveTests(unittest.TestCase):
    def test_multicycle(self):
        self.assertEqual(seasonal_naive([1,2,3,4,5,6],3,7),[4,5,6,4,5,6,4])
    def test_nonseasonal(self):
        self.assertEqual(seasonal_naive([3,7,11],1,4),[11]*4)
    def test_zero_horizon(self):
        self.assertEqual(seasonal_naive([2,3],2,0),[])
    def test_short_history(self):
        with self.assertRaises(ValueError):seasonal_naive([1,2],3,1)
    def test_nonfinite(self):
        with self.assertRaises(ValueError):seasonal_naive([1,float('nan')],1,1)
    def test_invalid_period(self):
        for p in (0,-1,1.2,True):
            with self.assertRaises(ValueError):seasonal_naive([1,2],p,2)
    def test_history_unchanged(self):
        h=[1,2,3];seasonal_naive(h,2,5);self.assertEqual(h,[1,2,3])


class SplitTests(unittest.TestCase):
    def test_forward_gap(self):
        result=check_temporal_split([1,2,3,4,5,6],[0,1,2],[4,5],gap_steps=1)
        self.assertEqual(result['status'],'PASS');self.assertFalse(result['feature_availability_checked'])
    def test_row_overlap(self):
        with self.assertRaises(ValueError):check_temporal_split([1,2,3],[0,1],[1,2])
    def test_time_reversal(self):
        with self.assertRaises(ValueError):check_temporal_split([1,2,3],[2],[0,1])
    def test_same_time_is_not_future(self):
        with self.assertRaises(ValueError):check_temporal_split([1,2,2],[0,1],[2])
    def test_gap_too_small(self):
        with self.assertRaises(ValueError):check_temporal_split([1,2,3,4],[0,1],[2,3],1)
    def test_group_leakage(self):
        with self.assertRaises(ValueError):check_temporal_split([1,2,3,4],[0,1],[2,3],groups=['a','b','a','c'],require_group_disjoint=True)
    def test_group_isolation(self):
        self.assertTrue(check_temporal_split([1,2,3,4],[0,1],[2,3],groups=['a','b','c','d'],require_group_disjoint=True)['group_isolation_checked'])
    def test_unsorted_observations(self):
        with self.assertRaises(ValueError):check_temporal_split([1,3,2],[0],[2])
    def test_missing_groups(self):
        with self.assertRaises(ValueError):check_temporal_split([1,2],[0],[1],require_group_disjoint=True)
    def test_ordered_iterables_are_read_once(self):
        result=check_temporal_split((t for t in [1,2,3]),[0],[1,2],groups=(g for g in ['a','b','c']),require_group_disjoint=True)
        self.assertEqual(result['status'],'PASS')
    def test_bad_times_and_index_shapes_have_controlled_errors(self):
        for times in ('123',None,[1,float('inf')]):
            with self.subTest(times=times),self.assertRaises(ValueError):check_temporal_split(times,[0],[1])
        with self.assertRaises(ValueError):check_temporal_split([1,2],[[0]],[1])
    def test_unknown_group_identity_cannot_prove_isolation(self):
        for groups in ([None,'b'],[float('nan'),'b'],[['a'],['b']]):
            with self.subTest(groups=groups),self.assertRaises(ValueError):check_temporal_split([1,2],[0],[1],groups=groups,require_group_disjoint=True)
        with self.assertRaises(ValueError):check_temporal_split([1,2],[0],[1],require_group_disjoint='false')
    def test_unknown_identity_outside_checked_rows_is_out_of_scope(self):
        result=check_temporal_split([1,2,3],[0],[1],groups=['a','b',None],require_group_disjoint=True)
        self.assertTrue(result['group_isolation_checked'])
    @unittest.skipIf(np is None, 'NumPy interoperability only')
    def test_numpy_integer_indices_and_period_are_valid(self):
        result=check_temporal_split([1,2,3],np.array([0]),np.array([1,2]))
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(seasonal_naive([1,2],np.int64(1),np.int64(2)),[2.,2.])


if __name__=='__main__':
    unittest.main(verbosity=2)
