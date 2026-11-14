"""줄 넘치는 글: 문단마다 접은 줄 수와 «마지막 줄 길이» — 마지막 줄이 짧은 문단은 몇 글자만 줄이면 한 줄이 빠진다"""
from common import *
import sys, re
from r10_reflow import reflow, wrap, w
want = set(sys.argv[1:])
for r in rows():
    if want and r['no'] not in want: continue
    nj = r['jp'].count(NL)
    if not re.match(r'text/(museum|story)#', r['loc']) or r['ko'].count(NL) == nj: continue
    W, out = reflow(r['jp'], r['ko'])
    over = len(out) - nj - 1
    if over <= 0: continue
    print('=====', r['no'], r['loc'], '폭', W, '넘침 +%d' % over)
    for i, l in enumerate(out):
        print('  %2d [%4.1f] %s' % (i, w(l), l))
