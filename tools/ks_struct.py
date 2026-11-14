# -*- coding: utf-8 -*-
"""demo 키 한 주기(1875 B)의 내부 구조: 약수 간격 XOR/차, 다음 바이트 분포.
python tools/ks_struct.py
"""
import os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def load(name):
    ct = open(os.path.join(TEXT, name), 'rb').read()
    pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
    return bytes(a ^ b for a, b in zip(ct, pt))


def minper(seq):
    n = len(seq)
    for p in range(1, n + 1):
        if n % p == 0 and all(seq[i] == seq[i % p] for i in range(n)):
            return p


def main():
    P = 1875
    T = load('subtitle_demo.msu')[:P]
    for d in (1, 3, 5, 15, 25, 75, 125, 375, 625):
        x = [T[i] ^ T[(i + d) % P] for i in range(P)]
        s = [(T[(i + d) % P] - T[i]) & 255 for i in range(P)]
        print('간격 %4d  XOR 값 %3d 종 주기 %4d | 차 값 %3d 종 주기 %4d' % (d, len(set(x)), minper(x), len(set(s)), minper(s)))
    # 다음 바이트 분포
    nx = collections.defaultdict(collections.Counter)
    for i in range(P):
        nx[T[i]][T[(i + 1) % P]] += 1
    for v in (0x44, 0x2b, 0xea, 0xca, 0xa0, 0x01, 0x57, 0x58):
        print('  %02x ->' % v, [('%02x' % k, c) for k, c in nx[v].most_common(8)])
    # 비트별 주기
    for bit in range(8):
        seq = [(t >> bit) & 1 for t in T]
        print('  비트 %d 주기 %d  1의 수 %d' % (bit, minper(seq), sum(seq)))
    print(T[:128].hex())
    print(' '.join('%3d' % t for t in T[:96]))


if __name__ == '__main__':
    main()
