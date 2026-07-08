import os, sys, json
sys.path.insert(0, os.environ['TOKENIZER_PATH'])
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
words=json.loads(open(sys.argv[1],encoding='utf-8').read())
rows=[]
for w in words:
    out=T(w)
    rows.append({'word':w,'n':len(out),'single_root':len(out)==1 and out[0].get('token_type')=='ROOT','tokens':[(d.get('token','').strip(),d.get('token_type'),d.get('morph_pos'),d.get('_canonical')) for d in out]})
print(json.dumps(rows,ensure_ascii=False))
