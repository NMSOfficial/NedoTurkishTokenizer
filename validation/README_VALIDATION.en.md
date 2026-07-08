# Validation and Error Analysis

[Türkçe](README_VALIDATION.md)

This directory contains error analysis and validation files for the Final1000 results.

## Files

| File | Description |
|---|---|
| [`error_examples_20_correct_20_wrong.md`](error_examples_20_correct_20_wrong.md) | 20 correct and 20 incorrect examples |
| [`error_examples_20_correct_20_wrong.csv`](error_examples_20_correct_20_wrong.csv) | CSV version of the same examples |
| [`segmentation_error_inventory.json`](segmentation_error_inventory.json) | Segmentation error inventory |
| [`label_error_summary.json`](label_error_summary.json) | Labeling error summary |
| [`long_word_analysis.json`](long_word_analysis.json) | Long-word analysis |
| [`foreign_root_error_analysis.json`](foreign_root_error_analysis.json) | Foreign-root / code-mix analysis |

## Summary

NedoTurkishTokenizer reports Boundary F1 `0.6966` on Final1000.

Additional metrics:

| Metric | Value |
|---|---:|
| Precision | 0.7717 |
| Recall | 0.6348 |
| Exact boundary-set accuracy | 64.7% |
| Over-segmentation | 16.7% |
| Under-segmentation | 30.9% |
| Label Precision | 0.5318 |
| Label Recall | 0.4129 |

## Code-mix / foreign roots

Performance drops on foreign-root + Turkish-suffix forms.

| Metric | Value |
|---|---:|
| Cases | 240 |
| Precision | 0.5882 |
| Recall | 0.1667 |
| F1 | 0.2597 |

## Long words

Boundary exact accuracy is lower on long words than on short words. See [`long_word_analysis.json`](long_word_analysis.json) for details.
