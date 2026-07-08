import sys,json,pathlib
sys.path.insert(0,'.'); sys.path.insert(0,'experiments')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
import article_clean_eval as ce
T=NedoTurkishTokenizer()
texts=[w for w,_,_,_ in ce.CASES]+['https://example.com/test?a=1','www.example.org','site.com/test','@kullanici','#Türkçe','H200','%92.64','12:30']
bad=[]
for x in texts:
    y=''.join(str(t.get('token','')).strip() for t in T(x))
    if y!=x:
        bad.append((x,y))
res={'cases':len(texts),'exact_surface_reconstruction':len(texts)-len(bad),'mismatches':len(bad),'bad':bad[:10]}
pathlib.Path('reports/article_extra/clean_reversibility.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
