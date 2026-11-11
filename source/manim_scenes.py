"""16 editable Manim Community scenes, one for each Beamer frame.

This deliberately keeps text and formulas in Beamer, not in the videos. The
stage geometry is in storyboards.py and can be edited independently.
"""
from manim import (
    Scene, Dot, Line, CubicBezier, Polygon, VGroup, FadeIn, FadeOut, AnimationGroup,
    LaggedStart, Create, config
)
import numpy as np
from storyboards import graphs, SCENE_NAMES, BG, CYAN

config.background_color = BG
INVALID_COLOR = '#c62828'


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


def complete_highlight(model, vertices, color, face=None, omit_vertices=(), omit_edges=()):
    vertex_set=set(vertices)
    edges=[(a,b) for a,b in model['edges'] if a in vertex_set and b in vertex_set]
    omitted_edge_sets={frozenset(edge) for edge in omit_edges}
    highlights=VGroup()
    if face:
        light_color,opacity=face
        highlights.add(Polygon(
            *[(*model['pos'][vertex],0) for vertex in vertices],
            color=light_color,stroke_color=light_color,stroke_width=8,
            fill_color=light_color,fill_opacity=opacity,
        ))
    for start,end in edges:
        if frozenset((start,end)) in omitted_edge_sets:
            continue
        highlights.add(Line(
            (*model['pos'][start],0),(*model['pos'][end],0),
            color=color,stroke_width=20,
        ))
    for vertex in vertices:
        if vertex in omit_vertices:
            continue
        highlights.add(Dot(
            point=(*model['pos'][vertex],0),
            radius=.36*model['node_size'],
            color=color,
        ))
    return highlights


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
class Completas(_Storyboard):
    key='completas'

    def construct(self):
        model=graphs()[self.key][0][0]
        self.add(visual_graph(model))

        examples=[
            (('0','2','3'),'#d1493f',('#f0aaa4',.28)),
            (('0','1','4'),'#008c95',('#99d9dc',.28)),
            (('0','1','2','3'),'#a56a00',None),
            (('0','1'),'#d1493f',None),
            (('4',),'#a56a00',None),
        ]
        for vertices,color,triangle in examples:
            highlights=complete_highlight(model,vertices,color,triangle)
            self.play(FadeIn(highlights))
            self.wait(2)
            self.play(FadeOut(highlights))
            self.wait(.5)


class Clanes(_Storyboard):
    key='clanes'

    def construct(self):
        model=graphs()[self.key][0][0]
        self.add(visual_graph(model))
        first=complete_highlight(model,('0','1','4'),'#008c95',('#99d9dc',.28))
        second=complete_highlight(model,('0','1','2','3'),'#d1493f')
        shared_vertices=('0','1')
        shared_edges=(('0','1'),)

        self.play(FadeIn(first))
        self.wait(2)
        self.play(FadeOut(first))
        self.wait(.5)
        self.play(FadeIn(second))
        self.wait(2)
        self.play(FadeOut(second))
        self.wait(.5)
        left, right = (np.array((*model['pos'][vertex], 0)) for vertex in shared_vertices)
        edge_direction=(right-left)/np.linalg.norm(right-left)
        edge_normal=np.array([-edge_direction[1],edge_direction[0],0])
        edge_half_width=.1
        edge_halves=VGroup(
            Polygon(
                left+edge_normal*edge_half_width,
                right+edge_normal*edge_half_width,
                right, left,
                color='#008c95',stroke_width=0,fill_color='#008c95',fill_opacity=1,
            ),
            Polygon(
                left, right,
                right-edge_normal*edge_half_width,
                left-edge_normal*edge_half_width,
                color='#d1493f',stroke_width=0,fill_color='#d1493f',fill_opacity=1,
            ),
        )
        split_vertices=VGroup()
        radius=.36*model['node_size']
        for vertex in shared_vertices:
            center=np.array((*model['pos'][vertex],0))
            for start_angle,end_angle,color in (
                (0,np.pi,'#008c95'),
                (np.pi,2*np.pi,'#d1493f'),
            ):
                angles=np.linspace(start_angle,end_angle,25)
                arc=[center+radius*np.array([np.cos(angle),np.sin(angle),0])
                     for angle in angles]
                split_vertices.add(Polygon(
                    center,*arc,color=color,stroke_color=color,stroke_width=0,
                    fill_color=color,fill_opacity=1,
                ))
        combined=VGroup(
            complete_highlight(
                model,('0','1','4'),'#008c95',('#99d9dc',.28),
                omit_vertices=shared_vertices,omit_edges=shared_edges,
            ),
            complete_highlight(
                model,('0','1','2','3'),'#d1493f',
                omit_vertices=shared_vertices,omit_edges=shared_edges,
            ),
            edge_halves,
            split_vertices,
        )
        self.play(FadeIn(combined))
        self.wait(2)


