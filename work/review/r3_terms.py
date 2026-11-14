from common import *
import collections, re
R = rows()
TOKRE = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/|<[^>]*>|%[-+0-9.]*[a-zA-Z]|\n')
def clean(s): return TOKRE.sub(' ', s)
KATA = re.compile('[ァ-ヺー・＝]{3,}')
jp_terms = collections.Counter()
for r in R:
    for m in set(KATA.findall(clean(r['jp']))):
        for t in m.split('・'):
            if len(t) >= 3: jp_terms[t] += 1
# Hangul substrings index
HW = re.compile('[가-힣]+')
def subs(s):
    out = set()
    for w in HW.findall(s):
        for i in range(len(w)):
            for j in range(i+2, min(len(w), i+8)+1): out.add(w[i:j])
    return out
ko_sub = [subs(clean(r['ko'])) for r in R]
glob_cnt = collections.Counter()
for s in ko_sub: glob_cnt.update(s)
out = []
for t, n in jp_terms.most_common():
    if n < 3: break
    idx = [i for i, r in enumerate(R) if t in r['jp']]
    c = collections.Counter()
    for i in idx: c.update(ko_sub[i])
    best = None
    for s, k in c.items():
        if k < 2: continue
        sc = (k/len(idx)) * (k/glob_cnt[s]) * (len(s) ** 0.3)
        if not best or sc > best[0]: best = (sc, s, k)
    if not best: continue
    _, s, k = best
    miss = [i for i in idx if s not in ko_sub[i]]
    out.append((t, n, s, k, miss))
with open('r3_terms.tsv', 'w', encoding='utf-8') as f:
    for t, n, s, k, miss in out:
        f.write('%s\t%d\t%s\t%d\t%s\n' % (t, n, s, k, ' '.join(R[i]['no'] for i in miss[:30])))
print(len(out), 'terms;', sum(1 for o in out if o[4]), 'with misses')
for t, n, s, k, miss in out:
    if miss and len(miss) / n > 0.05:
        print('%s(%d) → %s %d/%d  예: %s' % (t, n, s, k, n, ' / '.join(clean(R[i]['ko'])[:40] for i in miss[:2])))
