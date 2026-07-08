import json,re,pathlib,csv,random,sys
sys.path.insert(0,'.')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
T=NedoTurkishTokenizer()
WORD_RE=re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]{4,}")
paths=[
'/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_balanced_source_audit/sample.jsonl',
'/arf/scratch/egitimg16u1/turkformer/data/raw/nedo_final_sample_audit/sample.jsonl']
seen=[]; bag=[]
for p in paths:
    pp=pathlib.Path(p)
    if not pp.exists(): continue
    with pp.open(encoding='utf-8',errors='ignore') as f:
        for line in f:
            try:
                obj=json.loads(line); txt=obj.get('text') or obj.get('content') or ''
            except Exception:
                txt=line
            for w in WORD_RE.findall(txt):
                lw=w.lower()
                if lw not in seen:
                    seen.append(lw); bag.append(w)
                if len(bag)>=3000: break
            if len(bag)>=3000: break
random.seed(42)
random.shuffle(bag)
items=bag[:1000]
outdir=pathlib.Path('reports/annotation_pack_v1'); outdir.mkdir(parents=True,exist_ok=True)
with (outdir/'annotation_items.csv').open('w',encoding='utf-8',newline='') as f:
    wr=csv.writer(f)
    wr.writerow(['id','word','nedo_suggestion','annotator_segments','annotator_labels','notes'])
    for i,w in enumerate(items,1):
        toks=T(w)
        sug='+'.join(str(x.get('token','')).strip() for x in toks)
        wr.writerow([i,w,sug,'','',''])
(outdir/'README_ANNOTATION.md').write_text('''# NedoTurkishTokenizer annotation task\n\nAmaç: 1000 kelimelik bağımsız morfolojik sınır kontrolü.\n\nKurallar:\n1. `word` sütunundaki yüzey biçime bak.\n2. `nedo_suggestion` sadece öneridir; doğru kabul etme.\n3. `annotator_segments` alanına morfolojik parçaları `+` ile yaz. Örn: `kitap+lar+ımız+dan`.\n4. Emin olmadığın yerde `notes` alanına `AMBIG` yaz ve kısa gerekçe ekle.\n5. Özel isim/kısaltma/URL/İngilizce kök varsa yüzeyi koru ve not düş.\n6. Etiket biliyorsan `annotator_labels` alanına `PL,P1PL,ABL` gibi yaz; bilmiyorsan boş bırakma, `UNK` yaz.\n7. Başka annotator ile konuşma; bağımsız işaretle.\n''',encoding='utf-8')
print(str(outdir/'annotation_items.csv'))
print(len(items))
