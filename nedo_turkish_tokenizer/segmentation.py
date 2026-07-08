"""Word-level segmentation with candidate generation and selection.

This is the core of the tokenizer.  For each word it:
1. Generates multiple segmentation candidates (whole-word ROOT, suffix
   chains, foreign root, etc.)
2. Scores each candidate deterministically
3. Selects the highest-scoring segmentation

The scoring rules are transparent and tunable:
- TDK root match gives a large bonus
- Domain vocabulary match gives a moderate bonus
- Longer roots are preferred over shorter ones
- Each recognised suffix adds a small bonus
- Unknown / unvalidated roots get a low base score
"""

from __future__ import annotations

import re
from typing import Any

from ._domain_vocab import ALL_DOMAIN_ROOTS
from ._suffix_table import (
    SHORT_AMBIGUOUS_SUFFIXES,
    SUFFIX_ENTRIES,
    SUFFIX_MAP,
)
from .normalization import has_turkish_chars, turkish_lower
from .resources import load_proper_nouns, load_tdk_words
from .types import PUNCT_CHARS, SegmentationCandidate, Token, is_punct_token

                                                                               
                                                                           
                                                                         
                                                                          

_TDK_BONUS = 10                                       
_DOMAIN_BONUS = 8                                         
_SUFFIX_BONUS = 2                                
_ROOT_LEN_WEIGHT = 2                                                                
_WHOLE_WORD_BONUS = 5                                                          
_FOREIGN_BASE = 3                                                         
_UNKNOWN_BASE = 1                                          
_SHORT_ROOT_PENALTY = 4                                                    
_MIN_ROOT_LEN = 2                                                  
_MAX_SUFFIX_DEPTH = 5                                         

                                                                               
                                                                        
                                                                         
                                                          
 
                                                                         
                                                                         

KNOWN_INTACT: frozenset[str] = frozenset({
                                                                 
                                                          
    "dedi", "dedim", "dedin", "dedik", "dediniz", "dediler",
    "demiş", "demişti", "demiştir",
    "dese", "desem", "desen", "desek",
    "der", "derim", "dersin", "deriz",
    "denir", "dendi", "denmiş",
                                                     
    "yemiş", "yese", "yesem", "yesen",
    "yer", "yerim", "yersin", "yeriz",
    "yenir", "yendi", "yenmiş",
                                                                       
                                                                           
    "diye", "niye", "nice",
})


                                                                               

                                                               
_APOSTROPHE_RE = re.compile(r"(['\u2019])")

                                                         
_LEADING_PUNCT_RE = re.compile(r"^([^\w]+)")
_TRAILING_PUNCT_RE = re.compile(r"([^\w]+)$")


def _split_punctuation(word: str) -> list[tuple[str, str]]:
    """Split a raw word token into (text, type) pairs.

    Separates leading and trailing punctuation from the core word.
    For example: ``'"hello,'`` → ``[('"', 'PUNCT'), ('hello', 'WORD'), (',', 'PUNCT')]``
    """
    if not word:
        return []

    parts: list[tuple[str, str]] = []

                                              
    if is_punct_token(word):
        return [(word, "PUNCT")]

                               
    lead_m = _LEADING_PUNCT_RE.match(word)
    if lead_m:
        for ch in lead_m.group(1):
            parts.append((ch, "PUNCT"))
        word = word[lead_m.end():]

                                
    trail_m = _TRAILING_PUNCT_RE.search(word)
    trailing: list[tuple[str, str]] = []
    if trail_m:
        for ch in trail_m.group(1):
            trailing.append((ch, "PUNCT"))
        word = word[:trail_m.start()]

    if word:
        parts.append((word, "WORD"))

    parts.extend(trailing)
    return parts


                                                                               

def split_into_words(text: str) -> list[str]:
    """Split text into whitespace-delimited word tokens.

    Preserves the original casing and punctuation within each token.
    """
    return text.split()


                                                                              

