# -*- coding: utf-8 -*-
r"""버퍼 시험용 가짜 번역 → work/text/stress_ko.tsv (2026-11-14).
  번역 대상 모든 일본어 문장을 «토큰·줄바꿈은 그대로, 글자 부분은 한글 음절로(일본어 글자 수 × 1.2, 4음절마다 띄어쓰기)» 채움.
  음절은 KS X 1001 완성형 2,350자를 차례로 돌려 써서 글꼴 칸도 넉넉히 씀.
  python tools/make_stress.py → python tools/build.py --stress"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

SYL = [c for c in (chr(x) for x in range(0xAC00, 0xD7A4)) if len(c.encode('euc_kr', 'ignore')) == 2]   # 완성형 2,350(KS X 1001 — cp949 는 확장 11,172 자 전부라 안 됨)
RATIO = 1.2


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    rows = [l.rstrip('\n').split('\t') for l in open(B.R('work', 'extract', 'all.tsv'), encoding='utf-8')][1:]
    seen = []; s_ = set()
    for id_, jp, en, flag in rows:
        if not flag and jp not in s_: s_.add(jp); seen.append((id_, jp))
    k = 0; out = ['번호\t위치\t겹침\tJP\tKO']
    for n, (id_, jp) in enumerate(seen, 1):
        parts = []; pos = 0
        for m in B.TOK.finditer(jp):
            parts.append(('t', jp[pos:m.start()])); parts.append(('k', m.group())); pos = m.end()
        parts.append(('t', jp[pos:]))
        ko = []
        for kind, txt in parts:
            if kind == 'k': ko.append(txt); continue
            c = sum(1 for ch in txt if not ch.isspace())
            if not c: ko.append(txt); continue
            want = max(1, math.ceil(c * RATIO)); seg = []
            for i in range(want):
                seg.append(SYL[k % len(SYL)]); k += 1
                if i % 4 == 3 and i != want - 1: seg.append(' ')
            ko.append(''.join(seg))
        out.append('%05d\t%s\t1\t%s\t%s' % (n, id_, jp, ''.join(ko)))
    os.makedirs(B.R('work', 'text'), exist_ok=True)
    open(B.R('work', 'text', 'stress_ko.tsv'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('가짜 번역 %d줄 · 음절 %d개 돌려 씀' % (len(seen), len(SYL)))


if __name__ == '__main__':
    main()
