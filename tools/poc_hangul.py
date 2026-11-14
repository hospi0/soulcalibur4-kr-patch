# -*- coding: utf-8 -*-
"""한글 시험 파일을 work/poc/ 에 만든다(게임 폴더에는 쓰지 않는다).

1) subtitle_aplwin.msu : 영어 표에 원래 들어 있던 한국어(.msk) 승리·등장 대사
2) regtext_u.dtp       : 모드 선택 표의 아케이드 설명 한 줄(메뉴 이름은 장식 글꼴이라 원문 그대로)
3) gt_KanjiTexturePs3.nut · fntdata.fnt : 쓰인 음절을 한자 칸에 그린 글꼴
   글은 한글 대신 «대역 한자»의 UTF-8 로 들어간다.

python tools/poc_hangul.py
"""
import os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstext, font_kr

SRC = os.path.join(mstext.ROOT, 'work', 'orig', 'text')
OUT = os.path.join(mstext.ROOT, 'work', 'poc')

MENU = {
    b'$P1/Fight through 8 stages without equipment and weapon effects. The final score will be ranked.':
        '$P1/장비와 무기 효과 없이 8스테이지를 싸웁니다. 최종 점수는 랭킹에 오릅니다.',
}


def md5(b):
    return hashlib.md5(b).hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    lang, en = mstext.read_table(open(os.path.join(SRC, 'subtitle_aplwin.msu'), 'rb').read())
    _, ko = mstext.read_table(open(os.path.join(SRC, 'subtitle_aplwin.msk'), 'rb').read(), plain=True)
    assert len(en) == len(ko)
    ko = [k.decode('utf-8') for k in ko]
    # 음절 모으기(나온 차례) + 한글·ASCII 밖 글자 검사
    syl = []
    other = set()
    for s in ko + list(MENU.values()):
        for ch in s:
            if '가' <= ch <= '힣':
                syl.append(ch)
            elif ord(ch) > 0x7E:
                other.add(ch)
    bad = []
    for ch in sorted(other):
        try:
            ch.encode('cp932')
        except UnicodeEncodeError:
            bad.append(ch)
    print('한글·ASCII 밖 글자:', ''.join(sorted(other)), '| 글꼴(JIS)에 없는 것:', bad)
    cmap = font_kr.assign(syl)
    n = font_kr.build(cmap, OUT)
    print('글꼴: 음절 %d 개를 한자 칸에 그림' % n)
    for f in ('gt_KanjiTexturePs3.nut', 'fntdata.fnt'):
        print('  %s md5 %s' % (f, md5(open(os.path.join(OUT, f), 'rb').read())))
    # 1) 승리 대사
    new = [font_kr.encode_text(k, cmap).encode('utf-8') if k else e for e, k in zip(en, ko)]
    out = mstext.write_table(lang, new)
    assert mstext.read_table(out) == (lang, new)
    open(os.path.join(OUT, 'subtitle_aplwin.msu'), 'wb').write(out)
    print('subtitle_aplwin.msu: 한국어 %d / %d 줄, %d B, md5 %s' % (sum(1 for k in ko if k), len(en), len(out), md5(out)))
    # 2) 메뉴 설명
    b = open(os.path.join(SRC, 'regtext_u.dtp'), 'rb').read()
    chunks = [mstext.chunk_trim(c, False) for c in mstext.pack_split(b)]
    hit = 0
    for i, c in enumerate(chunks):
        lang, strs = mstext.read_table(c)
        ch = False
        for j, s in enumerate(strs):
            if s in MENU:
                strs[j] = font_kr.encode_text(MENU[s], cmap).encode('utf-8'); ch = True; hit += 1
        if ch:
            chunks[i] = mstext.write_table(lang, strs)
    out = mstext.pack_join(chunks)
    open(os.path.join(OUT, 'regtext_u.dtp'), 'wb').write(out)
    print('regtext_u.dtp: 바꾼 줄 %d, %d B(원본 %d), md5 %s' % (hit, len(out), len(b), md5(out)))


if __name__ == '__main__':
    main()
