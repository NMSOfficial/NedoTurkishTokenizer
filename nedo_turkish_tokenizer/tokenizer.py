"""NedoTurkishTokenizer — self-contained Turkish morphological tokenizer.

A zero-dependency Turkish tokenizer that segments text into
morphologically meaningful tokens using deterministic heuristics,
a bundled TDK dictionary, and a candidate-based segmentation engine.

Usage::

    from nedo_turkish_tokenizer import NedoTurkishTokenizer

    tok = NedoTurkishTokenizer()
    tokens = tok.tokenize("İstanbul'da meeting'e katılamadım")
    for t in tokens:
        print(t["token"], t["token_type"], t["morph_pos"])

Output fields per token:
    token       : str  — token string (leading space = word-initial)
    token_type  : str  — ROOT | SUFFIX | FOREIGN | PUNCT |
                         NUM | DATE | UNIT | URL | MENTION | HASHTAG | EMOJI | ACRONYM
    morph_pos   : int  — 0=root/word-initial, 1=first suffix, 2=second suffix…
    (+ optional _* metadata fields)
"""

from __future__ import annotations

import os
import re
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

from .engine import TokenizationEngine
from .types import SPECIAL_TYPES


                                                                               

_worker_tok: "NedoTurkishTokenizer | None" = None


def _init_worker() -> None:
    global _worker_tok
    _worker_tok = NedoTurkishTokenizer()


def _tokenize_one(text: str) -> list[dict]:
    assert _worker_tok is not None
    return _worker_tok.tokenize(text)


                                                                                


class NedoTurkishTokenizer:
    """Self-contained Turkish morphological tokenizer.

    Requires **no external dependencies** — all tokenization logic,
    dictionaries, and heuristics are bundled within the package.

    Example::

        from nedo_turkish_tokenizer import NedoTurkishTokenizer

        tok = NedoTurkishTokenizer()
        tokens = tok("İstanbul'da meeting'e katılamadım")
        for t in tokens:
            print(t["token"], t["token_type"], t["morph_pos"])
    """

    def __init__(self) -> None:
        self._engine = TokenizationEngine()

                                                                             

    def __call__(self, text: str) -> list[dict]:
        """Shorthand for ``tokenize(text)``."""
        return self.tokenize(text)

    def tokenize(self, text: str) -> list[dict]:
        """Tokenize a single text string.

        Returns a list of token dicts, each containing at minimum:
        ``token``, ``token_type``, ``morph_pos``, plus optional
        ``_*`` metadata fields.
        """
        return self._engine.tokenize(text)

    def tokenize_lossless(self, text: str) -> list[dict]:
        if text == "":
            return []
        out: list[dict] = []
        for m in re.finditer(r"\s+|\S+", text):
            piece = m.group(0)
            if piece.isspace():
                out.append({"token": piece, "token_type": "WS", "morph_pos": 0, "_whitespace": True})
            else:
                toks = self.tokenize(piece)
                if toks:
                    toks[0]["_lossless_text"] = piece
                    for t in toks[1:]:
                        t["_lossless_skip"] = True
                    out.extend(toks)
                else:
                    out.append({"token": piece, "token_type": "RAW", "morph_pos": 0, "_lossless_text": piece})
        return out

    def detokenize(self, tokens: list[dict]) -> str:
        parts: list[str] = []
        for t in tokens:
            if t.get("_lossless_skip"):
                continue
            if "_lossless_text" in t:
                parts.append(str(t.get("_lossless_text", "")))
            else:
                parts.append(str(t.get("token", "")))
        return "".join(parts)

    def batch_tokenize(
        self,
        texts: list[str],
        workers: int | None = None,
        chunk_size: int = 64,
    ) -> list[list[dict]]:
        """Tokenize a list of texts in parallel.

        Args:
            texts: List of strings to tokenize.
            workers: Number of worker processes (``None`` = all CPUs).
            chunk_size: Below this count, run sequentially.

        Returns:
            List of token lists, in the same order as *texts*.
        """
        if not texts:
            return []

        n = workers or os.cpu_count() or 4

        if len(texts) <= chunk_size or n == 1:
            return [self.tokenize(t) for t in texts]

        results: list[list[dict] | None] = [None] * len(texts)

        with ProcessPoolExecutor(max_workers=n, initializer=_init_worker) as pool:
            futs = {pool.submit(_tokenize_one, t): i for i, t in enumerate(texts)}
            for fut in as_completed(futs):
                i = futs[fut]
                try:
                    results[i] = fut.result()
                except Exception as exc:
                                                            
                    results[i] = self.tokenize(texts[i])
                    print(f"[NedoTurkishTokenizer] fallback at idx={i}: {exc}")

        return results                              

                                                                             

    def stats(self, tokens: list[dict]) -> dict:
        """Compute morphological coverage statistics for a token list."""
        total = len(tokens)
        if total == 0:
            return {k: 0 for k in (
                "total", "roots", "suffixes", "foreign",
                "punct", "special", "tr_pct", "pure_pct",
            )}
        roots = sum(1 for t in tokens if t["token_type"] == "ROOT")
        suffixes = sum(1 for t in tokens if t["token_type"] == "SUFFIX")
        foreign = sum(1 for t in tokens if t["token_type"] == "FOREIGN")
        punct = sum(1 for t in tokens if t["token_type"] == "PUNCT")
        special = sum(1 for t in tokens if t["token_type"] in SPECIAL_TYPES)
        tr = roots + suffixes + foreign + punct + special
        pure = sum(
            1 for t in tokens
            if t["token_type"] in ("ROOT", "SUFFIX", "FOREIGN")
            and not t["token"].strip().startswith("<")
        )
        return {
            "total":    total,
            "roots":    roots,
            "suffixes": suffixes,
            "foreign":  foreign,
            "punct":    punct,
            "special":  special,
            "tr_pct":   round(tr / total * 100, 2),
            "pure_pct": round(pure / total * 100, 2),
        }
