# -*- coding: utf-8 -*-
"""RPCS3 세이브스테이트(.SAVESTAT.zst) 를 풀고, 메모리에서 풀린 글(.ms?) 평문을 찾는다.

python tools/state_find.py unpack            -> work/states_20261114/*.raw
python tools/state_find.py find              -> 화면 글귀·머리(00000007+항목 수) 위치
"""
import sys, os, struct, re, glob
import zstandard

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, 'work', 'states_20261114')
TEXT = os.path.join(ROOT, 'work', 'orig', 'text')


def unpack():
    for src in glob.glob(os.path.join(SDIR, '*.zst')):
        dst = src[:-4] + '.raw'
        if os.path.exists(dst):
            print('있음', dst, os.path.getsize(dst)); continue
        d = zstandard.ZstdDecompressor()
        n = 0
        with open(src, 'rb') as f, open(dst, 'wb') as o:
            # 여러 프레임이 이어 붙어 있을 수 있다
            r = d.stream_reader(f, read_across_frames=True)
            while True:
                b = r.read(1 << 24)
                if not b: break
                o.write(b); n += len(b)
        print('풀림', os.path.basename(dst), n)


def counts():
    """.msk(평문) 머리에서 화면별 항목 수"""
    out = {}
    for p in glob.glob(os.path.join(TEXT, '*.msk')):
        b = open(p, 'rb').read()
        ver, n = struct.unpack('>II', b[:8])
        out[os.path.basename(p)[:-4]] = (ver, n)
    return out


def find():
    cn = counts()
    print('항목 수(.msk):', cn)
    needles = [b'Fight through 8 stages', b'Ready?', b'Move Cursor', b'SINGLE PLAYER',
               'Fight through 8 stages'.encode('utf-16-be'), 'Ready?'.encode('utf-16-be'),
               'Fight through 8 stages'.encode('utf-16-le')]
    for raw in sorted(glob.glob(os.path.join(SDIR, '*.raw'))):
        b = open(raw, 'rb').read()
        print('==', os.path.basename(raw), len(b))
        for nd in needles:
            ps = [m.start() for m in re.finditer(re.escape(nd), b)]
            print('  ', nd[:30], len(ps), [hex(x) for x in ps[:8]])
        # 머리: 00000007 + 항목 수(.msk 와 같은 수)
        for name, (ver, n) in sorted(cn.items()):
            hd = struct.pack('>II', 7, n)
            ps = [m.start() for m in re.finditer(re.escape(hd), b)]
            good = []
            for p in ps:
                # 오프셋표 첫 값이 표 크기(8+4n) 근처인지
                o0 = struct.unpack('>I', b[p + 8:p + 12])[0]
                good.append((hex(p), hex(o0)))
            print('  머리', name, n, len(ps), good[:10])


if __name__ == '__main__':
    {'unpack': unpack, 'find': find}[sys.argv[1]]()