def _generate_suffix_candidates(
    word_lower: str,
    tdk: set[str],
    domain_roots: frozenset[str],
    depth: int = 0,
) -> list[SegmentationCandidate]:
    """Recursively generate segmentation candidates by stripping suffixes.

    Tries each suffix in the table (longest first).  If the remainder
    is a valid root, produces a candidate.  If not, recurses to try
    stripping additional suffixes from the remainder.
    """
    if depth >= _MAX_SUFFIX_DEPTH or len(word_lower) < _MIN_ROOT_LEN:
        return []

    candidates: list[SegmentationCandidate] = []

    for suffix_surface, suffix_label in SUFFIX_ENTRIES:
        if not word_lower.endswith(suffix_surface):
            continue

        remainder = word_lower[: -len(suffix_surface)]
        if len(remainder) < _MIN_ROOT_LEN:
            continue

                                                           
        if suffix_surface in SHORT_AMBIGUOUS_SUFFIXES and len(remainder) < 3:
            continue

        suffix_token = Token(
            text=suffix_surface,
            token_type="SUFFIX",
            metadata={"_suffix_label": suffix_label},
        )

                                            
        root_in_tdk = remainder in tdk
        root_in_domain = remainder in domain_roots
        root_score = len(remainder) * _ROOT_LEN_WEIGHT

        if root_in_tdk:
            root_score += _TDK_BONUS
        elif root_in_domain:
            root_score += _DOMAIN_BONUS
        else:
            root_score += _UNKNOWN_BASE

                                                                       
                                                                      
                                                                       
                                                          
        if len(remainder) <= _MIN_ROOT_LEN:
            root_score -= _SHORT_ROOT_PENALTY

        if root_in_tdk or root_in_domain:
                                                              
            root_token = Token(
                text=remainder,
                token_type="ROOT",
                metadata={"_tdk": root_in_tdk, "_domain": root_in_domain} if root_in_domain else {},
            )
            total_score = root_score + _SUFFIX_BONUS
            candidates.append(SegmentationCandidate(
                tokens=[root_token, suffix_token],
                score=total_score,
                source="suffix_chain",
            ))

                                                                 
        if depth < _MAX_SUFFIX_DEPTH - 1:
            sub_candidates = _generate_suffix_candidates(
                remainder, tdk, domain_roots, depth + 1
            )
            for sc in sub_candidates:
                                                                      
                if sc.score > len(remainder) + _UNKNOWN_BASE:
                    extended = SegmentationCandidate(
                        tokens=sc.tokens + [suffix_token],
                        score=sc.score + _SUFFIX_BONUS,
                        source="suffix_chain",
                    )
                    candidates.append(extended)

    return candidates


def generate_candidates(
    word: str,
    tdk: set[str],
    domain_roots: frozenset[str],
    caps_set: frozenset[str],
) -> list[SegmentationCandidate]:
    """Generate all plausible segmentation candidates for a single word.

    Returns a list of candidates sorted by score (highest first).
    """
    wl = turkish_lower(word)
    candidates: list[SegmentationCandidate] = []

    is_caps = wl in caps_set
    is_tr_chars = has_turkish_chars(wl)

                                                                           
                                                                      
    if wl in KNOWN_INTACT:
        root_meta_intact: dict[str, Any] = {}
        if is_caps:
            root_meta_intact["_caps"] = True
        return [SegmentationCandidate(
            tokens=[Token(text=wl, token_type="ROOT", metadata=root_meta_intact)],
            score=len(wl) * _ROOT_LEN_WEIGHT + _TDK_BONUS + _WHOLE_WORD_BONUS,
            source="known_intact",
        )]

                                                                           
    in_tdk = wl in tdk
    in_proper = wl in load_proper_nouns()
    in_domain = wl in domain_roots
    whole_score = len(wl) * _ROOT_LEN_WEIGHT
    if in_tdk or in_proper:
                                                                         
                                                                  
                       
        whole_score += _TDK_BONUS + _WHOLE_WORD_BONUS
    elif in_domain:
        whole_score += _DOMAIN_BONUS + _WHOLE_WORD_BONUS
    else:
        whole_score += _UNKNOWN_BASE

    root_meta: dict[str, Any] = {}
    if is_caps:
        root_meta["_caps"] = True
    if in_domain:
        root_meta["_domain"] = True

    whole_root = Token(text=wl, token_type="ROOT", metadata=root_meta)
    candidates.append(SegmentationCandidate(
        tokens=[whole_root],
        score=whole_score,
        source="whole_word",
    ))

                                                                           
    suffix_cands = _generate_suffix_candidates(wl, tdk, domain_roots)
    for sc in suffix_cands:
                                               
        if is_caps and sc.tokens:
            sc.tokens[0].metadata["_caps"] = True
        candidates.append(sc)

                                                                           
    if not in_tdk and not in_proper and not is_tr_chars and len(wl) >= 2:
        foreign_token = Token(
            text=wl, token_type="FOREIGN",
            metadata={"_foreign": True},
        )
                                                                        
                                                                  
        foreign_score = _FOREIGN_BASE + len(wl)
        candidates.append(SegmentationCandidate(
            tokens=[foreign_token],
            score=foreign_score,
            source="foreign",
        ))

                                              
    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates


                                                                               

