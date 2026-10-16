# Mini Speech Commands: measured EDA

Target keyword: **stop**. Valid clips: **8000**; speaker IDs: **1750**.

| Split | Clips | Speakers | Positive | Other words | Minutes |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 6409 | 1390 | 798 | 5611 | 105.12 |
| validation | 832 | 185 | 109 | 723 | 13.68 |
| test | 759 | 175 | 93 | 666 | 12.36 |

Custom deterministic speaker-group split, approximately 80/10/10. Exact duplicate audio links speakers into the same split group. This is not the official full-corpus split.

Duration range: 0.427–1.000 seconds. Shorter than one second: 822 clips.

Rejected clips: 0. Exact duplicate PCM groups: 27. Clips with saturated samples: 363 (flagged, not automatically rejected).

Low-level clips below -50 dBFS: 204 (heuristic review flag; not automatically removed).

Checked: zero speaker-ID overlap and zero exact-PCM overlap across splits. Duplicate clips within a split are retained and should be deduplicated or weighted before final benchmarking.

## Word counts

| Word | Train | Validation | Test |
| --- | ---: | ---: | ---: |
| down | 793 | 102 | 105 |
| go | 805 | 97 | 98 |
| left | 834 | 90 | 76 |
| no | 790 | 106 | 104 |
| right | 824 | 94 | 82 |
| stop | 798 | 109 | 93 |
| up | 776 | 127 | 97 |
| yes | 789 | 107 | 104 |

## Limits

- Word labels only; no verified keyword boundaries or phonetic-state alignments
- Other-word clips are not silence and not representative continuous background
- Exact hashes do not detect near-duplicates or unidentified repeat contributors
- No model trained; no manual audio-quality or label audit performed

Do not infer phoneme states from whole-file thirds: files can include silence. Obtain or inspect speech boundaries before approximate temporal labels, and use forced alignment for phonetic labels.

Archive SHA256: `49650f2341b26d886b46b3f4fb8fed59e30300b17550f1ee4a768b3106cf93a0`. This is a locally computed provenance hash, not an independently published checksum.
