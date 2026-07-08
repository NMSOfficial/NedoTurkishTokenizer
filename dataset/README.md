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

## Sonuç dosyaları

Bu veri setiyle üretilen dondurulmuş metrikler için:

- [`../frozen_results/RESULTS_FREEZE.md`](../frozen_results/RESULTS_FREEZE.md)
- [`../frozen_results/README_FINAL1000.md`](../frozen_results/README_FINAL1000.md)

Hata analizleri için:

- [`../validation/README_VALIDATION.md`](../validation/README_VALIDATION.md)

## Not

Hugging Face veya Zenodo sürümü oluşturulduğunda bağlantılar bu dosyaya eklenecektir.
