# -*- coding: utf-8 -*-
"""키 비트열들의 선형 복잡도(벌리캠프-매시, GF(2)).
python tools/ks_bm.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def load(name):
    ct = open(os.path.join(TEXT, name), 'rb').read()
    pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
    return bytes(a ^ b for a, b in zip(ct, pt))


def bm(s):
    n = len(s)
    c = [0] * n; b = [0] * n
    c[0] = b[0] = 1
    L, m = 0, -1
    for i in range(n):
        d = s[i]
        for j in range(1, L + 1):
            d ^= c[j] & s[i - j]
        if d:
            t = c[:]
            sh = i - m
            for j in range(0, n - sh):
                c[j + sh] ^= b[j]
            if L <= i // 2:
                L = i + 1 - L; m = i; b = t
    return L, c[:L + 1]


def main():
    for name in ('subtitle_demo.msu', 'arcade.msu'):
        k = load(name)[:2600]
        n = len(k)
        e = [((k[i + 1] >> 7) ^ (((5 * (k[i] >> 1) + 1) >> 7) & 1)) for i in range(n - 1)]
        print('==', name)
        L, c = bm(e)
        print('  e 선형 복잡도 %d / %d' % (L, len(e)))
        for bit in range(8):
            s = [(x >> bit) & 1 for x in k]
            L, c = bm(s)
            taps = [j for j in range(1, L + 1) if c[j]] if L < 200 else '...'
            print('  비트 %d 선형 복잡도 %d / %d  %s' % (bit, L, n, taps))
        # 전체 비트열(MSB 먼저 / LSB 먼저)
        for nm, order in (('MSB', range(7, -1, -1)), ('LSB', range(8))):
            s = [(x >> b) & 1 for x in k[:400] for b in order]
            L, c = bm(s)
            print('  바이트 풀어 %s 먼저: %d / %d' % (nm, L, len(s)))


if __name__ == '__main__':
    main()
