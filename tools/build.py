# -*- coding: utf-8 -*-
r"""소울칼리버 IV 한글 빌드 (2026-11-14).

입력
  work/extract/all.tsv          id(묶음/표#항목) · 일본어 · 영어 · 표시(keep/empty)   (tools/extract.py)
  work/text/fixed/sc4_*.tsv     번호 · 위치 · 겹침 · JP · KO   (my files/번역 하스피 번역 → tools/apply_fixes.py 용어 통일)
  work/text/ko_extra.tsv        (있으면) 같은 꼴 — 시험·손질용, my files 보다 우선
  원본: cdata/text = work/orig/text · cpudata/tectext = work/orig/tectext (게임 폴더엔 시험 파일이 섞여 있음) · 글꼴 = work/orig/font
방식
  · 번역은 «일본어 문장»으로 찾아 같은 문장 전부에 — 영어 자리(.msu · regtext_u.dtp 의 표 · waza_*.msu)에 넣음(언어 선택이 한국어→영어 자리)
  · 한글은 «대역 한자»(JIS 1·2수준 한자 칸 차례) UTF-8 로 — 글꼴의 그 칸에 한글을 그림(EBOOT 무수정)
  · 글꼴 = 64px 판(4096²×2, font_hires 방식) + fntdata.fnt 폭 바이트
  · 적재 검사(어기면 그 줄은 넣지 않고 보고): 토큰($P1/ · <s$Q25/s> · %d %s · <FONT_…> · <N> 등) 순서·개수 = 원문,
    줄바꿈(\n) 수 = 원문, 한자 금지(대역 한자와 겹침), 가나 금지(미번역), 글꼴(JIS)에 없는 글자 금지
  · 문장부호 뒤 공백 지움(규칙) · «……»/«...» → «…» 한 칸(바닥 점 셋으로 다시 그림)
출력  work/build/USRDIR/…(게임 폴더와 같은 상대 경로) · work/build/report.txt · charmap.tsv · 미리보기
  python tools/build.py
"""
import os, sys, re, glob, struct, hashlib, collections
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstext, font_kr, font_hires, nut

ROOT = mstext.ROOT
GAME = mstext.GAME
R = lambda *p: os.path.join(ROOT, *p)
STRESS = '--stress' in sys.argv          # 버퍼 시험: 모든 줄을 가짜 한글(work/text/stress_ko.tsv)로 → work/build_stress
BUILD = R('work', 'build_stress' if STRESS else 'build')
OUT = os.path.join(BUILD, 'USRDIR')
TOK = re.compile(r'\$[A-Za-z][0-9]*/|<s\$Q[0-9]+/s>|%[-+0-9.]*[a-zA-Z]|<[A-Z_ 0-9]+>|\\n')
PUNCT_SP = re.compile(r'([,.!?…‼⁉、。，．！？：；:;～~])[ 　]+')
KANA = re.compile('[ぁ-ヿｦ-ﾟ]')
JPCHR = re.compile('[぀-ヿ㐀-鿿ｦ-ﾟ]')


def is_sysdlg(id_, jp):
    """PS3 시스템 대화상자로 뜨는 문장 = regtext 표 0(저장·로드·설치 안내)의 «$» 머리 없는 것 — 게임 글꼴이 아니라
    시스템 글꼴이라 대역 한자가 한자로 보임(2026-11-14 실기 자동 저장 안내) → 진짜 한글 UTF-8 로 넣음"""
    return id_.startswith('regtext/0#') and not jp.startswith('$')
HAN = re.compile('[㐀-鿿豈-﫿]')
ELLIPSIS_CELL = (0x2144 >> 8) - 0x21, (0x2144 & 0xFF) - 0x21      # JIS 1-4 «…» → 칸 (1-1)*94 + 3 = 3


def unesc(s):
    out = []; i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            out.append({'n': '\n', 't': '\t', '\\': '\\'}.get(s[i + 1], '\\' + s[i + 1])); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


