# -*- coding: utf-8 -*-
"""스테이트에서 찾은 평문(arcade·subtitle_demo 영어)과 암호문(.msu)을 맞대어 키 흐름을 본다.
python tools/ks_probe.py
"""
import os, glob, struct, zlib, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, 'work', 'states_20261114')
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')
OUT = os.path.join(ROOT, 'work', 'plain')

# (스테이트, 위치, 평문 크기(끝 NUL 까지), 파일)
SRC = [('1_0', 0x65D9, 16540, 'subtitle_demo.msu'), ('1_0', 0xA3AA9, 2726, 'arcade.msu')]


def main():
    os.makedirs(OUT, exist_ok=True)
    for st, pos, size, name in SRC:
        raw = [p for p in glob.glob(os.path.join(SDIR, '*.raw')) if st in os.path.basename(p)][0]
        with open(raw, 'rb') as f:
            f.seek(pos - 64); pre = f.read(64); pt = f.read(size + 64)
        ct = open(os.path.join(TEXT, name), 'rb').read()
        open(os.path.join(OUT, name + '.mem'), 'wb').write(pt[:size])
        print('==', name, '암호문', len(ct), '평문', size, '차', len(ct) - size)
        print(' 평문 앞 64B 전:', pre[-32:].hex())
        print(' 평문 뒤:', pt[size:size + 32].hex())
        print(' 암호문 머리:', ct[:32].hex())
        print(' 암호문 꼬리:', ct[-32:].hex())
        for sh in range(0, 17):
            ks = bytes(a ^ b for a, b in zip(ct[sh:], pt[:size]))
            # 키 흐름 주기·분포
            c = collections.Counter(ks)
            per = None
            for p in (1, 2, 4, 8, 16, 32, 64, 128, 256):
                if ks[:-p] == ks[p:]:
                    per = p; break
            print('  밀기 %2d  서로 다른 값 %3d  최빈 %s  주기 %s  앞 %s' % (sh, len(c), c.most_common(2), per, ks[:24].hex()))


if __name__ == '__main__':
    main()
