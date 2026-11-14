import sys, glob, os, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import build
rows = []
for p in sorted(glob.glob('work/text/fixed/*.tsv')):
    with open(p, encoding='utf-8-sig') as f:
        hdr = f.readline().rstrip('\r\n').split('\t')
        if hdr[:5] != ['번호','위치','겹침','JP','KO']: print('머리 다름', p, hdr)
        for ln in f:
            c = ln.rstrip('\r\n').split('\t')
            rows.append((os.path.basename(p), c))
print('행', len(rows))
# compare with original export
orig = {}
for p in sorted(glob.glob('my files/tsv/*.tsv')):
    with open(p, encoding='utf-8') as f:
        next(f)
        for ln in f:
            c = ln.rstrip('\r\n').split('\t'); orig[c[0]] = c[3]
seen = set(); errs = collections.Counter(); bad = []
for fn, c in rows:
    if len(c) != 5: bad.append((fn, c[0], '열 %d' % len(c))); continue
    if c[0] in seen: bad.append((fn, c[0], '번호 중복'))
    seen.add(c[0])
    if orig.get(c[0]) != c[3]: bad.append((fn, c[0], 'JP 원문 바뀜'))
    if not c[4].strip(): bad.append((fn, c[0], '빈 번역')); continue
    ko, e = build.check(c[3], c[4])
    for x in e: bad.append((fn, c[0], x)); errs[x.split(' ')[0]] += 1
print('누락 번호', len(set(orig) - seen))
print(collections.Counter(b[2].split(' ')[0] for b in bad))
with open('work/review/r1_mech_fixed.tsv', 'w', encoding='utf-8') as f:
    for b in bad: f.write('\t'.join(b) + '\n')
