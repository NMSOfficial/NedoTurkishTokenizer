from __future__ import annotations

import csv
import json
import math
import pathlib
import random
import re
import sys
import time
import traceback
import subprocess
from collections import Counter

ROOT = pathlib.Path('/arf/scratch/egitimg16u1/nedoturkishtokenizer')
OUT = ROOT / 'reports' / 'q1_remaining7'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))


def write_json(name, obj):
    path = OUT / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def safe_run(name, fn):
    t0 = time.time()
    try:
        res = fn()
        res = {'ok': True, 'seconds': round(time.time() - t0, 3), 'result': res}
    except Exception as e:
        res = {'ok': False, 'seconds': round(time.time() - t0, 3), 'error': repr(e), 'traceback': traceback.format_exc()[-6000:]}
    write_json(name + '.json', res)
    return res


                                                    
def patch_lossless_api():
    p = ROOT / 'nedo_turkish_tokenizer' / 'tokenizer.py'
    s = p.read_text(encoding='utf-8')
    changed = False
    if 'import re\n' not in s:
        s = s.replace('import os\nimport multiprocessing\n', 'import os\nimport re\nimport multiprocessing\n')
        changed = True
    if 'def tokenize_lossless' not in s:
        anchor = '''    def tokenize(self, text: str) -> list[dict]:\n        \"\"\"Tokenize a single text string.\n\n        Returns a list of token dicts, each containing at minimum:\n        ``token``, ``token_type``, ``morph_pos``, plus optional\n        ``_*`` metadata fields.\n        \"\"\"\n        return self._engine.tokenize(text)\n\n'''
        insert = '''    def tokenize(self, text: str) -> list[dict]:\n        \"\"\"Tokenize a single text string.\n\n        Returns a list of token dicts, each containing at minimum:\n        ``token``, ``token_type``, ``morph_pos``, plus optional\n        ``_*`` metadata fields.\n        \"\"\"\n        return self._engine.tokenize(text)\n\n    def tokenize_lossless(self, text: str) -> list[dict]:\n        \"\"\"Tokenize text while preserving whitespace as explicit WS tokens.\n\n        The default tokenize API returns clean morphological token text.\n        This method is for exact text roundtrip: whitespace spans are\n        represented by tokens with token_type=\"WS\".\n        \"\"\"\n        if text == \"\":\n            return []\n        out: list[dict] = []\n        for m in re.finditer(r\"\\s+|\\S+\", text):\n            piece = m.group(0)\n            if piece.isspace():\n                out.append({\"token\": piece, \"token_type\": \"WS\", \"morph_pos\": 0, \"_whitespace\": True})\n            else:\n                out.extend(self.tokenize(piece))\n        return out\n\n    def detokenize(self, tokens: list[dict]) -> str:\n        \"\"\"Reconstruct surface text from a lossless token stream.\"\"\"\n        return \"\".join(str(t.get(\"token\", \"\")) for t in tokens)\n\n'''
        if anchor not in s:
            raise RuntimeError('tokenize anchor not found')
        s = s.replace(anchor, insert)
        changed = True
    if changed:
        bak = p.with_suffix('.py.bak_remaining7_' + str(int(time.time())))
        bak.write_text(p.read_text(encoding='utf-8'), encoding='utf-8')
        p.write_text(s, encoding='utf-8')
    subprocess.check_call([sys.executable, '-m', 'py_compile', str(p)])
    return {'patched': changed, 'file': str(p)}


                               
def load_gold(path='reports/q1_final/final_gold_804.jsonl'):
    fp = ROOT / path
    return [json.loads(x) for x in fp.read_text(encoding='utf-8').splitlines() if x.strip()]


def bounds(parts):
    b = set(); n = 0
    for x in parts[:-1]:
        n += len(x); b.add(n)
    return b


