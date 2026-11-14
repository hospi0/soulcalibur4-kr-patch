# -*- coding: utf-8 -*-
"""키 흐름의 되풀이(자기 상관)와 두 파일 사이 공통 조각을 잰다.
python tools/ks_period.py
"""
import os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def load(name):
    ct = open(os.path.join(TEXT, name), 'rb').read()
    pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
    return ct, pt, bytes(a ^ b for a, b in zip(ct, pt))


def main():
    ks = {}
    for name in ('subtitle_demo.msu', 'arcade.msu'):
        ct, pt, k = load(name)
        ks[name] = k
        n = len(k)
        best = []
        for p in range(1, min(n - 64, 9000)):
            m = sum(1 for i in range(0, n - p) if k[i] == k[i + p])
            best.append((m / (n - p), p))
        best.sort(reverse=True)
        print('==', name, '자기 상관 상위:', [(round(a, 3), p) for a, p in best[:12]])
        # 낱말 안 바이트 자리별 값 종류
        for j in range(4):
            c = collections.Counter(k[j::4])
            print('  바이트 자리 %d: 값 %d 종, 상위 %s' % (j, len(c), c.most_common(6)))
    a, b = ks['subtitle_demo.msu'], ks['arcade.msu']
    # 공통 8바이트 조각
    idx = collections.defaultdict(list)
    for i in range(len(a) - 8):
        idx[a[i:i + 8]].append(i)
    hits = [(j, idx[b[j:j + 8]][0]) for j in range(len(b) - 8) if b[j:j + 8] in idx]
    print('공통 8B 조각', len(hits), hits[:20])
    d = collections.Counter(i - j for j, i in hits)
    print('위치 차 분포', d.most_common(8))


if __name__ == '__main__':
    main()
