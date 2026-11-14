# -*- coding: utf-8 -*-
r"""하스피 번역(my files/번역, 읽기만) → 용어 통일 → work/text/fixed/ + 바꾼 기록 work/text/fixes_log.tsv

규칙 = (원문 조건 정규식, 번역에서 찾을 정규식, 바꿀 말, 이유). 원문(JP)에 조건이 있는 줄에서만 바꾼다.
바꾼 말 바로 뒤 조사는 새 말 받침에 맞춘다(키리크는 → 키릭은, 자사라메르를 → 자사라멜을).
용어는 다수결 금지 — 하스피가 정한 것만(2026-11-14 «성미나 탈림 알골 자사라멜 셰헤라자드 피아 아프렌티스 취소 자동 랜덤 재시도 히트»
+ 추천 표기: 소울엣지·소울칼리버·키릭·리저드맨·힐다·세츠카·카미키리무시·윤성·록·샹렌).
  python tools/apply_fixes.py
"""
import os, re, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kana_kr
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'my files', '번역')
OUT = os.path.join(ROOT, 'work', 'text', 'fixed')
LOG = os.path.join(ROOT, 'work', 'text', 'fixes_log.tsv')

NH = r'(?<![가-힣])'          # 앞이 한글 아님(낱말 시작)
RULES = [
    # 이름
    (r'ソウル\s*エッジ|ソウルエッ', r'소울 ?에지', '소울엣지', '소울엣지(전작 표기)'),
    (r'ソウル\s*キャリバー', r'소울 칼리버', '소울칼리버', '소울칼리버'),
    (r'キリク', NH + r'(?:키리크|킬리크|킬릭)', '키릭', '키릭'),
    (r'リザードマン', r'리자드맨', '리저드맨', '리저드맨'),
    (r'タリム', NH + r'타림', '탈림', '탈림(하스피)'),
    (r'ユンスン|潤星', r'윤승', '윤성', '윤성'),
    (r'ミナ|美那', NH + r'(?:성 미나|송 미나|손미나)', '성미나', '성미나(하스피)'),
    (r'ロック(?!オン)', NH + r'락(?=$|[^가-힣]|[의은는이가을를과와도])', '록', '록'),
    (r'ザサラメール', r'자사라메르', '자사라멜', '자사라멜(하스피)'),
    (r'ヒルダ', NH + r'힐데(?!가르)', '힐다', '힐다(원문 ヒルダ)'),
    (r'アルゴル', r'아르골', '알골', '알골(하스피)'),
    (r'アンゴル・フィア|アンゴル', r'앙골 피어', '앙골 피아', '앙골 피아(하스피)'),
    (r'シェラザード', r'(?:셰에라자드|셰라자드)', '셰헤라자드', '셰헤라자드(하스피)'),
    (r'アプレンティス', r'어프렌티스', '아프렌티스', '아프렌티스(하스피)'),
    (r'雪華|セツカ', r'설화', '세츠카', '세츠카'),
    (r'神斬蝕', r'신참식', '카미키리무시', '카미키리무시'),
    (r'シャンレン', r'샨렌', '샹렌', '샹렌'),
    # 2차 결정(2026-11-14 «힐데가르트 슈라 카르니에르크 라일라 라일라 반구 벨치 이블 철포 캐릭터 선택»)
    (r'ヒルデガルド', r'힐데가르드', '힐데가르트', '힐데가르트(하스피)'),
    (r'修羅（シュラ）|^(\$P1/)?修羅(1|2|1P|2P|　カスタム)?$|スタイル：修羅|スタイル： 修羅|【修羅】|「修羅[12]?」|修羅の\\n【STORY】',
     NH + r'수라', '슈라', '슈라(하스피 — 인물 이름만)'),
    (r'カルニェルク', r'카르녜르크', '카르니에르크', '카르니에르크(하스피)'),
    (r'ライラライラ', r'라일라라일라', '라일라 라일라', '라일라 라일라(하스피)'),
    (r'バングー', r'방구', '반구', '반구(하스피)'),
    (r'ベルチー', r'베르치', '벨치', '벨치(하스피)'),
    (r'イヴィル', r'이빌', '이블', '이블(하스피·전작)'),
    (r'イヴィルスパーム', r'(?:이블스펌|이블 스퍼름)', '이블 시드', '이블 시드(하스피 — 영어판 Evil Seed)'),
    (r'鉄砲', r'(?:총포|' + NH + r'총(?![가-힣]))', '철포', '철포(하스피)'),
    (r'キャラクターセレクト', r'캐릭터 셀렉트', '캐릭터 선택', '캐릭터 선택(하스피)'),
    # 일본어 음차 = 거센소리(か행 ㅋ·た행 ㅌ·つ 츠, 전프로젝트 규칙) — 기술 읽는 법 줄은 아래 kana_kr.aspirate 가 통째로
    (r'月詠|つくよみ', r'쓰쿠요미', '츠쿠요미', '거센소리(つ=츠)'),
    (r'松浦|まつら', r'마쓰라', '마츠라', '거센소리(つ=츠)'),
    (r'対馬', r'쓰시마', '츠시마', '거센소리(つ=츠)'),
    (r'浅沓', r'아사구쓰', '아사구츠', '거센소리(つ=츠)'),
    # UI
    (r'オートセーブ', r'오토 세이브', '자동 저장', '자동 저장(하스피)'),
    (r'ランダム', r'무작위', '랜덤', '랜덤(하스피)'),
    (r'リトライ', r'(?:재도전|리트라이)', '재시도', '재시도(하스피)'),
    (r'ヒット', r'적중', '히트', '히트(하스피)'),
]