def eval_predictions(rows, pred_fn):
    c = Counter()
    for r in rows:
        p, labs = pred_fn(r['word'])
        g = r['segments']; gl = r.get('labels') or []
        gb, pb = bounds(g), bounds(p)
        c['tp'] += len(gb & pb); c['fp'] += len(pb - gb); c['fn'] += len(gb - pb)
        c['tok'] += len(p); c['cases'] += 1
        c['single'] += int(len(p) == 1 and len(g) > 1)
        c['exact'] += int(gb == pb)
        c['over'] += int(bool(pb - gb)); c['under'] += int(bool(gb - pb))
        cc = Counter(labs); hit = 0
        for x in gl:
            if cc[x] > 0:
                cc[x] -= 1; hit += 1
        c['lh'] += hit; c['lg'] += len(gl); c['lp'] += len(labs)
    P = c['tp'] / max(c['tp'] + c['fp'], 1); R = c['tp'] / max(c['tp'] + c['fn'], 1)
    F = 2 * P * R / max(P + R, 1e-12)
    return {'cases': c['cases'], 'P': round(P,4), 'R': round(R,4), 'F1': round(F,4), 'avg_tok': round(c['tok']/max(c['cases'],1),4), 'single_pct': round(100*c['single']/max(c['cases'],1),2), 'exact_pct': round(100*c['exact']/max(c['cases'],1),2), 'over_pct': round(100*c['over']/max(c['cases'],1),2), 'under_pct': round(100*c['under']/max(c['cases'],1),2), 'LP': round(c['lh']/max(c['lp'],1),4), 'LR': round(c['lh']/max(c['lg'],1),4)}


def make_nedo_pred(tok=None):
    if tok is None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        tok = NedoTurkishTokenizer()
    def pred(w):
        out = tok(w); ps = []; labs = []
        for t in out:
            if str(t.get('token_type')) != 'PUNCT':
                s = str(t.get('token','')).strip()
                if s: ps.append(s)
            if str(t.get('token_type')) == 'SUFFIX':
                z = str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
                if z: labs.append(z)
        return ps, labs
    return pred


                                                     
