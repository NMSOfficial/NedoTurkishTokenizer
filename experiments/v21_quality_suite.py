import json, time, re, pathlib, collections, statistics, sys
from typing import Any

ROOT = pathlib.Path('/arf/scratch/egitimg16u1/nedoturkishtokenizer')
TURKFORMER = pathlib.Path('/arf/scratch/egitimg16u1/turkformer')
REPORT = ROOT / 'reports' / 'quality_v21'
REPORT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from nedo_turkish_tokenizer import NedoTurkishTokenizer

TOK = NedoTurkishTokenizer()
WORD_RE = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü']{2,}")
TARGET_SUFFIXES = (
    'lerinden','larından','lerimizden','larımızdan','lerimizin','larımızın','lerimiz','larımız',
    'abileceklerinden','ebileceklerinden','abileceklerimizden','ebileceklerimizden',
    'eceğiz','acağız','yeceğiz','yacağız','acaklar','ecekler','mayacağız','meyeceğiz',
    'diklerimizden','dıklarımızdan','dakilerden','dekilerden'
)

CURATED = [
    {'word':'yapabileceklerinden','want_suffix_min':4,'must_any':['ABIL','FUT','PL','ABL']},
    {'word':'gidebileceklerimizden','want_suffix_min':4,'must_any':['ABIL','FUT','PL','P1PL','ABL']},
    {'word':'çalışmalarımızdan','want_suffix_min':3,'must_any':['PL','P1PL','ABL']},
    {'word':'değerlendireceğiz','want_suffix_min':1,'must_any':['FUT']},
    {'word':'okullarımızdakilerden','want_suffix_min':5,'must_any':['PL','P1PL','LOC','KI','ABL']},
    {'word':'anlamlandıramadıklarımızdan','want_suffix_min':4,'must_any':['NEG','DIK','PL','P1PL','ABL']},
    {'word':'üreticilerimizin','want_suffix_min':3,'must_any':['PL','P1PL','GEN']},
    {'word':'müşterilerimizin','want_suffix_min':3,'must_any':['PL','P1PL','GEN']},
    {'word':'sağlayacağız','want_suffix_min':1,'must_any':['FUT']},
    {'word':'unutmayacağız','want_suffix_min':2,'must_any':['NEG','FUT']},
    {'word':'kitaptan','want_suffix_min':1,'must_any':['ABL']},
    {'word':'defterlerden','want_suffix_min':2,'must_any':['PL','ABL']},
    {'word':'Türkiye\'de','want_suffix_min':1,'must_any':['LOC']},
    {'word':'H200','want_suffix_min':0,'must_type_any':['ACRONYM','NUM','ROOT']},
]

def tokens_for(text: str):
    return TOK(text)

def canon(tok: dict[str, Any]) -> str:
    return str(tok.get('_canonical') or tok.get('_suffix_label') or '').lstrip('-').upper()

def summarize_tokens(items):
    return [
        {
            'token': str(t.get('token','')).strip(),
            'type': t.get('token_type'),
            'pos': t.get('morph_pos'),
            'canon': canon(t),
            'canonical_root': t.get('_canonical_root'),
        }
        for t in items
    ]

def eval_word_case(case):
    out = tokens_for(case['word'])
    toks = summarize_tokens(out)
    suffix = [x for x in toks if x['type'] == 'SUFFIX']
    labels = [x['canon'] for x in suffix]
    types = [x['type'] for x in toks]
    errors = []
    if len(suffix) < case.get('want_suffix_min', 0):
        errors.append('too_few_suffix')
    for m in case.get('must_any', []):
        if m not in labels:
            errors.append('missing_'+m)
    if case.get('must_type_any') and not any(t in case['must_type_any'] for t in types):
        errors.append('missing_type')
    if len(out) == 1 and out[0].get('token_type') == 'ROOT' and case.get('want_suffix_min', 0) > 0:
        errors.append('single_root')
    return {'case': case, 'tokens': toks, 'labels': labels, 'ok': not errors, 'errors': errors}

def curated_regression():
    rows = [eval_word_case(c) for c in CURATED]
    summary = collections.Counter()
    for r in rows:
        summary['total'] += 1
        summary['ok' if r['ok'] else 'fail'] += 1
        for e in r['errors']:
            summary[e] += 1
    return {'summary': dict(summary), 'rows': rows}