class Graficas(_Storyboard):
    key='graficas'

    def construct(self):
        wheel=graphs()[self.key][0][0]
        edge_model=wheel
        vertices=VGroup(*(
            Dot(point=(*position,0),radius=.25*wheel['node_size'],
                color=wheel['node_colors'].get(name,CYAN))
            for name,position in wheel['pos'].items()
        ))
        self.add(vertices)
        self.wait(2)

        edges=VGroup(*(
            Line((*wheel['pos'][a],0),(*wheel['pos'][b],0),
                 color=wheel['edge_color'],stroke_width=15,
                 stroke_opacity=wheel['edge_opacity'])
            for a,b in wheel['edges']
        ))
        self.play(AnimationGroup(*(Create(edge) for edge in edges),lag_ratio=0),
                  run_time=1.5)
        self.bring_to_front(vertices)
        self.wait(2)

        vertex=np.array([*wheel['pos']['0'],0])
        outward=vertex/np.linalg.norm(vertex)
        tangent=np.array([-outward[1],outward[0],0])
        loop=CubicBezier(
            vertex+outward*.2-tangent*.15,
            vertex+outward*1.05-tangent*.8,
            vertex+outward*1.05+tangent*.8,
            vertex+outward*.2+tangent*.15,
            color=edge_model['edge_color'],stroke_width=12,
        )
        cross_center=vertex+outward*.8375
        loop_cross=VGroup(
            Line(cross_center+np.array([-.18,-.18,0]),cross_center+np.array([.18,.18,0]),
                 color=INVALID_COLOR,stroke_width=12),
            Line(cross_center+np.array([-.18,.18,0]),cross_center+np.array([.18,-.18,0]),
                 color=INVALID_COLOR,stroke_width=12),
        )
        self.play(Create(loop),Create(loop_cross))
        self.wait(2)
        self.play(FadeOut(loop),FadeOut(loop_cross))

        start=np.array([*wheel['pos']['2'],0])
        end=np.array([*wheel['pos']['3'],0])
        direction=end-start
        direction=direction/np.linalg.norm(direction)
        normal=(start+end)/2
        normal=normal/np.linalg.norm(normal)
        curve_start=start+direction*.2
        curve_end=end-direction*.2
        duplicate_edge=CubicBezier(
            curve_start,
            curve_start+normal*.8,
            curve_end+normal*.8,
            curve_end,
            color=edge_model['edge_color'],stroke_width=15,
        )
        midpoint=(start+end)/2+normal*.6
        cross_center=midpoint
        edge_cross=VGroup(
            Line(cross_center+np.array([-.18,-.18,0]),cross_center+np.array([.18,.18,0]),
                 color=INVALID_COLOR,stroke_width=12),
            Line(cross_center+np.array([-.18,.18,0]),cross_center+np.array([.18,-.18,0]),
                 color=INVALID_COLOR,stroke_width=12),
        )
        self.play(Create(duplicate_edge),Create(edge_cross))
        self.wait(2)
        self.play(FadeOut(duplicate_edge),FadeOut(edge_cross))


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
