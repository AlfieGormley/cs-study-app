# Digital signal processing: beginner to intermediate

Add a standalone Digital Signal Processing subject (`content/dsp`, id `dsp`, title **Digital Signal
Processing**, order 15). The learner knows basic arithmetic/algebra and can read simple Python loops,
lists and functions. Explain unfamiliar notation and NumPy/SciPy operations before relying on them;
assume no calculus, complex-number, Fourier-analysis or electronics background.

Use three modules of nine short lessons. Teach concrete intuition, then mechanisms and small worked
examples, then applications and limitations. Each lesson normally takes 3–5 minutes and has three
focused worked questions, including applied multi-select questions where useful. Use basic and
intermediate difficulty, no advanced trivia. Aim for 27 lessons and 81 questions.

## Course structure and stable lesson ids

1. `01-signals`, id `dsp-signals`, title **Samples, Signals and Levels**, order 1:
   - `ds-samples-time`: sequences, indices, sample rate, sample period and record duration; a record of
     N samples has duration N/Fs, whereas the first-to-last timestamp span is (N-1)/Fs.
   - `ds-sines-phase`: amplitude, frequency, phase and sampled sinusoids; radians and normalised frequency.
   - `ds-sampling-aliasing`: spectral ambiguity, strict Nyquist condition for a baseband signal and why
     an analogue anti-alias filter must act before sampling; an explicit folding example.
   - `ds-quantisation-clipping`: discrete amplitude levels, quantisation error and clipping as different
     mechanisms; an explicitly stated toy quantiser, no unsupported universal noise claims.
   - `ds-mean-rms`: DC/mean, peak and RMS from short finite records; explain offset and units.
   - `ds-decibels`: amplitude versus power ratios, stated references and zero/silence handling;
     no universal dBFS sine-RMS convention asserted.
   - `ds-signal-operations`: gain, mixing and delay with explicit zero-extension/record boundaries.
   - `ds-complex-components`: real/imaginary components, magnitude and rotating phasors as a preparation
     for Fourier bins; introduce j and complex conjugation gently where required.
   - `ds-correlation`: recognise a template/time shift; define the lag convention and distinguish
     correlation from convolution; identify amplitude/DC bias and finite-overlap limitations.
2. `02-filters`, id `dsp-filters`, title **Systems, Convolution and Filters**, order 2:
   - `df-lti-systems`: linearity and time invariance through input/output counterexamples, zero-state assumptions.
   - `df-impulse-response`: unit impulse, impulse response, causality and the limits of impulse testing.
   - `df-convolution`: finite linear convolution, sliding weighted sums and output length/boundaries.
   - `df-moving-average`: a causal moving average, smoothing versus delay and zero-state startup.
   - `df-frequency-response`: sinusoidal steady-state gain/phase, passband/stopband/transition band and
     why a smoothing filter is not a universal solution.
   - `df-fir-design`: finite coefficients and a modest verified FIR low-pass example; normalisation,
     transition/ripple trade-offs and the delay condition for symmetric coefficients.
   - `df-iir-feedback`: feedforward versus feedback, a one-pole smoother and remembered state.
   - `df-stability-precision`: separate mathematical stability from finite-precision overflow/rounding;
     a precisely scoped stable-pole example and bounded-input/bounded-output reasoning.
   - `df-block-processing`: state continuity and equivalent sample/block outputs, startup/tail policy,
     processing budget versus end-to-end latency; no device benchmark claims.
3. `03-spectra`, id `dsp-spectra`, title **Fourier Analysis and Practical DSP**, order 3:
   - `dp-dft-bins`: DFT, FFT as an algorithm, signed/real-spectrum bins and sample-rate mapping.
   - `dp-spectrum-scaling`: amplitude calibration for a real bin-centred tone; DC/Nyquist doubling
     exceptions and a clear distinction between amplitude spectrum, power and PSD.
   - `dp-window-leakage`: finite records and leakage; rectangular versus an explicitly named Hann
     convention, coherent-gain correction and main-lobe/sidelobe trade-offs.
   - `dp-zero-padding`: interpolated frequency-grid samples versus genuine resolving ability/record duration.
   - `dp-time-frequency`: a short-time spectrum/spectrogram, frame length versus hop and time/frequency trade-offs.
   - `dp-downsampling`: low-pass before decimation, new Nyquist limit and a controlled aliased counterexample.
   - `dp-interpolation`: zero insertion, spectral images and low-pass/gain requirements; optionally demonstrate
     a documented rational-resampling API without hiding what it does.
   - `dp-fast-convolution`: circular versus linear FFT convolution, sufficient padding and overlap-add tail handling.
   - `dp-measurement-project`: a reproducible synthetic sensor/tone measurement combining sample timing,
     levels, filtering and a correctly calibrated spectrum, with explicit checks and uncertainty boundaries.

## Relationship to existing content

