from pathlib import Path
                                         
p=Path('nedo_turkish_tokenizer/morphology.py')
t=p.read_text(encoding='utf-8')
if '# NEDO_V21_CANONICAL_FIX_CORE' not in t:
    t += '''\n\n# NEDO_V21_CANONICAL_FIX_CORE\nALLOMORPH_MAP.update({\n    "ım":"P1S", "im":"P1S", "um":"P1S", "üm":"P1S", "m":"P1S",\n    "ın":"P2S", "in":"P2S", "un":"P2S", "ün":"P2S", "n":"P2S",\n    "ınız":"P2PL", "iniz":"P2PL", "unuz":"P2PL", "ünüz":"P2PL",\n    "nız":"P2PL", "niz":"P2PL", "nuz":"P2PL", "nüz":"P2PL",\n})\n'''
    p.write_text(t,encoding='utf-8')
                                                               
p=Path('nedo_turkish_tokenizer/_suffix_table.py')
t=p.read_text(encoding='utf-8')
if '# NEDO_V21_SUFFIX_FIX_CORE' not in t:
    t += '''\n\n# NEDO_V21_SUFFIX_FIX_CORE\n_V21_SUFFIX_FIX_CORE = {\n    "ınız":"P2PL", "iniz":"P2PL", "unuz":"P2PL", "ünüz":"P2PL",\n    "nız":"P2PL", "niz":"P2PL", "nuz":"P2PL", "nüz":"P2PL",\n}\nfor _surface, _label in _V21_SUFFIX_FIX_CORE.items():\n    SUFFIX_MAP.setdefault(_surface, _label)\nSUFFIX_ENTRIES = sorted(SUFFIX_MAP.items(), key=lambda kv: len(kv[0]), reverse=True)\n'''
    p.write_text(t,encoding='utf-8')
                                                                                            
p=Path('nedo_turkish_tokenizer/segmentation.py')
t=p.read_text(encoding='utf-8')
if '# NEDO_V21_FIX_CORE_SELECTION' not in t:
    t += '''\n\n# NEDO_V21_FIX_CORE_SELECTION\nKNOWN_INTACT.update({"türkiye", "turkiye"})\n_V21_STRONG = _V21_STRONG | {"P2PL"}\n\ndef _v21_pick_chain(cands):\n    if not cands:\n        return None\n    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):\n        return None\n    if not any(_v21_whole_unknown(c) for c in cands) and cands[0].source != "suffix_chain":\n        return None\n    good=[]\n    for c in cands:\n        if c.source != "suffix_chain":\n            continue\n        labs=_v21_labels(c)\n        sc=len(labs)\n        strong=sum(1 for z in labs if z in _V21_STRONG)\n        rl=_v21_root_len(c)\n        known=_v21_root_known(c)\n        if strong == 0:\n            continue\n        if rl < 3 and not (known and strong >= 1):\n            continue\n        valid=(sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and known and rl >= 2)\n        if not valid:\n            continue\n        bonus=0\n        if "ABIL" in labs: bonus += 100\n        if "NEG" in labs and "FUT" in labs: bonus += 90\n        if "DIK" in labs: bonus += 85\n        if "P2PL" in labs: bonus += 30\n        if "KI" in labs: bonus += 15\n        unknown=sc-strong\n        good.append((bonus, strong, -unknown, -sc, rl, c.score, c))\n    if not good:\n        return None\n    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))\n    return good[0][6]\n\ndef select_best_candidate(candidates):\n    if not candidates:\n        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")\n    p=_v21_pick_chain(candidates)\n    if p is not None:\n        return p\n    if len(candidates)==1:\n        return candidates[0]\n    bs=candidates[0].score\n    tied=[c for c in candidates if c.score==bs]\n    if len(tied)==1:\n        return tied[0]\n    tied.sort(key=lambda c:(len(c.tokens), -max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)))\n    return tied[0]\n'''
    p.write_text(t,encoding='utf-8')
print('core_fixes_written')
