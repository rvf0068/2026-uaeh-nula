#!/usr/bin/env python3
"""Reproduce the 10-vertex K-null S² certificates and the 2008 disk example.

Run from repository root with ``python scripts/verify_s2_null.py``.
Requires networkx (also listed in requirements.txt).
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / 'source'))
from segunda_parte_data import EXAMPLES, graph6, verify_example, planar_disc, octahedral_retract_witness

for code in EXAMPLES:
    result=verify_example(code)
    print('\n',result['graph6'])
    print('  |V|:',result['vertices'],'|E|:',result['edges'])
    print('  20 elementary collapses give sphere f-vector:',result['core_f_vector'])
    print('  |G|, |K(G)|, |K²(G)|, |K³(G)|:',result['iterated_orders'])
    print('  dominated deletions in K³:',result['K3_folds'])
    print('  Conclusion:',result['homotopy'],'and K-null')
    assert result['clique_null']
h,_=planar_disc()
cliques, nonedges=octahedral_retract_witness(h)
print('\n2008 Figure 2: H has',len(h),'vertices and',h.number_of_edges(),'edges.')
print('Susp H has',len(h)+2,'vertices, K(Susp H) has',cliques,'vertices.')
print('The eight specified maximal-clique vertices induce O4 with',len(nonedges),'nonedges.')
print('The retraction follows from Theorem 3.1 (2008), not from this computation alone.')
