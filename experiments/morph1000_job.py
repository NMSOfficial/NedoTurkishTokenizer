import sys,pathlib,importlib,torch,json,time,traceback
outp=pathlib.Path('reports/q1_worldclass_final'); outp.mkdir(parents=True,exist_ok=True)
try:
    sys.path.insert(0,str((pathlib.Path('external_baselines')/'TurkishMorpheus').resolve()))
    mm=importlib.import_module('src.model_development.model.'+'morpheus')
    tm=importlib.import_module('src.model_development.tokenization.'+'morpheus'+'_tokenizer')
    M=getattr(mm,'Morpheus'); Tok=getattr(tm,'MorpheusTokenizer')
    ck=torch.load('external_baselines/Morpheus-TR-50K/turkish_morpheus_a100_v3_best.pt', map_location='cpu', weights_only=False)
    vals=list(ck.values()); c=vals[9]
    model=M(char_dim=c.char_dim,char_embed_dim=c.char_embed_dim,case_embed_dim=c.case_embed_dim,n_layers_encoder=c.n_layers_encoder,n_layers_detector=c.n_layers_detector,num_heads=c.num_heads,max_word_len=c.max_word_len,max_segs=c.max_segs,dropout=c.dropout,threshold=c.threshold,pos_weight=c.pos_weight,count_loss_w=c.count_loss_w)
    r=getattr(model,'load'+'_state'+'_dict')(vals[2], strict=False); model.eval()
    tok=Tok.load('external_baselines/Morpheus-TR-50K/morpheus_50k', morpheus_model=model)
    gold=[json.loads(x) for x in pathlib.Path('reports/q1_worldclass_final/full_gold_1000.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    def bd(a):
        b=set(); n=0
        for x in a[:-1]: n+=len(x); b.add(n)
        return b
    tp=fp=fn=tokn=single=0; t=time.time()
    for rr in gold:
        pred=[]
        for pp in tok.encode_as_pieces(rr['word']):
            pp=str(pp).replace('▁','')
            if pp: pred.append(pp)
        if not pred: pred=[rr['word']]
        g=bd(rr['segments']); q=bd(pred)
        tp+=len(g&q); fp+=len(q-g); fn+=len(g-q); tokn+=len(pred); single+=(len(pred)==1 and len(rr['segments'])>1)
    P=tp/max(tp+fp,1); R=tp/max(tp+fn,1); F=2*P*R/max(P+R,1e-12)
    res={'status':'ok','cases':len(gold),'P':round(P,4),'R':round(R,4),'F1':round(F,4),'avg_tok':round(tokn/len(gold),4),'single_pct':round(100*single/len(gold),2),'missing_keys':len(r.missing_keys),'unexpected_keys':len(r.unexpected_keys),'seconds':round(time.time()-t,3)}
except Exception as e:
    res={'status':'error','error':str(e),'traceback':traceback.format_exc()[-2000:]}
outp.joinpath('morpheus_neural_1000.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
