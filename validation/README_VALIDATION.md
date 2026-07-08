# Doğrulama ve Hata Analizi

[English](README_VALIDATION.en.md)

Bu klasör, Final1000 sonuçları için üretilen hata analizi ve doğrulama dosyalarını içerir.

## Dosyalar

| Dosya | Açıklama |
|---|---|
| [`error_examples_20_correct_20_wrong.md`](error_examples_20_correct_20_wrong.md) | 20 doğru ve 20 hatalı örnek |
| [`error_examples_20_correct_20_wrong.csv`](error_examples_20_correct_20_wrong.csv) | Aynı örneklerin CSV sürümü |
| [`segmentation_error_inventory.json`](segmentation_error_inventory.json) | Segmentasyon hata envanteri |
| [`label_error_summary.json`](label_error_summary.json) | Etiketleme hata özeti |
| [`long_word_analysis.json`](long_word_analysis.json) | Uzun kelime analizi |
| [`foreign_root_error_analysis.json`](foreign_root_error_analysis.json) | Yabancı kök / code-mix analizi |

## Özet

Final1000 üzerinde NedoTurkishTokenizer Boundary F1 değeri `0.6966` olarak raporlanmıştır.

Ek metrikler:

| Metrik | Değer |
|---|---:|
| Precision | 0.7717 |
| Recall | 0.6348 |
| Exact boundary-set accuracy | 64.7% |
| Over-segmentation | 16.7% |
| Under-segmentation | 30.9% |
| Label Precision | 0.5318 |
| Label Recall | 0.4129 |

## Code-mix / foreign-root

Yabancı kök + Türkçe ek içeren yapılarda performans düşüktür.

| Metrik | Değer |
|---|---:|
| Örnek sayısı | 240 |
| Precision | 0.5882 |
| Recall | 0.1667 |
| F1 | 0.2597 |

## Uzun kelimeler

Uzun kelimelerde boundary exact accuracy kısa kelimelere göre daha düşüktür. Ayrıntı için [`long_word_analysis.json`](long_word_analysis.json) dosyasına bakın.
