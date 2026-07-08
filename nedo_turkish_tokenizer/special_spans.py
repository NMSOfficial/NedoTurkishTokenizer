"""Special span detection: URLs, numbers, dates, mentions, hashtags, emojis, acronyms.

Detects non-textual spans in the input text **before** the word-level
segmentation runs, so they are never mistakenly split by suffix
stripping.  Returns a sorted, non-overlapping list of spans.
"""

from __future__ import annotations

import re

from ._acronym_table import ACRONYM_EXPANSIONS
from ._suffix_table import APOSTROPHE_SUFFIXES
from .normalization import turkish_lower
from .resources import load_proper_nouns, load_tdk_words

                                                                               

MONTH_NAMES: frozenset[str] = frozenset({
    "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
    "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık",
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
})

UNITS: frozenset[str] = frozenset({
    "km", "m", "cm", "mm", "nm",
    "kg", "g", "mg", "ton",
    "sn", "dk", "sa", "ms",
    "tl", "usd", "eur", "gbp",
    "kb", "mb", "gb", "tb", "pb",
    "ml", "mcg", "meq", "iu", "mmhg", "mosm",
    "hz", "mhz", "ghz", "watt", "kw", "mw", "kcal", "cal",
})

ROMAN_NUMERALS: frozenset[str] = frozenset({
    "i", "ii", "iii", "iv", "vi", "vii", "viii", "ix",
    "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
})

                                                                               

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@[\w\u00C0-\u024F]+")
HASHTAG_RE = re.compile(r"#[\w\u00C0-\u024F]+")

_SUFFIX_ALT = "|".join(re.escape(s) for s in APOSTROPHE_SUFFIXES)

                                          
NUM_APOSTROPHE_RE = re.compile(
    r"\d+(?:[.:,]\d+)*['\u2019](?:" + _SUFFIX_ALT + r")+\b",
    re.IGNORECASE,
)

DATE_RE = re.compile(
    r"\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}"
    r"|\d{4}[./\-]\d{1,2}[./\-]\d{1,2}"
)
CURRENCY_RE = re.compile(r"[$€£¥₺₽]\d+[\.,]?\d*|\d+[\.,]?\d*[$€£¥₺₽]")
NUMBER_RE = re.compile(
    r"%\d+[\.,]?\d*"
    r"|\d{1,3}(?:\.\d{3})+"                            
    r"|\d+[\.,]\d+"                      
    r"|\d+%"
    r"|\d+/\d+"
)
TIME_RE = re.compile(r"\d{1,2}:\d{2}(?::\d{2})?")
PLAIN_NUM_RE = re.compile(r"\b\d+\b")

                                                                 
ACRONYM_RE = re.compile(
    r"\b[A-ZÇĞİÖŞÜ]{2,}[0-9]*\b"
    r"|\b[A-ZÇĞİÖŞÜ][0-9]+\b"
)

                                           
ACRONYM_APOSTROPHE_RE = re.compile(
    r"\b(?:[A-ZÇĞİÖŞÜ]{2,}[0-9]*|[A-ZÇĞİÖŞÜ][0-9]+)['\u2019](?:"
    + _SUFFIX_ALT + r")+\b"
)

TEXT_EMOJI_RE = re.compile(r"[:;=]-?[\)\(\]\[dDpPoO3]|<3")
UNICODE_EMOJI_RE = re.compile(
    "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF\U0001F900-\U0001F9FF"
    "\U00002600-\U000026FF]+",
    flags=re.UNICODE,
)

                                                        
_SPAN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (URL_RE,                "URL"),
    (MENTION_RE,            "MENTION"),
    (HASHTAG_RE,            "HASHTAG"),
    (DATE_RE,               "DATE"),
    (CURRENCY_RE,           "UNIT"),
    (NUM_APOSTROPHE_RE,     "NUM_APO"),
    (ACRONYM_APOSTROPHE_RE, "ACRONYM_APO"),
    (ACRONYM_RE,            "ACRONYM"),
    (NUMBER_RE,             "NUM"),
    (TIME_RE,               "NUM"),
    (PLAIN_NUM_RE,          "NUM"),
    (UNICODE_EMOJI_RE,      "EMOJI"),
    (TEXT_EMOJI_RE,          "EMOJI"),
]


                                                                               

def _is_known_turkish_word(word_upper: str) -> bool:
    """Return True if *word_upper* (ALL CAPS) is actually a Turkish word.

    Checks:
    1. ACRONYM_EXPANSIONS dict → always acronym (return False)
    2. TDK dictionary → Turkish word (return True)
    3. Proper nouns → Turkish word (return True)
    4. Otherwise → treat as acronym (return False)
    """
                               
    if word_upper in ACRONYM_EXPANSIONS:
        return False
    base = word_upper.rstrip("0123456789")
    if base and base != word_upper and base in ACRONYM_EXPANSIONS:
        return False

    wl = turkish_lower(word_upper)

    tdk = load_tdk_words()
    if tdk and wl in tdk:
        return True

    if wl in load_proper_nouns():
        return True

    return False


                                                                               

