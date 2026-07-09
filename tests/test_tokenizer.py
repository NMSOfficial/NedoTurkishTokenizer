"""Comprehensive regression test suite for NedoTurkishTokenizer.

Tests the public API and core segmentation with gold-standard examples
covering: basic Turkish, suffix chains, apostrophes, foreign words,
acronyms, special spans, ALL CAPS, compound words, and edge cases.

TOKEN FORMAT CONTRACT:
    token text does NOT include leading whitespace.
    Whether a token is word-initial is indicated by morph_pos == 0.
"""

from __future__ import annotations

import unittest


class TestTokenizerPublicAPI(unittest.TestCase):
    """Smoke tests for the public API surface."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_import_and_instantiate(self) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        t = NedoTurkishTokenizer()
        self.assertIsNotNone(t)

    def test_version(self) -> None:
        from importlib.metadata import version
        from nedo_turkish_tokenizer import __version__
        self.assertEqual(__version__, version("nedo-turkish-tokenizer"))

    def test_empty_input(self) -> None:
        self.assertEqual(self.tok.tokenize(""), [])
        self.assertEqual(self.tok.tokenize("   "), [])

    def test_callable_shorthand(self) -> None:
        result = self.tok("Merhaba")
        self.assertTrue(len(result) > 0)

    def test_token_dict_fields(self) -> None:
        tokens = self.tok.tokenize("ev")
        self.assertTrue(len(tokens) >= 1)
        t = tokens[0]
        self.assertIn("token", t)
        self.assertIn("token_type", t)
        self.assertIn("morph_pos", t)

    def test_batch_tokenize(self) -> None:
        texts = ["ev", "araba", "merhaba"]
        results = self.tok.batch_tokenize(texts, chunk_size=1000)
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIsInstance(r, list)
            self.assertTrue(len(r) >= 1)

    def test_stats(self) -> None:
        tokens = self.tok.tokenize("evde oturuyorum")
        stats = self.tok.stats(tokens)
        self.assertIn("total", stats)
        self.assertIn("roots", stats)
        self.assertIn("suffixes", stats)
        self.assertIn("tr_pct", stats)
        self.assertGreater(stats["total"], 0)


class TestTokenFormat(unittest.TestCase):
    """Token text must NOT include leading whitespace."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_no_leading_space_root(self) -> None:
        tokens = self.tok.tokenize("merhaba")
        self.assertEqual(tokens[0]["token"], "merhaba")

    def test_no_leading_space_suffix(self) -> None:
        tokens = self.tok.tokenize("evde")
        for t in tokens:
            self.assertFalse(
                t["token"].startswith(" "),
                f"Token {t['token']!r} has a leading space",
            )

    def test_no_leading_space_url(self) -> None:
        tokens = self.tok.tokenize("https://example.com")
        self.assertEqual(tokens[0]["token"], "https://example.com")

    def test_no_leading_space_num(self) -> None:
        tokens = self.tok.tokenize("%85")
        self.assertEqual(tokens[0]["token"], "%85")

    def test_no_leading_space_any_token(self) -> None:
        """No token in the output should ever start with a space."""
        text = "İstanbul'da meeting'e katılamadım https://example.com %85"
        tokens = self.tok.tokenize(text)
        for t in tokens:
            self.assertFalse(
                t["token"].startswith(" "),
                f"Token {t['token']!r} (type={t['token_type']}) has a leading space",
            )