The Synth Building subject already includes sound/sampling and synthesis-specific DSP. Keep that
content untouched. This subject is a general route through DSP reasoning and implementation, including
time-series/sensor applications, LTI/convolution, correlation, FIR/IIR, spectrum calibration and rate
conversion. Introduce necessary sampling/level prerequisites concisely; do not copy synth lessons,
MIDI/pitch tables, oscillators, envelopes, modulation designs or hardware wiring.

## Mandatory format and independent process

Follow this worktree's `CLAUDE.md`, `CONTENT_SPEC.md`, `docs/CONTENT_PROCESS.md`, `docs/new-module.md`,
`docs/verify-brief.md`, `.claude/skills/writing-formulas/SKILL.md` and
`.claude/skills/glossary-terms/SKILL.md`. Existing briefs that name the primary checkout apply to this
isolated worktree's corresponding files. Each module has its own author and a different independent
verifier; the orchestrator must never self-stamp. No legacy-list changes or other-subject edits.

Every equation/relation/calculation with symbols belongs in a formula block, including question feedback.
Define EVERY symbol, index, unit, constant and function separately in each card, plus an **In words:**
line. Explain finite summation notation and limits in ordinary language. Do not introduce undefined
transform notation or a formula just because a library can evaluate it. Every card must be usable alone.
Use conventional algebra and explicit brackets; code syntax belongs in Python fences. Keep equation/code
lines within 44 characters in lessons and 40 in questions. Formula definitions may wrap freely.

Provide useful concise optional `[!analogy]` disclosures with **How it maps:** and **Where it stops:**;
never put required maths, definitions or quiz facts inside them. Do not force repetitive comparisons
onto calculations. Independent `analogyReview` entries must cover all active lessons, using specific
added/not-needed decisions/rationales, distinct author/verifier identities, actual sources and current hashes.

Give every unfamiliar term and acronym a precise sourced glossary entry, unique `dsp-` ids, and aliases
that do not capture ordinary words or conflicting meanings. Module1 owns general signals/sampling/
level/complex/correlation vocabulary; module2 owns new systems/filter/convolution/state vocabulary;
module3 owns Fourier/window/spectrogram/resampling vocabulary. Reuse earlier entries and inspect actual
glossary targets with all modules present. Avoid importing wrong synthesiser/electronics definitions.

## Executable verification and mathematical care

Use Python, with standard-library calculations for elementary examples and NumPy/SciPy where helpful.
Dependencies belong only in `/tmp/dsp-course-venv`, not the study app. Root installs the environment and
reports exact versions. Label complete examples and excerpts; make imports, initial states, array shapes,
boundary modes, normalisation and units explicit. Do not play sound or depend on external files/devices.

Authors execute every lesson/question code fence and record expected outputs/tolerances. Independent
verifiers extract and rerun the exact snippets, recompute ALL formula cards/numeric questions with their
own calculations, and test edge cases. Use direct finite sums or a second implementation as an oracle
when comparing FFT/filter library output; reproducing the same formula once is not independent validation.

Check especially: Nyquist endpoint/phase ambiguity; quantiser endpoint/rounding assumptions; RMS versus
mean and reference levels; correlation lag sign; linear versus circular convolution; zero initial state;
FIR delay assumptions; one-pole recursion coefficient convention/stability and finite precision; block
state retention; DFT normalisation; real-spectrum DC/Nyquist exceptions; periodic versus symmetric Hann;
coherent gain versus noise scaling; zero-padding versus resolving close tones; STFT frame/hop distinction;
aliasing versus interpolation images; filter transients and delay; resampling output length/gain; FFT tail
handling. Do not silently compare causal and zero-phase filtering as if timing were identical.

## Primary sources and scope limits

Fetch actual relevant passages from MIT OpenCourseWare Signals and Systems / DSP lecture material,
original author DSP textbooks (such as dspguide.com or Julius O. Smith's online books), official
NumPy/SciPy documentation and manufacturer application notes when genuinely needed. Prefer direct
topic pages over homepages; verify that every URL loads and supports the attached claim. Context7 is
unavailable, so use official documentation directly for numerical-library APIs and record versions.

The course does not cover full calculus/proofs, z-transform/pole-zero design in depth, adaptive filters,
communications modems, multichannel beamforming, production hard-real-time guarantees, hardware
converter design or fixed-point implementation. Introduce boundaries where relevant without turning
beginner lessons into caveat lists. State where synthetic/host tests stop; no real-device performance claims.

Authors save `/tmp/dsp-course-<signals|filters|spectra>-author.json` with ids/counts, formula/glossary counts,
analogy decisions, fetched sources, every code check, lint exceptions, gaps and uncertain claims. Do not
write verification records as author. Verifiers fix assigned modules, write full `verification.json`,
independently stamp, and save `/tmp/dsp-course-<signals|filters|spectra>-verified.json` with honest grouped
counts, significant corrections, assumptions, sources, confidence and gaps. Run scoped build, formula/
glossary checks and links until valid. Root runs a whole build, all app tests and mobile/desktop browser
checks of lessons/questions/formulas/dictionary/practice/search/offline/progress, then publishes through
the same established commit-and-Pages release workflow while preserving all existing courses.
