# -*- coding: utf-8 -*-
"""게임 폴더 전체에서 «sc4-text» 암호 글 덩어리를 찾는다(묶음 파일 안 포함).
꼬리 = 씨앗 2 B + 암호 서명 8 B + 00 + FFFFFFFF 로 찾고, 시작은 평문 합 검산이 맞는 자리.

python tools/scan_sc4text.py <폴더> [<폴더> ...]   -> work/scan_sc4text.tsv
"""
import os, sys, mmap, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mscrypt import stream, xor, rotr, seed_of, SIG, ROOT

PAT = b'\x00\xff\xff\xff\xff'


def find_start(m, n_end, seed, lo):
    """본문 끝 n_end(씨앗 2 B 앞). 시작 후보를 뒤에서 앞으로 — 머리(언어·항목 수·첫 오프셋 0)와 합이 맞는 곳."""
    maxlen = min(n_end - lo, 0x40000)
    # 키 흐름은 시작에서 0 번째이므로 시작마다 다시 맞춰야 한다 -> 머리 12 B 만 먼저 본다
    ks12 = stream(seed, 12)
    for start in range(n_end - 16, n_end - maxlen - 1, -1):
        h = xor(m[start:start + 12], ks12)
        lang, cnt, o0 = struct.unpack('>III', h)
        if lang <= 16 and 0 < cnt < 20000 and o0 == 0 and 8 + 4 * cnt <= n_end - start:
            pt = xor(m[start:n_end], stream(seed, n_end - start))
            if seed_of(pt) == seed:
                return start, pt
    return None, None


def main():
    rows = []
    for top in sys.argv[1:]:
        for dp, dn, fn in os.walk(top):
            for f in fn:
                p = os.path.join(dp, f)
                size = os.path.getsize(p)
                if size < 32:
                    continue
                with open(p, 'rb') as fh:
                    m = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                    pos = 0
                    prev_end = 0
                    while True:
                        q = m.find(PAT, pos)
                        if q < 0:
                            break
                        pos = q + 1
                        n = q - 10
                        if n < 12:
                            continue
                        v = m[n] | (m[n + 1] << 8)
                        if xor(m[n + 2:n + 10], stream(v, 8, 5)) != SIG:
                            continue
                        seed = rotr(v, 3) ^ 0xEB7D
                        start, pt = find_start(m, n, seed, prev_end)
                        if start is None:
                            rows.append((p, -1, q + 5, -1, -1, ''))
                            continue
                        lang, cnt = struct.unpack('>II', pt[:8])
                        base = 8 + 4 * cnt
                        offs = struct.unpack('>%dI' % cnt, pt[8:base])
                        first = b''
                        for o in offs:
                            e = pt.index(b'\0', base + o)
                            if e > base + o:
                                first = pt[base + o:e]; break
                        rows.append((p, start, q + 5, lang, cnt, first[:40].decode('utf-8', 'replace').replace('\n', '/')))
                        prev_end = q + 5
                    m.close()
    out = os.path.join(ROOT, 'work', 'scan_sc4text.tsv')
    with open(out, 'w', encoding='utf-8') as o:
        o.write('파일\t시작\t끝\t언어\t항목\t첫 문자열\n')
        for r in rows:
            o.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (r[0], '%X' % r[1] if r[1] >= 0 else '?', '%X' % r[2], r[3], r[4], r[5]))
    print('찾음', len(rows), '->', out)
    import collections
    c = collections.Counter(os.path.relpath(r[0], sys.argv[1]) if r[0].startswith(sys.argv[1]) else r[0] for r in rows)
    for k, v in sorted(c.items()):
        if v > 1 or 'text' not in k:
            print('  %4d  %s' % (v, k))


if __name__ == '__main__':
    main()
