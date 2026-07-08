import sys,json,time,pathlib
sys.path.insert(0,'.')
sys.path.insert(0,'experiments')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
import article_clean_eval as ce
T=NedoTurkishTokenizer()
def norm(o): return json.dumps(o,ensure_ascii=False,sort_keys=True)
words=[w for w,_,_,_ in ce.CASES]
t0=time.perf_counter(); base=[norm(T(w)) for w in words]; bad=[]
for _ in range(5):
    now=[norm(T(w)) for w in words]
    for w,a,b in zip(words,base,now):
        if a!=b: bad.append(w)
sec=time.perf_counter()-t0
special=[('https://example.com/test?a=1','URL'),('www.example.org','URL'),('site.com/test','URL'),('@kullanici','MENTION'),('#Türkçe','HASHTAG'),('H200','ACRONYM'),('%92.64','NUM'),('12:30','NUM')]
rows=[]
for text,typ in special:
    out=T(text); ok=any(x.get('token_type')==typ and str(x.get('token','')).strip()==text for x in out)
    rows.append({'text':text,'expected':typ,'ok':ok,'tokens':[(str(x.get('token','')).strip(),x.get('token_type')) for x in out]})
res={'determinism':{'cases':len(words),'repetitions':5,'mismatches':len(bad),'seconds':round(sec,4),'cases_per_sec':round(len(words)*6/max(sec,1e-9),2)},'special_spans':{'cases':len(rows),'ok':sum(r['ok'] for r in rows),'fail':sum(not r['ok'] for r in rows),'rows':rows}}
print(json.dumps(res,ensure_ascii=False,indent=2))
