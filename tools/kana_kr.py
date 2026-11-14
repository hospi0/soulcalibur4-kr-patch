# -*- coding: utf-8 -*-
"""히라가나 → 한글(하스피 규칙: か행 ㅋ · た행 ㅌ · つ 츠, 어두도 거센소리, 탁음은 유성음, 장음 안 적음)
+ 번역의 읽는 법 줄을 이 규칙에 맞추기(aspirate): 음절 수가 같을 때 «ㄱ↔ㅋ · ㄷ↔ㅌ · 쓰↔츠»만 다른 음절을 고침."""
import re

ONSET = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
VOWEL = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
CODA = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'


def syl(o, v, c=' '):
    return chr(0xAC00 + (ONSET.index(o) * 21 + VOWEL.index(v)) * 28 + CODA.index(c))


def split(s):
    i = ord(s) - 0xAC00
    return ONSET[i // 588], VOWEL[i % 588 // 28], CODA[i % 28]


V5 = 'ㅏㅣㅜㅔㅗ'
ROWS = {  # 자음 줄: 가나 5개 → 초성
    'あいうえお': 'ㅇ', 'かきくけこ': 'ㅋ', 'がぎぐげご': 'ㄱ', 'さしすせそ': 'ㅅ', 'ざじずぜぞ': 'ㅈ',
    'たちつてと': 'ㅌ', 'だぢづでど': 'ㄷ', 'なにぬねの': 'ㄴ', 'はひふへほ': 'ㅎ', 'ばびぶべぼ': 'ㅂ',
    'ぱぴぷぺぽ': 'ㅍ', 'まみむめも': 'ㅁ', 'らりるれろ': 'ㄹ',
}
K = {}
for row, o in ROWS.items():
    for ch, v in zip(row, V5):
        K[ch] = syl(o, v)
K.update({'し': '시', 'ち': '치', 'つ': '츠', 'ぢ': '지', 'づ': '즈', 'じ': '지', 'す': '스', 'ず': '즈', 'ふ': '후',
          'や': '야', 'ゆ': '유', 'よ': '요', 'わ': '와', 'を': '오', 'ゐ': '이', 'ゑ': '에'})
YO = {'ゃ': 'ㅑ', 'ゅ': 'ㅠ', 'ょ': 'ㅛ'}
SMALLV = {'ぁ': 'ㅏ', 'ぃ': 'ㅣ', 'ぅ': 'ㅜ', 'ぇ': 'ㅔ', 'ぉ': 'ㅗ'}


def kana2kr(s):
    """히라가나 문자열 → 한글 음절 목록(구분자는 그대로 문자열로)"""
    s = ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
    out = []
    i = 0
    while i < len(s):
        c = s[i]; n = s[i + 1] if i + 1 < len(s) else ''
        if out and '가' <= out[-1] <= '힣' and split(out[-1])[2] == ' ' and (
                c == 'う' and split(out[-1])[1] in 'ㅗㅜㅛㅠ' or c == 'い' and split(out[-1])[1] == 'ㅔ'):
            i += 1; continue                       # 장음 안 적음(おう·ゆう·えい — 번역 관례와 같음)
        if c in K and n in YO:
            o, v, _ = split(K[c])
            if c in 'しじちぢ':
                o = {'し': 'ㅅ', 'じ': 'ㅈ', 'ち': 'ㅊ', 'ぢ': 'ㅈ'}[c]
                out.append(syl(o, {'ㅑ': 'ㅏ', 'ㅠ': 'ㅜ', 'ㅛ': 'ㅗ'}[YO[n]] if o != 'ㅅ' else YO[n]))
            else:
                out.append(syl(o, YO[n]))
            i += 2; continue
        if c in K and n in SMALLV:
            o, v, _ = split(K[c]); out.append(syl(o, SMALLV[n])); i += 2; continue
        if c in K:
            out.append(K[c]); i += 1; continue
        if c in 'んっ' and out and len(out[-1]) == 1 and '가' <= out[-1] <= '힣':
            o, v, cd = split(out[-1]); out[-1] = syl(o, v, 'ㄴ' if c == 'ん' else 'ㅅ'); i += 1; continue
        if c == 'ー':
            i += 1; continue
        out.append(c); i += 1
    return out


EQUIV = {('ㄱ', 'ㅋ'), ('ㄷ', 'ㅌ')}


def _norm(ch):
    if ch == '츠':
        return '쓰'
    o, v, c = split(ch)
    return syl({'ㅋ': 'ㄱ', 'ㅌ': 'ㄷ', 'ㅊ': 'ㅈ'}.get(o, o), v, c)


def aspirate(jp, ko):
    """번역 ko(읽는 법)를 jp 가나 기준으로 거센소리 규칙에 맞춤.
    두 음절열을 «ㄱ=ㅋ·ㄷ=ㅌ·ㅈ=ㅊ·쓰=츠» 로 같게 보고 맞대어(장음·띄어쓰기 차이는 건너뜀) 일치 구간만 가나 쪽 음절로 바꿈"""
    import difflib
    mine = [x for x in kana2kr(jp) if '가' <= x <= '힣']
    ks = [(i, ch) for i, ch in enumerate(ko) if '가' <= ch <= '힣']
    a = [_norm(ch) for _, ch in ks]; b = [_norm(x) for x in mine]
    out = list(ko)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for t in range(blk.size):
            i, k = ks[blk.a + t]
            out[i] = mine[blk.b + t]
    return ''.join(out)
