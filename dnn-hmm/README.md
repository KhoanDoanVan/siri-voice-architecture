# DNN–HMM preprocessing and alignment notebooks

**Start with [01 · Raw data ingestion](01_raw_data_ingestion.ipynb).** Follow the notebooks in order. Each notebook contains the actual implementation for its stage, organized into focused code cells beside its explanations and figures. There is no separate `src/` implementation.

| Notebook | Main output |
| --- | --- |
| [01 · Raw data ingestion](01_raw_data_ingestion.ipynb) | Source inventory, hashes and word/speaker coverage |
| [02 · Data profiling](02_data_profiling.ipynb) | Audio measurements, distributions, flags and an audio playback example |
| [03 · Data cleaning](03_data_cleaning.ipynb) | Exact duplicate removal and exclusion audit |
| [04 · Dataset splitting](04_dataset_splitting.ipynb) | Speaker-disjoint training/validation/test manifests |
| [05 · Signal standardization](05_signal_standardization.ipynb) | Consistent audio format and waveform comparison |
| [06 · Data augmentation](06_data_augmentation.ipynb) | Training-only gain/noise variants and parent lineage |
| [07 · Feature extraction](07_feature_extraction.ipynb) | Causal log-Mel features and spectrogram |
| [08 · Feature normalization](08_feature_normalization.ipynb) | Frozen training statistics and per-split distribution checks |
| [09 · Quality assurance](09_quality_assurance.ipynb) | Acceptance checks, final report and dataset-fit assessment |
| [10 · HMM topology and bootstrap alignment](10_hmm_topology_and_bootstrap_alignment.ipynb) | Four-state topology, energy boundary and frame pseudo-labels |

Open these files in VS Code's notebook editor or another Jupyter-compatible environment and select the repository's `.venv/bin/python` kernel. Run each notebook top to bottom. Each stage reads persisted artifacts from the previous stage, so kernels do not need to share variables.

Numerical code cells are preceded by **Math for the next code block** notes. Each note gives the equivalent equation, defines its symbols, states array shapes where relevant, and explains the audio meaning. Common symbols are: $N$ samples, $f_s$ sample rate, $W$ window length, $H$ frame hop, $T$ feature frames, and $M$ Mel bands.

Configuration: [preprocessing.json](../configs/preprocessing.json). Output: `../data/processed/baseline_v1/`. Figures: `../reports/preprocessing/baseline_v1/figures/`, in PNG and SVG. The earlier `data/manifests/` split remains historical; do not mix it with these outputs.

To execute all ten notebooks and save their figures/tables from the project root:

```sh
.venv/bin/python scripts/execute_notebooks.py
```

**Dataset fit:** suitable for learning the mechanics of a small `stop` detector. It is not yet a supervised phonetic DNN–HMM training set: timing/state labels are missing. Continuous background, confusable phrases and representative mobile recordings are also needed before evaluating production behavior. Notebook 09 makes these limits explicit.

Notebook 10 creates explicitly marked bootstrap pseudo-labels for the first modeling experiment. They do not change the dataset-fit verdict: energy boundaries and uniform keyword states are initialization targets, not verified phonetic annotations.
