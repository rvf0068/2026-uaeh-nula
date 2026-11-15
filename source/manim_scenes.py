"""Editable Manim Community scenes, one for each Beamer frame.

Most slide text and formulas stay in Beamer; graph labels appear in the videos.
The stage geometry is in storyboards.py and can be edited independently.
"""
from itertools import combinations

from manim import (
    Scene, Dot, Line, Circle, CubicBezier, Polygon, MathTex, Tex, TexTemplate, VGroup, FadeIn, FadeOut, AnimationGroup,
    LaggedStart, Create, config
)
import numpy as np
from storyboards import graphs, SCENE_NAMES, BG, CYAN, CORAL, MINT, PRISM_CLIQUES, K23_CLIQUES, SUSP_CLIQUES

config.background_color = BG
INVALID_COLOR = '#c62828'
LATIN_MODERN_TEMPLATE = TexTemplate()
LATIN_MODERN_TEMPLATE.add_to_preamble(r'\usepackage[T1]{fontenc}')
LATIN_MODERN_TEMPLATE.add_to_preamble(r'\usepackage{lmodern}')


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


def combined_complete_highlight(
    model, first_vertices, first_color, second_vertices, second_color,
    shared_vertices, shared_edges, first_face=None,
):
    shared_vertices=set(shared_vertices)
    shared_edge_sets={frozenset(edge) for edge in shared_edges}
    first=complete_highlight(
        model,first_vertices,first_color,first_face,
        omit_vertices=shared_vertices,omit_edges=shared_edge_sets,
    )
    second=complete_highlight(
        model,second_vertices,second_color,
        omit_vertices=shared_vertices,omit_edges=shared_edge_sets,
    )

    split_edges=VGroup()
    for start,end in shared_edges:
        left=np.array((*model['pos'][start],0))
        right=np.array((*model['pos'][end],0))
        direction=(right-left)/np.linalg.norm(right-left)
        normal=np.array([-direction[1],direction[0],0])
        if normal[1] < 0:
            normal=-normal
        half_width=.1
        split_edges.add(
            Polygon(
                left+normal*half_width,right+normal*half_width,right,left,
                color=first_color,stroke_width=0,
                fill_color=first_color,fill_opacity=1,
            ),
            Polygon(
                left,right,right-normal*half_width,left-normal*half_width,
                color=second_color,stroke_width=0,
                fill_color=second_color,fill_opacity=1,
            ),
        )

    split_vertices=VGroup()
    radius=.36*model['node_size']
    for vertex in shared_vertices:
        center=np.array((*model['pos'][vertex],0))
        for start_angle,end_angle,color in (
            (0,np.pi,first_color),
            (np.pi,2*np.pi,second_color),
        ):
            angles=np.linspace(start_angle,end_angle,25)
            arc=[center+radius*np.array([np.cos(angle),np.sin(angle),0])
                 for angle in angles]
            split_vertices.add(Polygon(
                center,*arc,color=color,stroke_color=color,stroke_width=0,
                fill_color=color,fill_opacity=1,
            ))
    return VGroup(first,second,split_edges,split_vertices)


class _Storyboard(Scene):
    key=None

    def make_snapshot(self, snapshot):
        return visual_snapshot(snapshot)

    def construct(self):
        stages=graphs(self.key)[self.key]
        current=None
        for index, snapshot in enumerate(stages):
            nxt=self.make_snapshot(snapshot)
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
        model=graphs(self.key)[self.key][0][0]
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
        model=graphs(self.key)[self.key][0][0]
        self.add(visual_graph(model))
        first=complete_highlight(model,('0','1','4'),'#008c95',('#99d9dc',.28))
        second=complete_highlight(model,('0','1','2','3'),'#d1493f')

        self.play(FadeIn(first))
        self.wait(2)
        self.play(FadeOut(first))
        self.wait(.5)
        self.play(FadeIn(second))
        self.wait(2)
        self.play(FadeOut(second))
        self.wait(.5)
        combined=combined_complete_highlight(
            model,('0','1','4'),'#008c95',
            ('0','1','2','3'),'#d1493f',
            ('0','1'),(('0','1'),),('#99d9dc',.28),
        )
        self.play(FadeIn(combined))
        self.wait(2)


