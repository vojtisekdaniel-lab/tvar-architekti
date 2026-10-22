"""Varianty prvního tvaru pro klidový pohyb: posun hran (jen kolmo), kontrola křížení a minimální velikosti detailů."""
import json, random, math, sys
sys.path.insert(0, 'tools')
from morph import self_intersections, lerp

T = json.load(open('tools/trans.json'))
pad = [(T[0][0]['a'][i], T[0][0]['a'][i+1]) for i in range(0, len(T[0][0]['a']), 2)]
base = []
for p in pad:                      # původní tvar bez zdvojených vertexů z morfování
    if not base or p != base[-1]: base.append(p)
if base[0] == base[-1]: base.pop()
n = len(base)
idx = [min(range(n), key=lambda j: (base[j][0]-p[0])**2 + (base[j][1]-p[1])**2) for p in pad]

def apply(off):
    out = []
    for i in range(n):
        x, y = base[i]
        if i % 2 == 0: x += off[(i-1) % n]; y += off[i]
        else: x += off[i]; y += off[i-1]
        out.append((x, y))
    return out

def ok(pts, minlen=16):
    for i in range(n):
        a, b = pts[i], pts[(i+1) % n]
        if math.hypot(a[0]-b[0], a[1]-b[1]) < minlen: return False
    if self_intersections(pts): return False
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs) > 120 and max(xs) < 1800 and min(ys) > 150 and max(ys) < 1000

def leg_ok(A, B):
    return all(ok(lerp(A, B, t/24), 10) for t in range(25))

random.seed(11)
AMP = 64
variants, offs = [], []
tries = 0
while len(variants) < 6 and tries < 400000:
    tries += 1
    off = [random.uniform(-AMP, AMP) * (1 if random.random() < 0.6 else 0.25) for _ in range(n)]
    pts = apply(off)
    if not ok(pts): continue
    prev = variants[-1] if variants else base
    if not leg_ok(prev, pts): continue
    variants.append(pts); offs.append(off)
# poslední noha zpět na základ
print(len(variants), 'variant po', tries, 'pokusech', 'návrat ok:', leg_ok(variants[-1], base) if variants else None)
json.dump([[round(v, 1) for i in range(len(pad)) for v in pts[idx[i]]] for pts in variants], open('tools/idle.json', 'w'))
print(n, 'vertexů v základu')

# --- keyframy klidového pohybu: základ -> tvary podobné dalším krokům (míchání s tvarem kroku 2) a náhodné varianty
A = T[0][0]['a']; B = T[0][0]['b']
P = lambda arr: [(arr[i], arr[i+1]) for i in range(0, len(arr), 2)]
def mix(m): return [A[i] + (B[i]-A[i]) * m for i in range(len(A))]
Vv = json.load(open('tools/idle.json'))
kf = [A, mix(0.55), Vv[0], mix(0.3), Vv[2], mix(0.8), Vv[4], mix(0.15), A]
good = True
for i in range(len(kf)-1):
    g = all(not self_intersections(lerp(P(kf[i]), P(kf[i+1]), t/24)) for t in range(25))
    print('noha', i, 'ok' if g else 'KŘÍŽENÍ'); good &= g
json.dump([[round(v, 1) for v in k] for k in kf], open('tools/idle.json', 'w'))
