"""인물 이름 칸(캐릭터 선택·스토리 안내·숙련도·탑·크리에이션·일러스트·파츠·프로필) 별 한글 표기 표"""
from common import *
import re, collections
R = rows()
P = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/')
def strip(s): return P.sub('', s).replace(NL, '\n')
PATS = [  # (칸 이름, 위치 정규식, JP 이름 뽑기, KO 이름 뽑기)
 ('선택', r'regtext/1#', r'^(.+)$', r'^(.+)$'),
 ('스토리안내', r'regtext/5#', r'\n(.+?)の\n【STORY】', r'\n(.+?)의\n【STORY】'),
 ('숙련도', r'regtext/7#', r'スタイル：(.+?)の熟練度', r'스타일: ?(.+?)의 숙련도'),
 ('탑', r'text/caliaga#1[4-8]\d$', r'^(.+)$', r'^(.+)$'),
 ('크리에이션', r'text/creation#1[2-5]\d$', r'スタイル： ?(.+?)  |【(.+?)】を', r'스타일: ?(.+?)  |【(.+?)】를'),
 ('일러스트', r'text/museum#', r'「(.+?)」の', r'「(.+?)」의'),
 ('파츠', r'text/parts#4\d\d$|text/parts#5\d\d$', r'^(.+?)(?:1P|2P|　カスタム)$', r'^(.+?)(?:1P|2P|　커스텀)$'),
 ('프로필', r'text/museum#\d+$', r'^(.+?)\n\n年齢', r'^(.+?)\n\n나이'),
]
table = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for r in R:
    j = strip(r['jp']).strip(); k = strip(r['ko']).strip()
    for slot, lp, jp_, kp in PATS:
        if not re.match(lp, r['loc']): continue
        mj = re.search(jp_, j, re.S); mk = re.search(kp, k, re.S)
        if not mj: continue
        jn = next(g for g in mj.groups() if g) if mj.groups() else mj.group(0)
        if '\n' in jn or len(jn) > 20: continue
        kn = (next(g for g in mk.groups() if g) if mk else '??' + k[:20])
        if slot == '프로필':
            jn = re.sub(r'（.*', '', jn); jn = jn.replace('　', '')
        jn = re.sub(r'[12]$', '', jn); kn = re.sub(r'[12]$', '', kn)
        table[jn][slot][kn] += 1
        break
# 프로필 이름(한자)과 가나 이름을 같은 줄로: 수동 합침
ALIAS = {'御剣平四郎': 'ミツルギ', '成美那': 'ミナ', '多喜': 'タキ', '真喜志': 'マキシ', '柴香華': 'シャンファ', '吉光': 'ヨシミツ',
         '洪潤星': 'ユンスン', '雪華': 'セツカ', '神斬蝕': 'カミキリムシ', '修羅': 'シュラ', 'ロック': 'ロック'}
with open('r6_names.tsv', 'w', encoding='utf-8') as f:
    for jn in sorted(table):
        row = table[jn]
        allk = collections.Counter()
        for s in row.values(): allk.update(s)
        mark = '◆' if len(allk) > 1 else ' '
        line = '%s %s\t%s' % (mark, jn, '  '.join('%s:%s' % (slot, '/'.join('%s×%d' % kv for kv in c.items())) for slot, c in row.items()))
        print(line); f.write(line + '\n')
