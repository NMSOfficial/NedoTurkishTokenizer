import json, pathlib, sys
sys.path.insert(0, '/arf/scratch/egitimg16u1/nedoturkishtokenizer')
from nedo_turkish_tokenizer import NedoTurkishTokenizer
TOK=NedoTurkishTokenizer()
OUT=pathlib.Path('reports/full_validation_v21'); OUT.mkdir(parents=True, exist_ok=True)

def c(t): return str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()
def simp(o): return [(str(t.get('token','')).strip(), t.get('token_type'), t.get('morph_pos'), c(t), t.get('_canonical_root')) for t in o]
def labs(o): return [c(t) for t in o if t.get('token_type')=='SUFFIX']
WORD_CASES=[]
GUARDS=[]
SPECIAL=[]
SENTS=[]
WORD_CASES += [
('yapabileceklerinden',['ABIL','FUT','PL','ABL'],4),
('gidebileceklerimizden',['ABIL','FUT','PL','P1PL','ABL'],5),
('sağlayabileceğiz',['ABIL','FUT'],2),
('yapabileceklerimizden',['ABIL','FUT','PL','P1PL','ABL'],5),
('unutmayacağız',['NEG','FUT'],2),
('gitmeyeceksiniz',['NEG','FUT'],2),
('yapmayacaklar',['NEG','FUT'],2),
('anlatmayacağım',['NEG','FUT'],2),
('çalışmalarımızdan',['PL','P1PL','ABL'],3),
('öğrencilerimizin',['PL','P1PL','GEN'],3),
('öğretmenlerimizin',['PL','P1PL','GEN'],3),
('müşterilerimizin',['PL','P1PL','GEN'],3),
('yıldızlarından',['PL','P3PL','ABL'],3),
('araçlarından',['PL','P3PL','ABL'],3),
('İllerimizin',['PL','P1PL','GEN'],3),
('okullarımızdakilerden',['PL','P1PL','LOC','KI','ABL'],5),
('anlamlandıramadıklarımızdan',['NEG','DIK','PL','P1PL','ABL'],5),
('gördüklerimizden',['DIK','PL','P1PL','ABL'],4),
('bildiklerinizden',['DIK','PL','P2PL','ABL'],4),
('kitaptan',['ABL'],1),
('ağaçtan',['ABL'],1),
('renkten',['ABL'],1),
('defterlerden',['PL','ABL'],2),
('evlerimizde',['PL','P1PL','LOC'],3),
('kitabımda',['P1S','LOC'],2),
("Türkiye'de",['LOC'],1),
("Ankara'dan",['ABL'],1),
("İstanbul'un",['GEN'],1),
]
GUARDS += ['gelecek','dünya','insan','bugün','yarın','merhaba','neden','ama','ile','değil','Türkiye','Ankara']
SPECIAL += [('site.com/test',['URL']),('@nedo #Turkce',['MENTION','HASHTAG']),('16 H200 GPU 3.5TB',['NUM','ACRONYM']),('%92.64 başarı elde edildi.',['NUM'])]
SENTS += ['Yapabileceklerinden söz etti.','Gidebileceklerimizden bahsediyoruz.','Çalışmalarımızdan elde edilen sonuçları değerlendireceğiz.','Okullarımızdakilerden bazıları yenilendi.','Anlamlandıramadıklarımızdan değildi.','Gelecek hafta geleceklerden bahsetmeyeceğiz.',"Türkiye'de doğal dil işleme çalışmaları hızlanıyor.",'TRUBA üzerinde 16 H200 GPU ile eğitim planlandı.']

def test_words():
 rows=[]
 for w,must,min_s in WORD_CASES:
  o=TOK(w); la=labs(o); errs=[]
  if sum(1 for t in o if t.get('token_type')=='SUFFIX')<min_s: errs.append('too_few_suffix')
  if len(o)==1 and o[0].get('token_type')=='ROOT': errs.append('single_root')
  for m in must:
   if m not in la: errs.append('missing_'+m)
  rows.append({'word':w,'ok':not errs,'errors':errs,'labels':la,'tokens':simp(o)})
 return rows

def test_guards():
 rows=[]
 for w in GUARDS:
  o=TOK(w); errs=[]
  if sum(1 for t in o if t.get('token_type')=='SUFFIX')>0: errs.append('oversegmented')
  rows.append({'word':w,'ok':not errs,'errors':errs,'tokens':simp(o)})
 return rows

def test_special():
 rows=[]
 for text, req in SPECIAL:
  o=TOK(text); ts=set(t.get('token_type') for t in o); errs=[]
  for r in req:
   if r not in ts: errs.append('missing_type_'+r)
  rows.append({'text':text,'ok':not errs,'errors':errs,'types':list(ts),'tokens':simp(o)})
 return rows

def test_sents():
 rows=[]
 for s in SENTS:
  o=TOK(s); o2=TOK(s); errs=[]
  if json.dumps(o,ensure_ascii=False,sort_keys=True)!=json.dumps(o2,ensure_ascii=False,sort_keys=True): errs.append('nondeterministic')
  for t in o:
   if t.get('token_type')=='SUFFIX' and int(t.get('morph_pos',0))<=0: errs.append('bad_suffix_pos'); break
  rows.append({'text':s,'ok':not errs,'errors':errs,'tokens':simp(o)})
 return rows

def summarize(rows): return {'total':len(rows),'ok':sum(bool(r['ok']) for r in rows),'fail':sum(not r['ok'] for r in rows)}
res={'version':getattr(__import__('nedo_turkish_tokenizer'),'__version__','unknown')}
for name,fn in [('word_cases',test_words),('guards',test_guards),('special',test_special),('sentences',test_sents)]: res[name]=fn()
res['summary']={k:summarize(res[k]) for k in ['word_cases','guards','special','sentences']}
(OUT/'core_validation.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res['summary'],ensure_ascii=False))
for k in ['word_cases','guards','special','sentences']:
 for r in res[k]:
  if not r['ok']: print('FAIL',k,json.dumps(r,ensure_ascii=False))
