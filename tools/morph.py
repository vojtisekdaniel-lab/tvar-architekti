"""Aligns rectilinear polygons for morphing (equal vertex counts, parity-preserving so edges stay axis-aligned)."""
import json, math, sys
sys.path.insert(0, '.')
from shapes import build

INF = float('inf')

def d2(p, q):
    return (p[0]-q[0])**2 + (p[1]-q[1])**2

def dp_assign(S, L):
    """S shorter (n), L longer (m), both start with a horizontal outgoing edge.
    Returns (cost, idx) with idx[j] = index of S vertex matched to L vertex j; every S vertex used an odd number of times."""
    n, m = len(S), len(L)
    dp = [[INF]*(m+1) for _ in range(n+1)]
    back = [[0]*(m+1) for _ in range(n+1)]
    dp[0][0] = 0.0
    for i in range(1, n+1):
        for j in range(i, m+1):
            best, bc = INF, 0
            acc = 0.0
            c = 1
            while c <= j:
                acc += d2(S[i-1], L[j-c])
                if c % 2 == 1 and dp[i-1][j-c] < INF:
                    v = dp[i-1][j-c] + acc
                    if v < best:
                        best, bc = v, c
                c += 1
            dp[i][j] = best
            back[i][j] = bc
    if dp[n][m] == INF:
        return INF, None
    idx = [0]*m
    j = m
    for i in range(n, 0, -1):
        c = back[i][j]
        for t in range(j-c, j):
            idx[t] = i-1
        j -= c
    return dp[n][m], idx

def align(P, Q):
    """returns (P_pad, Q_pad) with equal length"""
    swap = len(P) > len(Q)
    S, L = (Q, P) if swap else (P, Q)
    best = (INF, None, None)
    m = len(L)
    for r in range(0, m, 2):            # rotations of L keeping a horizontal first edge
        Lr = L[r:] + L[:r]
        cost, idx = dp_assign(S, Lr)
        if cost < best[0]:
            best = (cost, idx, Lr)
    cost, idx, Lr = best
    Spad = [S[i] for i in idx]
    return (Lr, Spad) if swap else (Spad, Lr)

def seg_intersect(a, b, c, d):
    def ccw(p, q, r):
        return (r[1]-p[1])*(q[0]-p[0]) - (q[1]-p[1])*(r[0]-p[0])
    d1 = ccw(a, b, c); d2_ = ccw(a, b, d); d3 = ccw(c, d, a); d4 = ccw(c, d, b)
    e = 1e-6
    return ((d1 > e and d2_ < -e) or (d1 < -e and d2_ > e)) and ((d3 > e and d4 < -e) or (d3 < -e and d4 > e))

def self_intersections(pts):
    n = len(pts)
    cnt = 0
    for i in range(n):
        a, b = pts[i], pts[(i+1) % n]
        if abs(a[0]-b[0]) < 1e-6 and abs(a[1]-b[1]) < 1e-6:
            continue
        for j in range(i+2, n):
            if i == 0 and j == n-1:
                continue
            c, d = pts[j], pts[(j+1) % n]
            if abs(c[0]-d[0]) < 1e-6 and abs(c[1]-d[1]) < 1e-6:
                continue
            if seg_intersect(a, b, c, d):
                cnt += 1
    return cnt

def lerp(A, B, s):
    return [(a[0]+(b[0]-a[0])*s, a[1]+(b[1]-a[1])*s) for a, b in zip(A, B)]

def diag_edges(pts):
    n = len(pts); bad = 0
    for i in range(n):
        a, b = pts[i], pts[(i+1) % n]
        if abs(a[0]-b[0]) > 1e-4 and abs(a[1]-b[1]) > 1e-4:
            bad += 1
    return bad

if __name__ == '__main__':
    P = build()
    steps = [['S1'], ['S2'], ['S3'], ['S4'], ['S5a', 'S5b', 'S5c'], ['S6'], ['S7'], ['S8'], ['S9']]
    def slots(k):
        ks = steps[k]
        return [P[ks[j] if j < len(ks) else ks[0]] for j in range(3)]
    trans = []
    report = []
    for k in range(8):
        sa, sb = slots(k), slots(k+1)
        need = 3 if k in (3, 4) else 1
        tr = []
        for j in range(need):
            A, B = align(sa[j], sb[j])
            worst = 0; diag = 0
            for t in range(0, 21):
                pts = lerp(A, B, t/20)
                worst = max(worst, self_intersections(pts))
                diag = max(diag, diag_edges(pts))
            report.append((k+1, k+2, j, len(A), worst, diag))
            tr.append({'a': [round(v, 2) for p in A for v in p], 'b': [round(v, 2) for p in B for v in p]})
        trans.append(tr)
    for r in report:
        print('S%d->S%d slot %d: %d verts, max self-intersections %d, max diagonal edges %d' % r)
    json.dump(trans, open('trans.json', 'w'))
    json.dump({k: [[round(x, 2), round(y, 2)] for x, y in v] for k, v in P.items()}, open('polys.json', 'w'))