class GraficaDeClanes(_Storyboard):
    key='grafica_clanes'

    def construct(self):
        stages=graphs(self.key)[self.key]
        model=stages[0][0]
        clique_graph=stages[2][1]
        node_positions=clique_graph['pos']
        center_x=np.mean([position[0] for position in node_positions.values()])
        half_distance=np.linalg.norm(
            np.array(node_positions['q1'])-np.array(node_positions['q0'])
        )/2
        clique_graph=dict(clique_graph,pos={
            'q0':(center_x,-half_distance),
            'q1':(center_x,half_distance),
        })
        graph_label=MathTex(
            r"\mathsf{G}",color='#263445',tex_template=LATIN_MODERN_TEMPLATE,
        ).scale(2).move_to((
            (min(x for x,_ in model['pos'].values())+
             max(x for x,_ in model['pos'].values()))/2,
            -2.65,
            0,
        ))
        self.add(visual_graph(model))
        self.add(graph_label)

        first=complete_highlight(model,('0','1','4'),'#008c95',('#99d9dc',.28))
        second=complete_highlight(model,('0','1','2','3'),'#d1493f')
        self.play(FadeIn(first))
        self.wait(2)
        self.play(FadeOut(first))
        self.wait(.5)
        self.play(FadeIn(second))
        self.wait(2)
        self.play(FadeOut(second))
        self.wait(.5)

        combined=combined_complete_highlight(
            model,('0','1','4'),'#008c95',
            ('0','1','2','3'),'#d1493f',
            ('0','1'),(('0','1'),),('#99d9dc',.28),
        )
        self.play(FadeIn(combined))
        self.wait(2)

        right_graph=visual_graph(clique_graph)
        vertices=right_graph[2]
        edges=right_graph[1]
        clique_label=MathTex(
            r"\mathsf{K}\mathopen{\text{\sffamily (}}\mathsf{G}"
            r"\mathclose{\text{\sffamily )}}",
            color='#263445',tex_template=LATIN_MODERN_TEMPLATE,
        ).scale(2).move_to((
            center_x,-2.65,0,
        ))
        self.play(FadeIn(vertices),FadeIn(clique_label))
        self.wait(.75)
        self.play(AnimationGroup(*(Create(edge) for edge in edges),lag_ratio=0),
                  run_time=1)
        self.wait(2)


class Graficas(_Storyboard):
    key='graficas'

    def construct(self):
        wheel=graphs(self.key)[self.key][0][0]
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


class _LabeledIterates(_Storyboard):
    labels=()
    label_y=-2.65

    def construct(self):
        models=graphs(self.key)[self.key][-1]
        groups=[]
        for model,label in zip(models,self.labels):
            xs=[x for x,_ in model['pos'].values()]
            graph_label=MathTex(
                label,color='#263445',tex_template=LATIN_MODERN_TEMPLATE,
            ).scale(1.7).move_to(((min(xs)+max(xs))/2,self.label_y,0))
            groups.append(VGroup(visual_graph(model),graph_label))

        self.add(groups[0])
        self.wait(.65)
        self.play(FadeIn(groups[1]),run_time=1.05)
        self.wait(.65)
        self.play(FadeIn(groups[2]),run_time=1.05)
        self.wait(1.15)


class Iteradas(_LabeledIterates):
    key='iteradas'
    labels=(
        r"\mathsf{G}",
        r"\mathsf{K}\mathopen{\text{\sffamily (}}\mathsf{G}"
        r"\mathclose{\text{\sffamily )}}",
        r"\mathsf{K}^{2}\mathopen{\text{\sffamily (}}\mathsf{G}"
        r"\mathclose{\text{\sffamily )}}",
    )


class _CliqueSteps(_Storyboard):
    cliques=()
    highlight_fade_time=.1
    highlight_hold_time=.3
    between_cliques_time=0

    def construct(self):
        stages=graphs(self.key)[self.key]
        model=stages[0][0]
        self.add(visual_graph(model))
        self.wait(.5)
        for vertices,color,face in self.cliques:
            highlight=complete_highlight(model,vertices,color,face)
            self.play(FadeIn(highlight),run_time=self.highlight_fade_time)
            self.wait(self.highlight_hold_time)
            self.play(FadeOut(highlight),run_time=self.highlight_fade_time)
            if self.between_cliques_time:
                self.wait(self.between_cliques_time)
        self.play(FadeIn(visual_graph(stages[-1][1])))
        self.wait(2)


class PrismaClanes(_CliqueSteps):
    key='prisma_clanes'
    cliques=PRISM_CLIQUES


class PrismaK23(_CliqueSteps):
    key='prisma_k23'
    cliques=K23_CLIQUES


class Prisma(_Storyboard): key='prisma'


class SuspensionC5(_CliqueSteps):
    key='suspension_c5'
    cliques=SUSP_CLIQUES


class Comportamiento(_Storyboard):
    key='comportamiento'

    def make_snapshot(self, snapshot):
        result=visual_snapshot(snapshot)
        for label,models in (('Nula',snapshot[:2]),('Divergente',snapshot[2:])):
            if not models:
                continue
            centers=[]
            for model in models:
                xs=[x for x,_ in model['pos'].values()]
                centers.append((min(xs)+max(xs))/2)
            result.add(Tex(
                r'\sffamily '+label,color='#263445',tex_template=LATIN_MODERN_TEMPLATE,
            ).scale(1.5).move_to((sum(centers)/len(centers),-2.55,0)))
        return result
class IteradasOctaedro(_LabeledIterates):
    key='iteradas_octaedro'
    label_y=-3.0
    labels=(
        r"\mathsf{G}=\mathsf{O}_{3}",
        r"\mathsf{K}\mathopen{\text{\sffamily (}}\mathsf{G}"
        r"\mathclose{\text{\sffamily )}}",
        r"\mathsf{K}^{2}\mathopen{\text{\sffamily (}}\mathsf{G}"
        r"\mathclose{\text{\sffamily )}}",
    )


