# -*- coding: utf-8 -*-
"""키 바이트 -> 다음 키 바이트 함수표(아래 7비트)를 두 파일에서 뽑아 찍는다.
python tools/ks_ftab.py
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
        nx = collections.defaultdict(collections.Counter)
        for i in range(len(k) - 1):
            nx[k[i]][k[i + 1]] += 1
        bad = 0
        F = {}
        for v in range(256):
            c = nx.get(v)
            if not c: continue
            low = collections.Counter()
            for s, n in c.items():
                low[s & 0x7F] += n
            F[v] = low.most_common(1)[0][0]
            if len(low) > 1:
                bad += 1
        print('==', name, '값 %d 종, 아래 7비트가 둘 이상인 값 %d' % (len(F), bad))
        for r in range(0, 256, 16):
            print('  %02x: ' % r + ' '.join('%02x' % F[x] if x in F else '--' for x in range(r, r + 16)))
        # 예외 표본
        ex = [(v, dict(nx[v])) for v in list(nx)[:400] if len({s & 0x7F for s in nx[v]}) > 1][:6]
        for v, d in ex:
            print('   예외 %02x ->' % v, {('%02x' % s): n for s, n in d.items()})


if __name__ == '__main__':
    main()
