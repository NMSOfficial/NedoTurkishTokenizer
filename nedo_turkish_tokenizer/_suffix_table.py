"""Turkish suffix pattern table (260+ entries).

Maps surface-form suffixes to morphological labels.  Used by the
segmentation engine for candidate generation (suffix stripping) and by
the post-annotation layer for ``_suffix_label`` metadata.

Suffixes are sorted longest-first at module load time so that the
candidate generator always tries the most specific match first.

Design note: some surface forms are ambiguous (e.g. "in" can be GEN or
2SG).  This table assigns a single canonical label per surface form —
the most common interpretation in written Turkish.  The candidate scoring
system resolves segmentation ambiguity via root validation, not via
suffix-label disambiguation.
"""

from __future__ import annotations

                                                                               
                                                      

SUFFIX_MAP: dict[str, str] = {
                                                                           
    "leri": "-PL+ACC",   "ları": "-PL+ACC",
    "lere": "-PL+DAT",   "lara": "-PL+DAT",
    "lerin": "-PL+GEN",  "ların": "-PL+GEN",
    "lerde": "-PL+LOC",  "larda": "-PL+LOC",
    "lerden": "-PL+ABL",  "lardan": "-PL+ABL",
    "lerle": "-PL+INS",  "larla": "-PL+INS",
    "lerce": "-PL+EQU",  "larca": "-PL+EQU",
                                                                           
    "yon": "-YON",   "iyon": "-YON",   "asyon": "-YON",   "izasyon": "-YON",
                                                                           
    "sal": "-ADJ.TR",  "sel": "-ADJ.TR",
                                                                           
    "imiz": "-P1PL",  "ımız": "-P1PL",  "umuz": "-P1PL",  "ümüz": "-P1PL",
    "iniz": "-P2PL",  "ınız": "-P2PL",  "unuz": "-P2PL",  "ünüz": "-P2PL",
                                                                           
    "ımı": "-P1+ACC",   "imi": "-P1+ACC",   "umu": "-P1+ACC",   "ümü": "-P1+ACC",
    "ıyla": "-INS.COMP", "iyle": "-INS.COMP", "uyla": "-INS.COMP", "üyle": "-INS.COMP",
    "kten": "-ABL.COMP", "ğından": "-ABL.COMP", "ğinden": "-ABL.COMP",
    "yla": "-COM",  "yle": "-COM",
                                                                           
    "liği": "-ABSTR+P3",   "lığı": "-ABSTR+P3",
    "luğu": "-ABSTR+P3",   "lüğü": "-ABSTR+P3",
    "liğini": "-ABSTR+P3+ACC",  "lığını": "-ABSTR+P3+ACC",
                                                                          
    "izm": "-ISM",     "izmi": "-ISM+P3",   "izmde": "-ISM+LOC",
    "izmden": "-ISM+ABL",  "izmin": "-ISM+GEN",
                                                                           
    "lir": "-AOR3SG",  "lır": "-AOR3SG",  "lur": "-AOR3SG",  "lür": "-AOR3SG",
                                                                           
    "ine": "-P3+DAT",   "ına": "-P3+DAT",   "une": "-P3+DAT",   "üne": "-P3+DAT",
    "inde": "-P3+LOC",  "ında": "-P3+LOC",  "unda": "-P3+LOC",  "ünde": "-P3+LOC",
    "ini": "-P3+ACC",   "ını": "-P3+ACC",   "unu": "-P3+ACC",   "ünü": "-P3+ACC",
    "inden": "-P3+ABL", "ından": "-P3+ABL", "undan": "-P3+ABL", "ünden": "-P3+ABL",
                                                                           
    "daki": "-LOC+REL",  "deki": "-LOC+REL",  "taki": "-LOC+REL",  "teki": "-LOC+REL",
                                                                           
    "lan": "-PASS+NZ",  "len": "-PASS+NZ",
                                                                           
    "mesi": "-VN3",      "ması": "-VN3",
    "mesini": "-VN3+ACC", "masını": "-VN3+ACC",
    "mesine": "-VN3+DAT", "masına": "-VN3+DAT",
    "mesinde": "-VN3+LOC", "masında": "-VN3+LOC",
                                                                           
    "ının": "-GEN+P",  "inin": "-GEN+P",  "unun": "-GEN+P",  "ünün": "-GEN+P",
                                                                           
    "diği": "-PART",   "dığı": "-PART",   "tiği": "-PART",   "tığı": "-PART",
    "duğu": "-PART",   "düğü": "-PART",   "tuğu": "-PART",   "tüğü": "-PART",
    "ği": "-PART.SFX",  "ğı": "-PART.SFX",  "gu": "-PART.SFX",  "gü": "-PART.SFX",
                                                                           
    "mas": "-NEG.VN",  "mes": "-NEG.VN",
                                                                           
    "sin": "-IMP2",  "sın": "-IMP2",  "sun": "-IMP2",  "sün": "-IMP2",
                                                                           
    "ıl": "-PASS",  "il": "-PASS",  "ul": "-PASS",  "ül": "-PASS",
                                                                           
    "irme": "-CAUS+VN", "ırma": "-CAUS+VN", "urma": "-CAUS+VN",
    "ürme": "-CAUS+VN", "erme": "-CAUS+VN", "arma": "-CAUS+VN",
                                                                           
    "dım": "-DI1SG", "dim": "-DI1SG", "dum": "-DI1SG", "düm": "-DI1SG",
    "tım": "-DI1SG", "tim": "-DI1SG", "tum": "-DI1SG", "tüm": "-DI1SG",
    "dık": "-DI1PL", "dik": "-DI1PL", "duk": "-DI1PL", "dük": "-DI1PL",
    "tık": "-DI1PL", "tik": "-DI1PL", "tuk": "-DI1PL", "tük": "-DI1PL",
    "dın": "-DI2SG", "din": "-DI2SG", "dun": "-DI2SG", "dün": "-DI2SG",
    "tın": "-DI2SG", "tin": "-DI2SG", "tun": "-DI2SG", "tün": "-DI2SG",
                                                                           
    "sa": "-COND",  "se": "-COND",
                                                                           
    "iyor": "-PROG",  "ıyor": "-PROG",  "uyor": "-PROG",  "üyor": "-PROG",
    "yor": "-PROG",
                                                                           
    "dı": "-PST",  "di": "-PST",  "du": "-PST",  "dü": "-PST",
    "tı": "-PST",  "ti": "-PST",  "tu": "-PST",  "tü": "-PST",
                                                                           
    "ir": "-AOR",  "ır": "-AOR",  "ur": "-AOR",  "ür": "-AOR",
    "er": "-AOR",  "ar": "-AOR",
                                                                           
    "mış": "-EVID",  "miş": "-EVID",  "muş": "-EVID",  "müş": "-EVID",
                                                                           
    "ma": "-NEG",  "me": "-NEG",
    "lama": "-VN+NEG",  "leme": "-VN+NEG",
    "maya": "-NEG.INF",
                                                                           
    "bil": "-ABIL",
                                                                           
    "malı": "-NECES",  "meli": "-NECES",
                                                                           
    "mak": "-INF",  "mek": "-INF",
                                                                           
    "ken": "-WHEN",
                                                                           
    "arak": "-CONV",  "erek": "-CONV",
                                                                           
    "lı": "-WITH",   "li": "-WITH",   "lu": "-WITH",   "lü": "-WITH",
    "sız": "-WITHOUT", "siz": "-WITHOUT", "suz": "-WITHOUT", "süz": "-WITHOUT",
                                                                           
    "cı": "-AGT",  "ci": "-AGT",  "cu": "-AGT",  "cü": "-AGT",
    "çı": "-AGT",  "çi": "-AGT",  "çu": "-AGT",  "çü": "-AGT",
                                                                           
    "lık": "-ABSTR",  "lik": "-ABSTR",  "luk": "-ABSTR",  "lük": "-ABSTR",
    "lığ": "-ABSTR",  "liğ": "-ABSTR",
                                                                           
    "elim": "-OPT1PL",  "alım": "-OPT1PL",
                                                                           
    "ım": "-1SG",  "im": "-1SG",  "um": "-1SG",  "üm": "-1SG",
    "sın": "-2SG",  "sin": "-2SG",  "sun": "-2SG",  "sün": "-2SG",
    "iz": "-1PL",  "ız": "-1PL",  "uz": "-1PL",  "üz": "-1PL",
    "nız": "-2PL",  "niz": "-2PL",  "nuz": "-2PL",  "nüz": "-2PL",
                                                                           
    "mı": "-Q",  "mi": "-Q",  "mu": "-Q",  "mü": "-Q",
                                                                           
    "yı": "-ACC",  "yi": "-ACC",  "yu": "-ACC",  "yü": "-ACC",
    "nı": "-ACC",  "ni": "-ACC",  "nu": "-ACC",  "nü": "-ACC",
                                                                           
    "ya": "-DAT",  "ye": "-DAT",
    "a": "-DAT",   "e": "-DAT",
                                                                           
    "dan": "-ABL",  "den": "-ABL",  "tan": "-ABL",  "ten": "-ABL",
                                                                           
    "da": "-LOC",  "de": "-LOC",  "ta": "-LOC",  "te": "-LOC",
                                                                           
    "lar": "-PL",  "ler": "-PL",
                                                                           
    "sı": "-P3",  "si": "-P3",  "su": "-P3",  "sü": "-P3",
                                                                           
    "nin": "-GEN",  "nın": "-GEN",  "nun": "-GEN",  "nün": "-GEN",
    "ın": "-GEN",   "in": "-GEN",   "un": "-GEN",   "ün": "-GEN",
                                                                           
    "le": "-INS",  "la": "-INS",
                                                                           
    "ce": "-EQU",  "ca": "-EQU",  "çe": "-EQU",  "ça": "-EQU",
                                                                           
    "eri": "-PL.SFX",  "una": "-P3+DAT",  "iril": "-PASS.SFX",
    "yan": "-PART.ACT", "ren": "-PART.ACT", "ıda": "-LOC.SFX",
    "üler": "-PL.SFX",  "ıler": "-PL.SFX",
    "ri": "-PL.SFX",
                                                                           
    "ı": "-ACC",  "i": "-ACC",  "u": "-ACC",  "ü": "-ACC",
}

                                                                   
                                                                       
                                                       
SHORT_AMBIGUOUS_SUFFIXES: frozenset[str] = frozenset(
    {"a", "e", "ı", "i", "u", "ü"}
)

                                                               
                                                                   
                                                     
SUFFIX_ENTRIES: list[tuple[str, str]] = sorted(
    SUFFIX_MAP.items(), key=lambda x: len(x[0]), reverse=True
)


                                                                               
                                                                       

