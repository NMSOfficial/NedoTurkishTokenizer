# Final1000 Dataset

[Türkçe](README.md)

This directory contains the Final1000 evaluation set used for NedoTurkishTokenizer.

## Files

| File | Description |
|---|---|
| [`nedo_final1000_gold.jsonl`](nedo_final1000_gold.jsonl) | Main gold set. One JSON object per line. |
| [`nedo_final1000_gold.csv`](nedo_final1000_gold.csv) | CSV version of the same data. |
| [`zenodo_metadata.json`](zenodo_metadata.json) | Draft metadata for a Zenodo release. |

## Content

Final1000 is a 1,000-item evaluation set for Turkish morphological tokenization.

Source distribution:

| Source | Count |
|---|---:|
| `annotator_agreed` | 754 |
| `adjudicated_new` | 196 |
| `adjudicated_old` | 50 |
| Total | 1000 |

The build check reports `0` invalid examples.

## Usage

```python
import json
from pathlib import Path

path = Path("dataset/nedo_final1000_gold.jsonl")
examples = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
print(len(examples))
```

## Result files

Frozen metrics:

- [`../frozen_results/RESULTS_FREEZE.md`](../frozen_results/RESULTS_FREEZE.md)
- [`../frozen_results/README_FINAL1000.md`](../frozen_results/README_FINAL1000.md)

Error analysis:

- [`../validation/README_VALIDATION.md`](../validation/README_VALIDATION.md)

## Note

## External links

| Resource | Link |
|---|---|
| GitHub repository | [`NMSOfficial/NedoTurkishTokenizer`](https://github.com/NMSOfficial/NedoTurkishTokenizer) |
| Hugging Face dataset | [`Ethosoft/NedoTurkishTokenizer-Final1000`](https://huggingface.co/datasets/Ethosoft/NedoTurkishTokenizer-Final1000) |
| Zenodo DOI | [`10.5281/zenodo.21274980`](https://doi.org/10.5281/zenodo.21274980) |

## Data and DOI

| Resource | Link |
|---|---|
| GitHub repository | [`NMSOfficial/NedoTurkishTokenizer`](https://github.com/NMSOfficial/NedoTurkishTokenizer) |
| Hugging Face dataset | [`Ethosoft/NedoTurkishTokenizer-Final1000`](https://huggingface.co/datasets/Ethosoft/NedoTurkishTokenizer-Final1000) |
| Zenodo DOI | [`10.5281/zenodo.21274980`](https://doi.org/10.5281/zenodo.21274980) |

## Citation

If you use this repository or the Final1000 evaluation set, cite the archived release:

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
