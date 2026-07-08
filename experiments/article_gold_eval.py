import os, sys, json, re, collections, math, pathlib, subprocess, statistics
from typing import List, Tuple

VOWELS='aeıioöuü'
BACK=set('aıou')
ROUND=set('ouöü')

def last_vowel(s):
    for ch in reversed(s.lower()):
        if ch in VOWELS: return ch
    return 'a'

def is_back(s): return last_vowel(s) in BACK

def pl(s): return 'lar' if is_back(s) else 'ler'
def loc(s): return 'da' if is_back(s) else 'de'
def abl(s): return 'dan' if is_back(s) else 'den'
def gen(s):
    v=last_vowel(s); return {'a':'ın','ı':'ın','o':'un','u':'un','e':'in','i':'in','ö':'ün','ü':'ün'}[v]
def acc(s):
    v=last_vowel(s); return {'a':'ı','ı':'ı','o':'u','u':'u','e':'i','i':'i','ö':'ü','ü':'ü'}[v]
def p1pl(s):
    v=last_vowel(s); return {'a':'ımız','ı':'ımız','o':'umuz','u':'umuz','e':'imiz','i':'imiz','ö':'ümüz','ü':'ümüz'}[v]
def p2pl(s):
    v=last_vowel(s); return {'a':'ınız','ı':'ınız','o':'unuz','u':'unuz','e':'iniz','i':'iniz','ö':'ünüz','ü':'ünüz'}[v]

def fut(root): return 'acak' if is_back(root) else 'ecek'
def neg(root): return 'ma' if is_back(root) else 'me'
def abil(root): return 'abil' if is_back(root) else 'ebil'
def yabil(root): return 'yabil' if is_back(root) else 'yebil'

def add_case(cases, segs, labels, group):
    word=''.join(segs)
    cases.append({'word':word,'segments':segs,'labels':labels,'group':group})
def build_cases():
    cases=[]
    roots=['okul','kitap','defter','öğrenci','öğretmen','şehir','ev','araç','çocuk','insan','proje','ders','kurum','müşteri','üretici','yıldız','sorun','sonuç','fikir','haber','gözyaş','işbirlik','hemşeri','çalışma','makale','bilgi','sistem','yöntem','alan','metin','kütüphane','bilgisayar','program','dosya','veri','model','ağaç','renk','kalem','masa','kapı','sınıf','bölüm','üniversite','hastane','doktor','hasta','rapor','deney','sonuç']
    for r in roots:
        s=[r,pl(r),p1pl(r+pl(r))]; add_case(cases,s,['PL','P1PL'],'NOM_PL_P1PL')
        s=[r,pl(r),p1pl(r+pl(r))]; s=[*s,gen(''.join(s))]; add_case(cases,s,['PL','P1PL','GEN'],'NOM_PL_P1PL_GEN')
        s=[r,pl(r),p1pl(r+pl(r))]; s=[*s,abl(''.join(s))]; add_case(cases,s,['PL','P1PL','ABL'],'NOM_PL_P1PL_ABL')
        s=[r,pl(r),gen(r+pl(r)),abl(r+pl(r)+gen(r+pl(r)))]; add_case(cases,s,['PL','GEN','ABL'],'NOM_PL_GEN_ABL')
        s=[r,loc(r),'ki',pl(r),abl(r+loc(r)+'ki'+pl(r))]; add_case(cases,s,['LOC','KI','PL','ABL'],'NOM_KI')
    verb_roots=['yap','git','gel','oku','yaz','gör','bil','unut','anlat','sağla','değerlendir','çalış','bekle','düşün','öğren','ara','başla','kullan','incele','üret','seç','al','ver','bul','kur','taşı','aç','kapat','yönet','ölç']
    for r in verb_roots:
        ab = abil(r) if not r.endswith(('a','e','ı','i','o','ö','u','ü')) else yabil(r)
        fu = fut(r)
                                               
        s=[r,ab,fut(r+ab),pl(r+ab+fut(r+ab)),gen(r+ab+fut(r+ab)+pl(r+ab+fut(r+ab))),abl(r+ab+fut(r+ab)+pl(r+ab+fut(r+ab))+gen(r+ab+fut(r+ab)+pl(r+ab+fut(r+ab))))]
        add_case(cases,s,['ABIL','FUT','PL','GEN','ABL'],'VERB_ABIL_FUT_CHAIN')
                            
        s=[r,neg(r),'y'+fut(r), 'ız' if is_back(r) else 'iz']
        add_case(cases,s,['NEG','FUT','1PL'],'VERB_NEG_FUT_1PL')
                       
        s=[r,fu]
        add_case(cases,s,['FUT'],'VERB_FUT')
                            
        dik='dık' if is_back(r) else 'dik'
        s=[r,dik,pl(r+dik),p1pl(r+dik+pl(r+dik))]; s=[*s,abl(''.join(s))]
        add_case(cases,s,['DIK','PL','P1PL','ABL'],'VERB_DIK_CHAIN')
                                                
    specials=[
      (['ed','eceğim'],['FUT'],'ED_FUT'),(['ed','eceğiz'],['FUT','1PL'],'ED_FUT'),
      (['kitab','ım','da'],['P1S','LOC'],'ROOT_ALTERNATION'),(['ağac','a'],['DAT'],'ROOT_ALTERNATION'),
      (['shirt','ler','imiz'],['PL','P1PL'],'FOREIGN_SUFFIX'),(['gpu','lar','ımız'],['PL','P1PL'],'FOREIGN_SUFFIX'),
      (['mod','lar','ın','dan'],['PL','GEN','ABL'],'FOREIGN_SUFFIX'),(['web','de'],['LOC'],'FOREIGN_SUFFIX'),
      (['okul','lar','ımız','da','ki','ler','den'],['PL','P1PL','LOC','KI','PL','ABL'],'KI_CHAIN'),
      (['anlamlandır','a','ma','dık','lar','ımız','dan'],['DAT','NEG','DIK','PL','P1PL','ABL'],'LONG_DERIV'),
    ]
    for segs,labels,g in specials: add_case(cases,segs,labels,g)
                                      
    return cases

