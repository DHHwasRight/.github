from art import G
G = ['.'*32]*2 + G[:30]          # center vertically
P = {'k':'#2a120a','o':'#e8622c','d':'#a8401c','h':'#ffab73','w':'#ffffff','e':'#111111','x':'#07080c','c':'#6ee7ff','v':'#5b2d8f','m':'#3c4458',
     'r':'#d3dae5','g':'#7c8594','s':'#8a5a34','t':'#5e3c22'}
BG='#151a24'
rects=[f'<rect width="32" height="32" fill="{BG}"/>']
for y,row in enumerate(G):
    for x,c in enumerate(row):
        if c in P: rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{P[c]}"/>')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="512" height="512" shape-rendering="crispEdges">{"".join(rects)}</svg>'
open('logo.svg','w').write(svg)
# transparent variant for READMEs
open('logo-transparent.svg','w').write(svg.replace(rects[0],''))
