"""줄 수가 원문과 다른 줄: 원문 최대 줄 폭(전각 1·반각 0.5)으로 다시 접으면 몇 줄인지"""
from common import *
import re, unicodedata
TOKW = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/|<[^>]*>')
def w(s):
    s = TOKW.sub('', s)
    return sum(0.5 if ord(c) < 0x80 or 0xFF61 <= ord(c) <= 0xFF9F else 1 for c in s)
def wrap(par, W):
    """공백에서 접기(한 낱말이 W 넘으면 글자 단위)"""
    lines, cur = [], ''
    for word in par.split(' '):
        cand = (cur + ' ' + word) if cur else word
        if w(cand) <= W: cur = cand; continue
        if cur: lines.append(cur)
        cur = word
        while w(cur) > W:
            k = len(cur)
            while w(cur[:k]) > W: k -= 1
            lines.append(cur[:k]); cur = cur[k:]
    lines.append(cur)
    return lines
def reflow(jp, ko, W=None):
    J = jp.split(NL); K = ko.split(NL)
    if W is None: W = max(w(x) for x in J)
    # 문단 = 빈 줄로 나뉨, 들여쓰기(　)로 시작하는 줄도 새 문단, 머리(：가 든 줄)·빈 줄은 그대로
    out = []; par = None
    def flush():
        nonlocal par
        if par is not None: out.extend(wrap(par, W)); par = None
    for line in K:
        if line.strip(' 　') == '' or '：' in line or ':' in line[:8] or line.startswith('　　'):   # 빈 줄·프로필 머리·머리 이어지는 줄
            flush()
            if w(line) <= W: out.append(line); continue
            # 폭 넘는 머리 줄: 값 부분을 접고 이어지는 줄은 전각 6칸 들여쓰기(원문 꼴)
            m = re.match(r'^(.*?：　|　+)(.*)$', line)
            head, val = (m.group(1), m.group(2)) if m else ('', line)
            ind = '　' * 6
            parts = wrap(val, W - w(ind))
            out.append(head + parts[0]); out.extend(ind + x for x in parts[1:]); continue
        quote = line.startswith(('「', '『')) and par is not None and re.search(r'[.!?…」』―/]$', par)   # 문장이 끝난 뒤 「…」로 시작하는 대사 줄
        if par is None or line.startswith('　') or quote or re.match(r'^(\$[A-Za-z][0-9.]*(/[0-9.]+)*/)+[　「『]', line):
            flush(); par = line
        else:
            par = par + ('' if par.endswith(' ') else ' ') + line.lstrip(' ')
    flush()
    return W, out
if __name__ == '__main__':
    for r in rows():
        nj = r['jp'].count(NL); nk = r['ko'].count(NL)
        if nj == nk: continue
        W, out = reflow(r['jp'], r['ko'])
        print(r['no'], r['loc'], '원문 %d줄 폭 %.1f · 번역 %d줄 → 다시 접기 %d줄 (%+d)' % (nj + 1, W, nk + 1, len(out), len(out) - nj - 1))