class RealizacionSimplicial(_Storyboard):
    key='realizacion_simplicial'

    def construct(self):
        model=graphs(self.key)[self.key][-1][0]
        faces,edges,dots=visual_graph(model)
        labels=realization_vertex_labels(model)
        self.add(dots[0],labels[0])
        self.wait(.65)
        for dot,label in zip(dots[1:],labels[1:]):
            self.play(FadeIn(dot),FadeIn(label),run_time=.6)
            self.wait(.35)
        for edge in edges:
            self.play(Create(edge),run_time=.6)
            self.bring_to_front(dots,labels)
            self.wait(.35)
        face=faces[0].set_z_index(-1)
        self.play(FadeIn(face),run_time=.7)
        self.wait(1.5)


def realization_vertex_labels(model):
    offsets={'1':(-.15,.5),'2':(-.15,-.5),'3':(0,.5),'4':(0,.5)}
    scale=model['node_size']
    return VGroup(*(
        MathTex(
            vertex,color='#263445',tex_template=LATIN_MODERN_TEMPLATE,
        ).scale(1.2*scale).move_to((
            x+offsets[vertex][0]*scale,y+offsets[vertex][1]*scale,0,
        ))
        for vertex,(x,y) in model['pos'].items()
    ))


class TopologiaGraficas(_Storyboard):
    key='topologia_graficas'

    def construct(self):
        left,right=graphs(self.key)[self.key][-1]
        left_group=VGroup(
            visual_graph(left),
            Tex(r'\sffamily Contraíble',color='#263445',
                tex_template=LATIN_MODERN_TEMPLATE).scale(1.4).move_to((-3.3,-3.1,0)),
        )
        faces,edges,dots=visual_graph(right)
        front_vertices={vertex for vertices,_,_ in right['faces'] for vertex in vertices}
        front_edge_ids={frozenset(edge) for vertices,_,_ in right['faces']
                        for edge in combinations(vertices,2)}
        back_edges=VGroup(*(edge for ids,edge in zip(right['edges'],edges)
                            if frozenset(ids) not in front_edge_ids))
        front_edges=VGroup(*(edge for ids,edge in zip(right['edges'],edges)
                             if frozenset(ids) in front_edge_ids))
        back_dots=VGroup(*(dot for vertex,dot in zip(right['pos'],dots)
                           if vertex not in front_vertices))
        front_dots=VGroup(*(dot for vertex,dot in zip(right['pos'],dots)
                            if vertex in front_vertices))
        right_group=VGroup(
            back_edges,back_dots,faces,front_edges,front_dots,
            Tex(r'\sffamily Homotópica a $S^2$',color='#263445',
                tex_template=LATIN_MODERN_TEMPLATE).scale(1.4).move_to((3.55,-3.1,0)),
        )
        self.add(left_group)
        self.wait(1.5)
        self.play(FadeIn(right_group),run_time=1)
        self.wait(2)


class Piramide(_Storyboard): key='piramide'
class Desmantelables(_Storyboard):
    key='desmantelables'

    def construct(self):
        stages=graphs(self.key)[self.key]
        model=stages[0][0]
        visual=visual_graph(model)
        dots=dict(zip(model['pos'],visual[2]))
        edges={frozenset(ids):line for ids,line in zip(model['edges'],visual[1])}
        self.add(visual)
        self.wait(1)
        for highlighted in stages[1::2]:
            colors=highlighted[0]['node_colors']
            dominated=next(vertex for vertex,color in colors.items() if color == CORAL)
            dominator=next(vertex for vertex,color in colors.items() if color == MINT)
            self.play(dots[dominated].animate.set_color(CORAL),
                      dots[dominator].animate.set_color(MINT),run_time=.4)
            self.wait(.9)
            incident=[edge for edge in edges if dominated in edge]
            self.play(FadeOut(dots[dominated]),
                      *(FadeOut(edges[edge]) for edge in incident),
                      dots[dominator].animate.set_color(CYAN),run_time=.5)
            for edge in incident:
                del edges[edge]
            self.wait(.4)
        self.wait(1)


class ConjuntosDominacion(_Storyboard):
    key='conjuntos_dominacion'

    def construct(self):
        sets=graphs(self.key)[self.key][-1][0]['sets']
        groups=[]
        for item in sets:
            outline=Circle(radius=item['radius'],color=item['color'],stroke_width=6)
            outline.move_to((*item['center'],0))
            label=Tex(r'\sffamily '+item['label'],color=item['color'],
                      tex_template=LATIN_MODERN_TEMPLATE)
            label.scale_to_fit_height(.34)
            if label.width > 2.4:
                label.scale_to_fit_width(2.4)
            label.move_to((*item['label_pos'],0))
            groups.append(VGroup(outline,label))
        self.add(groups[0])
        self.wait(1.5)
        for group in groups[1:]:
            self.play(FadeIn(group),run_time=1)
            self.wait(1.5)


class Dominados(_Storyboard): key='dominados'
