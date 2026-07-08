import csv,json,pathlib,collections,sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer(); OUT=pathlib.Path('reports/q1_worldclass_final'); OUT.mkdir(parents=True,exist_ok=True)
def read(fn):
 with open(fn,encoding='utf-8-sig',errors='ignore',newline='') as f:
  return {str(r.get('id','')).strip():r for r in csv.DictReader(f) if str(r.get('id','')).strip()}
def parts(s): return [x for x in (s or '').strip().replace(' ','').strip('+').split('+') if x]
def labs(s): return [x.strip().lstrip('-').upper() for x in (s or '').replace(';',',').replace('+',',').split(',') if x.strip()]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
a1=read('reports/annotation_pack_v1/annotation_items_annotator1.csv'); a2=read('reports/annotation_pack_v1/annotation_items_annotator2.csv')
adj=read('reports/q1_final/annotation_disagreements_adjudicated.csv'); done=read('reports/q1_worldclass/missing_adjudication_done.csv')
rows=[]; src=collections.Counter(); bad=[]
for rid in sorted(set(a1)&set(a2), key=lambda x:int(x)):
 w=(a1[rid].get('word') or a2[rid].get('word') or '').strip(); p1=parts(a1[rid].get('annotator_segments','')); p2=parts(a2[rid].get('annotator_segments',''))
 if rid in done and parts(done[rid].get('final_segments','')):
  ps=parts(done[rid].get('final_segments','')); ls=labs(done[rid].get('final_labels','')); origin='adjudicated_new'
 elif rid in adj and parts(adj[rid].get('final_segments','')):
  ps=parts(adj[rid].get('final_segments','')); ls=labs(adj[rid].get('final_labels','')); origin='adjudicated_old'
 elif bd(p1)==bd(p2) and p1:
  ps=p1; l1=labs(a1[rid].get('annotator_labels','')); l2=labs(a2[rid].get('annotator_labels','')); ls=l1 if l1==l2 else []; origin='annotator_agreed'
 else:
  bad.append({'id':rid,'word':w,'reason':'unresolved'}); continue
 if ''.join(ps).lower()!=w.lower(): bad.append({'id':rid,'word':w,'seg':'+'.join(ps),'reason':'surface_mismatch'}); continue
 rows.append({'id':rid,'word':w,'segments':ps,'labels':ls,'origin':origin}); src[origin]+=1
(OUT/'full_gold_1000.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows),encoding='utf-8')
(OUT/'full_gold_build_issues.json').write_text(json.dumps({'rows':len(rows),'source_counts':dict(src),'bad':bad[:50],'bad_count':len(bad)},ensure_ascii=False,indent=2),encoding='utf-8')
def metric(pred):
 c=collections.Counter()
 for r in rows:
  ps,ls=pred(r['word']); g=bd(r['segments']); p=bd(ps); gl=r.get('labels') or []
  c['tp']+=len(g&p); c['fp']+=len(p-g); c['fn']+=len(g-p); c['tok']+=len(ps); c['cases']+=1; c['single']+=(len(ps)==1 and len(r['segments'])>1); c['exact']+=(g==p); c['over']+=bool(p-g); c['under']+=bool(g-p)
  if gl:
   cc=collections.Counter(ls)
   for x in gl:
    if cc[x]>0: cc[x]-=1; c['lh']+=1
   c['lg']+=len(gl); c['lp']+=len(ls)
 P=c['tp']/max(c['tp']+c['fp'],1); R=c['tp']/max(c['tp']+c['fn'],1); F=2*P*R/max(P+R,1e-12)
 return {'cases':c['cases'],'P':round(P,4),'R':round(R,4),'F1':round(F,4),'avg_tok':round(c['tok']/c['cases'],4),'single_pct':round(100*c['single']/c['cases'],2),'exact_pct':round(100*c['exact']/c['cases'],2),'over_pct':round(100*c['over']/c['cases'],2),'under_pct':round(100*c['under']/c['cases'],2),'LP':round(c['lh']/max(c['lp'],1),4),'LR':round(c['lh']/max(c['lg'],1),4)}
def nedo(w):
 out=T(w); ps=[]; ls=[]
 for t in out:
  if str(t.get('token_type'))!='PUNCT' and str(t.get('token','')).strip(): ps.append(str(t.get('token','')).strip())
  if str(t.get('token_type'))=='SUFFIX':
   z=str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
   if z: ls.append(z)
 return ps,ls
res={'gold':{'rows':len(rows),'source_counts':dict(src),'bad_count':len(bad)},'nedo':metric(nedo),'whole':metric(lambda w:([w],[])),'char':metric(lambda w:(list(w),[]))}
(OUT/'final1000_nedo_metrics.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
