import json,re,sys,time,pathlib
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
WORD_RE=re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü0-9_./%-]{2,}")
paths=[
'/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_balanced_source_audit/sample.jsonl',
'/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_final_sample_audit/sample.jsonl',
'/arf/scratch/egitimg16u1/turkformer/data/raw/turkish_smoke/turkish_smoke.jsonl']
words=[]
for p in paths:
    pp=pathlib.Path(p)
    if not pp.exists():
        continue
    with pp.open(encoding='utf-8',errors='ignore') as f:
        for line in f:
            try:
                obj=json.loads(line); txt=obj.get('text') or obj.get('content') or ''
            except Exception:
                txt=line
            for w in WORD_RE.findall(txt):
                words.append(w)
                if len(words)>=20000: break
            if len(words)>=20000: break
    if len(words)>=20000: break
bad=[]; t0=time.time()
for w in words:
    out=T(w)
    recon=''.join(str(x.get('token','')).strip() for x in out)
    if recon!=w and len(bad)<30:
        bad.append({'word':w,'reconstructed':recon,'tokens':[(str(x.get('token','')).strip(),x.get('token_type')) for x in out]})
res={'cases':len(words),'exact_reconstruction':len(words)-sum(1 for w in words if ''.join(str(x.get('token','')).strip() for x in T(w))!=w),'mismatch_examples':bad,'seconds':round(time.time()-t0,3)}
pathlib.Path('reports/article_extra/extra_surface_20k.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':res['cases'],'exact_reconstruction':res['exact_reconstruction'],'mismatches':res['cases']-res['exact_reconstruction'],'seconds':res['seconds']},ensure_ascii=False))
