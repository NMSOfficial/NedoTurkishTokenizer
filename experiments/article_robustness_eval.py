import sys,json,pathlib,hashlib,time,collections,random
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
import article_gold_eval as ge
T=NedoTurkishTokenizer()

def norm(o):
    return json.dumps(o,ensure_ascii=False,sort_keys=True)

cases=[c['word'] for c in ge.CASES]
                                        
bad=[]
t0=time.perf_counter()
base=[norm(T(w)) for w in cases]
for r in range(5):
    now=[norm(T(w)) for w in cases]
    for w,a,b in zip(cases,base,now):
        if a!=b and len(bad)<10: bad.append(w)
sec=time.perf_counter()-t0
                           
special=[
    ('https://example.com/test?a=1','URL'),('www.example.org','URL'),('site.com/test','URL'),
    ('@kullanici','MENTION'),('#Türkçe','HASHTAG'),('H200','ACRONYM'),('%92.64','NUM'),('12:30','NUM')]
srows=[]
for text,typ in special:
    out=T(text); ok=any(x.get('token_type')==typ for x in out)
    srows.append({'text':text,'expected':typ,'ok':ok,'tokens':[(x.get('token','').strip(),x.get('token_type')) for x in out]})
res={'determinism':{'cases':len(cases),'repetitions':5,'mismatches':len(bad),'seconds':round(sec,4),'cases_per_sec':round(len(cases)*6/max(sec,1e-9),2)},'special_spans':{'cases':len(srows),'ok':sum(x['ok'] for x in srows),'fail':sum(not x['ok'] for x in srows),'rows':srows}}
pathlib.Path('reports/article_extra/robustness_eval.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
