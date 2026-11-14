import glob, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(92) + 'n'
def rows():
    out = []
    for p in sorted(glob.glob(os.environ.get('SC4_SRC', r'C:/claude/project/soulcalibur4-kr-patch/my files/번역') + '/*.tsv')):
        with open(p, encoding='utf-8') as f:
            next(f)
            for l in f:
                c = l.rstrip('\r\n').split('\t')
                out.append(dict(no=c[0], loc=c[1], jp=c[3], ko=c[4], file=os.path.basename(p)))
    return out
