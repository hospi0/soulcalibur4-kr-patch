# -*- coding: utf-8 -*-
"""스테이트 raw 의 한 위치 둘레를 보기 좋게 찍는다.
python tools/state_ctx.py <raw 이름 일부> <hex 위치> [앞] [뒤]
"""
import sys, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, 'work', 'states_20261114')


def main():
    raw = [p for p in glob.glob(os.path.join(SDIR, '*.raw')) if sys.argv[1] in os.path.basename(p)][0]
    pos = int(sys.argv[2], 16)
    pre = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x200
    post = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x200
    with open(raw, 'rb') as f:
        f.seek(max(0, pos - pre))
        b = f.read(pre + post)
    base = max(0, pos - pre)
    for i in range(0, len(b), 32):
        row = b[i:i + 32]
        txt = ''.join(chr(c) if 32 <= c < 127 else '.' for c in row)
        print('%08X  %s  %s' % (base + i, row.hex(), txt))


if __name__ == '__main__':
    main()