APOSTROPHE_SUFFIXES: list[str] = sorted(
    [
        "nın", "nin", "nun", "nün", "dan", "den", "tan", "ten",
        "da", "de", "ta", "te", "ya", "ye", "nda", "nde",
        "yı", "yi", "yu", "yü", "nı", "ni", "nu", "nü",
        "lar", "ler", "lara", "lere", "ları", "leri",
        "ım", "im", "um", "üm", "ın", "in", "un", "ün",
        "mız", "miz", "muz", "müz", "nız", "niz", "nuz", "nüz",
        "dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür",
        "ki", "li", "lı", "lu", "lü", "sız", "siz", "suz", "süz",
        "inci", "ıncı", "uncu", "üncü", "nci", "ncı",
        "lık", "lik", "luk", "lük",
        "a", "e", "ı", "i", "u", "ü",
    ],
    key=len,
    reverse=True,
)

                                                                                
                                                                                
                                             
_VERB_CHAIN_SUFFIX_MAP = {
    "abil": "ABIL",
    "ebil": "ABIL",
    "abilir": "ABIL",
    "ebilir": "ABIL",
    "acak": "FUT",
    "ecek": "FUT",
    "acağ": "FUT",
    "eceğ": "FUT",
}
for _surface, _label in _VERB_CHAIN_SUFFIX_MAP.items():
    SUFFIX_MAP.setdefault(_surface, _label)
SUFFIX_ENTRIES = sorted(SUFFIX_MAP.items(), key=lambda kv: len(kv[0]), reverse=True)


                              
_V21_SUFFIX_MAP_MIN = {
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
}
for _surface, _label in _V21_SUFFIX_MAP_MIN.items():
    SUFFIX_MAP.setdefault(_surface, _label)
SUFFIX_ENTRIES = sorted(SUFFIX_MAP.items(), key=lambda kv: len(kv[0]), reverse=True)


                          
_V21_SUFFIX_FIX_CORE = {
    "ınız":"P2PL", "iniz":"P2PL", "unuz":"P2PL", "ünüz":"P2PL",
    "nız":"P2PL", "niz":"P2PL", "nuz":"P2PL", "nüz":"P2PL",
}
for _surface, _label in _V21_SUFFIX_FIX_CORE.items():
    SUFFIX_MAP.setdefault(_surface, _label)
SUFFIX_ENTRIES = sorted(SUFFIX_MAP.items(), key=lambda kv: len(kv[0]), reverse=True)
