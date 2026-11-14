# -*- coding: utf-8 -*-
"""키 생성식 맞히기: s' = (5*(s>>1)+1) mod 2^N, 키 바이트 = s & 0xFF 가설.
윗비트를 키 흐름에서 하나씩 정해 가며 N 을 찾는다.
python tools/ks_fit.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def load(name):
    ct = open(os.path.join(TEXT, name), 'rb').read()
    pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
    return bytes(a ^ b for a, b in zip(ct, pt))


def gen(s, n, N):
    m = (1 << N) - 1
    out = bytearray()
    for _ in range(n):
        out.append(s & 0xFF)
        s = (5 * (s >> 1) + 1) & m
    return bytes(out)


def fit(k, N):
    s = k[0]
    for bit in range(8, N):
        # 이 비트는 (bit-7) 걸음 뒤 키 바이트의 비트 7 에 처음 나타난다
        need = bit - 7
        a = gen(s, need + 1, N)
        if a[:need + 1] != k[:need + 1]:
            s |= 1 << bit
            a = gen(s, need + 1, N)
            if a[:need + 1] != k[:need + 1]:
                return None, bit
    return s, None


def main():
    for name in ('subtitle_demo.msu', 'arcade.msu'):
        k = load(name)
        print('==', name)
        for N in range(9, 65):
            s, fail = fit(k, N)
            if s is None:
                continue
            g = gen(s, len(k), N)
            ok = next((i for i in range(len(k)) if g[i] != k[i]), len(k))
            if ok > N + 8:
                print('  N=%2d 씨앗 %x  맞는 길이 %d / %d' % (N, s, ok, len(k)))


if __name__ == '__main__':
    main()
