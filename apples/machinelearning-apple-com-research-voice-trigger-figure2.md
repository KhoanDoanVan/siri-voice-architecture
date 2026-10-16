[content type highlight](https://machinelearning.apple.com/highlights)published August 11, 2023

[research area Speech and Natural Language Processing](https://machinelearning.apple.com/highlights?domain=Speech%20and%20Natural%20Language%20Processing)

# Voice Trigger System for Siri

A growing number of consumer devices, including smart speakers, headphones, and watches, use speech as the primary means of user input. As a result, voice trigger detection systems—a mechanism that uses voice recognition technology to control access to a particular device or feature—have become an important component of the user interaction pipeline as they signal the start of an interaction between the user and a device. Since these systems are deployed entirely on-device, several considerations inform their design, like privacy, latency, accuracy, and power consumption.

In this article, we will discuss how Apple has designed a high-accuracy, privacy-centric, power-efficient, on-device voice trigger system with multiple stages to enable natural voice-driven interactions with Apple devices. The voice trigger system supports several Apple device categories like iPhone, iPad, HomePod, AirPods, Mac, Apple Watch, and Apple Vision Pro. Apple devices simultaneously support two keywords for voice trigger detection: “Hey Siri” and “Siri.”

We address four specific challenges of voice trigger detection in this article:

- Distinguishing a device’s primary user from other speakers
- Identifying and rejecting false triggers from background noise
- Identifying and rejecting acoustic segments that are phonetically similar to trigger phrases
- Supporting a shorter phonetically challenging trigger phrase (“Siri”) across multiple locales

## [Voice Trigger System Architecture](https://machinelearning.apple.com/research/voice-trigger\#voice-trigger-system-architecture)

The multistage architecture for the voice trigger system is shown in [Figure 1](https://machinelearning.apple.com/research/voice-trigger#figure1). On mobile devices, audio is analyzed in a streaming fashion on the Always On Processor (AOP). An on-device ring buffer is used to store this streaming audio. The user’s input audio is then analyzed by a streaming high-recall voice trigger detector system, and any audio that does not contain the trigger keywords is discarded. Audio that may contain the trigger keywords is analyzed using a high-precision voice trigger checker system on the Application Processor (AP). For personal devices, like iPhone, the speaker identification (speakerID) system is used to analyze if the trigger phrase is uttered by the owner of the device or another user. Siri directed speech detection (SDSD) analyzes the full user utterance, including the trigger phrase segment, and decides whether to mitigate any potential false voice trigger utterances. We detail individual systems in the following sections.

![Figure 1: System architecture of Siri Voice Trigger System](https://mlr.cdn-apple.com/media/Fig1_siri_0f3233cfb7.png)

Figure 1: Architecture of Siri voice trigger system. The detector analyzes audio continuously to detect a potential chunk of audio that may contain the trigger keywords. Checker and the speakerID systems analyze a chunk of audio to determine with high precision whether the enrolled user or someone else spoke the keywords. The Siri directed speech detection (SDSD) system analyzes the full utterance by the user to mitigate any potential false triggers.

## [Streaming Voice Trigger Detector](https://machinelearning.apple.com/research/voice-trigger\#streaming-voice-trigger-detector)

The first stage in the voice trigger detection system is a low-power, first-pass detector that receives streaming input from the microphone and is a deep neural network (DNN) hidden markov model (HMM) based keyword spotting model, as discussed in our research article, [Personalized Hey Siri.](https://machinelearning.apple.com/research/personalized-hey-siri) The DNN predicts the state probabilities of a given speech frame. At the same time, the HMM decoder uses dynamic programming to combine the DNN predictions of multiple speech frames to compute the keyword detection score. The DNN output contains 23 states:

- 21 corresponding to seven phonemes of the trigger phrases (three states for each phoneme)
- One state for silence
- One for background

Using a softmax layer, the DNN outputs probability distributions corresponding to 23 states for each speech frame and is trained to minimize the average cross-entropy loss between the predicted and ground-truth distributions. The softmax layer training ignores the HMM transition and prior probabilities, which are learned independently using training data statistics, according to the paper [Optimize What Matters.](https://arxiv.org/abs/2011.01151) A DNN model trained independently relies on the accuracy of the ground-truth phoneme labels and the HMM model. The DNN model also assumes that the set of keyword states is optimal, and each state is equally important for the keyword detection task. The DNN spends all of its capacity focusing equally on all states without considering its impact on the final metric of the detection score, resulting in a loss-metric mismatch. Through an end-to-end training strategy, we can fine-tune the DNN parameters by optimizing for detection scores.

To maximize the score for a keyword and minimize the score for non-keyword speech segments, we make the HMM decoder (dynamic programming) differentiable and backpropagate. Mobile devices have limited power and available computational resources, and memory is constrained for the always-on streaming voice trigger detector system. To address this challenge, we employ advanced palettization techniques to compress the DNN model to 4 bits per weight for inference, according to the papers [DKM: Differentiable K-Means Clustering Layer for Neural Network Compression](https://machinelearning.apple.com/research/differentiable-k-means) and [R^2: Range Regularization for Model Compression and Quantization.](https://arxiv.org/abs/2303.08253)

## [High Precision Conformer-Based Voice Trigger Checker](https://machinelearning.apple.com/research/voice-trigger\#high-precision-conformer-based-voice-trigger-checker)

If a detection is made at the first pass on stage, larger, more complex models are used to re-score the candidate acoustic segments from the first pass. We use a conformer encoder model with self-attention and convolutional layers, as shown in [Figure 2](https://machinelearning.apple.com/research/voice-trigger#figure2). Compared to bidirectional long short-term memory (BiLSTM) and transformer architectures, conformer layers provide better accuracy. Also, conformer layers process the entire input sequence with feed-forward matrix multiplications. We can significantly improve training and inference times because the feed-forward computations in the self-attention and convolutional layers with large matrix multiplication operations are easily parallelized using the available hardware.

We add an autoregressive self-attention layer-based decoder as an auxiliary loss. We demonstrate that when we jointly minimize the connectionist temporal classification (CTC) loss on the encoder and the cross-entropy loss on the decoder, we observe additional improvements compared to solely minimizing the CTC loss. During inference, we only utilize the encoder part of the network to prevent sequential computations in the autoregressive decoder. As a result, the transformer decoder plays a role in the regularization of the CTC loss. This setup can be viewed as an instance of multitask learning where we jointly minimize two different losses.

The model architectures outlined above are monophone acoustic models (AMs), which are designed to minimize the CTC loss alone or a combination of the CTC loss and the cross-entropy loss during training. As argued in [Multi-task Learning for Voice Trigger Detection,](https://arxiv.org/abs/2001.09519) this AM training objective does not match the final objective of our study, which is to discriminate between examples of true triggers and phonetically similar acoustic segments. This model improved further when we added a relatively small amount of trigger phrase-specific discriminative data and fine-tuned a pretrained phonetic AM to simultaneously minimize the CTC loss and the discriminative loss. We take the encoder branch of the model and add an additional output layer (affine transformation and softmax nonlinearity) with two output units at the end of the encoder network. One unit corresponds to the trigger phrase, while the other corresponds to the negative class.

The objective for the discriminative branch is as follows: For positive examples, we minimize the loss C{C}C = − max⁡t\\max\_tmaxt​log⁡ytP\\log y^P\_tlogytP​, where ytPy^P\_tytP​ is the network output at time ttt for the positive class. This loss function encourages the network to yield a high score independent of the temporal position; note that this is for networks that read the entire input at once. For negative examples, the loss function is C{C}C = −Σt\\Sigma\_tΣt​log⁡ytN\\log y^N\_tlogytN​, where ytNy^N\_tytN​ is the network output for the negative class at time ttt. This loss forces the network to output a high score for the negative class at every frame.

![Neural network architecture of Hybrid conformer/transformer CTC voice trigger system.](https://mlr.cdn-apple.com/media/Fig2_encoderdecoder_0633c3ded7.png)

Figure 2: Neural network architecture of hybrid conformer/transformer connectionist temporal classification (CTC) voice trigger system. A chunk of audio is transformed using a conformer encoder with CTC loss with regards to target phonemes as the training objective. There is an additional affine layer (not shown) at the end of the encoder embeddings, which is trained in a phrase-specific discriminative way to distinguish keywords from non-keywords.

## [Personalized Voice Trigger System](https://machinelearning.apple.com/research/voice-trigger\#personalized-voice-trigger-system)

In a voice trigger detection system, unintended activations can occur in three scenarios:

- When the primary user says a similar-sounding phrase (for example, “seriously”)
- When other users say the keyword (for example, “Hey Siri”)
- When other users say a similar-sounding phrase (for example, “cereal”)

To reduce the false triggers from users other than the device owner, we personalize each device, and it only wakes up when the primary user says the trigger keywords. To do so, we leverage techniques from the field of speaker recognition.

The overall goal of speaker recognition is to ascertain a person’s identity using their voice. We are interested in ascertaining who is speaking, as opposed to the problem of speech recognition, which aims to ascertain what was said. Applying a speaker recognition system involves two phases: enrollment and recognition. During the guided enrollment phase, the user is prompted to say the following sample phrases:

- “Siri, how’s the weather?”
- “Hey Siri, send a message.”
- “Siri, set a timer for three minutes.”
- “Hey Siri, get directions home.”
- “Siri, play some music.”

From these phrases, we create a statistical representation of the user’s voice. In the recognition phase, our speaker recognition system compares the incoming utterance to the user’s enrollment representation stored on-device and decides whether to accept it as the user or reject it as another user.

The core of speaker recognition is robustly representing a user’s speech, which can vary in duration via a fixed-length speaker embedding. In a 2018, [Personalized Hey Siri,](https://machinelearning.apple.com/research/personalized-hey-siri) we gave an overview of our speaker embedding extractor at the time. Since then, we have improved the accuracy and robustness by:

- Updating the model architecture
- Training on more generalized data
- Modifying the training loss to be better aligned with the setup at inference time

For model architecture, we demonstrated the efficacy of curriculum learning with a recurrent neural network (RNN) architecture (specifically LSTMs) to summarize speaker information from variable-length audio sequences. This allowed us to ship a single speaker embedding extractor that provides robust embeddings given audio containing: the trigger phrase (for example, “Hey Siri”) and both the trigger phrase and the subsequent utterance (“Siri, send a message.”)

The system architecture diagram in [Figure 1](https://machinelearning.apple.com/research/voice-trigger#figure1) shows the two distinct uses of the SpeakerID block. At the earlier stage, just after the AP voice trigger checker stage, our models are able to quickly decide whether or not the device should continue listening, given just the audio from the trigger phrase. Given the additional audio from both the trigger phrase and the utterance at the later false trigger mitigation stage, our models can make a more reliable and accurate decision about whether the incoming speech is coming from the enrolled user.

For additional data generalization, we found that training our LSTM speaker embedding extractor using data from all languages and locales improves accuracy everywhere. In locales with less abundant data, leveraging data from other languages improves generalization. And in locales where data is plentiful, incorporating data from other languages improves robustness. After all, if the same user speaks multiple languages, they are still the same user. Lastly, from an engineering efficiency standpoint, training a single speaker embedding extractor on all languages allows us to ship a single, high-quality model across all locales.

Finally, we took inspiration from the face recognition literature, [SphereFace2,](https://arxiv.org/abs/2108.01513) and incorporated ideas from a novel binary classification training framework into our training loss function. This helped bridge the gap between how speaker embedding extractors are typically trained as a multiclass classifier via cross-entropy loss and how they are used at inference—to make a binary accept/reject decisions.

## [False Trigger Mitigation (FTM)](https://machinelearning.apple.com/research/voice-trigger\#false-trigger-mitigation-ftm)

Although the trigger-phrase detection algorithms are precise and reliable, the operating point may allow nontrigger speech or background noise to unexpectedly falsely trigger the device, despite the user not having spoken the trigger phrase, according to the paper [Streaming Transformer for Hardware Efficient Voice Trigger Detection and False Trigger Mitigation.](https://arxiv.org/abs/2105.06598) To minimize false triggers, we implement an additional trigger phrase detector that utilizes a significantly larger statistical model. This detector would analyze the complete utterance, allowing for a more precise audio analysis and the ability to override the device’s initial trigger decision. We call this the Siri directed speech detection (SDSD) system. We deploy three distinct types of FTM systems to reduce the voice trigger system from responding to unintended false triggers. Each system tries to leverage different clues to identify false triggers.

**ASR lattice-based false trigger mitigation system (latticeRNN).** Our system uses automatic speech recognition (ASR) decoding lattices to determine whether a user request is a false trigger. Lattices are obtained as weighted finite state transducer (WFST) graphs during the beam-search decoding step in ASR, as referenced in the work [weighted finite-state transducers in Speech Recognition.](https://dl.acm.org/doi/10.1006/csla.2001.0184) They represent the top few competing word sequences hypothesized for the processed utterance. Our lattice RNN FTM approach is based on the hypothesis that a true (intended) utterance spoken by a user is less noisy. The best word-sequence hypothesis has zero (or few) competing hypotheses in the ASR lattice, according to our paper [Lattice-Based Improvements for Voice Triggering Using Graph Neural Networks.](https://machinelearning.apple.com/research/lattice-based-improvements-for-voice-triggering) On the other hand, false triggers often originate either from background noise or from speech that sounds similar to the trigger-phrase. Multiple ASR hypotheses may compete during decoding and be present as alternate paths in the lattices of false trigger utterances.

We do not rely on the one-best ASR hypothesis for FTM because the acoustic and language models can sometimes “hallucinate” the trigger-phrase. Instead, our approach leverages the whole ASR lattice for FTM. Along with the trigger phrase audio, we expect to exploit the uncertainty in the post-trigger-phrase audio as well. True triggers typically have device-directed speech (for example, “Siri, what time is it?”) with limited vocabulary and query-like grammar, whereas false triggers may have random noise or background speech (for example, “Let’s go grab lunch”). The decoding lattices explicitly exhibit these differences, and we model them using LSTM-based RNNs.

When a voice trigger detection mechanism detects a trigger, the system starts processing user audio using a full-blown ASR system. A dedicated algorithm determines the end-of-speech event, at which point we obtain the ASR output and the decoding lattice. We use word-aligned lattices such that each arc corresponds to a hypothesized word and derive feature vectors for lattice arcs. Lattices can be visualized as directed acyclic graphs defined using a collection of nodes and edges. If we denote lattice arcs as nodes of the graph, a directed edge exists between two nodes if the corresponding arcs in the lattice are connected. Each node (or arc) has a feature vector associated with it. The FTM task is to take a lattice as a graph input and do a binary classification between a true and false trigger class.

**Acoustic-based false trigger mitigation system (aFTM).** aFTM is a streaming transformer encoder architecture that processes incoming audio chunks and maintains audio context, as seen in [Figure 3](https://machinelearning.apple.com/research/voice-trigger#figure3). aFTM performs the FTM tasks using only acoustic features (filter banks), as referenced in our paper [Less Is More: A Unified Architecture for Device-Directed Speech Detection with Multiple Invocation Types.](https://machinelearning.apple.com/research/unified-architecture) The advantage of having an acoustic-only FTM system is that it is independent and unbiased from the ASR system, which tends to hallucinate the trigger keyword because of the dominance of keywords in the training data. Moreover, an acoustic-only system can learn and distinguish voice assistant intended speech by utilizing prosody features and other acoustic characteristics present in the audio, such as signal-to-noise ratio (for instance, in the presence of background speech).

The backbone—which we call the streaming acoustic encoder—extracts acoustic embeddings for each input audio frame. And instead of processing the trigger phrase only, it also processes the speech or request that comes after the trigger phrase). The backbone encoder replaces the vanilla self-attention (SA) layers with streaming SA layers. The streaming SA layers process the incoming audio in a block-wise manner with a certain shared left context and no look ahead. We simulate the streaming block processing in a single pass while training by assigning an attention mask to the attention weight matrix of the vanilla SA layer. The mask generates the equivalent attention output of a streaming SA and helps avoid slowdown of the training and the model inference by iterative block processing. The incoming input audio (speech) is passed through the SA layers (in this example, N = 3), where the processing is done in a block-wise manner (block size = 2S), with an overlap of S = 32 frames (~1 second of audio) to allow for context propagation.

For output summarization, we use the traditional attention-based mechanism, where attention weights are computed for each acoustic embedding (corresponding to the input audio frames), mapping the temporal sequence of audio embeddings (in the output of each streaming bock) onto a fixed-size acoustic embedding. Afterward, the acoustic embedding is passed through a fully-connected linear layer, which maps it to a 2D logits space. The final mitigation score (Y) is obtained via a softmax layer, outputting the probability of the input audio being device-directed.

![Figure 3: Streaming self-attention-based acoustic False Trigger Mitigation system](https://mlr.cdn-apple.com/media/Fig4_falsetriggere_aff9f79c28.png)

Figure 3: Streaming self-attention-based acoustic false trigger mitigation (FTM) system. Streaming self-attention (SA) layers act as audio feature encoders of the input filter-bank features (X). The summarization of the sequence of acoustic embeddings (Z) in the encoder output is performed with an attention-based summarization layer, followed by a linear layer that projects the fixed-size acoustic embedding to a 2D logits space. The final mitigation score (Y) is obtained via a softmax layer, outputting the probability of the input audio being device-directed.

**Text-based out-of-domain language detector (ODLD).** This text-based FTM system is a semantic understanding system that discriminates whether the user utterance is directed to a voice assistant or not, as shown in [Figure 4](https://machinelearning.apple.com/research/voice-trigger#figure4). Specifically, the keyword can be utilized as a noun or a verb in regular speech that is not directed toward an assistant, serving a nonvocative purpose. The ODLD system tries to suppress such utterances. We utilize a transformer-based natural language understanding model similar to BERT that is pretrained with large amounts of text data. The classifier heads of the text FTM model are built on top of the classification token output of the base embedding model. The classification heads are fine-tuned with positive training data from utterances directed toward an assistant, and negative training data from regular conversational utterances not directed toward a voice assistant. In addition to identifying if the user is addressing the assistant, the model identifies non-vocative uses of the word “Siri” to further refine its decisions. The model is optimized in size, latency, and power to run on-device on platforms like iPhone.

![Figure 4: BERT based Text ODLD FTM system](https://mlr.cdn-apple.com/media/Fig5_ODLD_4627c7f1d0.png)

Figure 4: Neural network architecture of text-based out-of-domain language detector (ODLD). Input text tokens are encoded into a sentence-level representation via transformer encoder layers, followed by classification heads for user intent and non-vocative detection.

## [Conclusion](https://machinelearning.apple.com/research/voice-trigger\#conclusion)

In this article, we presented the overall design of the voice trigger system enabling natural voice-driven interactions with Apple devices. The voice trigger system is designed to be power efficient and highly accurate, while preserving the user’s privacy. The voice trigger system is implemented entirely on-device for recent hardware-capable devices supporting on-device automatic speech recognition. With iOS 17, the voice trigger system will simultaneously support two trigger keywords, “Hey Siri” and “Siri” on most Apple device platforms. With this change, we have also improved the system’s ability to effectively mitigate any potential false triggers with a variety of state-of-the-art machine learning techniques, ensuring Apple’s commitment to user privacy while providing delightful experiences to our users.

## [Acknowledgments](https://machinelearning.apple.com/research/voice-trigger\#acknowledgments)

Many people contributed to this research including Saurabh Adya, Vineet Garg, Siddharth Sigtia, Pramod Simha, Arnav Kundu, Devang Naik, Oncel Tuzel, Wonil Chang, Pranay Dighe, Oggi Rudovic, Sachin Kajarekar, Ahmed Abdelaziz, Erik Marchi, John Bridle, Minsik Cho, Priyanka Padmanabhan, Chungkuk Yoo, Jack Berkowitz, Ahmed Tewfik, Hywel Richards, Pascal Clark, Panos Georgiou, Stephen Shum, David Snyder, Alan McCree, Aarshee Mishra, Alex Churchill, Anushree Prasanna Kumar, Xiaochuan Niu, Matt Mirsamadi, Sanatan Sharma, Rob Haynes, and Prateeth Nayak.

## [Apple Resources](https://machinelearning.apple.com/research/voice-trigger\#apple-resources)

Adya, Saurabh, Vineet Garg, Siddharth Sigtia, Pramod Simha, and Chandra Dhir. 2020. “Hybrid Transformer/CTC Networks for Hardware Efficient Voice Triggering.” August. [\[link.\]](https://arxiv.org/abs/2008.02323)

Cho, Minsik, Keivan A. Vahid, Saurabh Adya, and Mohammad Rastegari. 2022. “DKM: Differentiable K-Means Clustering Layer for Neural Network Compression.” February. [\[link.\]](https://machinelearning.apple.com/research/differentiable-k-means)

Dighe, Pranay, Saurabh Adya, Nuoyu Li, Srikanth Vishnubhotla, Devang Naik, Adithya Sagar, Ying Ma, Stephen Pulman, and Jason Williams. 2020. “Lattice-Based Improvements for Voice Triggering Using Graph Neural Networks.” January. [\[link.\]](https://arxiv.org/abs/2001.10822)

Garg, Vineet, Ognjen Rudovic, Pranay Dighe, Ahmed H. Abdelaziz, Erik Marchi, Saurabh Adya, Chandra Dhir, and Ahmed Tewfik. 2022. “Device-Directed Speech Detection: Regularization via Distillation for Weakly-Supervised Models.” March. [\[link.\]](https://arxiv.org/abs/2203.15975)

Garg, Vineet, Wonil Chang, Siddharth Sigtia, Saurabh Adya, Pramod Simha, Pranay Dighe, and Chandra Dhir. 2021. “Streaming Transformer for Hardware Efficient Voice Trigger Detection and False Trigger Mitigation.” May. [\[link.\]](https://arxiv.org/abs/2011.01151)

Jeon, Woojay, Leo Liu, and Henry Mason. 2019. “Voice Trigger Detection from LVCSR Hypothesis Lattices Using Bidirectional Lattice Recurrent Neural Networks.” _ICASSP 2019 - 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP),_ May, 6356–60. [\[link.\]](https://doi.org/10.1109/ICASSP.2019.8682617)

Kundu, Arnav, Chungkuk Yoo, Srijan Mishra, Minsik Cho, and Saurabh Adya. 2023. “R^2: Range Regularization for Model Compression and Quantization.” March. [\[link.\]](https://doi.org/10.48550/arXiv.2303.08253)

Erik Marchi, Stephen Shum, Kyuyeon Hwang, Sachin Kajarekar, Siddharth Sigtia, Hywel Richards, Rob Haynes, Yoon Kim, and John Bridle. 2018. “Generalised Discriminative Transform via Curriculum Learning for Speaker Recognition.” _Proceedings of the IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP)._ April. [\[link.\]](https://dl.acm.org/doi/10.1109/ICASSP.2018.8461296)

Rudovic, Ognjen, Akanksha Bindal, Vineet Garg, Pramod Simha, Pranay Dighe, and Sachin Kajarekar. 2023. “Less Is More: A Unified Architecture for Device-Directed Speech Detection with Multiple Invocation Types.” June. [\[link.\]](https://machinelearning.apple.com/research/unified-architecture)

Siri Team. 2018. “Personalized Hey Siri.” Apple Machine Learning Research. [\[link.\]](https://machinelearning.apple.com/research/personalized-hey-siri)

Shrivastava, Ashish, Arnav Kundu, Chandra Dhir, Devang Naik, and Oncel Tuzel. 2021. “Optimize What Matters: Training DNN-HMM Keyword Spotting Model Using End Metric.” February. [\[link.\]](https://arxiv.org/abs/2011.01151)

Sigtia, Siddharth, Erik Marchi, Sachin Kajarekar, Devang Naik, and John Bridle. 2020. “Multi-Task Learning for Speaker Verification and Voice Trigger Detection.” _ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP),_ May, 6844–48. [\[link.\]](https://doi.org/10.1109/ICASSP40776.2020.9054760)

Sigtia, Siddharth, Pascal Clark, Rob Haynes, Hywel Richards, and John Bridle. 2020. “Multi-Task Learning for Voice Trigger Detection.” May. [\[link.\]](https://doi.org/10.1109/ICASSP40776.2020.9053577)

## [External References](https://machinelearning.apple.com/research/voice-trigger\#external-references)

Mohri, Mehryar, Fernando Pereira, and Michael Riley. 2002. “Weighted Finite-State Transducers in Speech Recognition.” _Computer Speech & Language 16_ (1): 69–88. [\[link.\]](https://doi.org/10.1006/csla.2001.0184)

Wen, Yandong, Weiyang Liu, Adrian Weller, Bhiksha Raj, and Rita Singh. 2022. “SphereFace2: Binary Classification Is All You Need for Deep Face Recognition.” April. [\[link.\]](https://doi.org/10.48550/arXiv.2108.01513)

August 30, 2022 [research area Speech and Natural Language Processing](https://machinelearning.apple.com/research/?domain=Speech%20and%20Natural%20Language%20Processing) [conferenceInterspeech](https://machinelearning.apple.com/research/?event=Interspeech)

Voice trigger detection is an important task, which enables activating a voice assistant when a target user speaks a keyword phrase. A detector is typically trained on speech data independent of speaker information and used for the voice trigger detection task. However, such a speaker independent voice trigger detector typically suffers from performance degradation on speech from underrepresented groups, such as accented speakers. In this work,…

[Read more](https://machinelearning.apple.com/research/improving-voice-trigger)

May 4, 2020 [research area Speech and Natural Language Processing](https://machinelearning.apple.com/updates/?domain=Speech%20and%20Natural%20Language%20Processing) [conferenceICASSP](https://machinelearning.apple.com/updates/?event=ICASSP)

Apple sponsored the 45th International Conference on Acoustics, Speech, and Signal Processing (ICASSP) in May 2020. With a focus on signal processing and its applications, the conference took place virtually from May 4 - 8. Read Apple’s accepted papers below.

[Read more](https://machinelearning.apple.com/updates/apple-at-icassp-2020)

![Bottom banner](https://mlr.cdn-apple.com/media/Discover_1440x420_2x_9c465d585e.jpg)

## Discover opportunities in Machine Learning.

Our research in machine learning breaks new ground every day.

[Work with us](https://machinelearning.apple.com/work-with-us)