def select_best_candidate(
    candidates: list[SegmentationCandidate],
) -> SegmentationCandidate:
    """Select the best segmentation among candidates.

    Picks the highest-scoring candidate.  Ties are broken by:
    1. Fewer tokens (less fragmentation)
    2. Longer root token
    """
    if not candidates:
                                                       
        return SegmentationCandidate(
            tokens=[Token(text="", token_type="ROOT")],
            score=0.0,
            source="fallback",
        )

    if len(candidates) == 1:
        return candidates[0]

    best_score = candidates[0].score
    tied = [c for c in candidates if c.score == best_score]

    if len(tied) == 1:
        return tied[0]

                                                        
    def _tie_key(c: SegmentationCandidate) -> tuple[int, int]:
        root_len = max(
            (len(t.text) for t in c.tokens if t.token_type == "ROOT"),
            default=0,
        )
        return (len(c.tokens), -root_len)

    tied.sort(key=_tie_key)
    return tied[0]


                                                                               

def segment_word(
    word: str,
    tdk: set[str],
    domain_roots: frozenset[str],
    caps_set: frozenset[str],
) -> list[dict[str, object]]:
    """Segment a single word into token dicts.

    This is the main entry point for per-word segmentation.  It handles
    punctuation splitting, candidate generation, and selection.

    Args:
        word: Raw word string (may include surrounding punctuation).
        tdk: TDK dictionary set.
        domain_roots: Domain vocabulary set.
        caps_set: Set of words that were originally ALL CAPS.

    Returns:
        List of token dicts ready for inclusion in the output.
    """
    parts = _split_punctuation(word)
    result: list[dict[str, object]] = []
    is_first = True

    for text, part_type in parts:
        if part_type == "PUNCT":
            prefix = " " if is_first else ""
            result.append({
                "token": f"{prefix}{text}",
                "token_type": "PUNCT",
                "morph_pos": 0,
                "_punct": True,
            })
            is_first = False
            continue

                             
                                              
        if "'" in text or "\u2019" in text:
            apo_tokens = _segment_apostrophe_word(text, tdk, domain_roots, caps_set)
            for i, t in enumerate(apo_tokens):
                if i == 0 and is_first:
                    t["token"] = f" {t['token'].lstrip()}"
                result.append(t)
            is_first = False
            continue

                                                             
        candidates = generate_candidates(text, tdk, domain_roots, caps_set)
        best = select_best_candidate(candidates)

                                                                            
                                                                             
                                                                           
        norm_join = "".join(str(t.text).strip() for t in best.tokens)
        surface_projectable = turkish_lower(norm_join) == turkish_lower(str(text)) and len(norm_join) == len(str(text))
        surface_offset = 0

        for i, token in enumerate(best.tokens):
            tok_dict = token.to_dict()
            if surface_projectable:
                raw_token = str(tok_dict.get("token", "")).strip()
                raw_len = len(raw_token)
                surface_piece = str(text)[surface_offset:surface_offset + raw_len]
                surface_offset += raw_len
                if surface_piece and surface_piece != raw_token:
                    tok_dict["_normalized_form"] = raw_token
                    tok_dict["token"] = surface_piece
                                                               
            if i == 0 and is_first:
                tok_dict["token"] = f" {tok_dict['token'].lstrip()}"
                               
            if i == 0:
                tok_dict["morph_pos"] = 0
            else:
                tok_dict["morph_pos"] = i
            result.append(tok_dict)

        is_first = False

    return result


