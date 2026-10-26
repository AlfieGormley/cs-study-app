---
id: dp-measurement-project
title: A reproducible vibration measurement
level: intermediate
minutes: 4
summary: Combine known timing, RMS, causal filtering and a calibrated spectrum with explicit synthetic checks.
---

Before trusting a measurement chain, test it on a synthetic signal with known truth. A real vibration sensor adds calibration uncertainty, noise, drift and timing error. A generated record lets you first ask whether the processing behaves as intended.

This experiment uses an acceleration offset, a wanted 64 Hz tone and a 192 Hz interferer. The task is to preserve the wanted tone, reduce the interferer and explain the measured output. It tests numerical processing on a host computer; it does not establish physical sensor accuracy or device timing performance.

## State a reproducible contract

Use the following fixed setup, with no random noise or external files. Acceleration values are in metres per second squared.

| Setting | Choice |
|---|---|
| Sample rate | 1024 samples per second |
| Acquired length | 1280 samples |
| Constant offset | 0.4 |
| Wanted cosine peak | 2 at 64 Hz |
| Interfering cosine peak | 0.6 at 192 Hz |

Start both cosines at their positive peak at sample zero. They complete whole cycles over this acquired record, so their mean is zero and the measured mean should be the stated offset, allowing numerical rounding.

Remove that measured mean before analysing AC RMS, so the constant offset does not count as vibration around the mean. Both oscillating tones remain. RMS describes average squared size followed by a square root; it is not the sum or average of the tone peaks. For these whole-cycle, orthogonal cosines, mean-square contributions add because their cross-products average to zero.

## Separate filter behaviour from measurement behaviour

Apply a causal three-tap moving average with equal weights and zero initial state. Each output averages the current input and two preceding inputs. SciPy's `lfilter` can implement this causal operation; an offline zero-phase filter would be a different contract.

Discard the first 256 outputs, then analyse the remaining 1024. This keeps filter startup outside the analysed segment. Both tones complete whole cycles there too. The symmetric three-tap filter has one input-sample delay: discarding startup does not remove that delay when interpreting time events.

Apply a periodic Hann to the analysed segment. Use its actual weight sum for coherent-tone amplitude calibration, doubling only paired interior bins. Both test tones are interior bins, well away from DC and Nyquist. Use a separate frequency-response calculation to predict each output tone before comparing with the measured spectrum.

## Interpret the checks

The wanted output peak is approximately 1.899 and the interferer's approximately 0.353, in the same acceleration units as the input. The interferer is reduced, not eliminated. The wanted tone is also attenuated, so its output peak must not be reported as the original input peak.

Make separate checks for mean removal, RMS, filter response and spectrum scaling. A coherent-amplitude assertion can reveal a scaling or filtering error, but it cannot by itself prove time alignment, physical calibration or real-time performance. Inspect time events as well if timing matters.

A longer, suitably designed filter may reject the interferer better, with different delay and transition behaviour. On a real record, document sample-clock accuracy, calibration, detrending, window, bandwidth and transient handling. A peak's bin label alone does not supply an uncertainty interval.

## Key takeaways

- Known synthetic input lets you check each processing stage against a stated contract.
- Predict the filter's effect before interpreting an output peak as an input measurement.
- Numerical agreement establishes the tested behaviour; physical calibration and timing need their own evidence.

## Further reading

- [SciPy: causal filtering and initial conditions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
- [SciPy: frequency response of a digital filter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html)
- [SciPy: periodic and symmetric Hann windows](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.hann.html)
- [NumPy: FFT conventions](https://numpy.org/doc/stable/reference/routines.fft.html)
