import sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer.segmentation import turkish_lower, _v21_match_root
from nedo_turkish_tokenizer.resources import load_tdk_words
from nedo_turkish_tokenizer._domain_vocab import ALL_DOMAIN_ROOTS
from nedo_turkish_tokenizer._suffix_table import SUFFIX_ENTRIES
w=turkish_lower('edeceğim')
with open('reports/full_validation_v21/debug_edecegim_inner.txt','w',encoding='utf-8') as f:
 f.write('wl='+w+' repr='+repr(w)+'\n')
 for s,l in SUFFIX_ENTRIES[:50]:
  if 'eceğ' in s or 'ece' in s:
   f.write('entry '+repr(s)+' '+l+' ends='+str(w.endswith(s))+' rem='+repr(w[:-len(s)] if w.endswith(s) else '')+' match='+repr(_v21_match_root(w[:-len(s)],load_tdk_words(),ALL_DOMAIN_ROOTS) if w.endswith(s) else None)+'\n')
