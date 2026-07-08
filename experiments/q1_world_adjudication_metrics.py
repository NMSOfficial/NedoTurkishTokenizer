import csv,json,pathlib,collections,random,sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
OUT=pathlib.Path('reports/q1_worldclass'); OUT.mkdir(parents=True,exist_ok=True)
def parts(s): return [x for x in (s or '').strip().replace(' ','').strip('+').split('+') if x]
def labs(s): return [x.strip().lstrip('-').upper() for x in (s or '').replace(';',',').replace('+',',').split(',') if x.strip()]
def bd(a):
 b=set(); n=0
 for x in a[:-1]: n+=len(x); b.add(n)
 return b
def read(fn):
 with open(fn,encoding='utf-8-sig',errors='ignore',newline='') as f: return {str(r.get('id','')).strip():r for r in csv.DictReader(f) if str(r.get('id','')).strip()}
a1=read('reports/annotation_pack_v1/annotation_items_annotator1.csv'); a2=read('reports/annotation_pack_v1/annotation_items_annotator2.csv'); adj=read('reports/q1_final/annotation_disagreements_adjudicated.csv')
rows=[]; miss=[]; agreed=adjdone=0
for rid in sorted(set(a1)&set(a2), key=lambda x:int(x)):
 w=(a1[rid].get('word') or a2[rid].get('word') or '').strip(); p1=parts(a1[rid].get('annotator_segments','')); p2=parts(a2[rid].get('annotator_segments',''))
 if bd(p1)==bd(p2) and p1: agreed+=1
 else:
  item={'id':rid,'word':w,'a1':'+'.join(p1),'a2':'+'.join(p2),'final_segments':'','final_labels':''}
  if rid in adj and parts(adj[rid].get('final_segments','')):
   item['final_segments']=adj[rid].get('final_segments',''); item['final_labels']=adj[rid].get('final_labels',''); adjdone+=1
  else: miss.append(item)
  rows.append(item)
with (OUT/'all_boundary_disagreements.csv').open('w',encoding='utf-8',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=['id','word','a1','a2','final_segments','final_labels']); wr.writeheader(); wr.writerows(rows)
with (OUT/'missing_adjudication.csv').open('w',encoding='utf-8',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=['id','word','a1','a2','final_segments','final_labels']); wr.writeheader(); wr.writerows(miss)
G=[json.loads(x) for x in pathlib.Path('reports/q1_final/final_gold_804.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def pred(w):
 out=T(w); ps=[]; ls=[]
 for t in out:
  if str(t.get('token_type'))!='PUNCT':
   s=str(t.get('token','')).strip()
   if s: ps.append(s)
  if str(t.get('token_type'))=='SUFFIX':
   z=str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
   if z: ls.append(z)
 return ps,ls
def counts(sub):
 c=collections.Counter()
 for r in sub:
  ps,ls=pred(r['word']); g=r['segments']; gl=r.get('labels') or []
  gb,pb=bd(g),bd(ps)
  c['tp']+=len(gb&pb); c['fp']+=len(pb-gb); c['fn']+=len(gb-pb); c['tok']+=len(ps); c['single']+=(len(ps)==1 and len(g)>1); c['over']+=bool(pb-gb); c['under']+=bool(gb-pb); c['exact']+=(gb==pb); c['cases']+=1
  if gl:
   cc=collections.Counter(ls)
   for x in gl:
    if cc[x]>0: cc[x]-=1; c['lh']+=1
   c['lg']+=len(gl); c['lp']+=len(ls)
 p=c['tp']/max(c['tp']+c['fp'],1); r=c['tp']/max(c['tp']+c['fn'],1); f=2*p*r/max(p+r,1e-12)
 return {'cases':c['cases'],'P':round(p,4),'R':round(r,4),'F1':round(f,4),'avg_tok':round(c['tok']/c['cases'],4),'single_pct':round(100*c['single']/c['cases'],2),'over_pct':round(100*c['over']/c['cases'],2),'under_pct':round(100*c['under']/c['cases'],2),'exact_pct':round(100*c['exact']/c['cases'],2),'LP':round(c['lh']/max(c['lp'],1),4),'LR':round(c['lh']/max(c['lg'],1),4)}
main=counts(G)
rnd=random.Random(13); vals=[]
for _ in range(1000): vals.append(counts([G[rnd.randrange(len(G))] for __ in range(len(G))])['F1'])
vals.sort(); ci=[vals[25],vals[500],vals[974]]
bins={'short_lt10':counts([r for r in G if len(r['word'])<10]),'long_ge10':counts([r for r in G if len(r['word'])>=10]),'no_boundary':counts([r for r in G if len(bd(r['segments']))==0]),'one_boundary':counts([r for r in G if len(bd(r['segments']))==1]),'multi_boundary':counts([r for r in G if len(bd(r['segments']))>=2])}
res={'adjudication':{'total':1000,'agreed_boundary':agreed,'disagreements_total':len(rows),'adjudicated_done':adjdone,'missing_adjudication':len(miss),'secure_gold':len(G)},'nedo804':main,'f1_ci_95':ci,'bins':bins}
(OUT/'world_adjudication_metrics.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
