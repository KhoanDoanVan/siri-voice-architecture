# Study and experiment sequence

This is a proposed learning path, not Apple’s internal development plan. Source IDs resolve in the [reading catalog](03-reading-catalog.md). Suggested experiments are not implemented by this research task.

## 1. Understand the cascade

Read A03, A02, then A01. Trace one genuine request, one phonetic confusion, one other-speaker keyword and one incidental mention. Identify which stage has evidence to reject each case. Use the architecture diagram to distinguish always-on work from work performed only after a candidate.

Deliverable: an annotated diagram showing inputs, outputs, processor placement and provisional versus final decisions. Do not label the entire assistant as on-device solely because the activation system is on-device on supported hardware.

## 2. Learn acoustic features and temporal decoding

Study filter-bank features, MFCCs, state posteriors and dynamic programming before P01. Draw a tiny left-to-right keyword state graph. Compare framewise classification with sequence scoring on a fabricated example where isolated phonetic matches occur out of order.

Experiment: implement a small synthetic decoder and verify its score against enumeration of all allowed paths. This tests temporal reasoning without needing Apple data or weights. When studying differentiable decoding, inspect gradients and the exact score formulation rather than assuming every hard decoding operation has a conventional derivative everywhere.

## 3. Reproduce the personalization arithmetic

Read A02 and P11; use F07 and F05 for verification-aligned learning. Start with the historical supervector design to understand why alignment helps, then move to sequence embeddings.

Experiment: with consented speech and a suitable embedding extractor, implement enrollment and mean-cosine matching. Keep speakers disjoint across training, threshold selection and evaluation. Measure FR and IA as the threshold moves. Compare a fixed profile with a deliberately contaminated profile. This tests the adaptation risk; it is not a reproduction of Apple’s reported numbers.

## 4. Understand Figure 2 completely

Read F01, F02, F03, P04 and P05. Mark three distinct components: encoder CTC supervision, auxiliary autoregressive supervision, and the phrase-discriminative head. Identify which parts remain at inference.

Experiment: compare a phonetic-only checker with one receiving trigger-specific negatives, holding the evaluation set and false-alarm operating point fixed. The question is whether the added objective helps distinguish confusable phrases, not merely whether training loss falls.

## 5. Investigate directedness

Read P15, P06, P17 and P18, then the ODLD section of A01. Follow P16 if weak labels are important. Use P19 only as later exploratory context.

Experiment: construct paired utterances with the same keyword but different intent, and utterances with similar transcripts but different acoustic conditions. Compare acoustic and text evidence. If the ASR interface returns only a one-best transcript, a lattice experiment requires a different decoder/interface; a list of transcripts should not be mislabeled a full weighted lattice.

## 6. Measure resource use and deployment tradeoffs

Read P02, P03 and A10. Distinguish codebook weight storage, activation memory, runtime working space and audio buffers. P10 is a later alternative worth comparing once a baseline exists.

Experiment: measure actual weight bytes, peak memory, latency percentiles and device energy before and after compression. Recheck false accepts and false rejects. A smaller file alone does not demonstrate a better always-on system.

## 7. Extend beyond the trigger

Read A04 for far-field capture; A05/A06/P20 for ASR; A07 for readable transcripts; P24/P25 for understanding and ranking; A08/P29 for speech output. Read N01–N04 for later foundation-model context, retaining the publication dates in your architecture notes.

Experiment: draw a complete voice-assistant flow with endpointing, recognition, task interpretation, action execution and spoken response. Mark each block as supported by a specific source, your own implementation choice, or unknown. This prevents a plausible reconstruction from becoming an unsupported claim about Apple.

## Evaluation checklist for a future prototype

| Question | Measurement |
| --- | --- |
| Does it wake when intended? | FR on owner attempts, including quiet/noisy/far-field conditions |
| Does it wake in ordinary background audio? | FA per hour on long-form negatives |
| Does it accept another speaker? | IA on impostor attempts at a declared threshold |
| Is the profile drifting? | Owner/impostor performance before and after updates |
| How often does it wake the expensive processor? | Candidate/AP-wake rate, distinct from final false responses |
| How quickly does it react or cancel? | Median and tail latency for activation and mitigation |
| Can it fit and run continuously? | Weight size, peak RAM, measured power, thermal behavior |
| Does it understand the request? | WER plus task/intent success; report separately from triggering |
| Does performance transfer? | Results by held-out speaker, language, device and acoustic condition |

No production thresholds, model weights or benchmark results are provided by this study plan. Choose them from a documented validation protocol rather than importing historical Apple results as targets or guarantees.
