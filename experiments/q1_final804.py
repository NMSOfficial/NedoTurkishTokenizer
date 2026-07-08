import csv,json,pathlib,collections,sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer(); B=pathlib.Path('reports/q1_final')
def read(fn):
 d={}
 with open(fn,encoding='utf-8-sig',errors='ignore',newline='') as f:
  for r in csv.DictReader(f):
   if r.get('id'): d[str(r['id']).strip()]=r
 return d
def parts(s): return [x for x in (s or '').strip().replace(' ','').strip('+').split('+') if x]
def labs(s): return [x.strip().lstrip('-').upper() for x in (s or '').replace(';',',').replace('+',',').split(',') if x.strip()]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
def metric(rows,pred):
 C=collections.Counter()
 for r in rows:
  p,pl=pred(r['word']); g=bd(r['segments']); q=bd(p)
  C['tp']+=len(g&q); C['fp']+=len(q-g); C['fn']+=len(g-q); C['tok']+=len(p); C['cases']+=1; C['single']+=(len(p)==1 and len(r['segments'])>1)
  if r['labels']:
   cc=collections.Counter(pl); h=0
   for x in r['labels']:
    if cc[x]>0: cc[x]-=1; h+=1
   C['lh']+=h; C['lg']+=len(r['labels']); C['lp']+=len(pl)
 P=C['tp']/max(C['tp']+C['fp'],1); R=C['tp']/max(C['tp']+C['fn'],1); F=2*P*R/max(P+R,1e-12)
 return {'cases':C['cases'],'P':round(P,4),'R':round(R,4),'F1':round(F,4),'tok':round(C['tok']/C['cases'],4),'single':round(100*C['single']/C['cases'],2),'LP':round(C['lh']/max(C['lp'],1),4),'LR':round(C['lh']/max(C['lg'],1),4)}
a1=read('reports/annotation_pack_v1/annotation_items_annotator1.csv'); a2=read('reports/annotation_pack_v1/annotation_items_annotator2.csv'); adj=read('reports/q1_final/annotation_disagreements_adjudicated.csv')
rows=[]; src=collections.Counter()
for rid in sorted(set(a1)&set(a2), key=lambda x:int(x)):
 w=a1[rid].get('word','').strip(); p1=parts(a1[rid].get('annotator_segments','')); p2=parts(a2[rid].get('annotator_segments',''))
 if rid in adj and parts(adj[rid].get('final_segments','')):
  ps=parts(adj[rid].get('final_segments','')); ls=labs(adj[rid].get('final_labels','')); origin='adjudicated'
 elif bd(p1)==bd(p2) and p1:
  ps=p1; l1=labs(a1[rid].get('annotator_labels','')); l2=labs(a2[rid].get('annotator_labels','')); ls=l1 if l1==l2 else []; origin='agreed'
 else:
  continue
 if ''.join(ps).lower()==w.lower(): rows.append({'id':rid,'word':w,'segments':ps,'labels':ls,'origin':origin}); src[origin]+=1

def nedo(w):
 o=T(w); ps=[str(t.get('token','')).strip() for t in o if str(t.get('token_type'))!='PUNCT' and str(t.get('token','')).strip()]
 ls=[]
 for t in o:
  if str(t.get('token_type'))=='SUFFIX':
   z=str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
   if z: ls.append(z)
 return ps,ls
res={'rows':len(rows),'source_counts':dict(src),'whole':metric(rows,lambda w:([w],[])),'char':metric(rows,lambda w:(list(w),[])),'nedo':metric(rows,nedo)}
(B/'final_gold_804.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows),encoding='utf-8')
(B/'q1_final804_metrics.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
