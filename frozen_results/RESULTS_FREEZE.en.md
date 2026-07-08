# Frozen Results

[Türkçe](RESULTS_FREEZE.md)

This file is the frozen summary of the main metrics reported on Final1000.

Dataset: [`../dataset/nedo_final1000_gold.jsonl`](../dataset/nedo_final1000_gold.jsonl)

## Gold set

| Field | Value |
|---|---:|
| Examples | 1000 |
| Build issues | 0 |
| `annotator_agreed` | 754 |
| `adjudicated_new` | 196 |
| `adjudicated_old` | 50 |

## Main results

| System | Precision | Recall | Boundary F1 |
|---|---:|---:|---:|
| NedoTurkishTokenizer | 0.7717 | 0.6348 | 0.6966 |
| Morpheus neural | 0.6023 | 0.4965 | 0.5443 |
| XLM-R | 0.4831 | 0.3843 | 0.4281 |
| BERTurk | 0.4369 | 0.2078 | 0.2817 |
| mBERT | 0.2329 | 0.3513 | 0.2801 |
| Character | 0.1684 | 1.0000 | 0.2882 |
| Whole-word | 0.0000 | 0.0000 | 0.0000 |

## Additional Nedo metrics

| Metric | Value |
|---|---:|
| Average tokens | 1.946 |
| Single-token rate | 15.2% |
| Exact boundary-set accuracy | 64.7% |
| Over-segmentation | 16.7% |
| Under-segmentation | 30.9% |
| Label Precision | 0.5318 |
| Label Recall | 0.4129 |

## Code-mix / foreign-root stress test

File: [`../validation/foreign_root_error_analysis.json`](../validation/foreign_root_error_analysis.json)

| Metric | Value |
|---|---:|
| Cases | 240 |
| Precision | 0.5882 |
| Recall | 0.1667 |
| F1 | 0.2597 |

## Roundtrip

The exact roundtrip result applies to `tokenize_lossless()` + `detokenize()`.

| Metric | Value |
|---|---:|
| Cases | 10000 |
| Exact | 10000 |
| Mismatch | 0 |

## Note

For error analysis, see [`../validation/README_VALIDATION.md`](../validation/README_VALIDATION.md).
