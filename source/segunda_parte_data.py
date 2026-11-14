"""Models and independently checkable certificates for the new talk section.

The graph6 strings below are the exact ten-vertex examples. No files from the
large census are required. Calculations use NetworkX, with deterministic ties.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations
from math import pi, cos, sin

import networkx as nx

EXAMPLES = ("ICvbvy}|g", "IEivrzm}o")
COLORS = dict(ink="#263445", edge="#526779", cyan="#008c95", coral="#d1493f", gold="#a56a00")


def graph6(s):
    return nx.from_graph6_bytes(s.encode('ascii'))


def clique_graph(g):
    """Graph of inclusion-maximal complete vertex sets (not all completes)."""
    cliques = sorted(tuple(sorted(c)) for c in nx.find_cliques(g))
    h = nx.Graph()
    h.add_nodes_from(range(len(cliques)))
    h.add_edges_from((i, j) for i in range(len(cliques))
                     for j in range(i+1, len(cliques))
                     if set(cliques[i]).intersection(cliques[j]))
    return h


def all_simplices(g):
    """Non-empty faces of the clique complex."""
    out = set()
    for q in nx.find_cliques(g):
        q = sorted(q)
        for k in range(1, len(q)+1):
            out.update(frozenset(c) for c in combinations(q, k))
    return out


def simplicial_collapses(g):
    """A reproducible list of elementary (free face, facet) collapses.

    Prefer higher-dimensional facets; ties are sorted lexicographically.
    This does not silently identify simple-homotopy with homotopy.
    """
    faces = all_simplices(g)
    pairs = []
    while True:
        cover = Counter(frozenset(f - {v}) for f in faces for v in f if len(f)>1)
        options=[]
        for facet in faces:
            if len(facet)<2:
                continue
            for v in facet:
                free=facet-{v}
                if cover[free]==1:
                    options.append((len(facet), tuple(sorted(facet)), tuple(sorted(free))))
        if not options:
            break
        _, facet, free = sorted(options, key=lambda x:(-x[0],x[1],x[2]))[0]
        assert frozenset(facet) in faces and frozenset(free) in faces
        pairs.append((free, facet))
        faces.remove(frozenset(facet))
        faces.remove(frozenset(free))
    return faces, pairs


def dominated_folds(g):
    """Ordinary closed-neighborhood dominated deletions and remaining core."""
    h=g.copy()
    steps=[]
    while True:
        found=None
        for v in sorted(h):
            Nv=set(h[v])|{v}
            for w in sorted(h[v]):
                if Nv <= (set(h[w])|{w}):
                    found=(v,w);break
            if found:
                break
        if found is None:
            break
        steps.append(found)
        h.remove_node(found[0])
    return h,steps


def sphere_core(g):
    faces,steps=simplicial_collapses(g)
    one={next(iter(f)) for f in faces if len(f)==1}
    edges={f for f in faces if len(f)==2}
    tris={f for f in faces if len(f)==3}
    assert all(len(f)<=3 for f in faces)
    assert (len(one),len(edges),len(tris),len(steps))==(8,18,12,20)
    edge_count=Counter(frozenset(e) for tri in tris for e in combinations(sorted(tri),2))
    assert set(edge_count)==edges and set(edge_count.values())=={2}
    h=nx.Graph()
    h.add_nodes_from(one)
    h.add_edges_from(tuple(e) for e in edges)
    assert nx.is_connected(h) and nx.check_planarity(h)[0]
    for v in h:
        # Each vertex link must be a single circle (not a disjoint union).
        link=nx.Graph()
        link.add_edges_from((a,b) for a,b in combinations(sorted(h[v]),2)
                            if frozenset((a,b,v)) in tris)
        assert nx.is_connected(link) and all(d==2 for _,d in link.degree)
    assert len(one)-len(edges)+len(tris)==2
    return h, tris, steps


def planar_disc():
    """The nine-vertex triangulated disk H of Fig. 2 (2008), reconstructed
    using the labeled triangle pattern and cross-checked against Theorem 3.1.
    """
    pos={'A':(-2,2),'B':(2,2),'C':(2,-2),'D':(-2,-2),
         'U':(0,1),'L':(-1,0),'M':(0,0),'R':(1,0),'V':(0,-1)}
    e=[('A','B'),('B','C'),('C','D'),('D','A'),
       ('A','U'),('A','L'),('B','U'),('B','R'),
       ('C','R'),('C','V'),('D','L'),('D','V'),
       ('U','L'),('U','R'),('U','M'),('L','M'),('R','M'),
       ('L','V'),('R','V'),('M','V')]
    h=nx.Graph();h.add_nodes_from(pos);h.add_edges_from(e)
    assert h.number_of_nodes()==9 and h.number_of_edges()==20
    assert nx.check_planarity(h)[0]
    assert len(list(nx.find_cliques(h)))==12
    return h,pos


def suspension(h):
    g=h.copy()
    for p in ('X','Y'):
        g.add_node(p)
        g.add_edges_from((p,v) for v in h)
    return g


def octahedral_retract_witness(h):
    """Check the four-clique C4 and the induced O4 inside K(Susp H).
    The existence of the retraction uses Theorem 3.1 (2008).
    """
    fours=[frozenset(q) for q in (('A','B','U'),('B','C','R'),('C','D','V'),('D','A','L'))]
    cq=[frozenset(q) for q in nx.find_cliques(h)]
    assert all(q in cq for q in fours)
    assert all(not (q&fours[0] and q&fours[2]) and
               not (q&fours[1] and q&fours[3]) for q in cq if q not in fours)
    s=suspension(h)
    cliques=[frozenset(q) for q in nx.find_cliques(s)]
    selected=[q|{p} for p in ('X','Y') for q in fours]
    assert all(q in cliques for q in selected)
    edges=sum(bool(q&r) for q,r in combinations(selected,2))
    assert edges==24 # O4 has eight vertices and 24 edges
    nonedges=[(q,r) for q,r in combinations(selected,2) if not(q&r)]
    assert len(nonedges)==4
    return len(cliques),nonedges


def _scaled(pos,scale,dx=0,dy=0):
    return {str(v):(float(x)*scale+dx,float(y)*scale+dy) for v,(x,y) in pos.items()}


def model(g,pos,scale=1.,shift=(0,0),triangles=(),colors=None,fill="#a7d4d5",edge_opacity=.84,node_size=.88):
    vertices=_scaled(pos,scale,*shift)
    return dict(pos=vertices,
                edges=[(str(a),str(b)) for a,b in sorted(tuple(sorted(e)) for e in g.edges)],
                faces=[([str(v) for v in face],fill,.37) for face in triangles],
                node_colors={str(k):v for k,v in (colors or {}).items()},
                edge_color=COLORS['edge'],edge_opacity=edge_opacity,
                node_size=node_size)


def graph_example(s,scale=1.,shift=(0,0)):
    g=graph6(s)
    pos=nx.spring_layout(g,seed=2026,iterations=150)
    # Normalize to radius 2, with deterministic spring geometry.
    R=max((x*x+y*y)**.5 for x,y in pos.values())
    pos={k:(2*x/R,2*y/R) for k,(x,y) in pos.items()}
    return model(g,pos,scale,shift,edge_opacity=.60,node_size=.84)


def core_example(s,scale=1.,shift=(0,0)):
    """A Tutte (barycentric) planar drawing of the spherical core.

    Every face of a maximal planar graph can serve as the outer triangle.
    Choose the embedding that best separates the vertices. This avoids
    overlapping dots in the relatively narrow 16:9 Manim frames.
    """
    import numpy as np
    h,tris,_=sphere_core(graph6(s))
    best=None
    for face in sorted(tris,key=lambda q:tuple(sorted(q))):
        outer=sorted(face)
        inner=sorted(set(h)-set(outer))
        idx={v:i for i,v in enumerate(inner)}
        pos={outer[0]:(-2.,-1.4),outer[1]:(2.,-1.4),outer[2]:(0.,2.)}
        m=np.zeros((len(inner),len(inner)))
        rhs=np.zeros((len(inner),2))
        for u in inner:
            m[idx[u],idx[u]]=h.degree[u]
            for v in h[u]:
                if v in idx:
                    m[idx[u],idx[v]]-=1
                else:
                    rhs[idx[u]]+=pos[v]
        coords=np.linalg.solve(m,rhs)
        pos.update({v:tuple(map(float,coords[idx[v]])) for v in inner})
        gap=min(float(np.linalg.norm(np.subtract(pos[u],pos[v])))
                for u,v in combinations(sorted(h),2))
        if best is None or gap>best[0]:
            best=(gap,pos,frozenset(outer))
    _,pos,outer=best
    interior=[tuple(sorted(t)) for t in tris if t!=outer]
    assert len(interior)==11
    return model(h,pos,scale,shift,interior,node_size=.82)


def disc_example(scale=1.,shift=(0,0)):
    h,p=planar_disc()
    triangles=[tuple(sorted(q)) for q in nx.find_cliques(h)]
    return model(h,p,scale,shift,triangles,fill="#a7d4d5",node_size=.9)


def suspension_example(scale=1.,shift=(0,0)):
    h,p=planar_disc()
    g=suspension(h)
    pos={v:(x*.75,y*.6) for v,(x,y) in p.items()}
    pos.update(X=(0,2.9),Y=(0,-2.9))
    return model(g,pos,scale,shift,colors={'X':COLORS['coral'],'Y':COLORS['cyan']},
                 edge_opacity=.6,node_size=.72)


def verify_example(s):
    g=graph6(s)
    core,triangles,collapses=sphere_core(g)
    orders=[g.number_of_nodes()]
    cur=g
    for i in range(3):
        cur=clique_graph(cur)
        orders.append(cur.number_of_nodes())
    reduced,folds=dominated_folds(cur)
    assert len(reduced)==1 and len(folds)==cur.number_of_nodes()-1
    return dict(graph6=s,vertices=len(g),edges=g.number_of_edges(),
                core_f_vector=(len(core),core.number_of_edges(),len(triangles)),
                elementary_collapses=len(collapses),iterated_orders=orders,
                K3_folds=len(folds),clique_null=True,homotopy='S^2')

if __name__=='__main__':
    for code in EXAMPLES:
        print(verify_example(code))
    h,_=planar_disc();print('Fig2',octahedral_retract_witness(h))
