"""원문 높임(です·ます) ↔ 번역 높임(요·니다) 어긋남 — 대사 묶음과 UI 따로"""
from common import *
import re, collections
P = re.compile(r'\$[A-Za-z][0-9.]*(/[0-9.]+)*/|<[^>]*>|%[-+0-9.]*[a-zA-Z]')
JPOL = re.compile(r'(です|ます|ません|ました|ましょう|でしょう|ください|下さい|でした|ませ|まし|ですか|ますか|なさい)')
KPOL = re.compile(r'(니다|니까|세요|에요|예요|어요|아요|여요|해요|지요|죠|군요|네요|나요|가요|래요|게요|까요|십시오|시오|[가-힣]요)(?=[\s!?.…~,」』)」]*$|[\s!?.…~,]+)')
def seg_last(s):
    s = P.sub('', s).replace(NL, ' ').strip(' 　')
    return s
R = rows()
out = collections.defaultdict(list)
for r in R:
    grp = 'aplwin' if 'subtitle_aplwin' in r['loc'] else 'demo' if 'subtitle_demo' in r['loc'] else 'tectext' if r['loc'].startswith('tectext') else 'ui'
    if grp == 'tectext': continue
    j = seg_last(r['jp']); k = seg_last(r['ko'])
    jp_pol = bool(JPOL.search(j)); ko_pol = bool(KPOL.search(k))
    if jp_pol and not ko_pol: out[(grp, '원문 높임 → 번역 낮춤')].append(r)
    if not jp_pol and ko_pol and grp in ('aplwin', 'demo'): out[(grp, '원문 낮춤 → 번역 높임')].append(r)
with open('r8_register.txt', 'w', encoding='utf-8') as f:
    for key in sorted(out):
        f.write('== %s %s %d\n' % (key[0], key[1], len(out[key])))
        print(key, len(out[key]))
        for r in out[key]:
            f.write('  %s %s | %s | %s\n' % (r['no'], r['loc'], seg_last(r['jp']), seg_last(r['ko'])))