JOSA = [('이에요', '예요'), ('이야', '야'), ('이랑', '랑'), ('이나', '나'), ('이라', '라'), ('으로', '로'),
        ('은', '는'), ('을', '를'), ('과', '와'), ('이', '가')]
_JOSA_RE = '|'.join(sorted({x for p in JOSA for x in p}, key=len, reverse=True))


def jong(ch):
    o = ord(ch) - 0xAC00
    return (o % 28) if 0 <= o < 11172 else None


def fit_josa(word, josa):
    j = jong(word[-1])
    if j is None:
        return josa
    for cons, vow in JOSA:
        if josa in (cons, vow):
            if cons == '으로':
                return '로' if j in (0, 8) else '으로'
            return vow if j == 0 else cons
    return josa


def replace(t, pat, b):
    """pat → b, 바로 뒤 조사를 b 받침에 맞춤(«이/가·이야»는 뒤가 한글이면 조사로 안 봄)"""
    def sub(m):
        jo, nxt = m.group('jo'), m.group('nx')
        if jo is None:
            return b
        if jo in ('이', '가', '이야', '야') and nxt and jong(nxt) is not None:
            return b + jo
        return b + fit_josa(b, jo)
    return re.sub('(?:%s)(?P<jo>%s)?(?=(?P<nx>.?))' % (pat, _JOSA_RE), sub, t)


NL = '\\n'
TOKS = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/')
HIRA_ONLY = re.compile(r'^[ぁ-ゖー・～〜\s　]+$')     # 기술 읽는 법 줄(원문이 가나뿐)
KATA_READ = re.compile(r'^[ァ-ヺ・～〜\s　]+$')      # 한자음 기술(성미나·키릭·샹화·윤성)의 가타카나 읽는 법 — ー 든 줄은 외래어(토네이도 등)라 뺌
HANJA = re.compile('[㐀-鿿豈-﫿]')
HANJA_PAREN = re.compile(r' ?[(（][^()（）]*[㐀-鿿][^()（）]*[)）]')
PUNCT = str.maketrans({'・': '·', '～': '~', '：': ':', '？': '?', '！': '!', '、': ',', '。': '.', '，': ',', '．': '.'})
JOSA_PAREN = re.compile(r'\((?:으|를|을|이|가|와|과|은|는|이랑|랑|아|야)\)')
LAYOUT_COLON = chr(0xE000)      # 표 정렬용 «：　» 잠시 감춤
REFLOW_LOC = re.compile(r'text/(museum|story)#')
BOX_W = {'museum': 25, 'story': 33.5}     # 원문 여러 줄 글의 최대 줄 폭(전각 1·반각 0.5) — 이 화면 글 상자 폭으로 씀


def waza01(t):
    """미츠루기 기술표(waza_01) 한자 이름 → work/text/waza01_kr.tsv (긴 것부터), 〜 중 → « 중»"""
    for a, b in WAZA01:
        t = t.replace(a, b)
    return t


def restore_brackets(jp, ko):
    """괄호는 원문 유지(하스피 2026-11-14): 「」를 ''로, （）를 ()로 바꾼 줄을 원문 꼴로"""
    for o, c in (('「', '」'), ('『', '』')):
        need = jp.count(o) - ko.count(o)
        if need > 0:
            q = '\'' if o == '「' else '"'
            pat = re.compile(re.escape(q) + r'([^' + q + r']*)' + re.escape(q))
            ko = pat.sub(lambda m: o + m.group(1) + c, ko, count=need)
    need = jp.count('（') - ko.count('（')
    if need > 0:
        def sub(m):
            nonlocal need
            if need <= 0 or JOSA_PAREN.fullmatch(m.group(0)):
                return m.group(0)
            need -= 1
            return '（' + m.group(1) + '）'
        ko = re.sub(r'\(([^()]*)\)', sub, ko)
    return ko


