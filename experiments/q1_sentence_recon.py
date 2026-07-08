import json,pathlib,time,sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer(); OUT=pathlib.Path('reports/q1_worldclass'); OUT.mkdir(parents=True,exist_ok=True)
texts=[]
for p in ['/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_balanced_source_audit/sample.jsonl','/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_final_sample_audit/sample.jsonl']:
 pp=pathlib.Path(p)
 if not pp.exists(): continue
 for line in pp.open(encoding='utf-8',errors='ignore'):
  try: txt=json.loads(line).get('text','')
  except Exception: txt=line
  txt=' '.join(str(txt).split())[:300]
  if txt: texts.append(txt)
  if len(texts)>=1000: break
 if len(texts)>=1000: break
bad=0; t0=time.time()
for txt in texts:
 try: rec=''.join(str(x.get('token','')) for x in T(txt)).strip(); ok=(rec==txt.strip())
 except Exception: ok=False
 bad += (not ok)
res={'cases':len(texts),'exact':len(texts)-bad,'mismatch':bad,'seconds':round(time.time()-t0,3)}
(OUT/'sentence_reconstruction_1000.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
