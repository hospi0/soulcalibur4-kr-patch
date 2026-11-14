# -*- coding: utf-8 -*-
"""키 바이트 맨 윗비트가 어디서 오는지: e[i] = bit7(k[i+1]) ^ bit7(5*(k[i]>>1)+1) 의 무늬.
python tools/ks_top.py
"""
import os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def load(name):
    ct = open(os.path.join(TEXT, name), 'rb').read()
    pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
    return bytes(a ^ b for a, b in zip(ct, pt))


def main():
    for name in ('subtitle_demo.msu', 'arcade.msu'):
        k = load(name)
        n = len(k)
        e = [((k[i + 1] >> 7) ^ (((5 * (k[i] >> 1) + 1) >> 7) & 1)) for i in range(n - 1)]
        full = [(k[i + 1] - (5 * (k[i] >> 1) + 1)) & 0xFF for i in range(n - 1)]
        print('==', name, 'e 1의 비율 %.3f' % (sum(e) / len(e)), '차 종류', collections.Counter(full).most_common(4))
        print('  e 앞 96:', ''.join(map(str, e[:96])))
        print('  k bit0 :', ''.join(str(x & 1) for x in k[:96]))
        # e[i] 가 k[i-1], k[i-2] ... 의 어느 비트와 같은가
        for back in range(0, 6):
            for bit in range(8):
                m = sum(1 for i in range(back, n - 1) if e[i] == ((k[i - back] >> bit) & 1))
                r = m / (n - 1 - back)
                if r > 0.9 or r < 0.1:
                    print('   e[i] ~ k[i-%d] 비트 %d : %.3f' % (back, bit, r))
        # 캐리 포함: 실제 다음 바이트 전체 = 5*(k>>1)+1 + 128*x 인데 x 를 앞 두 바이트로 설명?
        d = collections.defaultdict(collections.Counter)
        for i in range(1, n - 1):
            d[(k[i - 1] & 1, k[i] & 1)][e[i]] += 1
        print('  (k[i-1]&1,k[i]&1)->e', {a: dict(b) for a, b in d.items()})


if __name__ == '__main__':
    main()
