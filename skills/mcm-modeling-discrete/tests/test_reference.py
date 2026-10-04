import importlib.util
import itertools
import math
from pathlib import Path
import sys
import unittest
try: import numpy as np
except ImportError: np = None

spec=importlib.util.spec_from_file_location('discrete_reference',Path(__file__).parents[1]/'assets/discrete_reference.py')
ref=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ref;spec.loader.exec_module(ref)

class DiscreteReferenceTest(unittest.TestCase):
    def test_knapsack_single_item_and_old_traceback_counterexample(self):
        self.assertEqual(ref.knapsack01([5],[2],2).selected,(0,))
        result=ref.knapsack01([100,1],[3,1],2)
        self.assertEqual(result.selected,(1,));self.assertEqual(result.weight,1);self.assertEqual(result.value,1)
    def test_knapsack_against_independent_subset_enumeration(self):
        values=[8,7,6,4,9];weights=[3,2,4,1,5];capacity=7
        feasible=[]
        for bits in itertools.product((0,1),repeat=len(values)):
            weight=sum(w*b for w,b in zip(weights,bits))
            if weight<=capacity:feasible.append(sum(v*b for v,b in zip(values,bits)))
        result=ref.knapsack01(values,weights,capacity)
        self.assertEqual(result.value,max(feasible));self.assertEqual(result.value,result.table_value)
        self.assertLessEqual(result.weight,capacity)
        self.assertEqual(len(result.selected),len(set(result.selected)))
    def test_knapsack_zero_weight_empty_and_zero_capacity(self):
        result=ref.knapsack01([4,3,-2],[0,0,0],0)
        self.assertEqual(result.selected,(0,1));self.assertEqual(result.value,7)
        self.assertEqual(ref.knapsack01([],[],0).value,0)
    def test_knapsack_invalid_and_budget(self):
        for values,weights,cap in (([1],[-1],1),([math.inf],[1],1),([1],[1.5],2),([1],[],1),([1],[1],-1)):
            with self.subTest(values=values,weights=weights,cap=cap),self.assertRaises(ValueError):ref.knapsack01(values,weights,cap)
        with self.assertRaises(ValueError):ref.knapsack01([1],[1],100,max_states=10)
    def test_dijkstra_zero_edge_unreachable_and_path_cost(self):
        graph={'a':{'b':0,'c':9},'b':{'c':2},'c':{},'isolated':{}}
        result=ref.dijkstra(graph,'a')
        self.assertEqual(result.distances['b'],0);self.assertEqual(result.distances['c'],2)
        path=result.path_to('c');self.assertEqual(path,['a','b','c'])
        self.assertEqual(sum(graph[u][v] for u,v in zip(path,path[1:])),result.distances['c'])
        self.assertTrue(math.isinf(result.distances['isolated']));self.assertIsNone(result.path_to('isolated'))
    def test_dijkstra_zero_cycle_and_mixed_node_types(self):
        graph={0:{'x':0,1:0},'x':{0:0,'target':2},1:{'target':3}}
        result=ref.dijkstra(graph,0)
        self.assertEqual(result.path_to('target'),[0,'x','target'])
    def test_none_is_a_valid_explicit_node_label(self):
        result=ref.dijkstra({'a':{None:0},None:{'b':2}},'a')
        self.assertEqual(result.path_to('b'),['a',None,'b'])
        self.assertEqual(ref.dijkstra({None:{'b':1}},None).path_to('b'),[None,'b'])
    def test_dijkstra_invalid_even_unreachable_negative_edge(self):
        for graph,source in (({},'x'),({'a':{}},'x'),({'a':{},'b':{'c':-1}},'a'),({'a':{'b':math.nan}},'a')):
            with self.subTest(graph=graph),self.assertRaises(ValueError):ref.dijkstra(graph,source)
    def test_overflowing_nonminimal_walk_does_not_hide_finite_route(self):
        graph={'s':{'a':1e308,'b':1.7e308},'a':{'t':1e308},'b':{'t':0},'t':{}}
        result=ref.dijkstra(graph,'s')
        self.assertEqual(result.distances['t'],1.7e308)
        self.assertEqual(result.path_to('t'),['s','b','t'])
    def test_overflow_only_route_is_not_reported_as_unreachable(self):
        with self.assertRaises(ValueError):ref.dijkstra({'s':{'a':1e308},'a':{'t':1e308}},'s')
    def test_boolean_and_nonfinite_knapsack_or_edges_are_rejected(self):
        for args in (([True],[1],1),([1],[True],1),([1],[1],True)):
            with self.subTest(args=args),self.assertRaises(ValueError):ref.knapsack01(*args)
        for value in (math.inf, True):
            with self.subTest(value=value),self.assertRaises(ValueError):ref.dijkstra({'s':{'t':value}},'s')
        with self.assertRaises(ValueError):ref.knapsack01([2**53,2**53+1],[1,1],1)
        with self.assertRaises(ValueError):ref.knapsack01([2**53,1],[1,1],2)
    @unittest.skipIf(np is None, 'NumPy interoperability only')
    def test_numpy_integer_weights_are_valid_integer_inputs(self):
        result=ref.knapsack01(np.array([3,4]),np.array([1,2]),np.int64(2))
        self.assertEqual(result.selected,(1,));self.assertEqual(result.value,4)

if __name__=='__main__':unittest.main()
