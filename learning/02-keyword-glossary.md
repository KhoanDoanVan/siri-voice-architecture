# Siri architecture keyword glossary

Read this alongside the [architecture analysis](01-architecture-analysis.md) and [annotated references](03-reading-catalog.md). Reference IDs below link to that catalog; A01 and A02 are the two supplied Apple documents. “Extension” marks concepts useful for the broader assistant or later research, not components established by those documents.

## Highest-priority search vocabulary

Start with **keyword spotting, DNN-HMM, differentiable decoding, loss-metric mismatch, Conformer, CTC, multi-task learning, speaker embeddings, enrollment, cosine similarity, curriculum learning, device-directed speech detection, false trigger mitigation, ASR lattices, streaming self-attention, ODLD, palettization, DKM, R² loss, FR/FA/IA/EER**.

## Runtime and audio

| Keyword | Meaning and architectural role | References |
| --- | --- | --- |
| 1. Voice trigger / wake word | Spoken phrase that starts an assistant interaction; Siri and Hey Siri are the examples here | A01, A03 |
| 2. Keyword spotting (KWS) | Detect a particular phrase in continuous audio without transcribing everything | A01, P01 |
| 3. Always On Processor (AOP) | Low-power processor responsible for continuous first-pass detection in the mobile architecture | A01 |
| 4. Application Processor (AP) | Runs the more expensive candidate checker after first-pass detection | A01 |
| 5. Ring buffer | Bounded rolling storage for streaming audio; supplies recent context around a candidate | A01 |
| 6. Cascade / two-pass detection | Cheap high-recall proposal followed by expensive high-precision checking | A01, A03, P05 |
| 7. Streaming inference | Process incrementally as audio arrives rather than waiting for an entire utterance | A01, P06, P17 |
| 8. Acoustic frame | Short-time representation of the waveform; distinguish feature window length from frame step | A01, A03 |
| 9. Filter-bank features | Frequency-band energy representation consumed by acoustic models | A01, A03 |
| 10. MFCC | Mel-frequency cepstral coefficients; historical personalization uses state-wise averages of these features | A02 |
| 11. Phoneme / monophone | Basic speech sound unit; monophone targets support the checker’s acoustic objective | A01 |
| 12. Voice activity detection (VAD) | Speech/non-speech detection; conceptual background, not interchangeable with keyword detection | Background distinction in analysis |
| 13. Endpointing / end-of-speech | Decide when the request has ended; relevant to latency and complete lattices | A01, A09 |
| 14. Far-field speech | Speech captured at a distance, often affected by noise and reverberation | A04 |
| 15. Acoustic echo cancellation (AEC) | Reduce device playback leaking into microphones; broader HomePod front-end concept | A04 |
| 16. Multichannel filtering / beamforming | Combine microphone signals to enhance desired speech | A04 |
| 17. Blind source separation (BSS) | Separate competing sound sources without a known source waveform | A04 |
| 18. Stream selection | Choose an enhanced/separated audio stream using trigger-related evidence | A04; P09 explores multichannel alternatives |

## Detection models and objectives

