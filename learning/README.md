# Siri architecture research collection

Prepared 2026-10-16 from the two Apple articles supplied in this project and primary-source web research.

| Document | What it contains |
| --- | --- |
| [Architecture analysis](01-architecture-analysis.md) | Detailed 2018/2023 analysis, pipeline diagram, training/inference distinctions, equations, evaluation, gaps and citation corrections |
| [Keyword glossary](02-keyword-glossary.md) | 81 concepts grouped by component, with reference IDs and search terms |
| [Reading catalog](03-reading-catalog.md) | 53 annotated Apple articles, papers and foundational references, with evidence and deployment distinctions |
| [Machine-readable sources](sources.json) | Same 53 entries for filtering or importing into a reference system |
| [Study and experiment sequence](04-study-plan.md) | Reading dependencies and small experiments to test understanding |
| [First-pass DNN–HMM experiment checklist](05-first-pass-dnn-hmm-experiment-checklist.md) | Concrete streaming baseline, label alignment, HMM decoding, data plan, evaluation gates and mobile measurements |
| [Public datasets and split plan](06-public-datasets.md) | Trusted corpus sources, selected starter data, EDA, leakage checks and missing-label guidance |
| [Nine-stage preprocessing implementation](../README.md) | Runnable pipeline, tests, versioned configuration and artifact layout |
| [Visual preprocessing report](../reports/preprocessing/baseline_v1/report.md) | Actual data measurements, six PNG/SVG figures, quality checks and dataset-fit verdict |

The core sources are [Voice Trigger System for Siri](https://machinelearning.apple.com/research/voice-trigger) (2023) and [Personalized Hey Siri](https://machinelearning.apple.com/research/personalized-hey-siri) (2018). Their full local copies are in `../apples/`. The three PDFs already in `../papers/` map to P01 (*Optimize What Matters*), P02 (*DKM*) and P03 (*R²*).

The main finding is that reliable activation combines four different judgments: **keyword presence, phonetic confirmation, speaker identity and assistant-directedness**. The two articles cover this activation path; additional catalog entries extend into ASR, NLU, synthesis and later foundation models.

The collection is broad but not an exhaustive inventory of every blog on the web. It prioritizes original Apple engineering articles and primary papers. The two supplied articles received full-text analysis; the catalog records the more limited review depth for other entries. Source links and annotations are collected here; copyrighted articles and additional PDFs have not been bulk copied.
