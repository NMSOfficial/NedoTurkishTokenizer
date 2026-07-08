import json, re, time, pathlib, sys, collections, statistics
sys.path.insert(0, '/arf/scratch/egitimg16u1/nedoturkishtokenizer')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
TOK=NedoTurkishTokenizer()
TF=pathlib.Path('/arf/scratch/egitimg16u1/turkformer')
OUT=pathlib.Path('reports/full_validation_v21'); OUT.mkdir(parents=True, exist_ok=True)
WORD_RE=re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü']{2,}")
TARGET=('lerinden','larından','lerimizden','larımızdan','lerimizin','larımızın','lerimiz','larımız','abileceklerinden','ebileceklerinden','abileceklerimizden','ebileceklerimizden','eceğiz','acağız','yeceğiz','yacağız','acaklar','ecekler','mayacağız','meyeceğiz','diklerimizden','dıklarımızdan','dakilerden','dekilerden','acağım','eceğim','acaksınız','eceksiniz')
paths=[TF/'data/raw/nedo_final_sample_audit/sample.jsonl',TF/'data/raw/nedo_balanced_source_audit/sample.jsonl',TF/'data/raw/turkish_smoke/turkish_smoke.jsonl',TF/'data/raw/real_turkish_medium/real_turkish_medium.jsonl',TF/'data/raw/real_turkish_probe/real_turkish_probe.jsonl']
def texts(max_docs):
 n=0
 for p in paths:
  if not p.exists(): continue
  with p.open(encoding='utf-8',errors='ignore') as f:
   for line in f:
    try:
     o=json.loads(line); text=o.get('text') or o.get('content') or o.get('sentence') or ''
    except Exception:
     text=line
    if text:
     yield text; n+=1
     if n>=max_docs: return
def canon(t): return str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
def simp(out): return [(str(t.get('token','')).strip(), t.get('token_type'), t.get('morph_pos'), canon(t)) for t in out]
st=collections.Counter(); target_bad=[]; long_bad=[]; tok_counts=[]; suff_counts=[]; t0=time.perf_counter()
MAX_DOCS=50000; MAX_WORDS=500000
for text in texts(MAX_DOCS):
 st['docs']+=1; st['doc_tokens']+=len(TOK(text))
 for w in WORD_RE.findall(text):
  if st['words']>=MAX_WORDS: break
  lw=w.lower().strip("'")
  out=TOK(w); st['words']+=1
  tok_counts.append(len(out)); suff_counts.append(sum(1 for x in out if x.get('token_type')=='SUFFIX'))
  if len(lw)>=10:
   st['long_words']+=1
   if len(out)==1 and out[0].get('token_type')=='ROOT':
    st['long_single_root']+=1
    if len(long_bad)<40: long_bad.append({'word':w,'tokens':simp(out)})
  if any(lw.endswith(s) for s in TARGET):
   st['target_suffix_words']+=1
   if len(out)==1 and out[0].get('token_type')=='ROOT':
    st['target_single_root']+=1
    if len(target_bad)<50: target_bad.append({'word':w,'tokens':simp(out)})
 if st['words']>=MAX_WORDS: break
sec=max(time.perf_counter()-t0,1e-9)
rates={'long_single_root_pct':round(100*st['long_single_root']/max(st['long_words'],1),4),'target_single_root_pct':round(100*st['target_single_root']/max(st['target_suffix_words'],1),4),'avg_tokens_per_word':round(statistics.mean(tok_counts),4),'avg_suffix_per_word':round(statistics.mean(suff_counts),4),'docs_per_sec':round(st['docs']/sec,2),'words_per_sec':round(st['words']/sec,2)}
res={'stats':dict(st),'rates':rates,'seconds':round(sec,3),'target_bad_examples':target_bad,'long_bad_examples':long_bad}
(OUT/'large_real_audit.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'stats':dict(st),'rates':rates,'seconds':round(sec,3)},ensure_ascii=False))