def _segment_apostrophe_word(
    word: str,
    tdk: set[str],
    domain_roots: frozenset[str],
    caps_set: frozenset[str],
) -> list[dict[str, object]]:
    """Segment a word containing an apostrophe.

    Splits at the apostrophe and determines whether the base is Turkish
    (proper name) or foreign.
    """
    from .apostrophe import is_turkish_base                                  

                                  
    apo_pos = word.find("'")
    if apo_pos == -1:
        apo_pos = word.find("\u2019")
    if apo_pos == -1:
                                                                        
        candidates = generate_candidates(word, tdk, domain_roots, caps_set)
        best = select_best_candidate(candidates)
        return [t.to_dict() for t in best.tokens]

    base = word[:apo_pos]
    suffix = word[apo_pos + 1:]

    wl = turkish_lower(base)
    is_caps = wl in caps_set

    if is_turkish_base(base):
                                                       
        suffix_label = SUFFIX_MAP.get(suffix.lower(), "-SFX")
        tokens: list[dict[str, object]] = [
            {
                "token": base, "token_type": "ROOT", "morph_pos": 0,
                **( {"_caps": True} if is_caps else {}),
            },
            {
                "token": "'", "token_type": "PUNCT", "morph_pos": 0,
                "_punct": True,
            },
        ]
        if suffix:
            tokens.append({
                "token": suffix, "token_type": "SUFFIX", "morph_pos": 1,
                "_apo_suffix": True, "_suffix_label": suffix_label,
            })
        return tokens
    else:
                                        
        suffix_label = SUFFIX_MAP.get(suffix.lower(), "-SFX")
        tokens = [
            {
                "token": base, "token_type": "FOREIGN", "morph_pos": 0,
                "_foreign": True,
            },
        ]
        if suffix:
            tokens.append({
                "token": suffix, "token_type": "SUFFIX", "morph_pos": 1,
                "_apo_suffix": True, "_suffix_label": suffix_label,
            })
        return tokens


                           
_MAX_SUFFIX_DEPTH = max(_MAX_SUFFIX_DEPTH, 8)
_V21_STRONG = {"ACC","DAT","LOC","ABL","GEN","PL","P1S","P2S","P3S","P1PL","P2PL","P3PL","KI","ABIL","FUT","PROG","PAST","NEG"}

def _v21_label(x):
    return str(x or "").strip().lstrip("-").upper()

def _v21_variants(s):
    out=[(s,None)]
    if len(s)>=3:
        m={"b":"p","c":"ç","d":"t","ğ":"k"}
        if s[-1] in m:
            out.append((s[:-1]+m[s[-1]], s[-1]+">"+m[s[-1]]))
        if s[-1]=="y" and len(s)>=4:
            out.append((s[:-1], "buffer_y"))
    seen=set(); ans=[]
    for a,b in out:
        if a not in seen:
            seen.add(a); ans.append((a,b))
    return ans

def _v21_match_root(rem, tdk, domain_roots):
    for cand, alt in _v21_variants(rem):
        if cand in tdk:
            return True, False, cand, alt
        if cand in domain_roots:
            return False, True, cand, alt
    return False, False, rem, None

def _generate_suffix_candidates(word_lower, tdk, domain_roots, depth=0):
    if depth >= _MAX_SUFFIX_DEPTH or len(word_lower) < _MIN_ROOT_LEN:
        return []
    ans=[]
    for suf, lab in SUFFIX_ENTRIES:
        if not word_lower.endswith(suf):
            continue
        rem = word_lower[:-len(suf)]
        if len(rem) < _MIN_ROOT_LEN:
            continue
        if suf in SHORT_AMBIGUOUS_SUFFIXES and len(rem) < 3:
            continue
        st = Token(text=suf, token_type="SUFFIX", metadata={"_suffix_label": lab})
        in_tdk, in_dom, canon, alt = _v21_match_root(rem, tdk, domain_roots)
        rs = len(rem) * _ROOT_LEN_WEIGHT + (_TDK_BONUS if in_tdk else (_DOMAIN_BONUS if in_dom else _UNKNOWN_BASE))
        if len(rem) <= _MIN_ROOT_LEN:
            rs -= _SHORT_ROOT_PENALTY
        if in_tdk or in_dom:
            meta={"_tdk": in_tdk, "_domain": in_dom}
            if canon != rem:
                meta["_canonical_root"] = canon
            if alt:
                meta["_root_alternation"] = alt
            rt = Token(text=rem, token_type="ROOT", metadata=meta)
            ans.append(SegmentationCandidate(tokens=[rt, st], score=rs+_SUFFIX_BONUS, source="suffix_chain"))
        if depth < _MAX_SUFFIX_DEPTH - 1:
            for sc in _generate_suffix_candidates(rem, tdk, domain_roots, depth+1):
                if sc.score > len(rem) + _UNKNOWN_BASE:
                    ans.append(SegmentationCandidate(tokens=sc.tokens+[st], score=sc.score+_SUFFIX_BONUS, source="suffix_chain"))
    return ans

def _v21_labels(c):
    return [_v21_label(t.metadata.get("_suffix_label")) for t in c.tokens if t.token_type=="SUFFIX"]

