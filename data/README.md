# First-experiment audio data

The current nine-stage pipeline is documented in the [project README](../README.md), with its [visual report](../reports/preprocessing/baseline_v1/report.md). Its cleaned, deduplicated manifests are in `processed/baseline_v1/09_final/`. The `manifests/` and `reports/` files listed below are the earlier ingestion/EDA baseline and remain preserved for provenance; do not mix their splits with the current pipeline run.

Source selection and limitations: [public dataset guide](../learning/06-public-datasets.md).

- `downloads/mini_speech_commands.zip`: original Google-hosted archive.
- `raw/mini_speech_commands/`: extracted audio and publisher README.
- `manifests/train.jsonl`, `validation.jsonl`, `test.jsonl`: custom speaker-group splits; provisional positive word is `stop`.
- `reports/mini_speech_commands_eda.md`: measured summary.
- `reports/mini_speech_commands_eda.json`: machine-readable counts and provenance.
- `reports/rejected_audio.json`: exclusions, if any.

Audio attribution: Google Speech Commands, Pete Warden and contributors; CC BY 4.0. See the retained publisher README, [original release](https://www.research.google/blog/launching-the-speech-commands-dataset/) and [dataset paper](https://arxiv.org/abs/1804.03209). The local preparation changes organization and adds metadata; the extracted WAV recordings are unmodified.

Paths inside manifests are relative to the project root. Other-word clips are not silence. Timing/phonetic alignment fields remain unavailable; none were fabricated. This small isolated-word corpus supports a mechanics experiment, not a production wake-word claim.
