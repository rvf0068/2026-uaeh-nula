"""Geometry and stages shared by Manim and the bundled MP4 preview renderer.

All vertex sets are represented by graph node IDs; maximal cliques are computed
mathematically in comments and never confused with arbitrary complete subsets.
"""
from __future__ import annotations
from itertools import combinations
from math import sin, cos, pi

INK = '#263445'
EDGE = '#526779'
CYAN = '#008c95'
CORAL = '#d1493f'
GOLD = '#a56a00'
PURPLE = '#7050b5'
MINT = '#16805d'
BG = '#ffffff'
PALETTE = (CYAN, CORAL, GOLD, PURPLE, MINT)


def graph(pos, edges=(), faces=(), node_colors=None, edge_color=EDGE, edge_opacity=.8, node_size=1., scale=1., shift=(0,0)):
    """Return a drawable graph with optional complete-set highlighting polygons.

    faces: [(vertex_order, color, opacity)] are visual highlights, not necessarily
    simplices in a clique complex.
    """
    x, y = shift
    scaled = {str(k): (float(v[0])*scale+x, float(v[1])*scale+y) for k,v in pos.items()}
    return dict(pos=scaled,
                edges=[[str(a), str(b)] for a,b in edges],
                faces=[(list(map(str,vs)), c, float(op)) for vs,c,op in faces],
                node_colors={str(k):v for k,v in (node_colors or {}).items()},
                edge_color=edge_color, edge_opacity=edge_opacity,
                node_size=node_size)


def move(m, s=1., x=0, y=0):
    p=m['pos']
    return dict(m, pos={k:(a*s+x,b*s+y) for k,(a,b) in p.items()}, node_size=m['node_size']*s)


def stage(*gs): return list(gs)


def house_pos():
    return {'0':(-1.6,.8),'1':(1.6,.8),'2':(1.6,-1.8),'3':(-1.6,-1.8),'4':(0,2.4)}


def house_edges():
    return list(combinations('0123',2))+[('0','4'),('1','4')]


def house(faces=(), edge_count=None):
    edges=house_edges()
    return graph(house_pos(), edges if edge_count is None else edges[:edge_count], faces)


def k2(): return graph({'q0':(-.55,0),'q1':(.55,0)}, [('q0','q1')], node_colors={'q0':CORAL,'q1':CYAN})
def k1(): return graph({'v':(0,0)}, [], node_colors={'v':GOLD}, node_size=1.4)


def circle_pos(n, r=2.05, offset=pi/2):
    return {str(i):(r*cos(offset+2*pi*i/n),r*sin(offset+2*pi*i/n)) for i in range(n)}


def complete(n):
    return graph(circle_pos(n), list(combinations([str(i) for i in range(n)],2)))


def octa(n):
    # Nonedges are exactly the n antipodal pairs (i,i+n).
    p=circle_pos(2*n, r=2.0 if n<=4 else 2.5, offset=pi/2)
    e=[(str(i),str(j)) for i,j in combinations(range(2*n),2) if (j-i)!=n]
    return graph(p,e,edge_opacity=.86 if n<=4 else .36,node_size=.91 if n<=4 else .76)


def prism():
    p={}
    for i in range(3):
        a=pi/2+2*pi*i/3
        p[str(i)]=(-1.65+1.08*cos(a),1.08*sin(a))
        p[str(i+3)]=(1.65+1.08*cos(a),1.08*sin(a))
    e=list(combinations('012',2))+list(combinations('345',2))+[(str(i),str(i+3)) for i in range(3)]
    return graph(p,e)


def k23():
    p={'a':(-1.3,1),'b':(-1.3,-1),'u':(1.2,1.5),'v':(1.2,0),'w':(1.2,-1.5)}
    return graph(p, [(a,b) for a in ('a','b') for b in ('u','v','w')], node_colors={'a':CORAL,'b':CORAL,'u':CYAN,'v':CYAN,'w':CYAN})


def susp():
    p={f'r{i}':(1.55*cos(pi/2+2*pi*i/5),.85*sin(pi/2+2*pi*i/5)) for i in range(5)}
    p.update(t=(0,2.55),b=(0,-2.55))
    e=[(f'r{i}',f'r{(i+1)%5}') for i in range(5)]
    e += [(a,f'r{i}') for a in ('t','b') for i in range(5)]
    return graph(p,e,node_colors={'t':CORAL,'b':CYAN})