class TestBasicTurkish(unittest.TestCase):
    """Core Turkish morphology tokenization."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def _roots(self, text: str) -> list[str]:
        return [t["token"] for t in self.tok.tokenize(text) if t["token_type"] == "ROOT"]

    def _types(self, text: str) -> list[str]:
        return [t["token_type"] for t in self.tok.tokenize(text)]

    def _suffixes(self, text: str) -> list[str]:
        return [t["token"] for t in self.tok.tokenize(text) if t["token_type"] == "SUFFIX"]

                                                                           

    def test_simple_root(self) -> None:
        tokens = self.tok.tokenize("merhaba")
        self.assertEqual(tokens[0]["token"], "merhaba")
        self.assertEqual(tokens[0]["token_type"], "ROOT")

    def test_whole_word_tdk_preserved(self) -> None:
        """'dünya' is in TDK — must NOT be split into 'dün' + 'ya'."""
        roots = self._roots("dünya")
        self.assertIn("dünya", roots)

    def test_suffix_loc(self) -> None:
        tokens = self.tok.tokenize("evde")
        self.assertEqual(tokens[0]["token"], "ev")
        self.assertEqual(tokens[0]["token_type"], "ROOT")
        self.assertEqual(tokens[1]["token"], "de")
        self.assertEqual(tokens[1]["token_type"], "SUFFIX")

    def test_suffix_plural_acc(self) -> None:
        tokens = self.tok.tokenize("kitapları")
        self.assertEqual(tokens[0]["token"], "kitap")
        types = [t["token_type"] for t in tokens]
        self.assertIn("SUFFIX", types)

    def test_verb_stem_past(self) -> None:
        """Verb stems derived from infinitives must be found."""
        roots = self._roots("geldim")
        self.assertIn("gel", roots)

    def test_verb_stem_progressive(self) -> None:
        roots = self._roots("geliyorum")
        self.assertIn("gel", roots)

    def test_verb_otur(self) -> None:
        roots = self._roots("oturuyorum")
        self.assertIn("otur", roots)

    def test_katil_root(self) -> None:
        roots = self._roots("katılamadım")
        self.assertIn("katıl", roots)

    def test_longer_root_wins(self) -> None:
        """'toplantısı' should segment as 'toplantı' + 'sı', not 'toplan' + 'tı' + 'sı'."""
        roots = self._roots("toplantısı")
        self.assertIn("toplantı", roots)

    def test_morph_pos_increments(self) -> None:
        tokens = self.tok.tokenize("evlerden")
        suffix_positions = [t["morph_pos"] for t in tokens if t["token_type"] == "SUFFIX"]
        for i, pos in enumerate(suffix_positions):
            self.assertGreater(pos, 0, f"Suffix at index {i} should have morph_pos > 0")


class TestFalseSuffixSplits(unittest.TestCase):
    """Regression tests: common words that must NOT be over-segmented.

    These words look like root+suffix but are standalone units.
    """

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def _assert_single_root(self, word: str) -> None:
        """Assert that *word* tokenizes to exactly one ROOT token."""
        tokens = self.tok.tokenize(word)
        roots = [t for t in tokens if t["token_type"] == "ROOT"]
        self.assertEqual(
            len(roots), 1,
            f"'{word}' should be a single ROOT, got: "
            f"{[(t['token'], t['token_type']) for t in tokens]}",
        )
        self.assertEqual(len(tokens), 1, f"'{word}' should produce 1 token, got {len(tokens)}")
        self.assertEqual(tokens[0]["token"], word)

                                                                           
                                                                      

    def test_dedi(self) -> None:
        self._assert_single_root("dedi")

    def test_dedim(self) -> None:
        self._assert_single_root("dedim")

    def test_demis(self) -> None:
        self._assert_single_root("demiş")

    def test_denir(self) -> None:
        self._assert_single_root("denir")

    def test_dese(self) -> None:
        self._assert_single_root("dese")

                                                                           
                                                                   

    def test_yani(self) -> None:
        self._assert_single_root("yani")

    def test_belki(self) -> None:
        self._assert_single_root("belki")

    def test_cunku(self) -> None:
        self._assert_single_root("çünkü")

    def test_sanki(self) -> None:
        self._assert_single_root("sanki")

                                                                           

    def test_dedi_mi(self) -> None:
        tokens = self.tok.tokenize("dedi mi")
        roots = [t for t in tokens if t["token_type"] == "ROOT"]
        self.assertEqual(len(roots), 2, "Both 'dedi' and 'mi' should be roots")
        root_texts = [t["token"] for t in roots]
        self.assertIn("dedi", root_texts)

                                                                           

    def test_bile(self) -> None:
        self._assert_single_root("bile")

    def test_daha(self) -> None:
        self._assert_single_root("daha")


class TestApostrophe(unittest.TestCase):
    """Apostrophe handling for Turkish proper names and foreign stems."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_turkish_proper_name(self) -> None:
        """İstanbul'da → ROOT + PUNCT(') + SUFFIX(da)."""
        tokens = self.tok.tokenize("İstanbul'da")
        types = [t["token_type"] for t in tokens]
        self.assertIn("ROOT", types)
        self.assertIn("PUNCT", types)
        self.assertIn("SUFFIX", types)

    def test_foreign_stem(self) -> None:
        """meeting'e → FOREIGN + SUFFIX."""
        tokens = self.tok.tokenize("meeting'e")
        types = [t["token_type"] for t in tokens]
        self.assertIn("FOREIGN", types)
        self.assertIn("SUFFIX", types)

    def test_apostrophe_suffix_label(self) -> None:
        tokens = self.tok.tokenize("İstanbul'da")
        suffix_tokens = [t for t in tokens if t["token_type"] == "SUFFIX"]
        self.assertTrue(len(suffix_tokens) >= 1)
        self.assertEqual(suffix_tokens[0].get("_suffix_label"), "-LOC")


