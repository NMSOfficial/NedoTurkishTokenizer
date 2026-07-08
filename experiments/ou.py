import sys,json,collections
sys.path.insert(0,'.'); sys.path.insert(0,'experiments')
import article_clean_eval as ce
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer(); C=collections.Counter()
def tk(t): return str(t.get('token','')).strip()
for w,segs,labels,grp in ce.CASES:
 o=T(w); toks=[tk(t) for t in o if tk(t) and tk(t)!="'"]
 b=set(); n=0
 for x in toks[:-1]: n+=len(x); b.add(n)
 g=ce.gold_boundaries(segs)
 C['cases']+=1; C['over']+=bool(b-g); C['under']+=bool(g-b); C['single']+=(len(o)==1 and o[0].get('token_type')=='ROOT' and len(segs)>1)
 C['tp']+=len(b&g); C['fp']+=len(b-g); C['fn']+=len(g-b)
p=C['tp']/max(C['tp']+C['fp'],1); r=C['tp']/max(C['tp']+C['fn'],1); f=2*p*r/max(p+r,1e-9)
print(json.dumps({'cases':C['cases'],'boundary_p':round(p,4),'boundary_r':round(r,4),'boundary_f1':round(f,4),'over_seg_pct':round(100*C['over']/C['cases'],2),'under_seg_pct':round(100*C['under']/C['cases'],2),'single_root_pct':round(100*C['single']/C['cases'],2)}))
