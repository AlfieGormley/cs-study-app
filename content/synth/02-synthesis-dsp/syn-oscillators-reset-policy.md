---
id: syn-oscillators-reset-policy
title: Choosing an oscillator reset policy
level: basic
minutes: 2
summary: Choosing an oscillator reset policy.
sourceLesson: syn-oscillators
---

## From oscillator to instrument

A practical oscillator also needs:

- **Band-limiting** for saw, square and pulse, or high notes alias badly (covered in the neighbouring synthesis units).
- **Smoothed or per-sample frequency** so pitch changes don't step audibly (covered in the neighbouring synthesis units).
- A **reset policy**: resetting phase on each note-on gives a consistent attack; free-running sounds more like analogue oscillators. Both are valid choices.

Libraries such as DaisySP (`Oscillator`) and the Teensy Audio Library (`AudioSynthWaveform`) provide alias-reducing waveform options and a way to set or reset phase. In the source revisions checked on 2026-10-16 (DaisySP 2c72eaf9eac5, PJRC Audio 3039be2773e8), the basic frequency setters recompute an increment without a pitch smoother, so smoothing remains your job. The roadmap suggests writing your own sine oscillator first, then comparing with a library's.

## Key takeaways

- Resetting at silent note starts makes attacks repeatable; free-running phase varies starts.
- Resetting an audible oscillator can click; band-limiting and smoothing remain separate requirements.

## Further reading

- [Oscillator interface — DaisySP](https://raw.githubusercontent.com/electro-smith/DaisySP/2c72eaf9eac5fc0dca1919d65d606da907832618/Source/Synthesis/oscillator.h)
- [Waveform interface — PJRC](https://raw.githubusercontent.com/PaulStoffregen/Audio/3039be2773e86daf1f381a1e8bdc1e6a55ed11f1/synth_waveform.h)
