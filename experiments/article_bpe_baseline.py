import json, re, pathlib, collections, statistics, sys
sys.path.insert(0,'.')
import article_gold_eval as ge
WORD_RE=re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]{2,}")
TF=pathlib.Path('/arf/scratch/egitimg16u1/turkformer')
paths=[TF/'data/raw/nedo_balanced_source_audit/sample.jsonl',TF/'data/raw/turkish_smoke/turkish_smoke.jsonl',TF/'data/raw/nedo_final_sample_audit/sample.jsonl']

def corpus_words(max_words=20000):
    out=[]
    for p in paths:
        if not p.exists(): continue
        with p.open(encoding='utf-8',errors='ignore') as f:
            for line in f:
                try:
                    o=json.loads(line); text=o.get('text') or o.get('content') or ''
                except Exception:
                    text=line
                for w in WORD_RE.findall(text.lower()):
                    out.append(w)
                    if len(out)>=max_words: return out
    return out

def train_bpe(words, merges_n=500):
    vocab=collections.Counter(tuple(w)+('</w>',) for w in words)
    merges=[]
    for _ in range(merges_n):
        pairs=collections.Counter()
        for seq,c in vocab.items():
            for a,b in zip(seq,seq[1:]): pairs[(a,b)] += c
        if not pairs: break
        best, count=pairs.most_common(1)[0]
        if count < 2: break
        merges.append(best); new=collections.Counter(); big=''.join(best)
        for seq,c in vocab.items():
            res=[]; i=0
            while i<len(seq):
                if i<len(seq)-1 and (seq[i],seq[i+1])==best:
                    res.append(big); i+=2
                else:
                    res.append(seq[i]); i+=1
            new[tuple(res)] += c
        vocab=new
    return merges

def apply_bpe(word, merges):
    seq=list(word)+['</w>']
    for pair in merges:
        big=''.join(pair); res=[]; i=0
        while i<len(seq):
            if i<len(seq)-1 and (seq[i],seq[i+1])==pair:
                res.append(big); i+=2
            else:
                res.append(seq[i]); i+=1
        seq=res
    toks=[]
    for x in seq:
        x=x.replace('</w>','')
        if x: toks.append(x)
    return toks

def main():
    words=corpus_words()
    merges=train_bpe(words, merges_n=500)
    rows=[]
    for c in ge.CASES:
        toks=apply_bpe(c['word'].lower(),merges)
        rows.append([{'token':t,'token_type':'BPE','morph_pos':0} for t in toks])
    res=ge.eval_tokens('CorpusBPE_500merge', rows)
    res['training_words']=len(words); res['merges']=len(merges)
    pathlib.Path('reports/article_extra/gold_eval_bpe.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(res['summary'],ensure_ascii=False))
if __name__=='__main__': main()
