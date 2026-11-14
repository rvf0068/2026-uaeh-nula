import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'source'))
from segunda_parte_data import (
    EXAMPLES, verify_example, graph6, clique_graph,
    sphere_core, planar_disc, suspension, octahedral_retract_witness,
)


class SecondPartReproducibilityTest(unittest.TestCase):
    def test_s2_noncontractible_and_k_null(self):
        for code,n1,n3,folds in zip(EXAMPLES,(15,14),(63,65),(62,64)):
            with self.subTest(graph6=code):
                r=verify_example(code)
                self.assertEqual((r['vertices'],r['edges']),(10,30))
                self.assertEqual(r['core_f_vector'],(8,18,12))
                self.assertEqual(r['elementary_collapses'],20)
                self.assertEqual(r['iterated_orders'],[10,n1,22,n3])
                self.assertEqual(r['K3_folds'],folds)
                self.assertTrue(r['clique_null'])

    def test_example_disk_and_octahedral_retract_hypothesis(self):
        h,_=planar_disc()
        self.assertEqual((len(h),h.number_of_edges()),(9,20))
        g=suspension(h)
        self.assertEqual((len(g),g.number_of_edges()),(11,38))
        self.assertEqual(octahedral_retract_witness(h)[0],24)

if __name__=='__main__':
    unittest.main()