def _v21_whole_unknown(c):
    if c.source != "whole_word" or not c.tokens:
        return False
    n=len(c.tokens[0].text.strip())
    return c.score <= n*_ROOT_LEN_WEIGHT + _UNKNOWN_BASE + 0.001

def _v21_pick_chain(cands):
    if not cands or not _v21_whole_unknown(cands[0]):
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c)
        sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG)
        root_len=max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)
        if root_len < 3 or strong == 0:
            continue
        if (sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and root_len >= 4):
            good.append((strong, sc, c.score, root_len, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3]))
    return good[0][4]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p=_v21_pick_chain(candidates)
    if p is not None:
        return p
    if len(candidates)==1:
        return candidates[0]
    bs=candidates[0].score
    tied=[c for c in candidates if c.score==bs]
    if len(tied)==1:
        return tied[0]
    def key(c):
        r=max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)
        return (len(c.tokens), -r)
    tied.sort(key=key)
    return tied[0]


                         
_V21_STRONG = _V21_STRONG | {"1PL", "DIK", "AGT", "INS"}

def _v21_pick_chain(cands):
    if not cands or not _v21_whole_unknown(cands[0]):
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c)
        sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG)
        root_len=max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)
        if root_len < 3 or strong == 0:
            continue
        if (sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and root_len >= 4):
            unknown=sc-strong
            good.append((root_len, -unknown, -sc, strong, c.score, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4]))
    return good[0][5]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p=_v21_pick_chain(candidates)
    if p is not None:
        return p
    if len(candidates)==1:
        return candidates[0]
    bs=candidates[0].score
    tied=[c for c in candidates if c.score==bs]
    if len(tied)==1:
        return tied[0]
    def key(c):
        r=max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)
        return (len(c.tokens), -r)
    tied.sort(key=key)
    return tied[0]


                   
def _v21_root_len(c):
    return max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)

def _v21_root_known(c):
    for t in c.tokens:
        if t.token_type == "ROOT":
            m=t.metadata
            return bool(m.get("_tdk") or m.get("_domain") or m.get("_canonical_root"))
    return False

def _v21_pick_chain(cands):
    if not cands or not _v21_whole_unknown(cands[0]):
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c)
        sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG)
        rl=_v21_root_len(c)
        known=_v21_root_known(c)
        if strong == 0:
            continue
        if rl < 3 and not (known and (strong >= 1)):
            continue
        valid = (sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and known and rl >= 2)
        if not valid:
            continue
        bonus=0
        if "ABIL" in labs:
            bonus += 100
        if "NEG" in labs and "FUT" in labs:
            bonus += 90
        if "KI" in labs:
            bonus += 15
        unknown=sc-strong
        good.append((bonus, strong, -unknown, -sc, rl, c.score, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))
    return good[0][6]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p=_v21_pick_chain(candidates)
    if p is not None:
        return p
    if len(candidates)==1:
        return candidates[0]
    bs=candidates[0].score
    tied=[c for c in candidates if c.score==bs]
    if len(tied)==1:
        return tied[0]
    tied.sort(key=lambda c:(len(c.tokens), -max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)))
    return tied[0]


                         
def _v21_variants(s):
    out=[(s,None)]
    if len(s)>=2:
        out.append((s+"mak", "verb_mak"))
        out.append((s+"mek", "verb_mek"))
    if len(s)>=3:
        m={"b":"p","c":"ç","d":"t","ğ":"k"}
        if s[-1] in m:
            base=s[:-1]+m[s[-1]]
            out.append((base, s[-1]+">"+m[s[-1]]))
            out.append((base+"mak", s[-1]+">"+m[s[-1]]+"+mak"))
            out.append((base+"mek", s[-1]+">"+m[s[-1]]+"+mek"))
        if s[-1]=="y" and len(s)>=4:
            base=s[:-1]
            out.append((base, "buffer_y"))
            out.append((base+"mak", "buffer_y+mak"))
            out.append((base+"mek", "buffer_y+mek"))
    seen=set(); ans=[]
    for a,b in out:
        if a not in seen:
            seen.add(a); ans.append((a,b))
    return ans


                         
