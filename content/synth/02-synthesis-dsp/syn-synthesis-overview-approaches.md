---
id: syn-synthesis-overview-approaches
title: Choosing a synthesis approach
level: basic
minutes: 3
summary: Choosing a synthesis approach.
sourceLesson: syn-synthesis-overview
---

A synthesiser is a program (or circuit) that turns *control* information, such as "play note 60, fairly hard", into an audio signal. In a digital synth that signal is a stream of samples; an analogue circuit produces a continuous signal. Every design answers the same two questions:

- **Where does the raw sound come from?** A waveform, a recording, a mathematical model.
- **How is it shaped over time?** Filters, envelopes and modulation.

The different "kinds" of synthesis are mostly different answers to the first question. Before choosing one for your instrument, it helps to know what each costs and what it is good at.

## The main approaches

| Approach | Raw material | Shaped by |
|---|---|---|
| Subtractive | Bright waves (saw, square) | Filters remove harmonics |
| Additive | Many sine waves | Per-partial levels |
| FM / PM | Sines modulating sines | Modulation index |
| Wavetable | Stored single cycles | Scanning through tables |
| Sample-based | Recordings | Pitch shift, envelopes |
| Physical modelling | Model of a vibrating object | Model parameters |

### Subtractive

Start with a waveform rich in harmonics and **remove** what you don't want with a filter. A sawtooth through a low-pass filter whose cutoff falls over time gives the classic "pluck" or brass sound. The Minimoog Model D is a concrete example of this architecture. We use subtractive synthesis for the learning experiments because its blocks can be tested separately; the project has not selected the finished instrument’s architecture.

### Additive

Under the usual Fourier-series conditions, a periodic sound can be described by a mean plus sine components; at an ideal jump, the series converges to the midpoint of the two limits. Additive synthesis builds the sound directly from those sines, each with its own frequency and level, often with its own envelope. It gives total control, but a low note can need hundreds of sines per voice, and controlling that many parameters musically is hard.

For this first instrument, a few oscillator and filter states need little working memory. Recorded sample libraries can consume much more storage, while a large additive bank can cost many oscillator evaluations. These are design trade-offs rather than universal rankings: measure the concrete implementation and target sound.

These are offline learning experiments. Later hardware exercises must use documented low-voltage development hardware, with the exact board and audio-interface manuals checked before making connections. Mains construction is outside this course’s project scope.

## Key takeaways

- Subtractive synthesis removes harmonics; additive synthesis builds them.
- Use the target sound, memory and processing cost to choose an approach.

## Further reading

- [Minimoog Model D user guide — Moog](https://cdn.inmusicbrands.com/Moog/Model%20D/Minimoog_Model_D_Manual.pdf)
- [Additive synthesis — Julius O. Smith](https://ccrma.stanford.edu/~jos/pasp/Additive_Synthesis.html)
