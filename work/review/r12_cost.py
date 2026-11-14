from common import *
import re
from r10_reflow import reflow, wrap, w
def paras(jp, ko):
    J = jp.split(NL); W = max(w(x) for x in J)
    K = ko.split(NL); out=[]; par=None
    for line in K:
        if line.strip(' 　')=='' or '：' in line or ':' in line[:8] or line.startswith('　　'):
            if par is not None: out.append(par); par=None
            continue
        if par is None or line.startswith('　') or re.match(r'^(\$[A-Za-z][0-9.]*(/[0-9.]+)*/)+　', line):
            if par is not None: out.append(par)
            par=line
        else: par = par + ('' if par.endswith(' ') else ' ') + line.lstrip(' ')
    if par is not None: out.append(par)
    return W, out
for r in rows():
    nj = r['jp'].count(NL)
    if not re.match(r'text/(museum|story)#', r['loc']) or r['ko'].count(NL) == nj: continue
    W, out = reflow(r['jp'], r['ko']); over = len(out)-nj-1
    if over <= 0: continue
    W, ps = paras(r['jp'], r['ko'])
    cs = sorted(((w(wrap(p,W)[-1]), i, p) for i,p in enumerate(ps) if len(wrap(p,W))>1))
    print('=====', r['no'], r['loc'], 'W', W, '+%d' % over)
    for c,i,p in cs[:over+2]:
        print('  비용 %4.1f | %s' % (c, p))