def _v21_pick_chain(cands):
    if not cands:
        return None
                                                                               
                                                                             
                                                                               
    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):
        return None
    if not any(_v21_whole_unknown(c) for c in cands) and cands[0].source != "suffix_chain":
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c)
        sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG)
        rl=_v21_root_len(c)
        known=_v21_root_known(c)
        if strong == 0:
            continue
        if rl < 3 and not (known and strong >= 1):
            continue
        valid=(sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and known and rl >= 2)
        if not valid:
            continue
        bonus=0
        if "ABIL" in labs:
            bonus += 100
        if "NEG" in labs and "FUT" in labs:
            bonus += 90
        if "KI" in labs:
            bonus += 15
        unknown=sc-strong
        good.append((bonus, strong, -unknown, -sc, rl, c.score, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))
    return good[0][6]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p=_v21_pick_chain(candidates)
    if p is not None:
        return p
    if len(candidates)==1:
        return candidates[0]
    bs=candidates[0].score
    tied=[c for c in candidates if c.score==bs]
    if len(tied)==1:
        return tied[0]
    tied.sort(key=lambda c:(len(c.tokens), -max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)))
    return tied[0]


                             
KNOWN_INTACT = frozenset(set(KNOWN_INTACT) | {"türkiye", "turkiye"})
_V21_STRONG = _V21_STRONG | {"P2PL"}

def _v21_pick_chain(cands):
    if not cands:
        return None
    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):
        return None
    if not any(_v21_whole_unknown(c) for c in cands) and cands[0].source != "suffix_chain":
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c)
        sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG)
        rl=_v21_root_len(c)
        known=_v21_root_known(c)
        if strong == 0:
            continue
        if rl < 3 and not (known and strong >= 1):
            continue
        valid=(sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and known and rl >= 2)
        if not valid:
            continue
        bonus=0
        if "ABIL" in labs: bonus += 100
        if "NEG" in labs and "FUT" in labs: bonus += 90
        if "DIK" in labs: bonus += 85
        if "P2PL" in labs: bonus += 30
        if "KI" in labs: bonus += 15
        unknown=sc-strong
        good.append((bonus, strong, -unknown, -sc, rl, c.score, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))
    return good[0][6]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p=_v21_pick_chain(candidates)
    if p is not None:
        return p
    if len(candidates)==1:
        return candidates[0]
    bs=candidates[0].score
    tied=[c for c in candidates if c.score==bs]
    if len(tied)==1:
        return tied[0]
    tied.sort(key=lambda c:(len(c.tokens), -max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)))
    return tied[0]

                                  
_V21_STRONG = _V21_STRONG | {"DI1PL", "DI2PL", "DI3PL", "DIK"}

def _v21_pick_chain(cands):
    if not cands:
        return None
    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):
        return None
    if not any(_v21_whole_unknown(c) for c in cands) and cands[0].source != "suffix_chain":
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c); sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG or z.startswith("DI"))
        rl=_v21_root_len(c); known=_v21_root_known(c)
        if strong==0 or (rl<3 and not (known and strong>=1)):
            continue
        valid=(sc>=2 and strong>=2) or (sc==1 and labs[0] in {"FUT","ABIL","PROG","PAST"} and known and rl>=2)
        if not valid:
            continue
        bonus=(100 if "ABIL" in labs else 0)+(90 if "NEG" in labs and "FUT" in labs else 0)+(85 if any(z.startswith("DI") for z in labs) else 0)+(30 if ("P2PL" in labs or "2PL" in labs) else 0)+(15 if "KI" in labs else 0)
        good.append((bonus,strong,-(sc-strong),-sc,rl,c.score,c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))
    return good[0][6]

                           
_v21_prev_variants_edfix = _v21_variants
def _v21_variants(s):
    out = list(_v21_prev_variants_edfix(s))
    if len(s) >= 2 and s[-1] == "d":
        b = s[:-1] + "t"
        out.extend([(b, "d>t"), (b+"mak", "d>t+mak"), (b+"mek", "d>t+mek")])
    seen=set(); ans=[]
    for a,b in out:
        if a not in seen:
            seen.add(a); ans.append((a,b))
    return ans

                                        
_v21_prev_generate_candidates_final = generate_candidates
def _v21_unknown_suffix_candidates(wl, depth=0):
    if depth >= _MAX_SUFFIX_DEPTH or len(wl) < _MIN_ROOT_LEN:
        return []
    ans=[]
    for suf, lab in SUFFIX_ENTRIES:
        if not wl.endswith(suf):
            continue
        rem=wl[:-len(suf)]
        if len(rem) < 3:
            continue
        labn=_v21_label(lab)
        st=Token(text=suf, token_type="SUFFIX", metadata={"_suffix_label": lab})
        if depth < _MAX_SUFFIX_DEPTH-1:
            for sc in _v21_unknown_suffix_candidates(rem, depth+1):
                ans.append(SegmentationCandidate(tokens=sc.tokens+[st], score=sc.score+_SUFFIX_BONUS, source="suffix_chain"))
        if labn in _V21_STRONG or labn.startswith("DI"):
            rtype="FOREIGN" if not has_turkish_chars(rem) else "ROOT"
            meta={"_foreign_suffix_root": True} if rtype=="FOREIGN" else {"_unknown_suffix_root": True}
            ans.append(SegmentationCandidate(tokens=[Token(text=rem, token_type=rtype, metadata=meta), st], score=len(rem)+_SUFFIX_BONUS, source="suffix_chain"))
    return ans

