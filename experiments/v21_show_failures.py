import json, pathlib
p=pathlib.Path('reports/quality_v21/v21_quality_report.json')
r=json.loads(p.read_text(encoding='utf-8'))
print('CURATED_FAILURES')
for row in r['curated_regression']['rows']:
    if not row['ok']:
        print(json.dumps({'word':row['case']['word'],'errors':row['errors'],'labels':row['labels'],'tokens':row['tokens']}, ensure_ascii=False))
print('REAL_TARGET_SINGLE_ROOT_EXAMPLES')
for ex in r['real_corpus_audit']['examples']:
    print(json.dumps(ex, ensure_ascii=False))
