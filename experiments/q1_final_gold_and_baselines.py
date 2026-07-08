import csv, json, pathlib, sys, re, collections, random, os, subprocess, tempfile
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
BASE=pathlib.Path('reports/q1_final'); BASE.mkdir(parents=True, exist_ok=True)
A1='reports/annotation_pack_v1/annotation_items_annotator1.csv'
A2='reports/annotation_pack_v1/annotation_items_annotator2.csv'
ADJ='reports/q1_final/annotation_disagreements_adjudicated.csv'

def normseg(s):
    s=(s or '').strip().replace('＋','+').replace(' + ','+').replace(' ','').strip('+')
    return s

def parts(s):
    return [x for x in normseg(s).split('+') if x]

def labels(s):
    s=(s or '').strip().upper().replace(';',',').replace('+',',')
    return [x.strip().lstrip('-') for x in s.split(',') if x.strip()]

def bounds(ps):
    b=set(); n=0
    for x in ps[:-1]:
        n+=len(x); b.add(n)
    return b

def read(fn):
    out={}
    with open(fn,encoding='utf-8-sig',errors='ignore',newline='') as f:
        for r in csv.DictReader(f):
            rid=str(r.get('id','')).strip()
            if rid: out[rid]=r
    return out

a1=read(A1); a2=read(A2); adj=read(ADJ) if pathlib.Path(ADJ).exists() else {}
ids=sorted(set(a1)&set(a2), key=lambda x:int(x) if x.isdigit() else x)
final=[]; src=collections.Counter()
for rid in ids:
    r1=a1[rid]; r2=a2[rid]
    w=(r1.get('word') or r2.get('word') or '').strip()
    p1=parts(r1.get('annotator_segments','')); p2=parts(r2.get('annotator_segments',''))
    l1=labels(r1.get('annotator_labels','')); l2=labels(r2.get('annotator_labels',''))
    use_p=[]; use_l=[]; origin=''
    ar=adj.get(rid)
    if ar and parts(ar.get('final_segments','')):
        use_p=parts(ar.get('final_segments','')); use_l=labels(ar.get('final_labels','')); origin='adjudicated'
    elif bounds(p1)==bounds(p2) and p1:
        use_p=p1; use_l=l1 if l1==l2 else []; origin='annotator_agreed'
    elif p1:
        use_p=p1; use_l=l1; origin='fallback_a1'
    else:
        continue
                                                                                    
    if ''.join(use_p).lower() != w.lower():
        src['bad_reconstruction_skipped']+=1
        continue
    src[origin]+=1
    final.append({'id':rid,'word':w,'segments':use_p,'labels':use_l,'origin':origin})

def pred_nedo(w):
    toks=T(w)
    ps=[str(t.get('token','')).strip() for t in toks if str(t.get('token','')).strip() and str(t.get('token_type'))!='PUNCT']
    labs=[]
    for t in toks:
        if str(t.get('token_type'))=='SUFFIX':
            lab=str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
            if lab: labs.append(lab)
    return ps,labs

def pred_whole(w): return [w], []
def pred_char(w): return list(w), []

def metrics(predictor, rows):
    C=collections.Counter(); examples=[]
    for r in rows:
        w=r['word']; gold=r['segments']; glabs=r.get('labels') or []
        pred, plabs=predictor(w)
        gb,pb=bounds(gold),bounds(pred)
        C['tp']+=len(gb&pb); C['fp']+=len(pb-gb); C['fn']+=len(gb-pb); C['cases']+=1; C['tokens']+=len(pred)
        C['single']+=(len(pred)==1 and len(gold)>1)
        if glabs:
            cc=collections.Counter(plabs); h=0
            for x in glabs:
                if cc[x]>0: cc[x]-=1; h+=1
            C['lhit']+=h; C['lgold']+=len(glabs); C['lpred']+=len(plabs)
        if len(examples)<20 and (gb!=pb):
            examples.append({'word':w,'gold':'+'.join(gold),'pred':'+'.join(pred)})
    P=C['tp']/max(C['tp']+C['fp'],1); R=C['tp']/max(C['tp']+C['fn'],1); F=2*P*R/max(P+R,1e-12)
    return {'cases':C['cases'],'boundary_precision':round(P,4),'boundary_recall':round(R,4),'boundary_f1':round(F,4),'avg_tokens_per_word':round(C['tokens']/max(C['cases'],1),4),'single_root_pct':round(100*C['single']/max(C['cases'],1),2),'label_precision':round(C['lhit']/max(C['lpred'],1),4),'label_recall':round(C['lhit']/max(C['lgold'],1),4),'label_gold_items':C['lgold'],'examples':examples}

results={'gold_summary':{'rows':len(final),'source_counts':dict(src)}}
results['whole_word']=metrics(pred_whole, final)
results['character']=metrics(pred_char, final)
results['nedo']=metrics(pred_nedo, final)
(BASE/'final_gold_1000.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in final),encoding='utf-8')
(BASE/'q1_final_baselines_partial.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
