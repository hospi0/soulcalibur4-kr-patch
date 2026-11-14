from common import *
import json, re, sys
R = {r['no']: r for r in rows()}
res = json.load(open('r4_vars.json', encoding='utf-8'))
TOKRE = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/')
def ctx(s, pat, w=22):
    s = TOKRE.sub('', s)
    m = re.search(pat, s)
    if not m: return s[:w*2]
    return s[max(0, m.start()-w):m.end()+w]
names = sys.argv[1:]
for n in names:
    tot, cnt, none = res[n]
    print('=====', n)
    for v, nos in cnt.items():
        if not nos: continue
        print(' [%s] %d' % (v, len(nos)))
        for no in nos[:8]:
            r = R[no]; print('   ', no, r['loc'], '|', ctx(r['jp'], '.', 0)[:0] + ctx(r['ko'], v))
    for no in none[:8]:
        r = R[no]; print('  [없음]', no, r['loc'], '|', TOKRE.sub('', r['jp'])[:50], '|', TOKRE.sub('', r['ko'])[:50])