def collect_texts(n=10000):
    files = [
        '/arf/scratch/egitimg16u1/turkformer/data/raw/full_v0/train_raw.jsonl',
        '/arf/scratch/egitimg16u1/turkformer/data/raw/full_v0/valid_raw.jsonl',
        '/arf/scratch/egitimg16u1/turkformer/data/raw/real_turkish_large_v1/real_turkish_large_top80k.jsonl',
        '/arf/scratch/egitimg16u1/turkformer/data/raw/real_turkish_medium_v2/real_turkish_medium_all.jsonl',
        '/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_balanced_source_audit/sample.jsonl',
        '/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_final_sample_audit/sample.jsonl',
    ]
    texts = []
    for f in files:
        fp = pathlib.Path(f)
        if not fp.exists():
            continue
        with fp.open(encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                    txt = obj.get('text') or obj.get('content') or obj.get('raw') or ''
                except Exception:
                    txt = line
                txt = str(txt)
                if txt and txt.strip():
                    texts.append(txt[:1000])
                if len(texts) >= n:
                    return texts
    return texts


def run_roundtrip10k():
    from nedo_turkish_tokenizer import NedoTurkishTokenizer
    tok = NedoTurkishTokenizer()
    if not hasattr(tok, 'tokenize_lossless'):
        raise RuntimeError('tokenize_lossless missing after patch')
    texts = collect_texts(10000)
    bad = 0; examples = []
    t0 = time.time()
    for i, txt in enumerate(texts):
        out = tok.tokenize_lossless(txt)
        rec = tok.detokenize(out)
        if rec != txt:
            bad += 1
            if len(examples) < 10:
                examples.append({'i': i, 'input_len': len(txt), 'recon_len': len(rec)})
    return {'cases': len(texts), 'exact': len(texts)-bad, 'mismatch': bad, 'exact_pct': round(100*(len(texts)-bad)/max(len(texts),1),4), 'seconds': round(time.time()-t0,3), 'examples': examples}


                                                    
def run_morpheus_neural():
    rows = load_gold()
    repo = ROOT / 'external_baselines' / 'TurkishMorpheus'
    hf = ROOT / 'external_baselines' / 'Morpheus-TR-50K'
    if not repo.exists():
        subprocess.check_call(['git', 'clone', 'https://github.com/lonewolf-rd/TurkishMorpheus.git', str(repo)])
    if not hf.exists():
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id='lonewolflab/Morpheus-TR-50K', local_dir=str(hf))
    sys.path.insert(0, str(repo))
    import importlib
    import torch
    mm = importlib.import_module('src.model_development.model.morpheus')
    tm = importlib.import_module('src.model_development.tokenization.morpheus_tokenizer')
    M = getattr(mm, 'Morpheus')
    Tok = getattr(tm, 'MorpheusTokenizer')
    ck = torch.load(str(hf / 'turkish_morpheus_a100_v3_best.pt'), map_location='cpu', weights_only=False)
    vals = list(ck.values())
    cfg = vals[9]
    model = M(char_dim=cfg.char_dim, char_embed_dim=cfg.char_embed_dim, case_embed_dim=cfg.case_embed_dim, n_layers_encoder=cfg.n_layers_encoder, n_layers_detector=cfg.n_layers_detector, num_heads=cfg.num_heads, max_word_len=cfg.max_word_len, max_segs=cfg.max_segs, dropout=cfg.dropout, threshold=cfg.threshold, pos_weight=cfg.pos_weight, count_loss_w=cfg.count_loss_w)
    ret = model.load_state_dict(vals[2], strict=False)
    model.eval()
    mtok = Tok.load(str(hf / 'morpheus_50k'), morpheus_model=model)
    def pred(w):
        pieces = mtok.encode_as_pieces(w)
        out = []
        for p in pieces:
            p = str(p).replace('▁','')
            if p: out.append(p)
        return out or [w], []
    res = eval_predictions(rows, pred)
    res['missing_keys'] = len(ret.missing_keys)
    res['unexpected_keys'] = len(ret.unexpected_keys)
    return res


                                              
def run_ablation():
    rows = load_gold()
    from nedo_turkish_tokenizer import NedoTurkishTokenizer
    from nedo_turkish_tokenizer import segmentation as seg
    from nedo_turkish_tokenizer import engine as eng
    original = {
        'MAX_SUFFIX_DEPTH': getattr(seg, '_MAX_SUFFIX_DEPTH', None),
        'DOMAIN_ROOTS': eng.ALL_DOMAIN_ROOTS,
        'TDK_BONUS': getattr(seg, '_TDK_BONUS', None),
        'DOMAIN_BONUS': getattr(seg, '_DOMAIN_BONUS', None),
        'SHORT_ROOT_PENALTY': getattr(seg, '_SHORT_ROOT_PENALTY', None),
    }
    def evaluate_variant(name, patch):
        for k,v in original.items():
            if k == 'MAX_SUFFIX_DEPTH' and v is not None: seg._MAX_SUFFIX_DEPTH = v
            if k == 'DOMAIN_ROOTS': eng.ALL_DOMAIN_ROOTS = v
            if k == 'TDK_BONUS' and v is not None: seg._TDK_BONUS = v
            if k == 'DOMAIN_BONUS' and v is not None: seg._DOMAIN_BONUS = v
            if k == 'SHORT_ROOT_PENALTY' and v is not None: seg._SHORT_ROOT_PENALTY = v
        patch()
        tok = NedoTurkishTokenizer()
        res = eval_predictions(rows, make_nedo_pred(tok))
        res['variant'] = name
        return res
    variants = []
    variants.append(evaluate_variant('full', lambda: None))
    variants.append(evaluate_variant('max_suffix_depth_3', lambda: setattr(seg, '_MAX_SUFFIX_DEPTH', 3)))
    variants.append(evaluate_variant('max_suffix_depth_1', lambda: setattr(seg, '_MAX_SUFFIX_DEPTH', 1)))
    variants.append(evaluate_variant('no_domain_roots', lambda: setattr(eng, 'ALL_DOMAIN_ROOTS', frozenset())))
    variants.append(evaluate_variant('no_short_root_penalty', lambda: setattr(seg, '_SHORT_ROOT_PENALTY', 0)))
    variants.append(evaluate_variant('weak_dictionary_bonus', lambda: setattr(seg, '_TDK_BONUS', 2)))
             
    if original['MAX_SUFFIX_DEPTH'] is not None: seg._MAX_SUFFIX_DEPTH = original['MAX_SUFFIX_DEPTH']
    eng.ALL_DOMAIN_ROOTS = original['DOMAIN_ROOTS']
    if original['TDK_BONUS'] is not None: seg._TDK_BONUS = original['TDK_BONUS']
    if original['DOMAIN_BONUS'] is not None: seg._DOMAIN_BONUS = original['DOMAIN_BONUS']
    if original['SHORT_ROOT_PENALTY'] is not None: seg._SHORT_ROOT_PENALTY = original['SHORT_ROOT_PENALTY']
    return {'variants': variants}


                                                        
