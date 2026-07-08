"""Text normalization utilities for Turkish text.

Handles:
- Turkish-aware lowercasing (İ→i, I→ı)
- Unicode NFC normalization
- Whitespace cleanup
- ALL CAPS word detection and lowercasing
"""

from __future__ import annotations

import re
import unicodedata

                                                                 
TR_CHARS: frozenset[str] = frozenset("çğışöüÇĞİŞÖÜ")

                                                             
_CAPS_RE = re.compile(r"\b([A-ZÇĞİÖŞÜ]{2,})\b")


def turkish_lower(s: str) -> str:
    """Turkish-aware lowercase: İ→i, I→ı, then standard ``str.lower()``.

    Standard Python ``str.lower()`` maps both I and İ to 'i', which is
    wrong for Turkish where I→ı and İ→i.
    """
    return s.replace("İ", "i").replace("I", "ı").lower()


def normalize_text(text: str) -> str:
    """Apply Unicode NFC normalization and collapse whitespace."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_turkish_chars(word: str) -> bool:
    """Return True if *word* contains Turkish-specific characters (ç,ğ,ı,ş,ö,ü)."""
    return any(c in TR_CHARS for c in word)


def detect_all_caps(text: str) -> tuple[str, frozenset[str]]:
    """Detect ALL CAPS words, lowercase them, and return the modified text.

    ALL CAPS words like ``İSTANBUL`` cause problems for suffix-based
    segmentation because the suffix table works on lowercase text.  This
    function lowercases them in-place and returns a set of the lowered
    forms so the output tokens can be annotated with ``_caps=True``.

    Returns:
        ``(modified_text, frozenset_of_lowered_caps_words)``
    """
    caps_collector: set[str] = set()

    def _replace(m: re.Match) -> str:
        word = m.group(1)
        lowered = turkish_lower(word)
        caps_collector.add(lowered)
        return lowered

                                                                     
                                                                          
                                                                             
    _CAPS_RE.sub(_replace, text)
    return text, frozenset(caps_collector)
