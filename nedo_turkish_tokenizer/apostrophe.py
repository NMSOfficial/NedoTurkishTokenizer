"""Apostrophe-aware segmentation for Turkish text.

Handles two distinct cases:
1. **Turkish proper names** — İstanbul'da, Ankara'ya
   → ROOT(İstanbul) + PUNCT(') + SUFFIX(da)
2. **Foreign stems with Turkish suffixes** — meeting'e, zoom'da
   → FOREIGN(meeting) + SUFFIX(e)

The decision between these two cases uses:
- Turkish character detection (ç,ğ,ı,ş,ö,ü → Turkish)
- TDK dictionary lookup
- Proper noun list
"""

from __future__ import annotations

import re

from ._suffix_table import APOSTROPHE_SUFFIXES, SUFFIX_MAP
from .normalization import has_turkish_chars, turkish_lower
from .resources import load_proper_nouns, load_tdk_words

                                                                   
_APO_RE = re.compile(
    r"([A-Za-zÇçĞğİıÖöŞşÜü0-9]{2,})['\u2019]([A-Za-zÇçĞğİıÖöŞşÜü]{1,6})\b"
)


def is_turkish_base(word: str) -> bool:
    """Return True if *word* should be treated as a Turkish word.

    Used to decide whether ``word'suffix`` is a Turkish proper name
    (keep apostrophe as punctuation boundary) or a foreign word
    (merge into FOREIGN root + SUFFIX).

    Decision order:
    1. Turkish-specific chars → definitely Turkish
    2. Proper nouns list → Turkish
    3. TDK dictionary → Turkish (or accepted loanword)
    4. Very short words (< 4 chars) → assume Turkish (because short
       words are ambiguous and Turkish short words are common)
    """
    wl = turkish_lower(word)

                                                     
    if has_turkish_chars(wl):
        return True

                        
    if wl in load_proper_nouns():
        return True

                    
    tdk = load_tdk_words()
    if tdk and wl in tdk:
        return True

                                                         
    return len(wl) < 4


def split_apostrophe_words(
    text: str,
) -> tuple[str, list[tuple[str, str]]]:
    """Process apostrophe patterns in *text*.

    For **foreign** stems followed by a Turkish suffix after apostrophe,
    replaces the apostrophe with a space so the word can later be
    segmented as FOREIGN ROOT + SUFFIX.

    For **Turkish** proper names (İstanbul'da), leaves the text
    unchanged — the apostrophe will be handled as punctuation by the
    word splitter.

    Returns:
        ``(modified_text, [(foreign_base_lower, suffix_lower), ...])``
    """
    foreign_splits: list[tuple[str, str]] = []

    def _repl(m: re.Match) -> str:
        base, suffix = m.group(1), m.group(2)

        if is_turkish_base(base):
            return m.group(0)                                     

        sl = suffix.lower()
        if any(sl == s for s in APOSTROPHE_SUFFIXES):
            foreign_splits.append((turkish_lower(base), sl))
            return f"{base} {suffix}"                           

        return m.group(0)

    modified = _APO_RE.sub(_repl, text)
    return modified, foreign_splits


def build_apostrophe_tokens(
    word: str, suffix_str: str, *, is_foreign: bool
) -> list[dict[str, object]]:
    """Create token dicts for a word + apostrophe + suffix pattern.

    Args:
        word: The base word (before apostrophe).
        suffix_str: The suffix string (after apostrophe).
        is_foreign: Whether the base word is foreign.

    Returns:
        List of token dicts.
    """
    label = SUFFIX_MAP.get(suffix_str.lower(), "-SFX")

    if is_foreign:
                                                 
        return [
            {
                "token": f" {word}", "token_type": "FOREIGN", "morph_pos": 0,
                "_foreign": True,
            },
            {
                "token": suffix_str, "token_type": "SUFFIX", "morph_pos": 1,
                "_apo_suffix": True, "_suffix_label": label,
            },
        ]
    else:
                                                         
        return [
            {
                "token": f" {word}", "token_type": "ROOT", "morph_pos": 0,
            },
            {
                "token": "'", "token_type": "PUNCT", "morph_pos": 0,
                "_punct": True,
            },
            {
                "token": suffix_str, "token_type": "SUFFIX", "morph_pos": 1,
                "_apo_suffix": True, "_suffix_label": label,
            },
        ]