def audit_texts(texts, max_words=200000):
    stats = collections.Counter()
    examples = []
    suffix_counts = []
    token_counts = []
    for text in texts:
        stats['docs'] += 1
        for w in WORD_RE.findall(text):
            if stats['words'] >= max_words:
                break
            lw = w.lower().strip("'")
            if len(lw) < 2:
                continue
            out = tokens_for(w)
            stats['words'] += 1
            token_counts.append(len(out))
            sc = sum(1 for t in out if t.get('token_type') == 'SUFFIX')
            suffix_counts.append(sc)
            if len(lw) >= 10:
                stats['long_words'] += 1
                if len(out) == 1 and out[0].get('token_type') == 'ROOT':
                    stats['long_single_root'] += 1
            if any(lw.endswith(s) for s in TARGET_SUFFIXES):
                stats['target_suffix_words'] += 1
                if len(out) == 1 and out[0].get('token_type') == 'ROOT':
                    stats['target_single_root'] += 1
                    if len(examples) < 40:
                        examples.append({'word': w, 'tokens': summarize_tokens(out)})
            if stats['words'] >= max_words:
                break
        if stats['words'] >= max_words:
            break
    denom_long = max(stats['long_words'], 1)
    denom_target = max(stats['target_suffix_words'], 1)
    return {
        'stats': dict(stats),
        'rates': {
            'long_single_root_pct': round(100*stats['long_single_root']/denom_long, 4),
            'target_single_root_pct': round(100*stats['target_single_root']/denom_target, 4),
            'avg_tokens_per_word': round(statistics.mean(token_counts), 4) if token_counts else 0,
            'avg_suffix_per_word': round(statistics.mean(suffix_counts), 4) if suffix_counts else 0,
        },
        'examples': examples,
    }

def iter_jsonl_texts(paths, max_docs=2000):
    n = 0
    for path in paths:
        p = pathlib.Path(path)
        if not p.exists():
            continue
        with p.open(encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    text = obj.get('text') or obj.get('content') or obj.get('sentence') or ''
                except Exception:
                    text = line
                if text:
                    yield text
                    n += 1
                    if n >= max_docs:
                        return

def real_corpus_audit():
    paths = [
        TURKFORMER/'data/raw/nedo_final_sample_audit/sample.jsonl',
        TURKFORMER/'data/raw/nedo_balanced_source_audit/sample.jsonl',
        TURKFORMER/'data/raw/turkish_smoke/turkish_smoke.jsonl',
        TURKFORMER/'data/raw/real_turkish_medium/real_turkish_medium.jsonl',
    ]
    return audit_texts(iter_jsonl_texts(paths, max_docs=2000), max_words=50000)

def speed_benchmark():
    paths = [TURKFORMER/'data/raw/nedo_balanced_source_audit/sample.jsonl', TURKFORMER/'data/raw/turkish_smoke/turkish_smoke.jsonl']
    texts = list(iter_jsonl_texts(paths, max_docs=1000))
    char_count = sum(len(x) for x in texts)
    word_count = sum(len(WORD_RE.findall(x)) for x in texts)
    t0 = time.perf_counter()
    token_count = 0
    for x in texts:
        token_count += len(tokens_for(x))
    dt = max(time.perf_counter() - t0, 1e-9)
    return {
        'docs': len(texts),
        'chars': char_count,
        'words_regex': word_count,
        'tokens': token_count,
        'seconds': round(dt, 6),
        'docs_per_sec': round(len(texts)/dt, 2) if texts else 0,
        'tokens_per_sec': round(token_count/dt, 2),
        'chars_per_sec': round(char_count/dt, 2),
    }

def v20_vs_v21_placeholder():
                                                                                      
                                                                               
    failure_words = ['yapabileceklerinden','gidebileceklerimizden','çalışmalarımızdan','değerlendireceğiz','okullarımızdakilerden','anlamlandıramadıklarımızdan','üreticilerimizin','öğrencilerimizin','sağlayacağız','unutmayacağız','müşterilerimizin']
    rows = []
    fixed = 0
    for w in failure_words:
        out = tokens_for(w)
        is_fixed = not (len(out) == 1 and out[0].get('token_type') == 'ROOT')
        fixed += int(is_fixed)
        rows.append({'word': w, 'v21_fixed_single_root': is_fixed, 'tokens': summarize_tokens(out)})
    return {'known_v20_single_root_failures': len(rows), 'v21_non_single_root': fixed, 'rows': rows}

report = {
    'tokenizer_version': getattr(__import__('nedo_turkish_tokenizer'), '__version__', 'unknown'),
    'curated_regression': curated_regression(),
    'v20_vs_v21_failure_set': v20_vs_v21_placeholder(),
    'real_corpus_audit': real_corpus_audit(),
    'speed_benchmark': speed_benchmark(),
}
(REPORT/'v21_quality_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
                                        
lines = []
lines.append('version=' + str(report['tokenizer_version']))
lines.append('curated=' + json.dumps(report['curated_regression']['summary'], ensure_ascii=False))
lines.append('v20_failset=' + json.dumps({k:v for k,v in report['v20_vs_v21_failure_set'].items() if k != 'rows'}, ensure_ascii=False))
lines.append('real_rates=' + json.dumps(report['real_corpus_audit']['rates'], ensure_ascii=False))
lines.append('real_stats=' + json.dumps(report['real_corpus_audit']['stats'], ensure_ascii=False))
lines.append('speed=' + json.dumps(report['speed_benchmark'], ensure_ascii=False))
(REPORT/'v21_quality_summary.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
