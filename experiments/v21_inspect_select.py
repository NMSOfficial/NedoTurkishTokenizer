import sys, inspect
sys.path.insert(0,'.')
import nedo_turkish_tokenizer.segmentation as s
with open('reports/quality_v21/select_source_tail.txt','w',encoding='utf-8') as f:
    f.write(inspect.getsource(s.select_best_candidate))
    f.write('\nPICK\n')
    f.write(inspect.getsource(s._v21_pick_chain))