def ksusp():
    # q^+_i={t,r_i,r_(i+1)}, q^-_i={b,r_i,r_(i+1)}.
    # Same-level cliques all meet at an apex. Opposite-level cliques meet
    # precisely when their rim edges share one of their two endpoints.
    p={}
    for i in range(5):
        theta=pi/2+2*pi*i/5
        p[f't{i}']=(1.6*cos(theta),1.55+0.7*sin(theta))
        p[f'b{i}']=(1.6*cos(theta),-1.55+0.7*sin(theta))
    e=[]
    for prefix in ('t','b'):
        e += [(f'{prefix}{i}',f'{prefix}{j}') for i,j in combinations(range(5),2)]
    for i in range(5):
        for j in range(5):
            if (i-j)%5 in (0,1,4): e.append((f't{i}',f'b{j}'))
    return graph(p,e,node_colors={f't{i}':CORAL for i in range(5)} | {f'b{i}':CYAN for i in range(5)},edge_opacity=.59,node_size=.88)


def pyramid():
    p={'x0':(-2.65,-1.5),'x1':(-.75,-.2),'x2':(2.65,-1.5),
       'y0':(-1.45,1.0),'y1':(1.45,1.0),'z0':(0,2.6)}
    e=[('x0','x1'),('x1','x2'),('y0','y1'),('x0','y0'),('y0','z0'),
       ('z0','y1'),('y1','x2'),('y0','x1'),('x1','y1')]
    return graph(p,e)


def pyramid_face(i):
    # Three pairwise intersecting maximal cliques with empty total intersection.
    faces=[(('x0','x1','y0'),CORAL,.25),
           (('x1','x2','y1'),CYAN,.25),
           (('y0','y1','z0'),GOLD,.25)]
    return graph(pyramid()['pos'],pyramid()['edges'],faces[:i])


def tree_nodes():
    p={'0':(-3,-.7),'1':(-2,0),'2':(-1,.5),'3':(0,0),'4':(1,.7),'5':(2,1.5),'6':(2,-.8),'7':(-.5,-1.5)}
    e=[('0','1'),('1','2'),('2','3'),('3','4'),('4','5'),('4','6'),('3','7')]
    return p,e


