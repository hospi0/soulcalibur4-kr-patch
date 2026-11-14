# -*- coding: utf-8 -*-
"""스테이트 메모리의 «칸 번호 -> 유니코드» 표(u16 BE, JIS 차례)를 뽑아 work/cellmap.tsv 로.
칸 = 32x32, 한 줄 64칸, 2048x2048 두 장(gt_KanjiTexturePs3.nut).

python tools/cellmap.py
"""
import os, glob, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, 'work', 'states_20261114')
ANCHOR = 0x4762539          # 逸稲茨芋 가 있는 자리(1_0 스테이트)


def main():
    raw = [p for p in glob.glob(os.path.join(SDIR, '*.raw')) if '1_0' in os.path.basename(p)][0]
    with open(raw, 'rb') as f:
        f.seek(ANCHOR - 0x4000)
        b = f.read(0x8000 + 0x4000)
    a = b.rfind(struct.pack('>H', 0x4E9C), 0, 0x4000 + 2)      # 亜
    start = a - 960 * 2
    base = ANCHOR - 0x4000 + start
    tab = struct.unpack('>8000H', b[start:start + 16000])
    print('표 시작 %X, 앞 8칸 %s' % (base, ' '.join('%04X' % x for x in tab[:8])))
    print('표 앞 32B 전:', b[start - 32:start].hex())
    print('표 뒤:', b[start + 16000:start + 16032].hex())
    n_used = sum(1 for x in tab if x)
    kan = [i for i, x in enumerate(tab) if 0x4E00 <= x <= 0x9FFF]
    print('채워진 칸 %d / 8000, 한자 칸 %d (첫 %d, 끝 %d), 마지막 0 아닌 칸 %d' % (
        n_used, len(kan), kan[0], kan[-1], max(i for i, x in enumerate(tab) if x)))
    out = os.path.join(ROOT, 'work', 'cellmap.tsv')
    with open(out, 'w', encoding='utf-8') as o:
        o.write('칸\t장\t열\t행\t유니코드\t글자\n')
        for i, x in enumerate(tab):
            page, r = divmod(i, 4096)
            o.write('%d\t%d\t%d\t%d\t%04X\t%s\n' % (i, page, r % 64, r // 64, x, chr(x) if x >= 0x20 else ''))
    open(os.path.join(ROOT, 'work', 'cellmap.bin'), 'wb').write(b[start:start + 16000])
    print('->', out)


if __name__ == '__main__':
    main()
