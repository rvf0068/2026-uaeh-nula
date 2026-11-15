#!/usr/bin/env python3
"""Independent preview renderer (Pillow + ffmpeg), not Manim.

The bundle contains its outputs for immediate PDF compilation. To generate the
actual Manim Community renders use `bash scripts/render_manim.sh` instead.
"""
from __future__ import annotations
import os, sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from storyboards import graphs, BG, CYAN

W,H,FPS=800,450,12
XSPAN,YSPAN=13.6,7.65

def xy(x,y): return (int(W/2+x*W/XSPAN),int(H/2-y*H/YSPAN))
def rgb(hexcode): return tuple(bytes.fromhex(hexcode.lstrip('#')))

def paint(snapshot):
    im=Image.new('RGBA',(W,H),(*rgb(BG),255))
    for model in snapshot:
        if model['faces']:
            overlay=Image.new('RGBA',(W,H),(0,0,0,0))
            dr=ImageDraw.Draw(overlay,'RGBA')
            for ids,color,a in model['faces']:
                dr.polygon([xy(*model['pos'][i]) for i in ids],fill=(*rgb(color),int(a*255)))
            im=Image.alpha_composite(im,overlay)
    d=ImageDraw.Draw(im,'RGBA')
    for model in snapshot:
        op=int(model['edge_opacity']*255)
        for a,b in model['edges']:
            d.line([xy(*model['pos'][a]),xy(*model['pos'][b])],fill=(*rgb(model['edge_color']),op),width=3)
    for model in snapshot:
        for name,(x,y) in model['pos'].items():
            cx,cy=xy(x,y)
            r=max(3,int(6*model['node_size']))
            c=rgb(model['node_colors'].get(name,CYAN))
            d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*c,255))
        for item in model.get('sets', ()):
            x,y=item['center']
            r=item['radius']
            d.ellipse((xy(x-r,y+r),xy(x+r,y-r)),
                      outline=(*rgb(item['color']),255),width=4)
            d.text(xy(*item['label_pos']),item['label'],
                   fill=(*rgb(item['color']),255),anchor='mm',
                   font=ImageFont.truetype('DejaVuSans.ttf',size=18))
    return im.convert('RGB')

def mix(a,b,t):
    return Image.blend(a,b,max(0,min(1,t)))

def render(slug, stages):
    imgs=[paint(s) for s in stages]
    imgs[0].save(ROOT/'posters'/f'{slug}.png', optimize=True)
    dest=ROOT/'videos'/f'{slug}.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo',
         '-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264',
         '-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        blank=Image.new('RGB',(W,H),rgb(BG))
        def send(im): p.stdin.write(im.tobytes())
        for k,im in enumerate(imgs):
            if k==0:
                for fr in range(8): send(mix(blank,im,(fr+1)/8))
            else:
                for fr in range(7): send(mix(imgs[k-1],im,(fr+1)/7))
            for fr in range(9): send(im)
        for fr in range(15): send(imgs[-1])
    finally:
        p.stdin.close()
    if p.wait(): raise RuntimeError('ffmpeg failed: '+slug)
    print(f'{slug:<25} {dest.stat().st_size/1024:.0f} KiB',flush=True)

if __name__=='__main__':
    for slug,stages in graphs().items(): render(slug, stages)
