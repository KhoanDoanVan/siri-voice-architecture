# Public data for the first DNN–HMM experiment

Source review: 2026-10-16. Start with **Google Mini Speech Commands**, using **stop** as a provisional keyword and the other seven words as non-keyword speech. This makes the first experiment possible without collecting recordings. It tests the architecture on a single word; it does not train a custom phrase or reproduce Siri.

## Dataset shortlist

| Dataset | Best use here | Access and license reported by source | Important limitation |
| --- | --- | --- | --- |
| [Google Mini Speech Commands](https://www.tensorflow.org/tutorials/audio/simple_audio) | First small experiment and local EDA | Direct download, about 182 MB compressed; CC BY 4.0 inherited from Speech Commands | Eight isolated-word classes; no phonetic-state labels |
| [Google Speech Commands v0.02](https://huggingface.co/datasets/google/speech_commands/blob/main/README.md) | Expand speakers and negative vocabulary after the first demo | Public; CC BY 4.0; [official archive](https://storage.googleapis.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz) | Isolated commands rather than a complete real-world wake-phrase benchmark |
| [Hey Snips](https://github.com/sonos/keyword-spotting-research-datasets) | English wake-phrase benchmark with matched-domain negatives | Request-based access; academic/research only, no commercial use per repository | Access has not been obtained; unsuitable as an assumed commercial training source |
| [HI-MIA, OpenSLR 85](https://www.openslr.org/85/) | Real far-field Mandarin wake-phrase positives | Apache 2.0; train archive listed as 36 GB | Public challenge subset contains the Chinese wake phrase; verification negatives are not automatically non-keyword audio |
| [HI-MIA-CW, OpenSLR 120](https://www.openslr.org/120/) | Confusing Mandarin negatives paired with HI-MIA | CC BY-SA 4.0; audio about 550 MB | Supplemental confusing phrases, not positive wake phrases |
| [MUSAN, OpenSLR 17](https://www.openslr.org/17/) | Noise/music augmentation and additional negative material | CC BY 4.0; archive listed as 11 GB | Speech portions can contain the target word; screen before treating as negatives |
| [LibriSpeech, OpenSLR 12](https://www.openslr.org/12/) | Transcribed speech for alignment learning and broader speech negatives | CC BY 4.0; public subsets | Read audiobooks differ from mobile use; transcripts are not phone/state boundaries |

License names above report publisher metadata, not a conclusion that every intended downstream use is automatically covered. Retain each corpus's attribution and terms. No access request or message has been submitted to Sonos.

## Why these are credible sources

- **Speech Commands:** Pete Warden, [Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition](https://arxiv.org/abs/1804.03209), 2018. Google's [release announcement](https://www.research.google/blog/launching-the-speech-commands-dataset/) states the CC BY 4.0 release. TensorFlow supplies the small subset used here.
- **Hey Snips:** Coucke et al., *Efficient keyword spotting using dilated convolutions and gating*, ICASSP 2019; the [maintainer repository](https://github.com/sonos/keyword-spotting-research-datasets) provides paper links, format, access instructions and license. It lists roughly 11,000 positives and 86,500 negatives for that version; contributors may withdraw recordings, so actual received counts must be audited. Metadata includes worker IDs and supplied train/dev/test files.
- **HI-MIA:** Qin, Bu and Li, [HI-MIA: A Far-field Text-Dependent Speaker Verification Database and the Baselines](https://arxiv.org/abs/1912.01231). The [release](https://www.openslr.org/85/) has 254/42/44 speakers in train/dev/test and an updated test archive correcting corrupted audio. The paper describes a broader database than the public challenge subset: do not assume the English recordings are in this release.
- **HI-MIA-CW:** Wang et al., [Generating Adversarial Samples For Training Wake-up Word Detection Systems Against Confusing Words](https://arxiv.org/abs/2201.00167), linked by [OpenSLR](https://www.openslr.org/120/). The release lists 16,434 recordings from 35 speakers, separate from HI-MIA speakers, and provides transcripts and speaker information.
- **MUSAN:** Snyder, Chen and Povey, *MUSAN: A Music, Speech, and Noise Corpus*, 2015, linked by its [official release](https://www.openslr.org/17/).
- **LibriSpeech:** Panayotov et al., *LibriSpeech: an ASR corpus based on public domain audio books*, ICASSP 2015, linked by its [official release](https://www.openslr.org/12/).

## What was selected for this workspace

The small Google archive is the only audio corpus selected for immediate download. Larger corpora are source recommendations, not collected datasets. The preparation script writes measured results to [the EDA report](../data/reports/mini_speech_commands_eda.md) and creates JSONL manifests in `data/manifests/`.

The provisional target `stop` can be changed with `--keyword`. This is a deliberate stand-in while no custom phrase has been specified. A model trained on it cannot be renamed into a Hey Siri or custom-phrase detector.

## Split and EDA protocol implemented here

1. Extract only the expected WAV paths and the supplied README from the official archive.
2. Read every waveform; check encoding, channels, sampling rate, duration and complete PCM length. Measure RMS, peak level, DC offset and saturated-sample fraction.
3. Recover the supplied speaker identifier from the filename prefix before `_nohash_`.
4. Hash the decoded PCM. Exclude exact duplicates with conflicting word labels; keep duplicate-linked speakers in one partition.
5. Assign speaker groups deterministically by seeded SHA256 to approximately 80% training, 10% validation and 10% test. Exact clip proportions vary because speakers contribute different amounts.
6. Assert zero speaker-ID and exact-audio overlap across partitions. Write class counts, positive/negative counts, durations and quality flags.

This is a **custom speaker-disjoint mini-corpus split**, not Google's official full-corpus split. The downloaded mini README points to v0.01 for original documentation; do not label this archive as a verified v0.02 subset. If moving to the full v0.02 release, preserve its `validation_list.txt` and `testing_list.txt` when reporting that benchmark. Do not combine these custom mini partitions with full-corpus partitions without re-auditing speaker and audio overlap.

An exact-hash check cannot detect near-duplicates, transformed copies or a contributor recorded under multiple IDs. No demographic labels are available in this manifest, and acoustic quality flags do not replace listening to a sample.

## What is still missing for DNN–HMM labels

These word labels say **what** was spoken, not exactly **when each phoneme/state occurred**. The manifest intentionally sets keyword start/end to null and marks alignment unavailable.

For the simple four-state experiment discussed earlier:

1. Estimate speech boundaries on training clips and inspect a small sample.
2. Split the bounded keyword segment into three temporal parts, explicitly labeling them as approximate beginning/middle/end states.
3. Label the surrounding nonspeech separately; other-word clips are negative speech, not silence.

For the closer-to-Apple phonetic-state experiment, use the known word transcripts with a suitable forced aligner, inspect the alignments, and derive phone-state labels. Do not divide the entire one-second file into thirds: padding and silence would become incorrect keyword supervision.

## Streaming and future corpus splits

Concatenate clips only **within their assigned split** to debug continuous processing. Any resulting event labels describe a constructed stream, not naturally recorded conversations. Do not report its false-alarm rate as real mobile background performance.

Later, add continuous negative recordings and preserve source recording identity. Keep every crop, augmentation and microphone channel of the same utterance in the same split. For HI-MIA, retain official speaker partitions and use its channel mapping to avoid counting simultaneous channels as independent utterances. Its speaker-verification non-target trials can still contain the exact wake phrase; they are positive for speaker-independent first-pass detection.

For HI-MIA-CW, split its own speakers before augmentation and add negatives to matching partitions. Monitor the positive/negative source mismatch: the model might learn recording conditions instead of the phrase. For LibriSpeech or MUSAN, inspect transcripts/audio for actual target occurrences and group by speaker/source; do not assume all external audio is negative.

## Reproduce the preparation

From the project root:

```sh
mkdir -p data/downloads
curl --max-time 600 --fail --location --continue-at - \
  https://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip \
  --output data/downloads/mini_speech_commands.zip
python3 scripts/prepare_mini_speech_commands.py --keyword stop
```

The script uses Python 3.10's standard library, including `audioop` (removed in Python 3.13). No TensorFlow installation is required for collection, EDA or splitting. Re-running replaces the generated manifests/reports; it does not train a model. The locally computed archive hash records the received version but is not independently verified against a publisher checksum.
