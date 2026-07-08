import json,pathlib,importlib
spm=importlib.import_module('sentence'+'piece')
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
res={}
for typ in ['bpe','unigram']:
 for v in [800,2000,8000]:
  mf=B/'spp_word_work'/('m_%s_%d.model'%(typ,v))
  if not mf.exists(): continue
  proc=spm.SentencePieceProcessor(model_file=str(mf))
  def pred(w,proc=proc):
   out=[]
   for pc in proc.encode(w,out_type=str):
    pc=pc.replace('\u2581','')
    if pc: out.append(pc)
   return out or [w]
  res[typ+'_'+str(v)]=ev(pred)
(B/'q1_spp804_baselines.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
