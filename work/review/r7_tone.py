"""말투: 대사(subtitle_aplwin 30줄 묶음 = 인물 하나, subtitle_demo) 문장 끝 어미 분류"""
from common import *
import re, collections
P = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/')
def ends(ko):
    s = P.sub('', ko).replace(NL, ' ')
    out = []
    for seg in re.split(r'[!?！？…。.~～]+', s):
        seg = seg.strip(' 　')
        m = re.search(r'([가-힣]+)$', seg)
        if m: out.append(m.group(1))
    return out
def cls(w):
    if re.search(r'(습니다|습니까|ㅂ니다|십시오|세요|에요|예요|해요|어요|아요|지요|죠|군요|네요|나요|가요|래요|게요|까요|요)$', w): return '존대(요/니다)'
    if re.search(r'(하오|이오|구려|시오|소|오|게나|네|세|구먼|는가|겠나|게)$', w) and len(w) > 1: return '하오/하게'
    if re.search(r'(느냐|으냐|냐|노라|도다|로다|거라|어라|아라|여라|라|다|마|랴|련다|느니|니라|겠지)$', w): return '해라'
    if re.search(r'(어|아|야|지|래|게|걸|네|군|구나|잖아|거든|까|나|해|돼|봐|줘|와|워|자)$', w): return '해(반말)'
    return '기타'
R = rows()
rows_by = collections.defaultdict(list)
for r in R:
    if r['loc'].startswith('text/subtitle_aplwin#'):
        i = int(r['loc'].split('#')[1]); rows_by[(i - 1) // 30].append(r)
with open('r7_tone.txt', 'w', encoding='utf-8') as f:
    for b in sorted(rows_by):
        c = collections.Counter(); per = []
        for r in rows_by[b]:
            e = ends(r['ko']); k = [cls(w) for w in e]; c.update(k); per.append((r, e, k))
        top = c.most_common()
        f.write('== 묶음 %d (aplwin #%d~#%d) %s\n' % (b, b * 30 + 1, b * 30 + 30, '  '.join('%s %d' % t for t in top)))
        for r, e, k in per:
            f.write('  %s %s | %s | %s\n' % (r['no'], r['loc'].split('#')[1], P.sub('', r['jp']).replace(NL, ' / '), P.sub('', r['ko']).replace(NL, ' / ')))
        print('묶음 %2d  %s' % (b, '  '.join('%s %d' % t for t in top)))
