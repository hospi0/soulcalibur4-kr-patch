# -*- coding: utf-8 -*-
"""번역 대상 전수 추출 -> work/extract/all.tsv  (id · 일본어 · 영어 · 표시)

id = <묶음>/<표>#<항목>   예) text/arcade#12 · regtext/4#53 · tectext/waza_01#7
표시: keep = 일본어판도 ASCII 뿐(장식 글꼴 메뉴 이름·기호·버튼 코드) -> 원문 유지 / empty = 빈 항목
줄바꿈은 «\\n» 으로 적는다.

python tools/extract.py
"""
import os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstext

G = mstext.GAME
OUT = os.path.join(mstext.ROOT, 'work', 'extract')


def tables(ext):
    """-> [(id 머리, 문자열 목록)]"""
    out = []
    for sub, tag in (('cdata/text', 'text'), ('cpudata/tectext', 'tectext')):
        for p in sorted(glob.glob(os.path.join(G, sub, '*.ms' + ext))):
            lang, strs = mstext.read_table(open(p, 'rb').read())
            out.append(('%s/%s' % (tag, os.path.basename(p)[:-4]), strs))
    b = open(os.path.join(mstext.ROOT, 'work', 'orig', 'text', 'regtext_%s.dtp' % ext), 'rb').read()
    for i, c in enumerate(mstext.pack_split(b)):
        lang, strs = mstext.read_table(mstext.chunk_trim(c, False))
        out.append(('regtext/%d' % i, strs))
    return out


def esc(s):
    return s.decode('utf-8').replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t')


def main():
    os.makedirs(OUT, exist_ok=True)
    jp, en = tables('j'), tables('u')
    assert [t[0] for t in jp] == [t[0] for t in en]
    stat = collections.defaultdict(lambda: [0, 0, 0, 0])   # 항목, 번역 대상, 일본어 글자, 고유
    uniq = set()
    with open(os.path.join(OUT, 'all.tsv'), 'w', encoding='utf-8', newline='\n') as o:
        o.write('id\t일본어\t영어\t표시\n')
        for (name, js), (_, es) in zip(jp, en):
            assert len(js) == len(es), name
            grp = name.split('/')[0]
            for i, (j, e) in enumerate(zip(js, es)):
                flag = 'empty' if not j and not e else ('keep' if all(c < 0x80 for c in j) else '')
                o.write('%s#%d\t%s\t%s\t%s\n' % (name, i, esc(j), esc(e), flag))
                st = stat[grp]
                st[0] += 1
                if not flag:
                    st[1] += 1; st[2] += len(j.decode('utf-8'))
                    if j not in uniq:
                        uniq.add(j); st[3] += 1
    for g, st in stat.items():
        print('%-8s 항목 %5d  번역 대상 %5d (고유 %5d)  일본어 %6d 자' % (g, st[0], st[1], st[3], st[2]))
    print('->', os.path.join(OUT, 'all.tsv'))


if __name__ == '__main__':
    main()