| Keyword | Meaning and architectural role | References |
| --- | --- | --- |
| 19. Deep neural network (DNN) | Learns frame-state probabilities or embeddings; the role depends on the stage | A01–A03 |
| 20. Hidden Markov model (HMM) | Temporal state model that accumulates phonetic evidence over a sequence | A01, P01 |
| 21. Dynamic programming / Viterbi | Efficient computation over allowed state paths; max-path decoding is a useful explanatory example | A03, P01 |
| 22. Softmax / state posterior | Normalize output scores into a state distribution; not automatically an acoustic likelihood | A01, A03 |
| 23. Cross-entropy (CE) | Classification objective used for state labels, decoder outputs or speaker classes | A01, A02 |
| 24. Loss-metric mismatch | Training optimizes an intermediate prediction while deployment cares about trigger acceptance | P01, P04 |
| 25. Differentiable HMM decoding | Backpropagate through temporal scoring to train for keyword-level outcomes | P01 |
| 26. Conformer | Encoder combining convolution and self-attention; the 2023 high-precision checker uses this family | A01, F03 |
| 27. Transformer / self-attention | Contextual sequence representation; used in checker, acoustic FTM and text FTM with different constraints | A01, F02 |
| 28. Connectionist temporal classification (CTC) | Sequence loss that sums over alignments using blank/repetition handling | A01, F01 |
| 29. Autoregressive decoder | Predicts each next output conditional on earlier outputs; training-only auxiliary component in the described checker | A01, P05 |
| 30. Multi-task learning (MTL) | Shared representations trained with multiple objectives | P04, P05, P12 |
| 31. Discriminative trigger head | Binary keyword/non-keyword branch beyond general phonetic modeling | A01, P04 |
| 32. Hard negatives / phonetic confusables | Non-triggers resembling the keyword; useful negatives include “seriously” and similar sounds | A01 |
| 33. Progressive detection | Delay uncertain decisions for more post-trigger context while accepting clear cases quickly | P07; related research |
| 34. Reparameterization | Train a richer network and algebraically simplify it at inference | P10; later research |

## Personalization and speaker recognition

| Keyword | Meaning and architectural role | References |
| --- | --- | --- |
| 35. Speaker verification / speakerID | Compare voice identity with the enrolled user; the product’s block name should not obscure the verification decision | A01, A02 |
| 36. Text-dependent speaker recognition | Identity inference for a known phrase, such as Hey Siri | A02 |
| 37. Text-independent speaker recognition | Identity inference without requiring a fixed lexical sequence; enables use of request audio | A02, P11 |
| 38. Explicit enrollment | Guided collection of reference utterances | A01, A02 |
| 39. Implicit enrollment | Update the stored profile from accepted real-world utterances in the 2018 description | A02 |
| 40. Profile contamination / drift | Incorrectly accepted audio corrupts adaptation; a risk explicitly identified in the older article | A02 |
| 41. Speech supervector | Concatenation of state-aligned acoustic means; not yet an identity-only representation | A02 |
| 42. Speaker embedding / speaker vector | Fixed-size learned representation intended to emphasize identity | A01, A02 |
| 43. Linear discriminant analysis (LDA) | Linear transform emphasizing between-speaker differences relative to within-speaker variation | A02 |
| 44. Cosine similarity | Normalized dot product; averaged over reference vectors in the 2018 profile matcher | A02 |
| 45. LSTM / recurrent neural network (RNN) | Sequence model used to summarize variable-length speaker audio | A01, P11 |
| 46. Curriculum learning | Organize training progression to support harder or more varied conditions | A01, A02, P11 |
| 47. Multi-style training | Augment training conditions with noise/reverberation and other variation | A02, P11 |
| 48. Multilingual speaker training | Pool languages to learn a shared identity representation | A01 |
| 49. Metric learning | Learn representations for similarity-based decisions; can personalize keyword detection as well as identity | P08, F07 |
| 50. Verification-oriented binary loss / SphereFace2 | Align representation training more closely with accept/reject use | A01, F05 |

## Directedness and mitigation