def load_ko():
    """JP(이스케이프 꼴) → KO(이스케이프 꼴). ko_extra 가 우선"""
    ko = {}; src = {}
    files = sorted(glob.glob(R('work', 'text', 'fixed', 'sc4_*.tsv')))     # = my files/번역 + tools/apply_fixes.py 용어 통일
    assert files, 'work/text/fixed 없음 — 먼저 python tools/apply_fixes.py'
    if os.path.exists(R('work', 'text', 'ko_extra.tsv')): files.append(R('work', 'text', 'ko_extra.tsv'))
    if STRESS: files = [R('work', 'text', 'stress_ko.tsv')]
    for p in files:
        with open(p, encoding='utf-8') as f:
            next(f)
            for ln in f:
                c = ln.rstrip('\n').rstrip('\r').split('\t')
                if len(c) >= 5 and c[4].strip():
                    ko[c[3]] = c[4]; src[c[3]] = os.path.basename(p) + ':' + c[0]
    return ko, src


def jis_ok(ch):
    try:
        b = ch.encode('cp932')
    except UnicodeEncodeError:
        return False
    return len(b) == 1 or 0x81 <= b[0] <= 0x84 or b[0] == 0x88 and b[1] < 0x9F   # 1바이트 · 비한자 기호·가나 구(1~8구)


def check(jp, ko):
    """-> (정리된 KO 이스케이프 꼴, 문제 목록)"""
    errs = []
    ko = PUNCT_SP.sub(lambda m: m.group(1), ko).replace('……', '…').replace('...', '…')
    tj = TOK.findall(jp); tk = TOK.findall(ko)
    if [t for t in tj if t != '\\n'] != [t for t in tk if t != '\\n']: errs.append('토큰 다름 %s / %s' % ([t for t in tj if t != '\\n'], [t for t in tk if t != '\\n']))
    if tj.count('\\n') != tk.count('\\n'): errs.append('줄 수 다름 %d / %d' % (tj.count('\\n') + 1, tk.count('\\n') + 1))
    plain = TOK.sub('', ko)
    if HAN.search(plain): errs.append('한자 %s' % ''.join(sorted(set(HAN.findall(plain)))))
    kana = set(KANA.findall(plain)) - {'・'}                       # ・ = 가운뎃점(JIS 1-6) — 가나 아님
    if kana: errs.append('가나 %s' % ''.join(sorted(kana)))
    bad = sorted({c for c in plain if not ('가' <= c <= '힣') and not HAN.match(c) and not KANA.match(c) and not jis_ok(c)
                  and c not in jp and c != '·'})                    # 원문에 있는 글자(®©™Ü①Ⅳ…)는 게임이 찍음 · «·»는 «・» 칸으로
    if bad: errs.append('글꼴에 없는 글자 %s' % ''.join(bad))
    return ko, errs


def src_path(rel):
    """원본 파일: cdata/text 는 work/orig/text(게임 폴더엔 시험 파일), 그 밖은 게임 폴더"""
    if rel.startswith('cdata/text/') or rel.startswith('cpudata/tectext/'):     # 게임 폴더엔 시험판이 깔려 있음 → 원본 백업에서
        p = R('work', 'orig', rel.split('/')[-2], rel.split('/')[-1])
        assert os.path.exists(p), p
        return p
    return os.path.join(GAME, *rel.split('/'))


