"""Morphology utilities: suffix analysis, allomorph canonicalization, compound annotation.

This module provides:
- Suffix stripping and matching against the suffix table
- Allomorph → canonical morpheme mapping (e.g. "lar"/"ler" → "PL")
- Compound word detection and decomposition
- Acronym expansion annotation
"""

from __future__ import annotations

from ._acronym_table import ACRONYM_EXPANSIONS
from ._suffix_table import SUFFIX_ENTRIES, SUFFIX_MAP

                                                                               
                                                                   
                                                              

ALLOMORPH_MAP: dict[str, str] = {
    "lar": "PL",   "ler": "PL",
    "ı":   "ACC",  "i":   "ACC",  "u":   "ACC",  "ü":   "ACC",
    "yı":  "ACC",  "yi":  "ACC",  "yu":  "ACC",  "yü":  "ACC",
    "a":   "DAT",  "e":   "DAT",  "ya":  "DAT",  "ye":  "DAT",
    "da":  "LOC",  "de":  "LOC",  "ta":  "LOC",  "te":  "LOC",
    "dan": "ABL",  "den": "ABL",  "tan": "ABL",  "ten": "ABL",
    "ın":  "GEN",  "in":  "GEN",  "un":  "GEN",  "ün":  "GEN",
    "nın": "GEN",  "nin": "GEN",  "nun": "GEN",  "nün": "GEN",
    "la":  "INS",  "le":  "INS",  "yla": "INS",  "yle": "INS",
    "dı":  "PAST", "di":  "PAST", "du":  "PAST", "dü":  "PAST",
    "tı":  "PAST", "ti":  "PAST", "tu":  "PAST", "tü":  "PAST",
    "yor": "PROG", "iyor": "PROG", "ıyor": "PROG", "uyor": "PROG", "üyor": "PROG",
    "ar":  "AOR",  "er":  "AOR",
    "ır":  "AOR",  "ir":  "AOR",  "ur":  "AOR",  "ür":  "AOR",
    "mış": "EVID", "miş": "EVID", "muş": "EVID", "müş": "EVID",
    "ma":  "NEG",  "me":  "NEG",
    "mak": "INF",  "mek": "INF",
    "ım":  "1SG",  "im":  "1SG",  "um":  "1SG",  "üm":  "1SG",
    "iz":  "1PL",  "ız":  "1PL",  "uz":  "1PL",  "üz":  "1PL",
    "mı":  "Q",    "mi":  "Q",    "mu":  "Q",    "mü":  "Q",
    "lı":  "WITH", "li":  "WITH", "lu":  "WITH", "lü":  "WITH",
    "sız": "WITHOUT", "siz": "WITHOUT", "suz": "WITHOUT", "süz": "WITHOUT",
    "cı":  "AGT",  "ci":  "AGT",  "cu":  "AGT",  "cü":  "AGT",
    "çı":  "AGT",  "çi":  "AGT",  "çu":  "AGT",  "çü":  "AGT",
    "lık": "ABSTR", "lik": "ABSTR", "luk": "ABSTR", "lük": "ABSTR",
    "sa":  "COND", "se":  "COND",
    "ıl":  "PASS", "il":  "PASS", "ul":  "PASS", "ül":  "PASS",
}


                                                                              

KNOWN_COMPOUNDS: dict[str, list[str]] = {
    "başbakan":         ["baş", "bakan"],
    "cumhurbaşkanı":    ["cumhur", "başkan"],
    "dışişleri":        ["dış", "iş"],
    "içişleri":         ["iç", "iş"],
    "maliye":           ["mal", "iye"],
    "belediye":         ["beled", "iye"],
    "ayakkabı":         ["ayak", "kap"],
    "yelkovan":         ["yel", "kovan"],
    "saatlik":          ["saat", "lik"],
    "günlük":           ["gün", "lük"],
    "yıllık":           ["yıl", "lık"],
    "aylık":            ["ay", "lık"],
    "haftalık":         ["hafta", "lık"],
    "gastrointestinal": ["gastro", "intestinal"],
    "kardiyovasküler":  ["kardio", "vasküler"],
    "nöropsikiyatri":   ["nöro", "psikiyatri"],
    "biyokimya":        ["biyo", "kimya"],
    "mikrobiyoloji":    ["mikro", "biyoloji"],
    "farmakoloji":      ["farma", "koloji"],
    "patoloji":         ["pato", "loji"],
    "hematoloji":       ["hemato", "loji"],
    "nefroloji":        ["nefro", "loji"],
    "kardiyoloji":      ["kardio", "loji"],
    "radyoloji":        ["radyo", "loji"],
    "onkoloji":         ["onko", "loji"],
    "elektromanyetik":  ["elektro", "manyetik"],
    "termodinamik":     ["termo", "dinamik"],
    "hidroelektrik":    ["hidro", "elektrik"],
    "biyoinformatik":   ["biyo", "informatik"],
    "nanoteknoloji":    ["nano", "teknoloji"],
    "futbolcu":         ["futbol", "cu"],
    "basketbolcu":      ["basketbol", "cu"],
    "voleybolcu":       ["voleybol", "cu"],
}


                                                                              

def get_suffix_label(surface: str) -> str | None:
    """Return the morphological label for a suffix surface form, or None."""
    return SUFFIX_MAP.get(surface.lower())


def get_canonical(surface: str) -> str | None:
    """Return the canonical morpheme label for a suffix, or None."""
    return ALLOMORPH_MAP.get(surface.lower())


                                                                              

