import sys,json,collections
sys.path.insert(0,'.'); sys.path.insert(0,'experiments')
import article_clean_eval as ce
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer(); S=collections.Counter()
def L(t): return str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
for w,segs,labels,grp in ce.CASES:
 o=T(w); pred=[L(t) for t in o if t.get('token_type')=='SUFFIX' and L(t)]
 c=collections.Counter(pred); h=0
 for x in labels:
  if c[x]>0: c[x]-=1; h+=1
 S['hit']+=h; S['gold']+=len(labels); S['pred']+=len(pred)
print(json.dumps({'label_precision':round(S['hit']/max(S['pred'],1),4),'label_recall':round(S['hit']/max(S['gold'],1),4),'pred_labels':S['pred'],'gold_labels':S['gold']}))
