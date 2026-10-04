import importlib.util
import math
from pathlib import Path
import sys
import unittest
try: import numpy as np
except ImportError: np = None

spec=importlib.util.spec_from_file_location('numerical_reference',Path(__file__).parents[1]/'assets/numerical_reference.py')
ref=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ref;spec.loader.exec_module(ref)

class NumericalReferenceTest(unittest.TestCase):
    def test_two_nodes_reproduce_linear_function(self):
        self.assertEqual(ref.newton_interpolate([0,1],[0,1],1),1)
        self.assertAlmostEqual(ref.newton_interpolate([0,1],[0,1],.3),.3)
    def test_cubic_values_and_node_consistency(self):
        nodes=[3,-2,0,1];values=[x**3+2*x-1 for x in nodes]
        for x,y in zip(nodes,values):self.assertAlmostEqual(ref.newton_interpolate(nodes,values,x),y)
        self.assertAlmostEqual(ref.newton_interpolate(nodes,values,1.5),1.5**3+2*1.5-1)
    def test_constant_single_node(self):
        self.assertEqual(ref.newton_interpolate([2],[7],-9),7)
    def test_invalid_interpolation_inputs(self):
        for xs,ys in (([],[]),([0,0],[1,2]),([0,1],[1]),([0,math.nan],[1,2]),([0],[math.inf])):
            with self.subTest(xs=xs,ys=ys),self.assertRaises(ValueError):ref.newton_interpolate(xs,ys,0)
    def test_bisection_sqrt2(self):
        result=ref.bisect(lambda x:x*x-2,0,2,xtol=1e-12,ftol=0)
        self.assertAlmostEqual(result.root,math.sqrt(2),places=11)
        self.assertLessEqual(result.bracket[0],math.sqrt(2))
        self.assertGreaterEqual(result.bracket[1],math.sqrt(2))
    def test_bisection_endpoint_and_large_bracket(self):
        self.assertEqual(ref.bisect(lambda x:x,0,3).root,0)
        self.assertEqual(ref.bisect(lambda x:x,-1e308,1e308).root,0)
    def test_bisection_rejects_no_bracket_and_nonfinite(self):
        with self.assertRaises(ValueError):ref.bisect(lambda x:x*x+1,-1,1)
        with self.assertRaises(ValueError):ref.bisect(lambda x:math.nan,0,1)
    def test_small_constant_residual_is_not_an_endpoint_root(self):
        with self.assertRaises(ValueError):ref.bisect(lambda x:1e-15,0,1,ftol=1e-12)
    def test_bisection_budget_and_tolerance(self):
        with self.assertRaises(RuntimeError):ref.bisect(lambda x:x*x-2,0,2,max_iter=1,ftol=0)
        with self.assertRaises(ValueError):ref.bisect(lambda x:x,0,1,xtol=0)
    def test_finite_nodes_cannot_hide_overflowed_subtraction(self):
        # The line through these nodes has value 0 at x=0, not -1.
        with self.assertRaises(ValueError):ref.newton_interpolate([-1e308,1e308],[-1,1],0)
        with self.assertRaises(ValueError):ref.newton_coefficients([0,1],[-1e308,1e308])
        with self.assertRaises(ValueError):ref.newton_coefficients([2**53+1],[1])
    def test_underflowed_nonzero_slope_is_not_silently_constant(self):
        with self.assertRaises(ValueError):ref.newton_interpolate([0,1e300],[0,1e-300],1e300)
    def test_bisection_bad_boolean_and_nonfinite_tolerances(self):
        for kwargs in ({'max_iter':True},{'xtol':math.inf},{'ftol':math.nan},{'ftol':-1}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):ref.bisect(lambda x:x,-1,1,**kwargs)
    @unittest.skipIf(np is None, 'NumPy interoperability only')
    def test_numpy_integer_iteration_budget_is_a_positive_integer(self):
        self.assertAlmostEqual(ref.bisect(lambda x:x*x-2,0,2,max_iter=np.int64(100)).root,math.sqrt(2),places=8)

if __name__=='__main__':unittest.main()
