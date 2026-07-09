# Final1000 Veri Seti

[English](README.en.md)

Bu klasör, NedoTurkishTokenizer için kullanılan Final1000 değerlendirme setini içerir.

## Dosyalar

| Dosya | Açıklama |
|---|---|
| [`nedo_final1000_gold.jsonl`](nedo_final1000_gold.jsonl) | Ana gold set. Her satır bir JSON örneğidir. |
| [`nedo_final1000_gold.csv`](nedo_final1000_gold.csv) | Aynı verinin CSV sürümü. |
| [`zenodo_metadata.json`](zenodo_metadata.json) | Zenodo release için taslak metadata. |

## İçerik

Final1000, Türkçe morfolojik tokenizasyon için hazırlanmış 1.000 örnekli değerlendirme setidir.

Kaynak dağılımı:

| Kaynak | Adet |
|---|---:|
| `annotator_agreed` | 754 |
| `adjudicated_new` | 196 |
| `adjudicated_old` | 50 |
| Toplam | 1000 |

Build kontrolünde hatalı örnek sayısı `0` olarak raporlanmıştır.

## Kullanım

JSONL dosyasını satır satır okuyarak kullanabilirsiniz:

```python
import json
from pathlib import Path

path = Path("dataset/nedo_final1000_gold.jsonl")
examples = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
print(len(examples))
```

## Veri ve DOI

| Kaynak | Bağlantı |
|---|---|
| GitHub repository | [`NMSOfficial/NedoTurkishTokenizer`](https://github.com/NMSOfficial/NedoTurkishTokenizer) |
| Hugging Face dataset | [`Ethosoft/NedoTurkishTokenizer-Final1000`](https://huggingface.co/datasets/Ethosoft/NedoTurkishTokenizer-Final1000) |
| Zenodo DOI | [`10.5281/zenodo.21274980`](https://doi.org/10.5281/zenodo.21274980) |

## Sonuç dosyaları

Bu veri setiyle üretilen dondurulmuş metrikler için:

- [`../frozen_results/RESULTS_FREEZE.md`](../frozen_results/RESULTS_FREEZE.md)
- [`../frozen_results/README_FINAL1000.md`](../frozen_results/README_FINAL1000.md)

Hata analizleri için:

- [`../validation/README_VALIDATION.md`](../validation/README_VALIDATION.md)

## Not

## Dış bağlantılar

| Kaynak | Bağlantı |
|---|---|
| GitHub repository | [`NMSOfficial/NedoTurkishTokenizer`](https://github.com/NMSOfficial/NedoTurkishTokenizer) |
| Hugging Face dataset | [`Ethosoft/NedoTurkishTokenizer-Final1000`](https://huggingface.co/datasets/Ethosoft/NedoTurkishTokenizer-Final1000) |
| Zenodo DOI | [`10.5281/zenodo.21274980`](https://doi.org/10.5281/zenodo.21274980) |

## Atıf

Bu repoyu veya Final1000 veri setini kullanırsanız aşağıdaki kaydı kullanabilirsiniz.

```bibtex
@software{sezer_nedoturkishtokenizer_2026,
  author    = {Sezer, Nedim Mutlu},
  title     = {NedoTurkishTokenizer: A Morphology-Aware Turkish Tokenizer},
  year      = {2026},
  version   = {2.1.3},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21274980},
  url       = {https://doi.org/10.5281/zenodo.21274980}
}
```
