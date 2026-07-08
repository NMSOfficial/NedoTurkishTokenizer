# Final1000 Sonuç Notları

[English](README_FINAL1000.en.md)

Bu klasör, Final1000 değerlendirme setiyle üretilen dondurulmuş sonuç özetlerini içerir.

## İlgili dosyalar

| Dosya | Açıklama |
|---|---|
| [`RESULTS_FREEZE.md`](RESULTS_FREEZE.md) | Ana metrik özeti |
| [`../dataset/nedo_final1000_gold.jsonl`](../dataset/nedo_final1000_gold.jsonl) | Final1000 gold set |
| [`../validation/README_VALIDATION.md`](../validation/README_VALIDATION.md) | Hata analizi özeti |

## Final1000

Final1000, 1.000 örnekli insan-denetimli Türkçe morfolojik tokenizasyon değerlendirme setidir.

| Kaynak | Adet |
|---|---:|
| `annotator_agreed` | 754 |
| `adjudicated_new` | 196 |
| `adjudicated_old` | 50 |
| Toplam | 1000 |

Build kontrolünde hatalı örnek sayısı: `0`.

## Ana sonuç

| Sistem | Boundary F1 |
|---|---:|
| NedoTurkishTokenizer | 0.6966 |
| Morpheus neural | 0.5443 |
| XLM-R | 0.4281 |
| BERTurk | 0.2817 |
| mBERT | 0.2801 |

Daha ayrıntılı sonuçlar için [`RESULTS_FREEZE.md`](RESULTS_FREEZE.md) dosyasına bakın.