def generate_candidates(word, tdk, domain_roots, caps_set):
    cands=_v21_prev_generate_candidates_final(word, tdk, domain_roots, caps_set)
    cands.extend(_v21_unknown_suffix_candidates(turkish_lower(word)))
    cands.sort(key=lambda c:c.score, reverse=True)
    return cands

                                  
def _v21_final_chain_pick(cands):
    if not cands:
        return None
    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs=_v21_labels(c); sc=len(labs)
        strong=sum(1 for z in labs if z in _V21_STRONG or z.startswith("DI"))
        rl=max((len(t.text) for t in c.tokens if t.token_type in {"ROOT","FOREIGN"}), default=0)
        if rl < 2 or strong == 0:
            continue
        if not ((sc >= 2 and strong >= 2) or (sc == 1 and labs[0] in {"FUT","ABIL","PROG","PAST"})):
            continue
        bonus=(100 if "ABIL" in labs else 0)+(90 if "NEG" in labs and "FUT" in labs else 0)+(85 if any(z.startswith("DI") for z in labs) else 0)+(30 if ("P1PL" in labs or "P2PL" in labs or "1PL" in labs) else 0)+(15 if "KI" in labs else 0)
        good.append((bonus,strong,-(sc-strong),-sc,rl,c.score,c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))
    return good[0][6]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p=_v21_final_chain_pick(candidates)
    if p is not None:
        return p
    if len(candidates)==1:
        return candidates[0]
    bs=candidates[0].score
    tied=[c for c in candidates if c.score==bs]
    if len(tied)==1:
        return tied[0]
    tied.sort(key=lambda c:(len(c.tokens), -max((len(t.text) for t in c.tokens if t.token_type=="ROOT"), default=0)))
    return tied[0]

                                         
_v21_prev_final_chain_pick_guard = _v21_final_chain_pick
def _v21_final_chain_pick(cands):
    if cands and cands[0].source == "known_intact":
        return None
    return _v21_prev_final_chain_pick_guard(cands)


                               
                                                      
                                                                             
                                                            
                                                                              
                                                     
                                                                                
_V211_CAP_PROPER = {"roma", "güler", "oytun"}
_V211_ABIL_SURFACES = {"abil", "ebil", "yabil", "yebil", "abilir", "ebilir", "yabilir", "yebilir"}
_v211_prev_generate_candidates = generate_candidates

def generate_candidates(word, tdk, domain_roots, caps_set):
    cands = _v211_prev_generate_candidates(word, tdk, domain_roots, caps_set)
    wl = turkish_lower(str(word))
                                                                            
                                                                                           
    if str(word) and str(word)[0].isupper() and wl in _V211_CAP_PROPER:
        top = max((c.score for c in cands), default=0)
        cands.append(SegmentationCandidate(
            tokens=[Token(text=wl, token_type="ROOT", metadata={"_proper": True, "_known_intact": True})],
            score=top + 100,
            source="known_intact",
        ))
        cands.sort(key=lambda c: c.score, reverse=True)
    return cands

def _v211_chain_features(c):
    labs = _v21_labels(c)
    suffixes = [t for t in c.tokens if t.token_type == "SUFFIX"]
    root_len = max((len(t.text) for t in c.tokens if t.token_type in {"ROOT", "FOREIGN"}), default=0)
    known = _v21_root_known(c)
    good_abil = any((_v21_label(t.metadata.get("_suffix_label")) == "ABIL" and t.text in _V211_ABIL_SURFACES) for t in suffixes)
    bad_abil_split = False
    for i in range(1, len(suffixes)):
        if _v21_label(suffixes[i].metadata.get("_suffix_label")) == "ABIL" and suffixes[i].text == "bil":
            if _v21_label(suffixes[i-1].metadata.get("_suffix_label")) == "DAT":
                bad_abil_split = True
    has_dik = any(z.startswith("DI") or z == "DIK" for z in labs)
    has_p2pl = ("P2PL" in labs or "2PL" in labs)
    has_neg_fut = ("NEG" in labs and "FUT" in labs)
    has_ki = "KI" in labs
                                                                                                         
    bad_1pl_noun_split = bool(labs and labs[0] == "1PL" and ("PL" in labs or "GEN" in labs or "ABL" in labs))
    strong = sum(1 for z in labs if z in _V21_STRONG or z.startswith("DI") or z == "DIK")
    return labs, suffixes, root_len, known, good_abil, bad_abil_split, has_dik, has_p2pl, has_neg_fut, has_ki, bad_1pl_noun_split, strong