def graphs():
    from copy import deepcopy
    frames={}
    # 0. A graphic on the title slide.
    frames['intro']=[stage(move(house(edge_count=0),.9)),stage(move(house(edge_count=4),.9)),stage(move(house(),.9))]
    # 1. A planar wheel graph, used to introduce simple graphs.
    p10={str(i):(2.85*cos(pi/2-2*pi*i/9),2.85*sin(pi/2-2*pi*i/9))
         for i in range(9)}
    p10['9']=(0,0)
    e10=[(str(i),str((i+1)%9)) for i in range(9)]+[(str(i),'9') for i in range(9)]
    frames['graficas']=[stage(graph(p10,e10))]
    # 2. Complete vertex subsets; a single vertex, triangles and K4.
    h=house()
    frames['completas']=[stage(h)]
    # 3. Maximal completes only, not arbitrary complete subsets.
    frames['clanes']=[stage(h),stage(house([(('0','1','4'),CYAN,.27)])),
                      stage(house([(('0','1','4'),CYAN,.23),(('0','1','2','3'),CORAL,.21)]))]
    # 4-5. Clique graph of the house: K2.
    left=move(h,.82,-3.45,0)
    right=move(k2(),1.5,3.4,0)
    frames['grafica_clanes']=[stage(left),stage(move(house([(('0','1','4'),CYAN,.28)]),.82,-3.45,0)),
                              stage(move(house([(('0','1','4'),CYAN,.21),(('0','1','2','3'),CORAL,.20)]),.82,-3.45,0),right)]
    frames['ejemplo']=[stage(left),stage(move(house([(('0','1','2','3'),CORAL,.25)]),.82,-3.45,0)),
                       stage(move(house([(('0','1','4'),CYAN,.25)]),.82,-3.45,0)),
                       stage(left,right)]
    # 6. Repeated clique graphs: house -> K2 -> K1.
    g1=move(h,.63,-4.1,0); g2=move(k2(),1.25,0,0); g3=move(k1(),1.0,3.95,0)
    frames['iteradas']=[stage(g1),stage(g1,g2),stage(g1,g2,g3)]
    # 7. Triangular prism -> K_{2,3} -> triangular prism.
    frames['prisma']=[stage(prism()),stage(move(prism(),.68,-3.45,0),move(k23(),.70,3.4,0)),
                      stage(move(prism(),.53,-4.5,0),move(k23(),.62,0,0),move(prism(),.53,4.5,0))]
    # 8. Suspension of C5 -> 10-vertex clique graph.
    frames['suspension_c5']=[stage(susp()),stage(move(susp(),.72,-3.55,0),move(ksusp(),.78,3.35,0))]
    # 9. Convergent and divergent examples; stage across horizontal layout.
    frames['comportamiento']=[stage(move(complete(3),.70,-3.6,0)),
             stage(move(complete(3),.70,-3.6,0),move(k1(),1.1,-1.7,0)),
             stage(move(complete(3),.55,-4.7,0),move(k1(),1,-2.8,0),move(octa(3),.52,1.0,0)),
             stage(move(complete(3),.55,-4.7,0),move(k1(),1,-2.8,0),move(octa(3),.52,1,0),move(octa(4),.47,4.7,0))]
    # 10. Order growth O3 -> O4 -> O8; latter has 16 vertices.
    frames['iteradas_octaedro']=[stage(octa(3)),
             stage(move(octa(3),.62,-3.8,0),move(octa(4),.65,3.3,0)),
             stage(move(octa(3),.46,-4.7,0),move(octa(4),.46,0,0),move(octa(8),.55,4.6,0))]
    # 11. Family of maximal cliques in a star, sharing a vertex.
    p={'z':(0,0),'a':(-2.8,1.5),'b':(2.8,1.5),'c':(0,-2.55)}
    star_e=[('z','a'),('z','b'),('z','c')]
    frames['helly']=[stage(graph(p,star_e)),
        stage(graph(p,star_e,node_colors={'z':GOLD,'a':CYAN})),
        stage(graph(p,star_e,node_colors={'z':GOLD,'a':CORAL,'b':CYAN,'c':MINT}))]
    # 12. The 'pyramid' counterexample to clique-Helly: 3 maximal cliques.
    frames['piramide']=[stage(pyramid()),stage(pyramid_face(1)),stage(pyramid_face(2)),stage(pyramid_face(3))]
    # 13. Clique graph of pyramid is K4; second iterate singleton.
    frames['escalante']=[stage(move(pyramid(),.72,-3.55,0)),
        stage(move(pyramid(),.72,-3.55,0),move(complete(4),.70,2.3,0)),
        stage(move(pyramid(),.57,-4.4,0),move(complete(4),.62,0,0),move(k1(),1.1,4.5,0))]
    # 14. Removing dominated vertices from a tree.
    p,e=tree_nodes()
    frames['desmantelables']=[stage(graph(p,e))]
    for removed in [('0','5','6','7'),('0','5','6','7','1'),('0','5','6','7','1','2'),('0','5','6','7','1','2','3')]:
        remain={k:v for k,v in p.items() if k not in removed}
        frames['desmantelables'].append(stage(graph(remain,[(a,b) for a,b in e if a in remain and b in remain])))
    # 15. Attached leaves on O3 are dominated; remove them.
    octg=octa(3); pp=dict(octg['pos']); pp.update(u=(-3.6,-.2),v=(3.6,.2))
    ee=octg['edges']+[('u','0'),('v','3')]
    frames['dominados']=[stage(graph(pp,ee,edge_opacity=.75)),
         stage(graph(pp,ee,node_colors={'u':CORAL,'v':CORAL},edge_opacity=.75)),
         stage(octa(3)),
         stage(move(octa(3),.75,-2.7,0),move(octa(4),.75,2.7,0))]
    return frames

SCENE_NAMES = {
    'Intro':'intro','Graficas':'graficas','Completas':'completas','Clanes':'clanes',
    'GraficaDeClanes':'grafica_clanes','Ejemplo':'ejemplo','Iteradas':'iteradas',
    'Prisma':'prisma','SuspensionC5':'suspension_c5','Comportamiento':'comportamiento',
    'IteradasOctaedro':'iteradas_octaedro','Helly':'helly','Piramide':'piramide',
    'Escalante':'escalante','Desmantelables':'desmantelables','Dominados':'dominados'
}
