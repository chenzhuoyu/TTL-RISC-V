#!/usr/bin/env python3
# -*- coding: utf-8 -8-

import svgwrite
import itertools

N = 33
L = []

d = 2
while True:
    L = [d] + L
    d = int(d * 1.5)
    if d >= N:
        break

def draw_tree(g, st, adj, tree):
    y = (st * (N + 2)) * 16 + 30
    t = 'Result' if st == len(L) else 'Stage j=%d, d=%d' % (len(L) - st, L[st])
    g.add(g.text(t, (16, y), font_size = '16px', font_family = 'monospace'))
    for i, (d, n) in enumerate(zip(adj, tree)):
        x = i * 16 + 26
        y = (st * (N + 2)) * 16 + 38
        for _ in range(d[1]):
            g.add(g.rect((x, y), (12, 44), rx = 6, ry = 6, fill = 'palegreen', stroke = 'green', stroke_width = 1.1))
            y += 48
        for _ in range(d[2]):
            g.add(g.rect((x, y), (12, 28), rx = 6, ry = 6, fill = 'lightpink', stroke = 'red', stroke_width = 1.1))
            y += 32
        x = i * 16 + 32
        y = st * (N + 2) * 16 + 44
        for _ in range(n):
            g.add(g.circle((x, y), 4, fill = 'black'))
            y += 16

g = svgwrite.Drawing('dadda.svg', size = ((N + 1) * 32, (len(L) + 1) * (N + 2) * 16 + 32), profile = 'tiny')
g.add(g.rect((0, 0), ('100%', '100%'), fill = 'white'))

tfa = 0
tha = 0
tree = list(itertools.chain(range(1, N + 1), range(N - 1, 0, -1)))

for st, n in enumerate(L):
    sfa = 0
    sha = 0
    adj = [(0, 0, 0)] * len(tree)
    for i, v in enumerate(tree[::-1], 1):
        if i != 0:
            v += adj[-i + 1][1]
            v += adj[-i + 1][2]
        if v > n:
            d = v - n
            fa = d // 2
            ha = 1 if d & 1 else 0
            sfa += fa
            sha += ha
            adj[-i] = (-d, fa, ha)
    tfa += sfa
    tha += sha
    print('Stage j=%d, d=%d:' % (len(L) - st, L[st]))
    print('  FA:', sfa)
    print('  HA:', sha)
    print()
    draw_tree(g, st, adj, tree)
    for i, v in enumerate(tree):
        tree[i] = v + adj[i][0] + (0 if i == len(tree) - 1 else (adj[i + 1][1] + adj[i + 1][2]))

print('Total:')
print('  FA:', tfa)
print('  HA:', tha)
print()
draw_tree(g, len(L), [(0, 0, 0)] * len(tree), tree)
g.save(pretty = True)
