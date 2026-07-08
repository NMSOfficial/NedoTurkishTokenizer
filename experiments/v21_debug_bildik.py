import sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer.segmentation import generate_candidates, select_best_candidate, _v21_labels
from nedo_turkish_tokenizer.resources import load_tdk_words
from nedo_turkish_tokenizer._domain_vocab import ALL_DOMAIN_ROOTS
w='bildiklerinizden'
cs=generate_candidates(w, load_tdk_words(), ALL_DOMAIN_ROOTS, frozenset())
b=select_best_candidate(cs)
with open('reports/full_validation_v21/debug_bildiklerinizden.txt','w',encoding='utf-8') as f:
    f.write('N '+str(len(cs))+'\n')
    for c in cs[:60]:
        toks=[(t.text,t.token_type,t.metadata.get('_suffix_label'),t.metadata.get('_canonical_root'),t.metadata.get('_root_alternation')) for t in c.tokens]
        f.write(('BEST ' if c is b else '')+str(c.score)+' '+c.source+' '+repr(_v21_labels(c))+' '+repr(toks)+'\n')