def font_build(cmap, outdir):
    """64px 판 글꼴(font_hires 방식, cmap 를 인자로) + fntdata.fnt"""
    src = open(os.path.join(font_kr.SRC, 'gt_KanjiTexturePs3.nut'), 'rb').read()
    es = nut.entries(src)
    K, C = font_hires.K, font_hires.C
    pages = [np.repeat(np.repeat(font_hires.classes(nut.decode(src, e)), K, 0), K, 1) for e in es]
    for s, (cell, kan) in cmap.items():
        p, r = divmod(cell, 4096); cy, cx = divmod(r, 64)
        pages[p][cy * C:cy * C + C, cx * C:cx * C + C] = font_hires.render(s)
    # «…» = 한국식 바닥 점 셋(칸 1-4)
    cell = ELLIPSIS_CELL[0] * 94 + ELLIPSIS_CELL[1]; cy, cx = divmod(cell, 64)
    g = np.full((C, C), 3, np.uint8); ink = np.zeros((C, C), bool)
    for k in range(3):
        x = 10 * K + k * 6 * K; ink[24 * K:27 * K, x:x + 3 * K] = True
    e = ink
    for _ in range(2 * K): e = font_kr._dil(e)
    g[e & ~ink] = 0; g[ink] = 1
    pages[0][cy * C:cy * C + C, cx * C:cx * C + C] = g
    out = bytearray(src[:0x10])
    for e, pg in zip(es, pages):
        data = font_hires.encode_page(pg); head = bytearray(e['head'])
        struct.pack_into('>I', head, 0, len(data) + e['hsize']); struct.pack_into('>I', head, 8, len(data))
        struct.pack_into('>HH', head, 0x14, pg.shape[1], pg.shape[0])
        out += head + data
    fd = bytearray(open(os.path.join(font_kr.SRC, 'fntdata.fnt'), 'rb').read())
    for s, (cell, kan) in cmap.items(): fd[cell] = font_kr.WIDTH_BYTE
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, 'gt_KanjiTexturePs3.nut'), 'wb').write(out)
    open(os.path.join(outdir, 'fntdata.fnt'), 'wb').write(fd)
    return bytes(out), bytes(fd)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    rep = []
    log = lambda *a: (rep.append(' '.join(str(x) for x in a)), print(*a))
    ko_raw, ko_src = load_ko()
    rows = [l.rstrip('\n').split('\t') for l in open(R('work', 'extract', 'all.tsv'), encoding='utf-8')][1:]
    # 1) 적재·검사
    ok, bad = {}, []
    jp_of = {r[1] for r in rows if not r[3]}
    for jp, k in ko_raw.items():
        if jp not in jp_of: bad.append((ko_src[jp], '원문을 찾지 못함', jp[:40])); continue
        k2, errs = check(jp, k)
        if errs: bad.append((ko_src[jp], ' · '.join(errs), jp[:40]))
        else: ok[jp] = k2
    log('번역 %d줄 읽음 · 넣음 %d · 문제로 뺌 %d' % (len(ko_raw), len(ok), len(bad)))
    for b in bad[:200]: log('  ⛔', *b)
    # 2) 음절 → 대역 한자(많이 쓰는 차례)
    freq = collections.Counter(c for k in ok.values() for c in unesc(k) if '가' <= c <= '힣')
    cmap = font_kr.assign([c for c, n in freq.most_common()])
    log('음절 %d개 (한자 칸 %d 중)' % (len(cmap), len(font_kr.cells())))
    # 3) 표 다시 짜기
    by_file = collections.defaultdict(dict)            # rel → {(표, 항목): 새 바이트}
    hit = collections.Counter(); miss = collections.Counter()
    keep_ascii = [0]; sysd = [0]
    for id_, jp, en, flag in rows:
        if flag: continue
        if not JPCHR.search(jp): keep_ascii[0] += 1; continue          # 일본판도 가나·한자 없음(PLAYSTATION®Network·곡명·©…) = 영어 그대로 — 장식 글꼴 메뉴 이름이 깨짐(2026-11-14 실기)
        grp, rest = id_.split('/', 1); tbl, idx = rest.split('#')
        if jp not in ok: miss[grp] += 1; continue
        if is_sysdlg(id_, jp): new = unesc(ok[jp]).encode('utf-8'); sysd[0] += 1          # 시스템 대화상자(PS3 시스템 글꼴) = 진짜 한글
        else: new = font_kr.encode_text(unesc(ok[jp]).replace('·', '・'), cmap).encode('utf-8')   # 한국식 가운뎃점 → 게임 글꼴 «・» 칸
        if grp == 'regtext': by_file['cdata/text/regtext_u.dtp'][(int(tbl), int(idx))] = new
        elif grp == 'text': by_file['cdata/text/%s.msu' % tbl][(0, int(idx))] = new
        else: by_file['cpudata/tectext/%s.msu' % tbl][(0, int(idx))] = new
        hit[grp] += 1
    log('넣은 항목 %s · 번역 없어 영어 그대로 %s' % (dict(hit), dict(miss)))
    log('일본판도 가나·한자 없어 영어 그대로 %d · 시스템 대화상자(진짜 한글) %d' % (keep_ascii[0], sysd[0]))
    sizes = []
    for rel, ch in sorted(by_file.items()):
        b = open(src_path(rel), 'rb').read()
        if rel.endswith('.dtp'):
            chunks = [mstext.chunk_trim(c, False) for c in mstext.pack_split(b)]
            for t in sorted({t for t, i in ch}):
                lang, strs = mstext.read_table(chunks[t])
                for (tt, i), v in ch.items():
                    if tt == t: strs[i] = v
                chunks[t] = mstext.write_table(lang, strs)
                assert mstext.read_table(chunks[t]) == (lang, strs)
            out = mstext.pack_join(chunks)
        else:
            lang, strs = mstext.read_table(b)
            for (t, i), v in ch.items(): strs[i] = v
            out = mstext.write_table(lang, strs)
            assert mstext.read_table(out) == (lang, strs)
        p = os.path.join(OUT, *rel.split('/')); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(out); sizes.append((len(out) / len(b), rel, len(b), len(out)))
    sizes.sort(reverse=True)
    log('글 파일 %d개 · 크기 늘어난 비율 큰 차례:' % len(sizes))
    for r_, rel, a, b in sizes[:12]: log('   %-40s %7d → %7d B (×%.2f)' % (rel, a, b, r_))
    # 4) 글꼴
    nutb, fdb = font_build(cmap, os.path.join(OUT, 'cdata', 'texture'))
    log('글꼴 gt_KanjiTexturePs3.nut %d B md5 %s · fntdata.fnt md5 %s' % (len(nutb), hashlib.md5(nutb).hexdigest(), hashlib.md5(fdb).hexdigest()))
    with open(os.path.join(BUILD, 'charmap.tsv'), 'w', encoding='utf-8') as o:
        o.write('음절\t칸\t대역 한자\t쓰인 수\n')
        for s, (cell, kan) in cmap.items(): o.write('%s\t%d\t%s\t%d\n' % (s, cell, kan, freq[s]))
    # 5) 검산: 만든 파일을 다시 읽어 대역 한자를 한글로 되돌리면 번역문과 같은지
    back = {kan: s for s, (cell, kan) in cmap.items()}
    n = 0
    for rel, ch in by_file.items():
        b = open(os.path.join(OUT, *rel.split('/')), 'rb').read()
        tabs = [mstext.read_table(mstext.chunk_trim(c, False))[1] for c in mstext.pack_split(b)] if rel.endswith('.dtp') else [mstext.read_table(b)[1]]
        for (t, i), v in ch.items():
            assert tabs[t][i] == v; n += 1
    log('검산: 써 넣은 %d항목 다시 읽어 일치' % n)
    open(os.path.join(BUILD, 'report.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    # 글자판 미리보기(빌드 파일 되읽음): 많이 쓰는 음절 앞 192개
    es = nut.entries(nutb); im = nut.decode(nutb, es[0]); C = font_hires.C
    cells_ = [cell for s, (cell, kan) in list(cmap.items())[:192] if cell < 4096]
    if cells_:
        tiles = [im[(c // 64) * C:(c // 64) * C + C, (c % 64) * C:(c % 64) * C + C] for c in cells_]
        while len(tiles) % 16: tiles.append(np.zeros_like(tiles[0]))
        grid = np.vstack([np.hstack(tiles[i:i + 16]) for i in range(0, len(tiles), 16)])
        rgb = grid[:, :, :3].astype(np.float32); al = grid[:, :, 3:4].astype(np.float32) / 255
        Image.fromarray((rgb * al + 96 * (1 - al)).astype(np.uint8)).save(os.path.join(BUILD, '미리보기_글자판_자주쓰는음절.png'))


if __name__ == '__main__':
    main()