def _v211_pick_chain(cands):
    if not cands:
        return None
    if cands[0].source == "known_intact":
        return None
    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):
        return None
    good = []
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs, suffixes, root_len, known, good_abil, bad_abil_split, has_dik, has_p2pl, has_neg_fut, has_ki, bad_1pl_noun_split, strong = _v211_chain_features(c)
        sc = len(labs)
        if root_len < 2 or strong == 0:
            continue
        valid = (
            good_abil or
            (has_dik and (has_p2pl or "P1PL" in labs or "P1S" in labs)) or
            has_neg_fut or
            (known and sc >= 2 and strong >= 2) or
            (sc == 1 and labs[0] in {"FUT", "ABIL", "PROG", "PAST"} and known)
        )
        if not valid:
            continue
        special = 0
        if good_abil: special += 10000
        if has_dik and has_p2pl: special += 7000
        elif has_dik: special += 2500
        if has_neg_fut: special += 2000
        if has_ki: special += 500
        if bad_abil_split: special -= 9000
        if bad_1pl_noun_split: special -= 5000
        if not known: special -= 1000
                                                                                                     
        good.append((special, int(known), c.score, root_len, strong, -sc, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]))
    return good[0][6]

def select_best_candidate(candidates):
    if not candidates:
        return SegmentationCandidate(tokens=[Token(text="", token_type="ROOT")], score=0.0, source="fallback")
    p = _v211_pick_chain(candidates)
    if p is not None:
        return p
    if len(candidates) == 1:
        return candidates[0]
    best_score = candidates[0].score
    tied = [c for c in candidates if c.score == best_score]
    if len(tied) == 1:
        return tied[0]
    tied.sort(key=lambda c: (len(c.tokens), -max((len(t.text) for t in c.tokens if t.token_type == "ROOT"), default=0)))
    return tied[0]


                             
                                                                         
                                                              
def _v211_has_split_p1pl(labs):
    for a, b in zip(labs, labs[1:]):
        if a in {"1SG", "P1S"} and b in {"1PL", "P1PL"}:
            return True
    return False

def _v211_pick_chain(cands):
    if not cands:
        return None
    if cands[0].source == "known_intact":
        return None
    if cands[0].source == "whole_word" and not _v21_whole_unknown(cands[0]):
        return None
    good=[]
    for c in cands:
        if c.source != "suffix_chain":
            continue
        labs, suffixes, root_len, known, good_abil, bad_abil_split, has_dik, has_p2pl, has_neg_fut, has_ki, bad_1pl_noun_split, strong = _v211_chain_features(c)
        sc=len(labs)
        if root_len < 2 or strong == 0:
            continue
        has_p1pl = "P1PL" in labs
        split_p1pl = _v211_has_split_p1pl(labs)
        valid = (
            good_abil or
            has_p1pl or
            (has_dik and (has_p2pl or has_p1pl or "P1S" in labs)) or
            has_neg_fut or
            (known and sc >= 2 and strong >= 2) or
            (sc == 1 and labs[0] in {"FUT", "ABIL", "PROG", "PAST"} and known)
        )
        if not valid:
            continue
        special=0
        if good_abil: special += 10000
        if has_dik and has_p2pl: special += 7000
        elif has_dik: special += 2500
        if has_p1pl: special += 3000
        if has_neg_fut: special += 2000
        if has_ki: special += 500
        if bad_abil_split: special -= 9000
        if split_p1pl: special -= 8000
        if bad_1pl_noun_split: special -= 5000
        if not known: special -= 1000
        good.append((special, int(known), c.score, root_len, strong, -sc, c))
    if not good:
        return None
    good.sort(reverse=True, key=lambda x:(x[0],x[1],x[2],x[3],x[4],x[5]))
    return good[0][6]
