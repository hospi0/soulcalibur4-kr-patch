# -*- coding: utf-8 -*-
"""알려진 키 흐름에서 실제 씨앗을 역산하고, 씨앗 = 0xA21F + 15*합(암호문[a:b]) 의 범위를 찾는다.
python tools/seed_probe.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mscrypt import stream, TEXT, ROOT

OUT = os.path.join(ROOT, 'work', 'plain')


def main():
    for name in ('subtitle_demo.msu', 'arcade.msu'):
        ct = open(os.path.join(TEXT, name), 'rb').read()
        pt = open(os.path.join(OUT, name + '.mem'), 'rb').read()
        ks = bytes(a ^ b for a, b in zip(ct, pt))
        seeds = [s for s in range(0x10000) if stream(s, 16) == ks[:16]]
        print('==', name, '씨앗', [hex(s) for s in seeds])
        if not seeds:
            continue
        s = seeds[0]
        full = stream(s, len(pt))
        print('  전체 일치:', full == ks[:len(pt)])
        acc = 0
        hits = []
        for m in range(len(ct) + 1):
            if (0xA21F + 15 * acc) & 0xFFFF == s:
                hits.append(m)
            if m < len(ct):
                acc += ct[m]
        print('  합 범위 [0:m) 가 맞는 m:', hits, '(파일 크기 %d)' % len(ct))
        # 다른 상수·곱 변형
        tot = sum(ct[:len(ct) - 4])
        print('  합(본문)=%d  15*합&FFFF=%04X  씨앗-그것=%04X' % (tot, (15 * tot) & 0xFFFF, (s - 15 * tot) & 0xFFFF))


if __name__ == '__main__':
    main()
