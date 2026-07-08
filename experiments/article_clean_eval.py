import sys,json,pathlib,collections
sys.path.insert(0,'.')

CASES = [
                                   
('okullarımız', ['okul','lar','ımız'], ['PL','P1PL'], 'NOUN_POSS'),
('okullarımızdan', ['okul','lar','ımız','dan'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('kitaplarımız', ['kitap','lar','ımız'], ['PL','P1PL'], 'NOUN_POSS'),
('kitaplarımızdan', ['kitap','lar','ımız','dan'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('defterlerimiz', ['defter','ler','imiz'], ['PL','P1PL'], 'NOUN_POSS'),
('defterlerimizden', ['defter','ler','imiz','den'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('öğrencilerimiz', ['öğrenci','ler','imiz'], ['PL','P1PL'], 'NOUN_POSS'),
('öğrencilerimizden', ['öğrenci','ler','imiz','den'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('şehirlerimiz', ['şehir','ler','imiz'], ['PL','P1PL'], 'NOUN_POSS'),
('şehirlerimizden', ['şehir','ler','imiz','den'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('araçlarımız', ['araç','lar','ımız'], ['PL','P1PL'], 'NOUN_POSS'),
('araçlarımızdan', ['araç','lar','ımız','dan'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('çocuklarımız', ['çocuk','lar','ımız'], ['PL','P1PL'], 'NOUN_POSS'),
('çocuklarımızdan', ['çocuk','lar','ımız','dan'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('projelerimiz', ['proje','ler','imiz'], ['PL','P1PL'], 'NOUN_POSS'),
('projelerimizden', ['proje','ler','imiz','den'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('kurumlarımız', ['kurum','lar','ımız'], ['PL','P1PL'], 'NOUN_POSS'),
('kurumlarımızdan', ['kurum','lar','ımız','dan'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
('müşterilerimiz', ['müşteri','ler','imiz'], ['PL','P1PL'], 'NOUN_POSS'),
('müşterilerimizden', ['müşteri','ler','imiz','den'], ['PL','P1PL','ABL'], 'NOUN_POSS_CASE'),
                                                                  
('okuldakilerden', ['okul','da','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('evdekilerden', ['ev','de','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('şehirdekilerden', ['şehir','de','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('defterdekilerden', ['defter','de','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('kitaptakilerden', ['kitap','ta','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('sınıftakilerden', ['sınıf','ta','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('araçtakilerden', ['araç','ta','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
('masadakilerden', ['masa','da','ki','ler','den'], ['LOC','KI','PL','ABL'], 'KI_CHAIN'),
             
('yapabileceklerinden', ['yap','abil','ecek','ler','in','den'], ['ABIL','FUT','PL','GEN','ABL'], 'VERB_ABIL'),
('gidebileceklerinden', ['git','ebil','ecek','ler','in','den'], ['ABIL','FUT','PL','GEN','ABL'], 'VERB_ABIL'),
('gelebileceklerimizden', ['gel','ebil','ecek','ler','imiz','den'], ['ABIL','FUT','PL','P1PL','ABL'], 'VERB_ABIL'),
('okuyabileceklerimizden', ['oku','yabil','ecek','ler','imiz','den'], ['ABIL','FUT','PL','P1PL','ABL'], 'VERB_ABIL'),
('yazabileceklerinden', ['yaz','abil','ecek','ler','in','den'], ['ABIL','FUT','PL','GEN','ABL'], 'VERB_ABIL'),
('unutmayacağız', ['unut','ma','yacağ','ız'], ['NEG','FUT','1PL'], 'VERB_NEG_FUT'),
('anlatmayacağız', ['anlat','ma','yacağ','ız'], ['NEG','FUT','1PL'], 'VERB_NEG_FUT'),
('gelmeyeceğiz', ['gel','me','yeceğ','iz'], ['NEG','FUT','1PL'], 'VERB_NEG_FUT'),
('beklemeyeceğiz', ['bekle','me','yeceğ','iz'], ['NEG','FUT','1PL'], 'VERB_NEG_FUT'),
('çalışmayacağız', ['çalış','ma','yacağ','ız'], ['NEG','FUT','1PL'], 'VERB_NEG_FUT'),
('bildiklerimizden', ['bil','dik','ler','imiz','den'], ['DIK','PL','P1PL','ABL'], 'DIK_CHAIN'),
('gördüklerimizden', ['gör','dük','ler','imiz','den'], ['DIK','PL','P1PL','ABL'], 'DIK_CHAIN'),
('okuduklarımızdan', ['oku','duk','lar','ımız','dan'], ['DIK','PL','P1PL','ABL'], 'DIK_CHAIN'),
('yazdıklarımızdan', ['yaz','dık','lar','ımız','dan'], ['DIK','PL','P1PL','ABL'], 'DIK_CHAIN'),
('incelediklerimizden', ['incele','dik','ler','imiz','den'], ['DIK','PL','P1PL','ABL'], 'DIK_CHAIN'),
                             
('edeceğim', ['ed','eceğim'], ['FUT'], 'ROOT_ALT'),
('edeceğiz', ['ed','eceğ','iz'], ['FUT','1PL'], 'ROOT_ALT'),
('kitabımda', ['kitab','ım','da'], ['P1S','LOC'], 'ROOT_ALT'),
('ağaca', ['ağac','a'], ['DAT'], 'ROOT_ALT'),
('shirtlerimiz', ['shirt','ler','imiz'], ['PL','P1PL'], 'FOREIGN_SUFFIX'),
('modlarından', ['mod','lar','ın','dan'], ['PL','GEN','ABL'], 'FOREIGN_SUFFIX'),
('bonuslarından', ['bonus','lar','ın','dan'], ['PL','GEN','ABL'], 'FOREIGN_SUFFIX'),
('slotlarından', ['slot','lar','ın','dan'], ['PL','GEN','ABL'], 'FOREIGN_SUFFIX'),
('site.com/test', ['site.com/test'], [], 'SPECIAL'),
('Türkiye', ['Türkiye'], [], 'SPECIAL'),
]

def gold_boundaries(segs):
    pos=[]; n=0
    for s in segs[:-1]:
        n += len(s); pos.append(n)
    return set(pos)

def strip_tok(t): return str(t.get('token','')).strip()
def label_of(t): return str(t.get('_canonical') or t.get('_suffix_label') or '').strip().lstrip('-').upper()

def eval_rows(name, rows):
    stats=collections.Counter(); by=collections.defaultdict(collections.Counter); bad=[]
    for (word,segs,labels,grp),out in zip(CASES, rows):
        toks=[strip_tok(t) for t in out if strip_tok(t) and strip_tok(t)!="'"]
        b=set(); n=0
        for tok in toks[:-1]: n+=len(tok); b.add(n)
        gb=gold_boundaries(segs)
        tp=len(b & gb); fp=len(b-gb); fn=len(gb-b)
        labs=[label_of(t) for t in out if str(t.get('token_type'))=='SUFFIX']
        hits=sum(1 for x in labels if x in labs)
        single=(len(out)==1 and str(out[0].get('token_type'))=='ROOT' and len(segs)>1)
        for c in (stats, by[grp]):
            c['cases']+=1; c['tp']+=tp; c['fp']+=fp; c['fn']+=fn; c['gold_labels']+=len(labels); c['hits']+=hits; c['tokens']+=len(toks); c['single']+=single
        if (fn or single or hits < len(labels)) and len(bad)<20:
            bad.append({'word':word,'gold':segs,'expected':labels,'tokens':[(strip_tok(t),t.get('token_type'),label_of(t)) for t in out]})
    def m(c):
        p=c['tp']/max(c['tp']+c['fp'],1); r=c['tp']/max(c['tp']+c['fn'],1); f=2*p*r/max(p+r,1e-12)
        return {'cases':c['cases'],'boundary_precision':round(p,4),'boundary_recall':round(r,4),'boundary_f1':round(f,4),'label_recall':round(c['hits']/max(c['gold_labels'],1),4),'single_root_pct':round(100*c['single']/max(c['cases'],1),4),'avg_tokens_per_word':round(c['tokens']/max(c['cases'],1),4)}
    return {'name':name,'summary':m(stats),'by_group':{k:m(v) for k,v in sorted(by.items())},'examples':bad}

if __name__=='__main__':
    import os
    sys.path.insert(0, os.environ['TOKENIZER_PATH'])
    from nedo_turkish_tokenizer import NedoTurkishTokenizer
    T=NedoTurkishTokenizer(); rows=[T(w) for w,_,_,_ in CASES]
    print(json.dumps(eval_rows(os.environ.get('TOKENIZER_NAME','tokenizer'), rows), ensure_ascii=False, indent=2))
