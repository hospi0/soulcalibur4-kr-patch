# -*- coding: utf-8 -*-
"""키 흐름이 무엇에 물리는지(앞 암호문·앞 평문·위치) 일관성으로 판정.
python tools/ks_dep.py
"""
import os, struct, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')


def consist(pairs):
    """(문맥, 값) 쌍 — 같은 문맥이 같은 값을 주는 비율"""
    d = collections.defaultdict(collections.Counter)
    for k, v in pairs:
        d[k][v] += 1
    rep = sum(sum(c.values()) for c in d.values() if sum(c.values()) > 1)
    ok = sum(max(c.values()) for c in d.values() if sum(c.values()) > 1)
    return len(d), rep, ok


def main():
    data = {}
    for name in ('subtitle_demo.msu', 'arcade.msu'):
        ct = open(os.path.join(TEXT, name), 'rb').read()
        pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
        n = len(pt)
        ks = bytes(a ^ b for a, b in zip(ct, pt))
        data[name] = (ct, pt, ks)
        print('==', name, n)
        tests = {
            'ks[i] | c[i-1]': [(ct[i - 1], ks[i]) for i in range(1, n)],
            'ks[i] | p[i-1]': [(pt[i - 1], ks[i]) for i in range(1, n)],
            'ks[i] | c[i-1],c[i-2]': [((ct[i - 1], ct[i - 2]), ks[i]) for i in range(2, n)],
            'ks[i] | p[i-1],p[i-2]': [((pt[i - 1], pt[i - 2]), ks[i]) for i in range(2, n)],
            'ks[i] | c[i-4]': [(ct[i - 4], ks[i]) for i in range(4, n)],
            'ks[i] | c[i-8]': [(ct[i - 8], ks[i]) for i in range(8, n)],
            'ks[i] | c[i-16]': [(ct[i - 16], ks[i]) for i in range(16, n)],
            'ks[i] | ks[i-1]': [(ks[i - 1], ks[i]) for i in range(1, n)],
            'c[i] | p[i]': [(pt[i], ct[i]) for i in range(n)],
            'c[i]-c[i-1] | p[i]': [(pt[i], (ct[i] - ct[i - 1]) & 255) for i in range(1, n)],
            'c[i]^c[i-1] | p[i]': [(pt[i], ct[i] ^ ct[i - 1]) for i in range(1, n)],
            'c[i]-p[i] | c[i-1]': [(ct[i - 1], (ct[i] - pt[i]) & 255) for i in range(1, n)],
            'c[i]-p[i] | p[i-1]': [(pt[i - 1], (ct[i] - pt[i]) & 255) for i in range(1, n)],
        }
        for k, v in tests.items():
            print('  %-24s 문맥 %5d 되풀이 %5d 일치 %5d' % ((k,) + consist(v)))
        # 32비트 낱말로
        w = n // 4
        cw = struct.unpack('>%dI' % w, ct[:w * 4]); pw = struct.unpack('>%dI' % w, pt[:w * 4])
        kw = [a ^ b for a, b in zip(cw, pw)]
        print('  낱말 키 앞:', ' '.join('%08x' % x for x in kw[:12]))
        print('  낱말 차(뺄셈):', ' '.join('%08x' % ((a - b) & 0xFFFFFFFF) for a, b in zip(cw[:12], pw[:12])))
    # 두 파일에서 같은 평문 8바이트 블록 → 같은 암호문?(ECB 판정)
    for bs in (8, 16):
        seen = collections.defaultdict(set)
        for name, (ct, pt, ks) in data.items():
            for i in range(0, len(pt) - bs, bs):
                seen[pt[i:i + bs]].add(ct[i:i + bs])
        multi = [(k, v) for k, v in seen.items() if len(v) > 1]
        print('블록 %d: 평문 블록 %d 종, 암호문 여럿인 것 %d' % (bs, len(seen), len(multi)))


if __name__ == '__main__':
    main()
