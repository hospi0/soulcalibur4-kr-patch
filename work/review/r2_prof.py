from common import *
for r in rows():
    if r['loc'].startswith('text/museum#') and '年齢' in r['jp']:
        j = r['jp'].split(NL); k = r['ko'].split(NL)
        g = lambda a, key: next((x for x in a if key in x), '').split('：')[-1].strip()
        print(r['no'], j[0].strip(), '|', k[0].strip(), '|', g(j,'武器名'), '→', g(k,'무기명'), '|', g(j,'流派'), '→', g(k,'유파'), '|', g(j,'出身'), '→', g(k,'출신'))