| Keyword | Meaning and architectural role | References |
| --- | --- | --- |
| 51. Siri-directed speech detection (SDSD) | Decide whether a full utterance is intended for Siri | A01 |
| 52. False trigger mitigation (FTM) | Cancel unintended activations using additional evidence | A01, P06, P15–P18 |
| 53. ASR lattice | Graph retaining competing recognized word sequences and scores | A01, P14, P15 |
| 54. Weighted finite-state transducer (WFST) | Weighted graph formalism used in recognition and decoding | A01, F06 |
| 55. Lattice RNN / graph neural network | Model a recognition graph rather than only its best text path | A01, P14, P15 |
| 56. Acoustic FTM (aFTM) | Directedness classification directly from audio features | A01, P06, P17, P18 |
| 57. Blockwise attention / left context | Restrict attention to available streaming context | A01, P06 |
| 58. Attention mask | Encode allowed context dependencies in training and inference | A01 |
| 59. Attention pooling / summarization | Reduce a variable-length sequence into a fixed-size acoustic representation | A01 |
| 60. Prosody / paralinguistics | Timing, pitch, emphasis and other vocal cues beyond the recognized words | A01, P27 |
| 61. Out-of-domain language detector (ODLD) | Text-based directedness and non-vocative classification | A01 |
| 62. Vocative / non-vocative | Addressing Siri versus mentioning Siri in ordinary speech | A01 |
| 63. BERT-like encoder / classification token | Text representation used by ODLD classification heads | A01, F04 |
| 64. Knowledge distillation / weak supervision | Learn from teacher outputs or imperfect labels when manual supervision is scarce | P16; related method |

## Compression, metrics and the broader assistant

| Keyword | Meaning and architectural role | References |
| --- | --- | --- |
| 65. Palettization / codebook | Store weight indices into a compact set of values | A01, P02 |
| 66. Differentiable k-means (DKM) | Learn weight clusters and network parameters jointly | P02 |
| 67. R² / range restriction | Reduce extreme weights to make low-bit representation more effective | P03 |
| 68. Quantization / bit width | Reduce numerical precision; assess weights, activations and runtime separately | A01, A02, P03 |
| 69. False accept (FA) / false alarm | Non-trigger causes activation; often measured per hour of negative audio | A02 |
| 70. False reject (FR / FRR) | Genuine owner invocation is missed | A02 |
| 71. Impostor accept (IA) | Another speaker’s attempt passes identity verification | A02 |
| 72. Equal error rate (EER) | Speaker-verification operating point with matching reject and impostor-accept rates | A02 |
| 73. Operating point / threshold | Trade off misses and unwanted activations; stage-specific thresholds need joint evaluation | A01, A02 |
| 74. Word error rate (WER) | Substitutions, deletions and insertions relative to reference words; measures ASR rather than triggering | A04, A09 |
| 75. Contextual language modeling / Geo-LM | Bias recognition using context such as nearby places | A06; extension |
| 76. Inverse text normalization (ITN) | Convert recognized spoken forms into readable written forms | A07; extension |
| 77. Intent ranking / entity labeling | Select the intended task and its arguments after language understanding | P24–P26; extension |
| 78. Text-to-speech (TTS) / neural vocoder | Generate speech from text and acoustic representations | A08, P29; extension |
| 79. Mixture density network (MDN) | Predict distributions of acoustic features; historical Siri hybrid synthesis | A08; extension |
| 80. Federated learning / differential privacy | Distributed learning and privacy protection mechanisms; distinct from merely running inference locally | P13, N05, N06; extension |
| 81. Foundation models / multimodal models | Later general-purpose language/audio/vision systems; do not assume they replace the trigger cascade | N01–N04; later context |

## Search phrases for deeper study

Use the exact paper titles in the catalog for reproducible lookup. Useful topic searches include:

- `site:machinelearning.apple.com/research voice trigger DNN HMM end metric`
- `site:machinelearning.apple.com/research speaker verification curriculum learning`
- `site:machinelearning.apple.com/research device directed speech false trigger`
- `site:machinelearning.apple.com/research lattice voice triggering`
- `site:machinelearning.apple.com/research Siri speech recognition language model`
- `site:machinelearning.apple.com/research on device neural speech synthesis`
- `site:machinelearning.apple.com/research palettization differentiable k means`
- `site:machinelearning.apple.com/research Siri foundation models`

Keep the distinctions explicit: **speaker recognition ≠ speech recognition; KWS ≠ VAD; ODLD ≠ complete NLU; low EER ≠ best deployed threshold; local inference ≠ federated training; research publication ≠ confirmed deployment**.