def run_paired_bootstrap():
    rows = load_gold()
    from nedo_turkish_tokenizer import NedoTurkishTokenizer
    nedo_pred = make_nedo_pred(NedoTurkishTokenizer())
                                                                 
    preds = {'nedo': nedo_pred, 'whole': lambda w: ([w], []), 'char': lambda w: (list(w), [])}
                                       
    try:
        import sentencepiece as spm
        sp_path = ROOT / 'reports/q1_final/spp_word_work/m_unigram_2000.model'
        if sp_path.exists():
            proc = spm.SentencePieceProcessor(model_file=str(sp_path))
            def sp_pred(w):
                out=[]
                for pc in proc.encode(w, out_type=str):
                    pc=pc.replace('▁','')
                    if pc: out.append(pc)
                return out or [w], []
            preds['sp_unigram_2000'] = sp_pred
    except Exception:
        pass
    try:
        from transformers import AutoTokenizer
        xlm = AutoTokenizer.from_pretrained('xlm-roberta-base', use_fast=True)
        def xlm_pred(w):
            out=[]
            for x in xlm.tokenize(w):
                x=x.replace('▁','').replace('##','')
                if x and x not in ['[UNK]','<unk>']: out.append(x)
            return out or [w], []
        preds['xlm_roberta_base'] = xlm_pred
    except Exception:
        pass
    def per_row_counts(pred_fn):
        arr=[]
        for r in rows:
            p,_=pred_fn(r['word']); g=r['segments']; gb,pb=bounds(g),bounds(p)
            arr.append((len(gb&pb), len(pb-gb), len(gb-pb)))
        return arr
    def f1_from(arr):
        tp=sum(x[0] for x in arr); fp=sum(x[1] for x in arr); fn=sum(x[2] for x in arr)
        P=tp/max(tp+fp,1); R=tp/max(tp+fn,1); return 2*P*R/max(P+R,1e-12)
    arrs={k:per_row_counts(v) for k,v in preds.items()}
    rnd=random.Random(42); B=2000; sig={}
    for name, arr in arrs.items():
        if name=='nedo': continue
        diffs=[]; n=len(rows)
        for _ in range(B):
            idx=[rnd.randrange(n) for __ in range(n)]
            diffs.append(f1_from([arrs['nedo'][i] for i in idx]) - f1_from([arr[i] for i in idx]))
        diffs.sort()
        sig[name]={'delta_f1_median': round(diffs[B//2],4), 'ci95': [round(diffs[int(.025*B)],4), round(diffs[int(.975*B)-1],4)], 'p_delta_le_0': round(sum(d<=0 for d in diffs)/B,5)}
    return {'baselines_compared': list(arrs.keys()), 'paired_bootstrap': sig}


                                                              
def run_codemix_gold():
    roots = ['link','repo','meeting','commit','branch','server','client','backend','frontend','dataset','model','script','pipeline','notebook','token','batch','debug','cache','checkpoint','driver','kernel','cluster','job','queue','merge','pull','issue','label','prompt','chat','file','folder','runtime','benchmark','baseline','embedding','decoder','encoder','router','adapter','plugin','module','class','function','config','logger','metric','epoch','loss','graph']
    suffixes = [(['ler'], ['PL']), (['lar'], ['PL']), (['de'], ['LOC']), (['da'], ['LOC']), (['den'], ['ABL']), (['dan'], ['ABL']), (['e'], ['DAT']), (['a'], ['DAT']), (['i'], ['ACC']), (['ı'], ['ACC']), (['imiz'], ['P1PL']), (['iniz'], ['P2PL']), (['ler','de'], ['PL','LOC']), (['lar','da'], ['PL','LOC']), (['ler','den'], ['PL','ABL']), (['lar','dan'], ['PL','ABL']), (['ler','imiz','den'], ['PL','P1PL','ABL']), (['lar','ımız','dan'], ['PL','P1PL','ABL']), (['ci'], ['DERIV']), (['cı'], ['DERIV'])]
    rows=[]; idx=1
    for r in roots:
        for sfx,labs in suffixes:
            if len(rows)>=240: break
            word=r+''.join(sfx)
            rows.append({'id':idx,'word':word,'segments':[r]+sfx,'labels':labs}); idx+=1
        if len(rows)>=240: break
    from nedo_turkish_tokenizer import NedoTurkishTokenizer
    res=eval_predictions(rows, make_nedo_pred(NedoTurkishTokenizer()))
    path=OUT/'codemix_foreign_gold_240.jsonl'
    path.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows),encoding='utf-8')
    res['gold_path']=str(path); res['cases_generated']=len(rows)
    return res


                                                   
def run_probe():
    rows = load_gold()
    from nedo_turkish_tokenizer import NedoTurkishTokenizer
    tok=NedoTurkishTokenizer()
    data=[]
    for r in rows:
        y=int(len(bounds(r['segments']))>0)
        o=tok(r['word'])
        toks=[str(t.get('token','')).strip() for t in o if str(t.get('token_type'))!='PUNCT' and str(t.get('token','')).strip()]
        data.append({'word':r['word'],'y':y,'fertility':len(toks),'len':len(r['word']),'has_suffix_pred':int(any(str(t.get('token_type'))=='SUFFIX' for t in o))})
    rnd=random.Random(3); rnd.shuffle(data)
    split=int(.8*len(data)); train=data[:split]; test=data[split:]
    def acc_rule(feat):
        return sum(int(feat(x)==x['y']) for x in test)/max(len(test),1)
                                                                               
    res={'task':'binary_has_gold_boundary_probe','test_cases':len(test),'majority_acc': round(max(sum(x['y'] for x in test), len(test)-sum(x['y'] for x in test))/len(test),4), 'pred_has_suffix_acc': round(acc_rule(lambda x:int(x['has_suffix_pred'])),4), 'fertility_gt1_acc': round(acc_rule(lambda x:int(x['fertility']>1)),4), 'length_gt7_acc': round(acc_rule(lambda x:int(x['len']>7)),4)}
    return res


if __name__ == '__main__':
    summary = {}
    tasks = [
        ('01_patch_lossless_api', patch_lossless_api),
        ('02_roundtrip_10k', run_roundtrip10k),
        ('03_morpheus_neural_same_gold', run_morpheus_neural),
        ('04_human_gold_ablation', run_ablation),
        ('05_paired_bootstrap', run_paired_bootstrap),
        ('06_codemix_foreign_gold', run_codemix_gold),
        ('07_downstream_probe', run_probe),
    ]
    for name, fn in tasks:
        print('START', name, flush=True)
        summary[name] = safe_run(name, fn)
        print('DONE', name, summary[name]['ok'], flush=True)
    write_json('summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
