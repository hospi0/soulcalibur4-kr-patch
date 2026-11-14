# -*- coding: utf-8 -*-
"""arcade 키 흐름을 subtitle_demo 키 한 주기(1875 B)의 조각들로 덮어 본다.
python tools/ks_seg.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def load(name):
    ct = open(os.path.join(TEXT, name), 'rb').read()
    pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
    return bytes(a ^ b for a, b in zip(ct, pt))


def main():
    a = load('subtitle_demo.msu')
    P = 1875
    assert a[:len(a) - P] == a[P:]
    T = a[:P]
    TT = T + T
    b = load('arcade.msu')
    print('demo 키 앞 64:', T[:64].hex())
    print('arcade 키 앞 64:', b[:64].hex())
    j = 0
    segs = []
    while j < len(b):
        best = (0, -1)
        for i in range(P):
            L = 0
            while j + L < len(b) and L < P and TT[i + L] == b[j + L]:
                L += 1
            if L > best[0]:
                best = (L, i)
        L, i = best
        if L < 3:
            segs.append((j, -1, 1)); j += 1
        else:
            segs.append((j, i, L)); j += L
    cov = sum(L for j, i, L in segs if i >= 0)
    print('덮임 %d / %d, 조각 %d' % (cov, len(b), len(segs)))
    for s in segs[:80]:
        print(s)


if __name__ == '__main__':
    main()
