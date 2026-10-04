import importlib.util
import math
from pathlib import Path
import sys
import unittest
try: import numpy as np
except ImportError: np = None

spec=importlib.util.spec_from_file_location('optimization_reference',Path(__file__).parents[1]/'assets/optimization_reference.py')
ref=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ref;spec.loader.exec_module(ref)

class OptimizationReferenceTest(unittest.TestCase):
    def test_objective_and_all_explicit_constraints(self):
        result=ref.check_linear_candidate([3,2],[1,1],A_ub=[[1,1]],b_ub=[2],A_eq=[[1,-1]],b_eq=[0],lower=[0,0],upper=[1,2],integer_indices=[0,1])
        self.assertTrue(result['feasible']);self.assertEqual(result['objective'],5)
        self.assertEqual(len(result['checks']),8)
    def test_constraint_and_integer_violations(self):
        report=ref.check_linear_candidate([1,1],[1.2,2],A_ub=[[1,1]],b_ub=[3],A_eq=[[1,-1]],b_eq=[0],lower=[0,0],upper=[1,3],integer_indices=[0])
        self.assertFalse(report['feasible'])
        failed={x['kind'] for x in report['checks'] if not x['passed']}
        self.assertEqual(failed,{'inequality','equality','upper','integer'})
    def test_no_invented_nonnegativity_and_no_relative_integrality_relaxation(self):
        self.assertTrue(ref.check_linear_candidate([1],[-2])['feasible'])
        self.assertFalse(ref.check_linear_candidate([1],[1.001],integer_indices=[0],atol=0,rtol=1)['feasible'])
    def test_complete_integer_box_known_optimum(self):
        report=ref.enumerate_integer_box([-4,-3],[(0,3),(0,3)],A_ub=[[2,1]],b_ub=[4],atol=0,rtol=0)
        self.assertEqual(report['status'],'OPTIMAL_ENUMERATED');self.assertEqual(report['x'],(1,2));self.assertEqual(report['objective'],-10)
        self.assertEqual(report['search_points'],16)
    def test_infeasible_box_and_budget(self):
        result=ref.enumerate_integer_box([1],[(0,2)],A_eq=[[1]],b_eq=[3])
        self.assertEqual(result['status'],'INFEASIBLE_ENUMERATED');self.assertIsNone(result['x'])
        with self.assertRaises(ValueError):ref.enumerate_integer_box([1],[(0,20)],max_points=10)
    def test_invalid_inputs_and_nonfinite(self):
        for c,x in (([],[]),([1],[math.inf]),([1],[1,2])):
            with self.subTest(c=c,x=x),self.assertRaises(ValueError):ref.check_linear_candidate(c,x)
        with self.assertRaises(ValueError):ref.check_linear_candidate([1],[0],A_ub=[[1]])
        with self.assertRaises(ValueError):ref.check_linear_candidate([1],[0],integer_indices=[-1])
        with self.assertRaises(ValueError):ref.check_linear_candidate([1],[0],lower=[2],upper=[1])
    def test_one_shot_constraints_are_not_lost_after_first_point(self):
        # x<=0 makes zero the only feasible point, although min(-x) prefers one.
        result=ref.enumerate_integer_box([-1],[(0,1)],A_ub=(r for r in [[1]]),b_ub=(b for b in [0]))
        self.assertEqual(result['x'],(0,));self.assertEqual(result['feasible_points'],1)
        result=ref.enumerate_integer_box([-1],[(0,2)],A_eq=(r for r in [[1]]),b_eq=(b for b in [1]))
        self.assertEqual(result['x'],(1,));self.assertEqual(result['feasible_points'],1)
    def test_overflow_does_not_turn_constraint_failure_into_pass(self):
        with self.assertRaises(ValueError):ref.check_linear_candidate([0],[1e308],upper=[-1e308],atol=0,rtol=2)
        with self.assertRaises(ValueError):ref.check_linear_candidate([0],[1e308],lower=[-1e308],atol=0,rtol=1e308)
        with self.assertRaises(ValueError):ref.check_linear_candidate([1,1],[1e308,1e308])
        with self.assertRaises(ValueError):ref.check_linear_candidate([1],[2**53+1],upper=[2**53],atol=0,rtol=0)
        with self.assertRaises(ValueError):ref.enumerate_integer_box([-1],[(2**53,2**53+1)])
        with self.assertRaises(ValueError):ref.check_linear_candidate([0,0],[2**53,1],A_ub=[[1,1]],b_ub=[2**53],atol=0,rtol=0)
    @unittest.skipIf(np is None, 'NumPy interoperability only')
    def test_numpy_integer_box_and_indices_keep_integer_semantics(self):
        result=ref.enumerate_integer_box([-1],np.array([[0,2]],dtype=np.int64),max_points=np.int64(3))
        self.assertEqual(result['x'],(2,))
        self.assertTrue(ref.check_linear_candidate([1],[2],integer_indices=np.array([0]))['feasible'])

if __name__=='__main__':unittest.main()
