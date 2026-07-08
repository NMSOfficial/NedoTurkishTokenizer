import sys,json,pathlib,importlib
sys.path.insert(0, str((pathlib.Path('external_baselines')/'TurkishMorpheus').resolve()))
mod=importlib.import_module('src.model_development.tokenization.'+'morpheus'+'_tokenizer')
Cls=getattr(mod,'MorpheusTokenizer')
B=pathlib.Path('reports/q1_final')
G=[json.loads(x) for x in (B/'final_gold_804.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
tok=Cls.load('external_baselines/Morpheus-TR-50K/morpheus_50k')
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
def pred(w):
 out=[]
 for p in tok.encode_as_pieces(w):
  p=str(p).replace('\u2581','')
  if p: out.append(p)
 return out or [w]
tp=fp=fn=tokn=single=0
for r in G:
 g=bd(r['segments']); p=pred(r['word']); q=bd(p)
 tp+=len(g&q); fp+=len(q-g); fn+=len(g-q); tokn+=len(p); single+=(len(p)==1 and len(r['segments'])>1)
P=tp/max(tp+fp,1); R=tp/max(tp+fn,1); F=2*P*R/max(P+R,1e-12)
res={'cases':len(G),'P':round(P,4),'R':round(R,4),'F1':round(F,4),'tok':round(tokn/len(G),4),'single':round(100*single/len(G),2)}
(B/'q1_morpheus804_baseline.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
