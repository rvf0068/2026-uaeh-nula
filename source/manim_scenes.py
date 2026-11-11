"""16 editable Manim Community scenes, one for each Beamer frame.

This deliberately keeps text and formulas in Beamer, not in the videos. The
stage geometry is in storyboards.py and can be edited independently.
"""
from manim import (
    Scene, Dot, Line, Polygon, VGroup, FadeIn, FadeOut, AnimationGroup,
    LaggedStart, Create, config
)
from storyboards import graphs, SCENE_NAMES, BG, CYAN

config.background_color = BG


def visual_graph(model):
    pos = model['pos']
    faces=VGroup()
    for ids, color, opacity in model['faces']:
        faces.add(Polygon(*[(*pos[i],0) for i in ids],
                          color=color, stroke_width=0,
                          fill_color=color, fill_opacity=opacity))
    lines=VGroup()
    for a,b in model['edges']:
        lines.add(Line((*pos[a],0),(*pos[b],0),
                       color=model['edge_color'], stroke_width=15,
                       stroke_opacity=model['edge_opacity']))
    dots=VGroup()
    for key,(x,y) in pos.items():
        dots.add(Dot(point=(x,y,0),radius=.25*model['node_size'],
                     color=model['node_colors'].get(key,CYAN)))
    return VGroup(faces,lines,dots)


def visual_snapshot(snapshot):
    return VGroup(*(visual_graph(model) for model in snapshot))


class _Storyboard(Scene):
    key=None
    def construct(self):
        stages=graphs()[self.key]
        current=None
        for index, snapshot in enumerate(stages):
            nxt=visual_snapshot(snapshot)
            if current is None:
                self.add(nxt)
            else:
                self.play(AnimationGroup(FadeOut(current),FadeIn(nxt),lag_ratio=0),run_time=1.05)
            self.wait(.65 if index<len(stages)-1 else 1.15)
            current=nxt


class Intro(_Storyboard): key='intro'
class Graficas(_Storyboard): key='graficas'
class Completas(_Storyboard): key='completas'
class Clanes(_Storyboard): key='clanes'
class GraficaDeClanes(_Storyboard): key='grafica_clanes'
class Ejemplo(_Storyboard): key='ejemplo'
class Iteradas(_Storyboard): key='iteradas'
class Prisma(_Storyboard): key='prisma'
class SuspensionC5(_Storyboard): key='suspension_c5'
class Comportamiento(_Storyboard): key='comportamiento'
class IteradasOctaedro(_Storyboard): key='iteradas_octaedro'
class Helly(_Storyboard): key='helly'
class Piramide(_Storyboard): key='piramide'
class Escalante(_Storyboard): key='escalante'
class Desmantelables(_Storyboard): key='desmantelables'
class Dominados(_Storyboard): key='dominados'
