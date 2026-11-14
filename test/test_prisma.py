import unittest
from itertools import combinations, permutations

from source.storyboards import K23_CLIQUES, PRISM_CLIQUES, graphs, k23, prism


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a, b, p):
    return (abs(cross(a, b, p)) < 1e-9
            and min(a[0], b[0]) - 1e-9 <= p[0] <= max(a[0], b[0]) + 1e-9
            and min(a[1], b[1]) - 1e-9 <= p[1] <= max(a[1], b[1]) + 1e-9)


class PrismGeometryTest(unittest.TestCase):
    def test_triangle_cliques_are_highlighted_small_first(self):
        pos = prism()['pos']
        first, second = (vertices for vertices, _, _ in PRISM_CLIQUES[:2])
        first_area = abs(cross(*(pos[vertex] for vertex in first)))
        second_area = abs(cross(*(pos[vertex] for vertex in second)))
        self.assertGreater(first_area, 0)
        self.assertLess(first_area, second_area)
        stages = graphs()['prisma_clanes']
        self.assertEqual(set(stages[1][1]['pos']), set(first))
        self.assertEqual(set(stages[3][1]['pos']), set(second))

    def test_prism_topology_and_planar_geometry_in_every_stage(self):
        expected = {frozenset(edge) for edge in (
            ('0', '1'), ('1', '2'), ('2', '0'),
            ('3', '4'), ('4', '5'), ('5', '3'),
            ('0', '3'), ('1', '4'), ('2', '5'),
        )}
        prism_graphs = [prism()]
        prism_graphs += [graph for stage in graphs()['prisma'] for graph in stage
                         if set(graph['pos']) == set('012345')]
        self.assertEqual(len(prism_graphs), 5)
        for model in prism_graphs:
            pos, edges = model['pos'], model['edges']
            self.assertEqual(len(edges), 9)
            self.assertEqual({frozenset(edge) for edge in edges}, expected)
            for a, b in edges:
                for vertex in pos.keys() - {a, b}:
                    self.assertFalse(on_segment(pos[a], pos[b], pos[vertex]),
                                     (a, b, vertex))
            for (a, b), (c, d) in combinations(edges, 2):
                if {a, b}.isdisjoint({c, d}):
                    ab_c, ab_d = cross(pos[a], pos[b], pos[c]), cross(pos[a], pos[b], pos[d])
                    cd_a, cd_b = cross(pos[c], pos[d], pos[a]), cross(pos[c], pos[d], pos[b])
                    self.assertFalse(ab_c * ab_d < 0 and cd_a * cd_b < 0,
                                     ((a, b), (c, d)))

    def test_clique_steps_and_clique_graphs(self):
        for slug, model, declared, result in (
            ('prisma_clanes', prism(), PRISM_CLIQUES, k23()),
            ('prisma_k23', k23(), K23_CLIQUES, prism()),
        ):
            with self.subTest(scene=slug):
                edges={frozenset(edge) for edge in model['edges']}
                vertices=list(model['pos'])
                complete=[frozenset(group) for size in range(1,len(vertices)+1)
                          for group in combinations(vertices,size)
                          if all(frozenset(pair) in edges for pair in combinations(group,2))]
                maximal={group for group in complete
                         if not any(group < other for other in complete)}
                cliques=[frozenset(vertices) for vertices,_,_ in declared]
                self.assertEqual(len(cliques),len(maximal))
                self.assertEqual(set(cliques),maximal)

                stages=graphs()[slug]
                self.assertEqual(len(stages),2*len(cliques)+2)
                self.assertEqual(len(stages[0]),1)
                for index,clique in enumerate(cliques):
                    self.assertEqual(set(stages[2*index+1][1]['pos']),clique)
                    self.assertEqual(len(stages[2*index+2]),1)
                self.assertEqual(len(stages[-1]),2)
                clique_edges={frozenset((i,j)) for i,j in combinations(range(len(cliques)),2)
                              if cliques[i] & cliques[j]}
                target_edges={frozenset(edge) for edge in result['edges']}
                self.assertTrue(any(
                    {frozenset((mapping[i],mapping[j])) for edge in clique_edges
                     for i,j in [tuple(edge)]} == target_edges
                    for mapping in permutations(result['pos'])
                ))
                self.assertEqual(
                    {frozenset(edge) for edge in stages[-1][1]['edges']},target_edges)


if __name__ == '__main__':
    unittest.main()