class TestSpecialSpans(unittest.TestCase):
    """URL, date, number, acronym, emoji detection."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def _find_type(self, text: str, ttype: str) -> list[dict]:
        return [t for t in self.tok.tokenize(text) if t["token_type"] == ttype]

    def test_url_detection(self) -> None:
        urls = self._find_type("https://example.com sitesine bak", "URL")
        self.assertEqual(len(urls), 1)
        self.assertIn("example.com", urls[0]["token"])

    def test_date_detection(self) -> None:
        dates = self._find_type("14.03.2026 tarihinde", "DATE")
        self.assertEqual(len(dates), 1)

    def test_number_detection(self) -> None:
        nums = self._find_type("%85 başarı", "NUM")
        self.assertEqual(len(nums), 1)

    def test_acronym_detection(self) -> None:
        tokens = self.tok.tokenize("NATO güçlü")
        acr = [t for t in tokens if t["token_type"] == "ACRONYM"]
        self.assertEqual(len(acr), 1)
        self.assertTrue(acr[0].get("_expansion"))

    def test_mention_detection(self) -> None:
        mentions = self._find_type("@kullanici çok iyi", "MENTION")
        self.assertEqual(len(mentions), 1)

    def test_hashtag_detection(self) -> None:
        tags = self._find_type("#türkiye çok güzel", "HASHTAG")
        self.assertEqual(len(tags), 1)


class TestAllCaps(unittest.TestCase):
    """ALL CAPS word handling."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_caps_detected(self) -> None:
        word = "\u0130STANBUL"
        tokens = self.tok.tokenize(f"{word} guzel")
        istanbul_tok = [t for t in tokens if t["token"] == word]
        self.assertTrue(len(istanbul_tok) >= 1)
        self.assertTrue(istanbul_tok[0].get("_caps"))

    def test_caps_preserves_surface(self) -> None:
        word = "\u0130STANBUL"
        tokens = self.tok.tokenize(word)
        self.assertEqual(tokens[0]["token"], word)
        self.assertTrue(tokens[0].get("_caps"))

    def test_caps_acronym(self) -> None:
        """Known acronyms in ALL CAPS should be ACRONYM type."""
        tokens = self.tok.tokenize("TBMM toplantisi")
        tbmm = [t for t in tokens if t["token_type"] == "ACRONYM"]
        self.assertTrue(len(tbmm) >= 1)


class TestCanonicalLabels(unittest.TestCase):
    """Allomorph canonicalization metadata."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_loc_canonical(self) -> None:
        tokens = self.tok.tokenize("evde")
        suffix = [t for t in tokens if t["token_type"] == "SUFFIX"]
        self.assertTrue(any(t.get("_canonical") == "LOC" for t in suffix))

    def test_pl_canonical(self) -> None:
        tokens = self.tok.tokenize("evler")
        suffix = [t for t in tokens if t["token_type"] == "SUFFIX"]
        self.assertTrue(any(t.get("_canonical") == "PL" for t in suffix))


class TestCompoundAnnotation(unittest.TestCase):
    """Compound word detection."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_known_compound(self) -> None:
        tokens = self.tok.tokenize("başbakan")
        root = [t for t in tokens if t["token_type"] == "ROOT"]
        if root and root[0]["token"] == "başbakan":
            self.assertTrue(root[0].get("_compound"))
            self.assertIn("baş", root[0].get("_parts", []))


class TestNoDependencies(unittest.TestCase):
    """Verify no external runtime dependencies are imported."""

    def test_no_external_imports(self) -> None:
        import ast
        from pathlib import Path

        pkg_dir = Path(__file__).parent.parent / "nedo_turkish_tokenizer"
        banned = {"turkish_tokenizer", "zemberek", "requests", "transformers"}

        for py_file in pkg_dir.glob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        self.assertNotIn(
                            top, banned,
                            f"{py_file.name} imports banned dependency: {alias.name}"
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top = node.module.split(".")[0]
                        self.assertNotIn(
                            top, banned,
                            f"{py_file.name} imports banned dependency: {node.module}"
                        )


class TestEdgeCases(unittest.TestCase):
    """Edge cases and regression guards."""

    @classmethod
    def setUpClass(cls) -> None:
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        cls.tok = NedoTurkishTokenizer()

    def test_punctuation_only(self) -> None:
        tokens = self.tok.tokenize("...")
        self.assertTrue(all(t["token_type"] == "PUNCT" for t in tokens))

    def test_mixed_punctuation(self) -> None:
        tokens = self.tok.tokenize('"Merhaba," dedi.')
        types = [t["token_type"] for t in tokens]
        self.assertIn("PUNCT", types)
        self.assertIn("ROOT", types)

    def test_unicode_normalized(self) -> None:
        tokens = self.tok.tokenize("  merhaba   dünya  ")
        roots = [t["token"] for t in tokens if t["token_type"] == "ROOT"]
        self.assertIn("merhaba", roots)
        self.assertIn("dünya", roots)

    def test_single_char_word(self) -> None:
        tokens = self.tok.tokenize("a")
        self.assertTrue(len(tokens) >= 1)

    def test_number_apostrophe_suffix(self) -> None:
        """3'te, 1990'larda should be NUM + SUFFIX."""
        tokens = self.tok.tokenize("3'te geldim")
        num = [t for t in tokens if t["token_type"] == "NUM"]
        self.assertTrue(len(num) >= 1)

    def test_integration_full_sentence(self) -> None:
        """Full integration test with mixed content."""
        tokens = self.tok.tokenize("İstanbul'da meeting'e katılamadım")
        self.assertTrue(len(tokens) > 0)
                                                 
        from nedo_turkish_tokenizer import NedoTurkishTokenizer
        t = NedoTurkishTokenizer()
        result = t.tokenize("İstanbul'da meeting'e katılamadım")
        self.assertIsInstance(result, list)
        self.assertTrue(all("token" in tok and "token_type" in tok for tok in result))


if __name__ == "__main__":
    unittest.main()
