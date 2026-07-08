import json,pathlib,collections
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
roots=['meeting','repo','server','plugin','driver','model','prompt','cache','batch','token','dataset','pipeline','branch','commit','notebook','script','cluster','debug','checkpoint','framework','adapter','module','encoder','decoder','router','kernel','thread','worker','queue','log']
suffs=[('ler',['PL']),('lar',['PL']),('de',['LOC']),('da',['LOC']),('den',['ABL']),('dan',['ABL']),('e',['DAT']),('a',['DAT'])]
items=[]
for r in roots:
 for s,l in suffs:
  items.append({'word':r+s,'segments':[r,s],'labels':l})
items=items[:240]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
c=collections.Counter(); examples=[]
for it in items:
 toks=T(it['word']); ps=[str(t.get('token','')).strip() for t in toks if str(t.get('token_type'))!='PUNCT' and str(t.get('token','')).strip()]
 g=bd(it['segments']); p=bd(ps)
 c['tp']+=len(g&p); c['fp']+=len(p-g); c['fn']+=len(g-p); c['single']+=(len(ps)==1); c['cases']+=1
 if g!=p and len(examples)<20: examples.append({'word':it['word'],'gold':'+'.join(it['segments']),'pred':'+'.join(ps)})
P=c['tp']/max(c['tp']+c['fp'],1); R=c['tp']/max(c['tp']+c['fn'],1); F=2*P*R/max(P+R,1e-12)
res={'cases':c['cases'],'P':round(P,4),'R':round(R,4),'F1':round(F,4),'single_pct':round(100*c['single']/c['cases'],2),'examples':examples}
pathlib.Path('reports/q1_worldclass_final/codemix_foreign_240.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
