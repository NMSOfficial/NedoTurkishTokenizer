import sys,json,importlib,os
sys.path.insert(0,'.'); sys.path.insert(0,'experiments')
import article_clean_eval as ce
from nedo_turkish_tokenizer import NedoTurkishTokenizer
import nedo_turkish_tokenizer.segmentation as sg

def run(name):
 T=NedoTurkishTokenizer(); rows=[T(w) for w,_,_,_ in ce.CASES]
 r=ce.eval_rows(name, rows)['summary']
 return {'variant':name,'boundary_f1':r['boundary_f1'],'label_recall':r['label_recall'],'single_root_pct':r['single_root_pct']}
res=[]
res.append(run('full'))
sg._v211_pick_chain=lambda c: None
res.append(run('no_chain_priority'))
importlib.reload(sg)
sg._MAX_SUFFIX_DEPTH=5
res.append(run('max_depth_5'))
importlib.reload(sg)
sg._SHORT_ROOT_PENALTY=0
res.append(run('no_short_root_penalty'))
importlib.reload(sg)
sg._DOMAIN_BONUS=0
res.append(run('no_domain_bonus'))
open('reports/article_extra/clean_ablation.json','w',encoding='utf-8').write(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False))
