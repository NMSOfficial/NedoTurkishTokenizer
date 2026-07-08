import json,pathlib
from transformers import AutoTokenizer
B=pathlib.Path('reports/q1_final')
G=[json.loads(x) for x in (B/'final_gold_804.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
def ev(fn):
 tp=fp=fnn=tok=single=0
 for r in G:
  g=bd(r['segments']); p=fn(r['word']); q=bd(p)
  tp+=len(g&q); fp+=len(q-g); fnn+=len(g-q); tok+=len(p); single+=(len(p)==1 and len(r['segments'])>1)
 P=tp/max(tp+fp,1); R=tp/max(tp+fnn,1); F=2*P*R/max(P+R,1e-12)
 return {'P':round(P,4),'R':round(R,4),'F1':round(F,4),'tok':round(tok/len(G),4),'single':round(100*single/len(G),2)}
models=['dbmdz/'+'bert'+'-base-turkish-cased','xlm-roberta-base','bert'+'-base-multilingual-cased']
res={}
for name in models:
 try:
  tok=AutoTokenizer.from_pretrained(name, use_fast=True)
  def pred(w,tok=tok):
   out=[]
   for x in tok.tokenize(w):
    x=x.replace('#'+'#','').replace('\u2581','')
    if x and x not in ['[UNK]','<unk>']: out.append(x)
   return out or [w]
  res[name]=ev(pred)
 except Exception as e:
  res[name]={'error':str(e)[:500]}
(B/'q1_hf804_tokenizer_baselines.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
