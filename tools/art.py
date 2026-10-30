# Left 16 columns; mirrored to 32. Rows 0..31.
L = [
"................",  # 0
"................",  # 1
"...k...k........",  # 2
"..khk.kok.......",  # 3
"..khk.kok.......",  # 4
"..kok.kok.......",  # 5
"..kooooodk......",  # 6
"...koooodk......",  # 7
"....kodddk......",  # 8
".....kdk....kk..",  # 9
"......kdk..kwek.",  # 10
".......kdk.kwek.",  # 11
"........kkkkkkkk",  # 12
".......koohooooo",  # 13
"......kohhoooooo",  # 14
".....koohooooooo",  # 15
".....kooooooooooo"[:16],  # 16
".....kooooooooko",  # 17
"..kk.kdoooooookk",  # 18
".kdk.kddoooooooo",  # 19
".kdkkkdddddddddd",  # 20
"..kdddkkkkkkkkkk",  # 21
"...kdk.kdk..kdk.",  # 22 legs
"...kdk.kdk..kdk.",  # 23
"rrrrrrrrrrrrrrrr",  # 24 rail
"gggggggggggggggg",  # 25
".ss...ss...ss...",  # 26 sleepers
".tt...tt...tt...",  # 27
"................",  # 28
"................",  # 29
"................",  # 30
"................",  # 31
]
for i,r in enumerate(L): assert len(r)==16,(i,len(r))
def mirror(r): return r + r[::-1]
G=[mirror(r) for r in L]
for y,ch in ((26,'s'),(27,'t')):
    G[y]=''.join(ch if (x%6) in (1,2) else '.' for x in range(32))
# sleepers should not mirror-collide oddly; fine.
if __name__=="__main__":
    for r in G: print(r.replace('.', ' '))

# Vibe coder sunglasses over the eyes (rows 9-11, before vertical centering).
def put(y, x0, x1, ch):
    G[y] = G[y][:x0] + ch * (x1 - x0 + 1) + G[y][x1 + 1:]
put(9, 9, 22, 'x')                     # frame bar, arms past the lenses
put(10, 9, 9, '.'); put(10, 22, 22, '.')
put(10, 10, 14, 'x'); put(10, 15, 16, '.'); put(10, 17, 21, 'x')
put(11, 11, 14, 'x'); put(11, 15, 16, '.'); put(11, 17, 20, 'x')
for x, c in ((11, 'w'), (12, 'c'), (18, 'w'), (19, 'c')):
    put(10, x, x, c)
put(11, 11, 14, 'v'); put(11, 17, 20, 'v')      # lens gradient
put(10, 13, 14, 'v'); put(10, 20, 21, 'v')
put(9, 10, 21, 'm')                               # frame top catches light
