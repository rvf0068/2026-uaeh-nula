"""Manim Community scenes for part II of the Org/Beamer talk.

Slides use the same white/teal/coral palette as part I. Numerical claims and
models come from segunda_parte_data.py, which is independent of Manim.
"""
from itertools import combinations
import numpy as np
from manim import (
    Scene, Dot, Line, Polygon, VGroup, Tex, MathTex, TexTemplate, Rectangle,
    RoundedRectangle, Arrow, FadeIn, FadeOut, Create, AnimationGroup, config,
)
from storyboards import BG, CYAN, CORAL, GOLD, INK, graphs
from segunda_parte_data import EXAMPLES, verify_example

config.background_color = BG
TEMPLATE = TexTemplate()
TEMPLATE.add_to_preamble(r'\usepackage[T1]{fontenc}')
TEMPLATE.add_to_preamble(r'\usepackage{lmodern}')


def draw_model(m):
    """Same visual grammar as visual_graph in source/manim_scenes.py."""
    pos=m['pos']
    faces=VGroup(*(
        Polygon(*[(pos[i][0],pos[i][1],0) for i in ids],
                color=color,stroke_width=0,fill_color=color,fill_opacity=opacity)
        for ids,color,opacity in m['faces']
    ))
    edges=VGroup(*(
        Line((*pos[u],0),(*pos[v],0),color=m['edge_color'],
             stroke_width=12,stroke_opacity=m['edge_opacity'])
        for u,v in m['edges']
    ))
    dots=VGroup(*(
        Dot(point=(*xy,0),radius=.22*m['node_size'],
            color=m['node_colors'].get(v,CYAN))
        for v,xy in pos.items()
    ))
    return VGroup(faces,edges,dots)


def text_at(tex,x,y,scale=.83):
    return Tex(tex,color=INK,tex_template=TEMPLATE).scale(scale).move_to((x,y,0))


def math_at(tex,x,y,scale=1):
    return MathTex(tex,color=INK,tex_template=TEMPLATE).scale(scale).move_to((x,y,0))


class BettiOctaedros(Scene):
    """O3 (S2) -> O4 (S3) -> O8 (S7), each with an increasing Betti degree."""
    def construct(self):
        models=graphs()['betti_octaedros'][-1]
        x=[-4.5,0,4.5]
        labels=(r'O_3\simeq S^2',r'O_4\simeq S^3',r'O_8\simeq S^7')
        group=[VGroup(draw_model(m),math_at(t,xx,-2.85,.87))
               for m,t,xx in zip(models,labels,x)]
        self.add(group[0]);self.wait(.65)
        for nxt in group[1:]:
            self.play(FadeIn(nxt),run_time=1.1)
            self.wait(.6)
        self.wait(1.3)


class DiscoSuspension(Scene):
    """The actual nine-vertex disk H and its eleven-vertex suspension."""
    def construct(self):
        h,s=graphs()['disco_suspension'][-1]
        left=VGroup(draw_model(h),math_at(r'H\simeq *',-3.45,-3,.96))
        right=VGroup(draw_model(s),math_at(r'G=\operatorname{Susp}(H)\simeq *',3.5,-3,.78))
        self.add(left);self.wait(1)
        self.play(FadeIn(right),run_time=1.3)
        self.wait(2)


class RetractoOctaedro(Scene):
    """The O4 retract guaranteed by Theorem 3.1 of the 2008 paper."""
    def construct(self):
        m=graphs()['retracto_octaedro'][-1][0]
        g=draw_model(m)
        self.add(g)
        self.wait(.65)
        # Antipodal nonedges of O4 are colored as four distinct pairs.
        for index,color in enumerate((CORAL,CYAN,GOLD,'#7050b5')):
            ids=(str(index),str(index+4))
            points=VGroup(*[
                Dot(point=(*m['pos'][v],0),radius=.35,color=color)
                for v in ids
            ])
            self.play(FadeIn(points),run_time=.3)
            self.wait(.35)
        caption=math_at(r'K(G)\longrightarrow O_4',0,-3.05,1.05)
        self.play(FadeIn(caption),run_time=.7)
        self.wait(2)


class DosEjemplosS2(Scene):
    def construct(self):
        a,b=graphs()['dos_ejemplos_s2'][-1]
        la=VGroup(draw_model(a),math_at('G_1',-3.5,-2.8,1.2))
        lb=VGroup(draw_model(b),math_at('G_2',3.5,-2.8,1.2))
        self.add(la);self.wait(.8)
        self.play(FadeIn(lb),run_time=1.05)
        self.wait(1.7)


class ColapsosS2(Scene):
    """Two exact 20-collapse certificates, shown as spherical triangulations."""
    def construct(self):
        stages=graphs()['colapsos_s2']
        for i,(original,core) in enumerate(stages):
            old=VGroup(draw_model(original),math_at(f'G_{{{i+1}}}',-3.45,-3.1,1.1))
            new=VGroup(draw_model(core),math_at(r'\simeq S^2',3.4,-3.1,1.06))
            if i==0:
                self.add(old)
            else:
                self.play(FadeOut(display),FadeIn(old),run_time=.9)
            self.wait(.55)
            caption=text_at(r'20 colapsos elementales',0,2.9,.83)
            self.play(FadeIn(new),FadeIn(caption),run_time=1)
            self.wait(1.3)
            display=VGroup(old,new,caption)
        self.wait(.6)


class IteradasNulas(Scene):
    """Orders 10 -> 15/14 -> 22 -> 63/65; the last graphs dismantle."""
    def construct(self):
        values=[verify_example(s)['iterated_orders'] for s in EXAMPLES]
        x=(-4.8,-1.6,1.6,4.8)
        tiles=VGroup()
        for row,data in enumerate(values):
            y=1.15 if row==0 else -1.4
            head=math_at('G_1' if row==0 else 'G_2',-6.5,y,.9)
            rowgroup=VGroup(head)
            for j,count in enumerate(data):
                tile=RoundedRectangle(width=2.2,height=1.22,corner_radius=.12,
                                      stroke_color=CYAN if row==0 else CORAL,
                                      stroke_width=3,fill_color='#f1f8f8',fill_opacity=1)
                tile.move_to((x[j],y,0))
                number=math_at(str(count),x[j],y+.05,1.2)
                label=math_at('G' if j==0 else ('K(G)' if j==1 else f'K^{{{j}}}(G)'),
                              x[j],y-.37,.5)
                rowgroup.add(tile,number,label)
                if j:
                    rowgroup.add(Arrow((x[j-1]+1.13,y,0),(x[j]-1.13,y,0),
                                       buff=0,color=INK,stroke_width=3,tip_length=.17))
            self.play(FadeIn(rowgroup),run_time=1.1)
            self.wait(.85)
            tiles.add(rowgroup)
        note=math_at(r'K^3(G_i)\ \text{es desmantelable}',0,-3.05,.89)
        self.play(FadeIn(note))
        self.wait(1.8)
