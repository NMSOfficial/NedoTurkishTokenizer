import csv, json, pathlib, sys, collections, re
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
A1='reports/annotation_pack_v1/annotation_items_annotator1.csv'
A2='reports/annotation_pack_v1/annotation_items_annotator2.csv'
OUT=pathlib.Path('reports/q1_final'); OUT.mkdir(parents=True, exist_ok=True)

def normseg(s):
    s=(s or '').strip()
    s=s.replace('＋','+').replace(' + ','+').replace(' ','')
    s=s.strip('+')
    return s

def parts(s):
    s=normseg(s)
    return [x for x in s.split('+') if x]

def labels(s):
    s=(s or '').strip().upper().replace(';',',').replace('+',',')
    return [x.strip().lstrip('-') for x in s.split(',') if x.strip()]

def bounds(ps):
    b=set(); n=0
    for x in ps[:-1]:
        n+=len(x); b.add(n)
    return b

def f1_counts(g,p):
    tp=len(g&p); fp=len(p-g); fn=len(g-p)
    return tp,fp,fn

def load(fn):
    d={}
    with open(fn,encoding='utf-8-sig',errors='ignore',newline='') as f:
        r=csv.DictReader(f)
        for row in r:
            rid=str(row.get('id','')).strip()
            if rid:
                d[rid]=row
    return d

def pred_word(w):
    toks=T(w)
    ps=[str(t.get('token','')).strip() for t in toks if str(t.get('token','')).strip() and str(t.get('token_type'))!='PUNCT']
    labs=[]
    for t in toks:
        if str(t.get('token_type'))=='SUFFIX':
            lab=str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
            if lab: labs.append(lab)
    return ps,labs

def m(tp,fp,fn):
    p=tp/max(tp+fp,1); r=tp/max(tp+fn,1); f=2*p*r/max(p+r,1e-12)
    return round(p,4),round(r,4),round(f,4)

def multihit(gold,pred):
    c=collections.Counter(pred); h=0
    for x in gold:
        if c[x]>0:
            c[x]-=1; h+=1
    return h

a1=load(A1); a2=load(A2); ids=sorted(set(a1)&set(a2), key=lambda x:int(x) if x.isdigit() else x)
rows=[]; C=collections.Counter(); A=collections.Counter(); N=collections.Counter(); L=collections.Counter()
by_len=collections.defaultdict(collections.Counter)
dis=[]
for rid in ids:
    r1=a1[rid]; r2=a2[rid]
    w=(r1.get('word') or r2.get('word') or '').strip()
    p1=parts(r1.get('annotator_segments','')); p2=parts(r2.get('annotator_segments',''))
    l1=labels(r1.get('annotator_labels','')); l2=labels(r2.get('annotator_labels',''))
    if not p1 or not p2:
        C['missing']+=1; continue
    C['covered']+=1
    b1,b2=bounds(p1),bounds(p2)
    tp,fp,fn=f1_counts(b1,b2); A['tp']+=tp; A['fp']+=fp; A['fn']+=fn
    if normseg(r1.get('annotator_segments',''))==normseg(r2.get('annotator_segments','')): C['exact_seg_agree']+=1
    if l1 and l2:
        lh=multihit(l1,l2); L['label_hits']+=lh; L['label_gold']+=len(l1); L['label_pred']+=len(l2)
        if l1==l2: C['exact_label_agree']+=1
    if b1==b2:
        C['boundary_set_agree']+=1
                                                                       
        gold=p1
        pred,labs_pred=pred_word(w)
        gb,pb=bounds(gold),bounds(pred)
        tp,fp,fn=f1_counts(gb,pb); N['tp']+=tp; N['fp']+=fp; N['fn']+=fn
        N['cases']+=1; N['tokens']+=len(pred); N['single_root']+=(len(pred)==1 and len(gold)>1)
                                                                                                
        if l1 and l1==l2:
            h=multihit(l1,labs_pred); N['label_hits']+=h; N['label_gold']+=len(l1); N['label_pred']+=len(labs_pred)
        key='long' if len(w)>=10 else 'short'
        by_len[key]['cases']+=1; by_len[key]['tp']+=tp; by_len[key]['fp']+=fp; by_len[key]['fn']+=fn
    else:
        if len(dis)<50:
            dis.append({'id':rid,'word':w,'a1':'+'.join(p1),'a2':'+'.join(p2),'labels1':','.join(l1),'labels2':','.join(l2),'notes1':r1.get('notes',''),'notes2':r2.get('notes','')})

ap,ar,af=m(A['tp'],A['fp'],A['fn'])
np,nr,nf=m(N['tp'],N['fp'],N['fn'])
res={
 'total_rows':len(ids),
 'covered_rows':C['covered'],
 'missing_rows':C['missing'],
 'exact_segmentation_agreement':C['exact_seg_agree'],
 'exact_segmentation_agreement_pct':round(100*C['exact_seg_agree']/max(C['covered'],1),2),
 'boundary_set_agreement':C['boundary_set_agree'],
 'boundary_set_agreement_pct':round(100*C['boundary_set_agree']/max(C['covered'],1),2),
 'inter_annotator_boundary_precision':ap,
 'inter_annotator_boundary_recall':ar,
 'inter_annotator_boundary_f1':af,
 'exact_label_sequence_agreement':C['exact_label_agree'],
 'label_overlap_precision_a2_vs_a1':round(L['label_hits']/max(L['label_pred'],1),4),
 'label_overlap_recall_a2_vs_a1':round(L['label_hits']/max(L['label_gold'],1),4),
 'agreed_boundary_gold_cases':N['cases'],
 'nedo_vs_agreed_boundary_precision':np,
 'nedo_vs_agreed_boundary_recall':nr,
 'nedo_vs_agreed_boundary_f1':nf,
 'nedo_label_precision_on_identical_label_subset':round(N['label_hits']/max(N['label_pred'],1),4),
 'nedo_label_recall_on_identical_label_subset':round(N['label_hits']/max(N['label_gold'],1),4),
 'nedo_single_root_pct_on_agreed':round(100*N['single_root']/max(N['cases'],1),2),
 'nedo_avg_tokens_per_word_on_agreed':round(N['tokens']/max(N['cases'],1),3),
 'by_length':{k:{'cases':v['cases'],'boundary_f1':m(v['tp'],v['fp'],v['fn'])[2]} for k,v in by_len.items()}
}
(OUT/'annotation_eval_summary.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'annotation_disagreements_for_adjudication.csv').open('w',encoding='utf-8',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=['id','word','a1','a2','labels1','labels2','notes1','notes2','final_segments','final_labels','adjudication_notes'])
    wr.writeheader();
    for d in dis:
        d.update({'final_segments':'','final_labels':'','adjudication_notes':''}); wr.writerow(d)
print(json.dumps(res,ensure_ascii=False))
