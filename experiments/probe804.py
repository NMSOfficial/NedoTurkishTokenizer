import json,pathlib,collections
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer(); G=[json.loads(x) for x in pathlib.Path('reports/q1_final/final_gold_804.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
c=collections.Counter(); bylen=collections.defaultdict(collections.Counter)
for r in G:
 toks=T(r['word']); ps=[str(t.get('token','')).strip() for t in toks if str(t.get('token_type'))!='PUNCT' and str(t.get('token','')).strip()]
 gold=r['segments']; c['cases']+=1
 c['root_exact']+=(ps and ps[0].lower()==gold[0].lower())
 c['suffix_count_exact']+=(max(len(ps)-1,0)==max(len(gold)-1,0))
 c['boundary_exact']+=(bd(ps)==bd(gold))
 c['suffix_count_abs_err']+=abs(max(len(ps)-1,0)-max(len(gold)-1,0))
 key='long_ge10' if len(r['word'])>=10 else 'short_lt10'
 bylen[key]['n']+=1; bylen[key]['root']+=(ps and ps[0].lower()==gold[0].lower()); bylen[key]['bexact']+=(bd(ps)==bd(gold))
res={'cases':c['cases'],'root_recovery_acc':round(c['root_exact']/c['cases'],4),'suffix_count_acc':round(c['suffix_count_exact']/c['cases'],4),'suffix_count_mae':round(c['suffix_count_abs_err']/c['cases'],4),'boundary_exact_acc':round(c['boundary_exact']/c['cases'],4),'by_length':{k:{'cases':v['n'],'root_acc':round(v['root']/v['n'],4),'boundary_exact_acc':round(v['bexact']/v['n'],4)} for k,v in bylen.items()}}
pathlib.Path('reports/q1_worldclass_final/morphological_probe_804.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
