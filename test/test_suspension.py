import math
import unittest
from itertools import combinations

from source.storyboards import SUSP_CLIQUES, graphs, ksusp, susp


def distance_to_segment(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    fraction = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy)
    fraction = max(0, min(1, fraction))
    return math.hypot(point[0] - start[0] - fraction * dx,
                      point[1] - start[1] - fraction * dy)


class SuspensionTest(unittest.TestCase):
    def test_cliques_and_clique_graph(self):
        model = susp()
        edges = {frozenset(edge) for edge in model['edges']}
        vertices = list(model['pos'])
        complete = [
            frozenset(group)
            for size in range(1, len(vertices) + 1)
            for group in combinations(vertices, size)
            if all(frozenset(pair) in edges for pair in combinations(group, 2))
        ]
        maximal = {group for group in complete if not any(group < other for other in complete)}
        cliques = {f'{apex}{i}': frozenset((apex, f'r{i}', f'r{(i + 1) % 5}'))
                   for apex in ('t', 'b') for i in range(5)}
        self.assertEqual(len(SUSP_CLIQUES), 10)
        self.assertEqual({frozenset(vertices) for vertices, _, _ in SUSP_CLIQUES}, maximal)
        self.assertEqual(set(cliques.values()), maximal)
        expected_edges = {frozenset((a, b)) for a, b in combinations(cliques, 2)
                          if cliques[a] & cliques[b]}
        self.assertEqual({frozenset(edge) for edge in ksusp()['edges']}, expected_edges)

    def test_stages_and_clearance(self):
        stages = graphs()['suspension_c5']
        self.assertEqual(len(stages), 2 * len(SUSP_CLIQUES) + 2)
        for index, (vertices, _, _) in enumerate(SUSP_CLIQUES):
            self.assertEqual(set(stages[2 * index + 1][1]['pos']), set(vertices))
            self.assertEqual(len(stages[2 * index + 2]), 1)
        left, right = stages[-1]
        self.assertEqual(left, stages[0][0])
        for a, b in right['edges']:
            for vertex, pos in right['pos'].items():
                if vertex not in (a, b):
                    self.assertGreater(distance_to_segment(pos, right['pos'][a], right['pos'][b]),
                                       .30, (a, b, vertex))
        for model in (left, right):
            for x, y in model['pos'].values():
                self.assertLess(abs(x) + .36 * model['node_size'], 7.1)
                self.assertLess(abs(y) + .36 * model['node_size'], 4)
        self.assertLess(max(x for x, _ in left['pos'].values()) + .36,
                        min(x for x, _ in right['pos'].values()) - .36)

    def test_triangle_visibility_and_aligned_prism_layers(self):
        model = susp()
        pos = model['pos']
        self.assertAlmostEqual(pos['t'][0], pos['b'][0])
        for a, b in model['edges']:
            for vertex, point in pos.items():
                if vertex not in (a, b):
                    self.assertGreater(distance_to_segment(point, pos[a], pos[b]),
                                       .30, (a, b, vertex))
        for vertices, _, _ in SUSP_CLIQUES:
            a, b, c = (pos[vertex] for vertex in vertices)
            twice_area = abs((b[0] - a[0]) * (c[1] - a[1])
                             - (b[1] - a[1]) * (c[0] - a[0]))
            longest_edge = max(math.dist(x, y) for x, y in combinations((a, b, c), 2))
            self.assertGreater(twice_area / longest_edge, .45, vertices)

        pos = ksusp()['pos']
        offsets = [(pos[f't{i}'][0] - pos[f'b{i}'][0],
                    pos[f't{i}'][1] - pos[f'b{i}'][1]) for i in range(5)]
        for offset in offsets:
            self.assertAlmostEqual(offset[0], 0)
            self.assertAlmostEqual(offset[1], offsets[0][1])


if __name__ == '__main__':
    unittest.main()
