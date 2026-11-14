# -*- coding: utf-8 -*-
"""스테이트 raw 에서 «u32 종류 · u32 항목 수 · 오름차순 오프셋표 · 문자열» 꼴 글 표를 전부 찾는다.
python tools/state_tables.py <raw 이름 일부> [시작hex 끝hex]
"""
import sys, os, glob, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, 'work', 'states_20261114')


def scan(b, lo, hi):
    out = []
    p = lo
    while p < hi - 16:
        kind, n = struct.unpack_from('>II', b, p)
        if 0 < kind <= 16 and 1 <= n <= 5000 and struct.unpack_from('>I', b, p + 8)[0] == 0:
            offs = struct.unpack_from('>%dI' % n, b, p + 8)
            if all(offs[i] <= offs[i + 1] for i in range(n - 1)) and offs[-1] < 0x80000:
                base = p + 8 + 4 * n
                # 각 오프셋 바로 앞이 NUL 인지(첫 것 빼고)
                ok = sum(1 for o in offs[1:] if b[base + o - 1] == 0)
                if ok >= (n - 1) * 0.9:
                    end = base + offs[-1]
                    end = b.index(b'\0', end) + 1
                    out.append((p, kind, n, base, end))
                    p = end
                    continue
        p += 1
    return out


def main():
    raw = [p for p in glob.glob(os.path.join(SDIR, '*.raw')) if sys.argv[1] in os.path.basename(p)][0]
    b = open(raw, 'rb').read()
    lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else len(b)
    for p, kind, n, base, end in scan(b, lo, hi):
        offs = struct.unpack_from('>%dI' % n, b, p + 8)
        def s(i):
            o = base + offs[i]
            return b[o:b.index(b'\0', o)][:40]
        print('%08X 종류 %d 항목 %4d 크기 %6d  %r | %r | %r' % (p, kind, n, end - p, s(0), s(min(1, n - 1)), s(n - 1)))


if __name__ == '__main__':
    main()
