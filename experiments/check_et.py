import sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer.resources import load_tdk_words
from nedo_turkish_tokenizer._suffix_table import SUFFIX_ENTRIES
words=load_tdk_words()
with open('reports/full_validation_v21/check_et.txt','w') as f:
 f.write('et '+str('et' in words)+'\n')
 f.write('etmek '+str('etmek' in words)+'\n')
 f.write('ecegim_suffix '+str(any(s=='eceğim' for s,l in SUFFIX_ENTRIES))+'\n')
 f.write('suffix_count '+str(len(SUFFIX_ENTRIES))+'\n')
