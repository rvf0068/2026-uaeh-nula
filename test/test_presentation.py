import ast
import math
import re
import unittest
from collections import Counter
from itertools import combinations
from pathlib import Path

from source.storyboards import CYAN, SCENE_NAMES, SUSP_CLIQUES, graphs, move, octa, susp


ROOT = Path(__file__).resolve().parents[1]


class PresentationScenesTest(unittest.TestCase):
    def test_slide_animations_match_rendered_scenes(self):
        org = (ROOT / 'presentacion.org').read_text(encoding='utf-8')
        slides = re.findall(r'\\Anim(?:Title|Side|Wide)\{([^}]+)\}', org)
        script = (ROOT / 'scripts/render_manim.sh').read_text(encoding='utf-8')
        scenes = re.findall(r"'([A-Za-z0-9]+):([a-z0-9_]+)'", script)
        classes = {
            node.name
            for source in ('manim_scenes.py', 'segunda_parte_manim.py')
            for node in ast.parse(
                (ROOT / 'source' / source).read_text(encoding='utf-8')
            ).body if isinstance(node, ast.ClassDef)
        }

        self.assertEqual([slug for _, slug in scenes], slides)
        self.assertEqual(dict(scenes), SCENE_NAMES)
        self.assertEqual(set(graphs()), set(slides))
        self.assertTrue(set(SCENE_NAMES) <= classes)

    def test_iterated_house_clique_graph_is_vertical_in_all_stages(self):
        stages = graphs()['iteradas']
        self.assertEqual([len(stage) for stage in stages], [1, 2, 3])
        for stage in stages[1:]:
            clique_graph = stage[1]
            self.assertEqual(clique_graph['edges'], [['q0', 'q1']])
            self.assertEqual(clique_graph['pos']['q0'][0], clique_graph['pos']['q1'][0])
            self.assertLess(clique_graph['pos']['q0'][1], clique_graph['pos']['q1'][1])

    def test_pyramid_stays_equilateral_in_all_stages(self):
        stages = graphs()['piramide']
        self.assertEqual(len(stages), 4)
        positions = stages[0][0]['pos']
        corners = [positions[vertex] for vertex in ('x0', 'x2', 'z0')]
        sides = [math.dist(a, b) for a, b in combinations(corners, 2)]
        for side in sides[1:]:
            self.assertAlmostEqual(side, sides[0])
        for vertex, a, b in (('x1', 'x0', 'x2'), ('y0', 'x0', 'z0'),
                             ('y1', 'x2', 'z0')):
            for value, start, end in zip(positions[vertex], positions[a], positions[b]):
                self.assertAlmostEqual(value, (start + end) / 2)
        for index, stage in enumerate(stages):
            self.assertEqual(stage[0]['pos'], positions)
            self.assertEqual(len(stage[0]['faces']), index)

    def test_dominated_vertices_end_with_octahedron(self):
        stages = graphs()['dominados']
        self.assertEqual([len(stage) for stage in stages], [1, 1, 1])
        self.assertEqual(set(stages[0][0]['pos']) - set(octa(3)['pos']), {'u', 'v'})
        self.assertEqual(stages[-1][0], octa(3))

    def test_octahedron_iterates_stay_large_and_separate(self):
        stages = graphs()['iteradas_octaedro']
        self.assertEqual([len(stage) for stage in stages], [1, 2, 3])
        self.assertEqual(stages[0], stages[2][:1])
        self.assertEqual(stages[1], stages[2][:2])
        self.assertEqual([len(model['pos']) for model in stages[-1]], [6, 8, 16])
        bounds = []
        for model in stages[-1]:
            points = list(model['pos'].values())
            xs = [x for x, _ in points]
            center = (min(xs) + max(xs)) / 2
            radius = max(math.hypot(x - center, y) for x, y in points)
            self.assertGreaterEqual(radius, 2.0)
            dot_radius = .25 * model['node_size']
            bounds.append((min(xs) - dot_radius, max(xs) + dot_radius))
            self.assertLess(max(abs(y) for _, y in points) + dot_radius, 2.4)
        self.assertGreater(bounds[0][0], -7.11)
        self.assertLess(bounds[-1][1], 7.11)
        for left, right in zip(bounds, bounds[1:]):
            self.assertGreater(right[0] - left[1], .05)

    def test_simplicial_realization_builds_the_example_in_order(self):
        stages = [stage[0] for stage in graphs()['realizacion_simplicial']]
        self.assertEqual(len(stages), 9)
        for index, model in enumerate(stages[:4], start=1):
            self.assertEqual(set(model['pos']), set('1234'[:index]))
            self.assertEqual(model['edges'], [])
            self.assertEqual(model['faces'], [])
        edges = [['1', '2'], ['1', '3'], ['2', '3'], ['3', '4']]
        for index, model in enumerate(stages[4:8], start=1):
            self.assertEqual(model['edges'], edges[:index])
            self.assertEqual(model['faces'], [])
        self.assertEqual(stages[-1]['edges'], edges)
        self.assertEqual([face[0] for face in stages[-1]['faces']], [['1', '2', '3']])

    def test_graph_topology_shows_the_same_complex_and_suspension_surface(self):
        frames = graphs()
        stages = frames['topologia_graficas']
        self.assertEqual([len(stage) for stage in stages], [1, 2])
        self.assertEqual(stages[0][0], stages[1][0])
        self.assertEqual(stages[1][0], move(frames['realizacion_simplicial'][-1][0], .72, -3.9, 0))

        faces = [frozenset(vertices) for vertices, _, _ in SUSP_CLIQUES]
        edge_counts = Counter(frozenset(edge) for face in faces for edge in combinations(face, 2))
        self.assertEqual(set(edge_counts), {frozenset(edge) for edge in susp()['edges']})
        self.assertTrue(all(count == 2 for count in edge_counts.values()))
        self.assertEqual(len(susp()['pos']) - len(edge_counts) + len(faces), 2)

        surface = stages[1][1]
        visible_faces = [frozenset(vertices) for vertices, _, _ in surface['faces']]
        self.assertTrue(visible_faces)
        self.assertTrue(set(visible_faces) <= set(faces))
        surface_edges = {frozenset(edge) for edge in surface['edges']}
        front_edges = {frozenset(edge) for face in visible_faces for edge in combinations(face, 2)}
        self.assertEqual(surface_edges, set(edge_counts))
        self.assertTrue(surface_edges - front_edges)
        self.assertEqual(set(surface['pos']), set(susp()['pos']))
        self.assertTrue(set(surface['pos']) - set().union(*visible_faces))
        self.assertTrue(all(0 < opacity < 1 for _, _, opacity in surface['faces']))
        self.assertTrue(all(surface['node_colors'].get(vertex, CYAN) == CYAN
                            for vertex in surface['pos']))


if __name__ == '__main__':
    unittest.main()