def find_special_spans(text: str) -> list[tuple[int, int, str, str]]:
    """Find all special-token spans in *text*.

    Returns a sorted, non-overlapping list of
    ``(start, end, token_type, original_text)``.
    """
    candidates: list[tuple[int, int, str, str]] = []
    for pattern, ttype in _SPAN_PATTERNS:
        for m in pattern.finditer(text):
            original = m.group(0)

                                                                            
            if ttype in ("ACRONYM", "ACRONYM_APO"):
                if ttype == "ACRONYM_APO":
                    apo = original.find("'")
                    if apo == -1:
                        apo = original.find("\u2019")
                    acr_base = original[:apo]
                else:
                    acr_base = original
                if _is_known_turkish_word(acr_base):
                    continue

            candidates.append((m.start(), m.end(), ttype, original))

                                                      
    candidates.sort(key=lambda x: (x[0], -(x[1] - x[0])))

                                      
    result: list[tuple[int, int, str, str]] = []
    last_end = 0
    for s, e, t, o in candidates:
        if s >= last_end:
            result.append((s, e, t, o))
            last_end = e
    return result


def split_apostrophe_suffixes(suffix_str: str) -> list[tuple[str, str]]:
    """Split a suffix string (after apostrophe) into individual suffix pieces.

    Returns a list of ``(surface_form, label)`` tuples.
    """
    from ._suffix_table import SUFFIX_MAP                                  

    pieces: list[tuple[str, str]] = []
    remaining = suffix_str.lower()
    while remaining:
        matched = False
        for s in APOSTROPHE_SUFFIXES:
            if remaining.startswith(s):
                label = SUFFIX_MAP.get(s, "-SFX")
                pieces.append((s, label))
                remaining = remaining[len(s):]
                matched = True
                break
        if not matched:
                                                                    
            pieces.append((remaining, "-SFX"))
            break
    return pieces


def make_special_tokens(
    span_type: str, original: str
) -> list[dict[str, object]]:
    """Create token dict(s) for a matched special span.

    ``NUM_APO`` and ``ACRONYM_APO`` spans are split into base + SUFFIX
    tokens.
    """
                                                                           
    if span_type == "NUM_APO":
        apo_pos = original.find("'")
        if apo_pos == -1:
            apo_pos = original.find("\u2019")
        num_part = original[:apo_pos]
        suffix_pieces = split_apostrophe_suffixes(original[apo_pos + 1:])
        result: list[dict[str, object]] = [
            {"token": f" {num_part}", "token_type": "NUM", "morph_pos": 0, "_num": True},
        ]
        for idx, (surf, label) in enumerate(suffix_pieces, start=1):
            result.append({
                "token": surf, "token_type": "SUFFIX", "morph_pos": idx,
                "_apo_suffix": True, "_suffix_label": label,
            })
        return result

                                                                           
    if span_type == "ACRONYM_APO":
        apo_pos = original.find("'")
        if apo_pos == -1:
            apo_pos = original.find("\u2019")
        acr_part = original[:apo_pos]
        suffix_pieces = split_apostrophe_suffixes(original[apo_pos + 1:])
        expansion = ACRONYM_EXPANSIONS.get(acr_part.upper())
        meta: dict[str, object] = {"_acronym": True}
        if expansion:
            meta["_expansion"] = expansion
            meta["_known_acronym"] = True
        result = [
            {"token": f" {acr_part}", "token_type": "ACRONYM", "morph_pos": 0, **meta},
        ]
        for idx, (surf, label) in enumerate(suffix_pieces, start=1):
            result.append({
                "token": surf, "token_type": "SUFFIX", "morph_pos": idx,
                "_apo_suffix": True, "_suffix_label": label,
            })
        return result

                                                                          
    if span_type == "ACRONYM":
        expansion = ACRONYM_EXPANSIONS.get(original.upper())
        meta = {"_acronym": True}
        if expansion:
            meta["_expansion"] = expansion
            meta["_known_acronym"] = True
        return [{"token": f" {original}", "token_type": "ACRONYM", "morph_pos": 0, **meta}]

                                                                           
    return [{
        "token": f" {original}",
        "token_type": span_type,
        "morph_pos": 0,
        f"_{span_type.lower()}": True,
    }]


def reclassify_numbers_in_tokens(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    """Post-pass: catch remaining numbers / units missed by span detection."""
    result: list[dict[str, object]] = []
    for tok in tokens:
        tt = tok["token_type"]
        if tt not in ("ROOT", "FOREIGN"):
            result.append(tok)
            continue

        raw = str(tok["token"]).strip()

        if NUMBER_RE.fullmatch(raw):
            result.append({**tok, "token_type": "NUM", "_num": True})
        elif raw.lower() in UNITS:
            result.append({**tok, "token_type": "UNIT", "_unit": True})
        elif raw.lower() in ROMAN_NUMERALS:
            result.append({**tok, "token_type": "NUM", "_roman": True})
        elif raw.lower() in MONTH_NAMES:
            result.append({**tok, "token_type": "ROOT", "_month": True})
        else:
            result.append(tok)

    return result

                          
                                                                             
BARE_URL_RE = re.compile(r"(?<![@\w])(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", re.IGNORECASE)
_SPAN_PATTERNS = [(BARE_URL_RE, "URL")] + _SPAN_PATTERNS