def main():
    global WAZA01
    WAZA01 = [ln.split('\t')[:2] for ln in open(os.path.join(ROOT, 'work', 'text', 'waza01_kr.tsv'), encoding='utf-8').read().splitlines()[1:] if ln.strip()]
    WAZA01.sort(key=lambda x: -len(x[0]))
    manual = {}
    mp = os.path.join(ROOT, 'work', 'text', 'manual.tsv')
    if os.path.exists(mp):
        for ln in open(mp, encoding='utf-8-sig').read().splitlines()[1:]:
            if ln.strip():
                no, a, b, why = ln.split('\t')
                manual.setdefault(no, []).append((a, b, why))
    sys.path.insert(0, os.path.join(ROOT, 'work', 'review'))
    from r10_reflow import reflow, w as rw
    os.makedirs(OUT, exist_ok=True)
    log = ['번호\t위치\tJP\t수정 전\t수정 후\t이유']
    n = 0; long_rows = []; seen_manual = set()
    for f in sorted(glob.glob(os.path.join(SRC, '*.tsv'))):
        lines = open(f, encoding='utf-8-sig').read().splitlines()
        out = [lines[0]]
        for ln in lines[1:]:
            c = ln.split('\t')
            before = c[4]; t = before; why = []
            for jre, kre, b, r in RULES:
                if re.search(jre, c[3]):
                    t2 = replace(t, kre, b)
                    if t2 != t:
                        t = t2; why.append(r)
            if c[1].startswith('tectext/waza_01#') and HANJA.search(t):
                t = waza01(t); t = re.sub(r'(?<=[가-힣]) ?중(?=\$|$)', ' 중', t); why.append('미츠루기 기술 번역')
            jplain = TOKS.sub('', c[3])
            if c[1].startswith('tectext/') and (HIRA_ONLY.match(jplain) or KATA_READ.match(jplain)):
                t2 = kana_kr.aspirate(jplain, t)       # 기술 읽는 법(가나) → 거센소리 규칙
                if t2 != t:
                    t = t2; why.append('거센소리(읽는 법)')
            t2 = HANJA_PAREN.sub('', t)
            if t2 != t:
                t = t2; why.append('한자 병기 삭제')
            t2 = re.sub('：(?=　)', LAYOUT_COLON, t).translate(PUNCT).replace(LAYOUT_COLON, '：')   # «：　» = 표 정렬용(프로필 머리) → 전각 유지
            if t2 != t:
                t = t2; why.append('한국식 부호')
            t2 = restore_brackets(c[3], t)
            if t2 != t:
                t = t2; why.append('괄호 원문 유지')
            nj = c[3].count(NL)
            BW = BOX_W.get(REFLOW_LOC.match(c[1]).group(1)) if REFLOW_LOC.match(c[1]) and nj >= 4 else None
            if c[0] in manual:                  # 손질(찾기→바꾸기): 뮤지엄·스토리 여러 줄 글은 문단을 한 줄로 이은 뒤 바꾸고 다시 접음
                if BW:
                    t = NL.join(reflow(c[3], t, W=10 ** 6)[1])
                for a, b, r in manual[c[0]]:
                    if a not in t:
                        raise SystemExit('manual.tsv 찾기 실패 %s: %s' % (c[0], a))
                    t = t.replace(a, b); why.append('손질: ' + r)
                seen_manual.add(c[0])
            if BW and (t.count(NL) != nj or c[0] in manual or max(rw(x) for x in t.split(NL)) > BW):
                W, lines_ = reflow(c[3], t, W=BW)
                if len(lines_) <= nj + 1:
                    lines_ += [''] * (nj + 1 - len(lines_))
                    t = NL.join(lines_); why.append('원문 폭 %g로 다시 접음' % W)
                else:
                    long_rows.append((c[0], c[1], len(lines_) - nj - 1))
            if t != before:
                c[4] = t; n += 1
                log.append('\t'.join((c[0], c[1], c[3], before, t, ' / '.join(why))))
            out.append('\t'.join(c))
        open(os.path.join(OUT, os.path.basename(f)), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    open(LOG, 'w', encoding='utf-8-sig', newline='\n').write('\n'.join(log) + '\n')
    assert seen_manual == set(manual), '손질 번호 못 찾음 %s' % (set(manual) - seen_manual)
    print('바꾼 줄 %d → %s · 기록 %s' % (n, OUT, LOG))
    for no, loc, d in long_rows:
        print('  ⚠줄 넘침 %s %s +%d줄 — work/text/manual.tsv 에서 줄여야 함' % (no, loc, d))


if __name__ == '__main__':
    main()
