"""Tokenization engine — orchestrates the full pipeline.

This is the central pipeline that ties together all modules:
1. Text normalization (Unicode, whitespace)
2. ALL CAPS detection and lowercasing
3. Special span extraction (URLs, numbers, dates, acronyms, emojis)
4. Word-level segmentation with candidate generation/selection
5. Post-annotation (allomorph labels, compound info, acronym expansion)
6. Number/unit reclassification safety net
"""

from __future__ import annotations

from ._domain_vocab import ALL_DOMAIN_ROOTS
from .morphology import annotate_acronyms, annotate_canonical, annotate_compounds
from .normalization import detect_all_caps, normalize_text
from .resources import load_tdk_words
from .segmentation import segment_word, split_into_words
from .special_spans import find_special_spans, make_special_tokens, reclassify_numbers_in_tokens


class TokenizationEngine:
    """Core tokenization engine.

    Stateless after initialisation: loads TDK and domain vocabulary once,
    then processes texts through a deterministic pipeline.

    This class is NOT the public API.  Use ``NedoTurkishTokenizer``
    instead, which delegates to this engine.
    """

    def __init__(self) -> None:
        self._tdk: set[str] = load_tdk_words()
        self._domain_roots: frozenset[str] = ALL_DOMAIN_ROOTS

    def tokenize(self, text: str) -> list[dict[str, object]]:
        """Run the full tokenization pipeline on *text*.

        Returns a list of token dicts, each with at minimum:
        ``token``, ``token_type``, ``morph_pos``.
        """
        if not text or not text.strip():
            return []

                                                                           
        text = normalize_text(text)

                                                                           
        text, caps_set = detect_all_caps(text)

                                                                           
        spans = find_special_spans(text)

        tokens: list[dict[str, object]] = []
        pos = 0

        for start, end, span_type, original in spans:
                                                           
            if pos < start:
                segment = text[pos:start]
                if segment.strip():
                    seg_tokens = self._tokenize_segment(segment, caps_set)
                    tokens.extend(seg_tokens)

                                            
            tokens.extend(make_special_tokens(span_type, original))
            pos = end

                                                         
        if pos < len(text):
            segment = text[pos:]
            if segment.strip():
                seg_tokens = self._tokenize_segment(segment, caps_set)
                tokens.extend(seg_tokens)

                                                                           
        tokens = reclassify_numbers_in_tokens(tokens)
        tokens = annotate_canonical(tokens)
        tokens = annotate_compounds(tokens)
        tokens = annotate_acronyms(tokens)

                                                                           
        tokens = _compute_morph_pos(tokens)

                                                                           
                                                                      
                                                                          
        tokens = _strip_token_text(tokens)

        return tokens

    def _tokenize_segment(
        self, segment: str, caps_set: frozenset[str]
    ) -> list[dict[str, object]]:
        """Tokenize a plain-text segment (no special spans)."""
        words = split_into_words(segment)
        tokens: list[dict[str, object]] = []

        for word in words:
            word_tokens = segment_word(
                word, self._tdk, self._domain_roots, caps_set
            )
            tokens.extend(word_tokens)

        return tokens


                                                                               

def _compute_morph_pos(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    """Recompute ``morph_pos`` consistently across the token stream.

    Rules:
    - Word-initial tokens (leading space, special types, PUNCT) → morph_pos = 0
    - SUFFIX tokens increment the position counter
    - Apostrophe suffixes continue from the previous word
    """
    result: list[dict[str, object]] = []
    word_pos = 0

    for tok in tokens:
        raw = str(tok["token"])
        token_type = str(tok["token_type"])

        is_word_start = raw.startswith(" ") or raw.strip().startswith("<")

                                                        
        if tok.get("_apo_suffix"):
            is_word_start = False

        if is_word_start or token_type in (
            "NUM", "DATE", "UNIT", "URL", "MENTION", "HASHTAG", "EMOJI", "ACRONYM", "PUNCT"
        ):
            word_pos = 0
            morph_pos = 0
        elif token_type == "SUFFIX":
            word_pos += 1
            morph_pos = word_pos
        else:
                                                                       
            word_pos = 0
            morph_pos = 0

        result.append({**tok, "morph_pos": morph_pos})

    return result


def _strip_token_text(tokens: list[dict[str, object]]) -> list[dict[str, object]]:
    """Remove internal leading whitespace from all token text strings.

    During pipeline processing, a leading space in ``token`` signals
    a word-initial token.  Once ``morph_pos`` has been computed, this
    space is no longer needed and must be stripped so the public API
    returns clean text.
    """
    return [{**tok, "token": str(tok["token"]).lstrip()} for tok in tokens]
