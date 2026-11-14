import ast
import re
import unittest
from pathlib import Path

from source.storyboards import SCENE_NAMES, graphs


ROOT = Path(__file__).resolve().parents[1]


class PresentationScenesTest(unittest.TestCase):
    def test_slide_animations_match_rendered_scenes(self):
        org = (ROOT / 'presentacion.org').read_text(encoding='utf-8')
        slides = re.findall(r'\\Anim(?:Title|Side|Wide)\{([^}]+)\}', org)
        script = (ROOT / 'scripts/render_manim.sh').read_text(encoding='utf-8')
        scenes = re.findall(r"'([A-Za-z0-9]+):([a-z0-9_]+)'", script)
        classes = {
            node.name for node in ast.parse(
                (ROOT / 'source/manim_scenes.py').read_text(encoding='utf-8')
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


if __name__ == '__main__':
    unittest.main()
