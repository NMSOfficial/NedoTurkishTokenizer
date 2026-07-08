import json,pathlib,collections
from nedo_turkish_tokenizer import NedoTurkishTokenizer
import nedo_turkish_tokenizer.segmentation as sg
G=[json.loads(x) for x in pathlib.Path('reports/q1_worldclass_final/full_gold_1000.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
def ev(T):
 c=collections.Counter()
 for r in G:
  ps=[str(t.get('token','')).strip() for t in T(r['word']) if str(t.get('token_type'))!='PUNCT' and str(t.get('token','')).strip()]
  g=bd(r['segments']); p=bd(ps)
  c['tp']+=len(g&p); c['fp']+=len(p-g); c['fn']+=len(g-p); c['tok']+=len(ps); c['cases']+=1; c['single']+=(len(ps)==1 and len(r['segments'])>1)
 P=c['tp']/max(c['tp']+c['fp'],1); R=c['tp']/max(c['tp']+c['fn'],1); F=2*P*R/max(P+R,1e-12)
 return {'P':round(P,4),'R':round(R,4),'F1':round(F,4),'tok':round(c['tok']/c['cases'],4),'single':round(100*c['single']/c['cases'],2)}
ans={}
T=NedoTurkishTokenizer(); ans['full']=ev(T)
T=NedoTurkishTokenizer(); T._engine._domain_roots=frozenset(); ans['no_domain']=ev(T)
T=NedoTurkishTokenizer(); T._engine._tdk=set(); ans['no_lexicon']=ev(T)
old=sg._MAX_SUFFIX_DEPTH
for d in [3,1]:
 sg._MAX_SUFFIX_DEPTH=d; ans['depth_'+str(d)]=ev(NedoTurkishTokenizer())
sg._MAX_SUFFIX_DEPTH=old
pathlib.Path('reports/q1_worldclass_final/human_gold_ablation_1000.json').write_text(json.dumps(ans,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(ans,ensure_ascii=False))