CASES=build_cases()
def gold_boundaries(segs):
    pos=[]; n=0
    for s in segs[:-1]:
        n+=len(s); pos.append(n)
    return set(pos)

def strip_tok(t): return str(t.get('token','')).strip()
def label_of(t): return str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()

def eval_tokens(name, rows):
    stats=collections.Counter(); examples=[]; group_stats=collections.defaultdict(collections.Counter)
    for case,out in zip(CASES, rows):
        word=case['word']; gb=gold_boundaries(case['segments'])
        toks=[strip_tok(t) for t in out if strip_tok(t) and strip_tok(t)!="'"]
        b=set(); n=0
        for tok in toks[:-1]:
            n+=len(tok); b.add(n)
        tp=len(gb & b); fp=len(b-gb); fn=len(gb-b)
        labs=[label_of(t) for t in out if str(t.get('token_type'))=='SUFFIX']
        exp=case['labels']
        lab_hit=sum(1 for x in exp if x in labs)
        single_root=(len(out)==1 and str(out[0].get('token_type'))=='ROOT')
        stats['cases']+=1; stats['tp']+=tp; stats['fp']+=fp; stats['fn']+=fn; stats['gold_labels']+=len(exp); stats['label_hits']+=lab_hit; stats['tokens']+=len(toks); stats['single_root']+=int(single_root)
        g=group_stats[case['group']]; g['cases']+=1; g['tp']+=tp; g['fp']+=fp; g['fn']+=fn; g['gold_labels']+=len(exp); g['label_hits']+=lab_hit; g['single_root']+=int(single_root)
        if (fn or single_root or lab_hit < len(exp)) and len(examples)<25:
            examples.append({'word':word,'gold':case['segments'],'expected':exp,'tokens':[(strip_tok(t),t.get('token_type'),label_of(t)) for t in out],'missing_labels':[x for x in exp if x not in labs]})
    def met(c):
        p=c['tp']/max(c['tp']+c['fp'],1); r=c['tp']/max(c['tp']+c['fn'],1); f=2*p*r/max(p+r,1e-12)
        return {'cases':c['cases'],'boundary_precision':round(p,4),'boundary_recall':round(r,4),'boundary_f1':round(f,4),'label_recall':round(c['label_hits']/max(c['gold_labels'],1),4),'single_root_pct':round(100*c['single_root']/max(c['cases'],1),4),'avg_tokens_per_word':round(c['tokens']/max(c['cases'],1),4)}
    return {'name':name,'summary':met(stats),'by_group':{k:met(v) for k,v in sorted(group_stats.items())},'examples':examples}

if __name__=='__main__':
    mode=os.environ.get('EVAL_MODE','tokenizer')
    if mode=='dump_cases':
        print(json.dumps(CASES,ensure_ascii=False,indent=2)); sys.exit(0)
    if mode=='tokenizer':
        sys.path.insert(0, os.environ['TOKENIZER_PATH'])
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        T=NedoTurkishTokenizer()
        rows=[T(c['word']) for c in CASES]
        print(json.dumps(eval_tokens(os.environ.get('TOKENIZER_NAME','tokenizer'), rows),ensure_ascii=False,indent=2))
