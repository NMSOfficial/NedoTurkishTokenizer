# Final1000 Result Notes

[Türkçe](README_FINAL1000.md)

This directory contains frozen result summaries produced on the Final1000 evaluation set.

## Files

| File | Description |
|---|---|
| [`RESULTS_FREEZE.md`](RESULTS_FREEZE.md) | Main metric summary |
| [`../dataset/nedo_final1000_gold.jsonl`](../dataset/nedo_final1000_gold.jsonl) | Final1000 gold set |
| [`../validation/README_VALIDATION.md`](../validation/README_VALIDATION.md) | Error analysis summary |

## Final1000

Final1000 is a 1,000-item human-adjudicated evaluation set for Turkish morphological tokenization.

| Source | Count |
|---|---:|
| `annotator_agreed` | 754 |
| `adjudicated_new` | 196 |
| `adjudicated_old` | 50 |
| Total | 1000 |

Invalid examples in build check: `0`.

## Main result

| System | Boundary F1 |
|---|---:|
| NedoTurkishTokenizer | 0.6966 |
| Morpheus neural | 0.5443 |
| XLM-R | 0.4281 |
| BERTurk | 0.2817 |
| mBERT | 0.2801 |

See [`RESULTS_FREEZE.md`](RESULTS_FREEZE.md) for details.