def annotate_canonical(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    """Add ``_canonical`` field to SUFFIX tokens (e.g. 'lar' → 'PL')."""
    result: list[dict[str, object]] = []
    for tok in tokens:
        if tok["token_type"] != "SUFFIX":
            result.append(tok)
            continue
        surface = str(tok["token"]).strip().lower()
        canonical = ALLOMORPH_MAP.get(surface)
        if canonical:
            result.append({**tok, "_canonical": canonical})
        else:
            result.append(tok)
    return result


def annotate_compounds(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    """Annotate ROOT tokens that are compound words."""
    result: list[dict[str, object]] = []
    for tok in tokens:
        if tok["token_type"] != "ROOT" or str(tok["token"]).strip().startswith("<"):
            result.append(tok)
            continue

        surface = str(tok["token"]).strip().lower()
        if surface in KNOWN_COMPOUNDS:
            result.append({
                **tok,
                "_compound": True,
                "_parts": KNOWN_COMPOUNDS[surface],
            })
        else:
            result.append(tok)
    return result


def annotate_acronyms(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    """Add ``_expansion`` to known acronyms; promote CAPS ROOTs to ACRONYM."""
    result: list[dict[str, object]] = []
    for tok in tokens:
        token_upper = str(tok["token"]).strip().upper()
        expansion = ACRONYM_EXPANSIONS.get(token_upper)

        if tok["token_type"] == "ACRONYM":
            if expansion:
                result.append({**tok, "_expansion": expansion, "_known_acronym": True})
            else:
                result.append(tok)
        elif tok["token_type"] == "ROOT" and (tok.get("_acronym") or tok.get("_caps")):
            if expansion:
                result.append({
                    **tok, "token_type": "ACRONYM",
                    "_expansion": expansion, "_known_acronym": True,
                })
            else:
                result.append(tok)
        else:
            result.append(tok)
    return result


                                 
ALLOMORPH_MAP.update({
    "abil": "ABIL", "ebil": "ABIL", "yabil": "ABIL", "yebil": "ABIL",
    "abilir": "ABIL", "ebilir": "ABIL", "yabilir": "ABIL", "yebilir": "ABIL",
    "acak": "FUT", "ecek": "FUT", "yacak": "FUT", "yecek": "FUT",
    "acağ": "FUT", "eceğ": "FUT", "yacağ": "FUT", "yeceğ": "FUT",
    "acağım": "FUT", "eceğim": "FUT", "yacağım": "FUT", "yeceğim": "FUT",
    "acağız": "FUT", "eceğiz": "FUT", "yacağız": "FUT", "yeceğiz": "FUT",
    "acaksın": "FUT", "eceksin": "FUT", "yacaksın": "FUT", "yeceksin": "FUT",
    "acaksınız": "FUT", "eceksiniz": "FUT", "yacaksınız": "FUT", "yeceksiniz": "FUT",
    "acaklar": "FUT", "ecekler": "FUT", "yacaklar": "FUT", "yecekler": "FUT",
    "ki": "KI",
})


                           
ALLOMORPH_MAP.update({
    "ımız":"P1PL", "imiz":"P1PL", "umuz":"P1PL", "ümüz":"P1PL",
    "mız":"P1PL", "miz":"P1PL", "muz":"P1PL", "müz":"P1PL",
    "ınız":"P2PL", "iniz":"P2PL", "unuz":"P2PL", "ünüz":"P2PL",
    "ız":"1PL", "iz":"1PL", "uz":"1PL", "üz":"1PL",
    "dık":"DIK", "dik":"DIK", "duk":"DIK", "dük":"DIK",
    "tık":"DIK", "tik":"DIK", "tuk":"DIK", "tük":"DIK",
    "cı":"AGT", "ci":"AGT", "cu":"AGT", "cü":"AGT",
    "çı":"AGT", "çi":"AGT", "çu":"AGT", "çü":"AGT",
    "la":"INS", "le":"INS",
})


                             
ALLOMORPH_MAP.update({
    "ım":"P1S", "im":"P1S", "um":"P1S", "üm":"P1S", "m":"P1S",
    "ın":"P2S", "in":"P2S", "un":"P2S", "ün":"P2S", "n":"P2S",
    "ınız":"P2PL", "iniz":"P2PL", "unuz":"P2PL", "ünüz":"P2PL",
    "nız":"P2PL", "niz":"P2PL", "nuz":"P2PL", "nüz":"P2PL",
})

                                   
ALLOMORPH_MAP.update({"ın": "GEN", "in": "GEN", "un": "GEN", "ün": "GEN", "n": "GEN"})


                             
                                                                               
                                                                        
ALLOMORPH_MAP.update({"bil": "ABIL"})
_v211_prev_annotate_canonical = annotate_canonical

def _v211_can(tok):
    return str(tok.get("_canonical") or tok.get("_suffix_label") or "").strip().lstrip("-").upper()

def annotate_canonical(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    result = _v211_prev_annotate_canonical(tokens)
    for i, tok in enumerate(result):
        if tok.get("token_type") != "SUFFIX":
            continue
        surf = str(tok.get("token", "")).lower()
        if surf not in {"ın", "in", "un", "ün"}:
            continue
        prev_can = _v211_can(result[i-1]) if i > 0 else ""
        next_can = _v211_can(result[i+1]) if i + 1 < len(result) else ""
        if prev_can == "PL" and next_can in {"ABL", "LOC"}:
            tok["_canonical"] = "P3PL"
    return result
