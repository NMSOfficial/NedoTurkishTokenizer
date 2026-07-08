import json, pathlib
v20=json.loads(pathlib.Path('reports/quality_v21/v20_words.json').read_text(encoding='utf-8'))
v21=json.loads(pathlib.Path('reports/quality_v21/v21_words.json').read_text(encoding='utf-8'))
rows=[]
for a,b in zip(v20,v21):
    rows.append({'word':a['word'],'v20_n':a['n'],'v21_n':b['n'],'v20_single_root':a['single_root'],'v21_single_root':b['single_root'],'v20_tokens':a['tokens'],'v21_tokens':b['tokens']})
summary={'cases':len(rows),'v20_single_root':sum(r['v20_single_root'] for r in rows),'v21_single_root':sum(r['v21_single_root'] for r in rows),'fixed_single_root':sum(r['v20_single_root'] and not r['v21_single_root'] for r in rows),'avg_tokens_v20':round(sum(r['v20_n'] for r in rows)/len(rows),3),'avg_tokens_v21':round(sum(r['v21_n'] for r in rows)/len(rows),3)}
pathlib.Path('reports/quality_v21/v20_vs_v21_actual.json').write_text(json.dumps({'summary':summary,'rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
