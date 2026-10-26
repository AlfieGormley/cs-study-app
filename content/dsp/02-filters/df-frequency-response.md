---
id: df-frequency-response
title: What happens to each frequency?
level: intermediate
minutes: 4
summary: Interpret steady-state gain and phase, and turn a vague smoothing goal into frequency requirements.
---

A filter can preserve a slowly varying trend while reducing faster oscillations. Its **frequency response** describes how a stable LTI system scales and shifts sinusoids at each frequency after startup effects have passed. **Amplitude response** gives the amplitude ratio; **phase response** gives the phase shift. A negative output value at one instant is not a negative amplitude ratio: amplitude ratios are nonnegative.

A steady 7 Hz sinusoid remains a 7 Hz sinusoid after filtering, unless the response removes it completely. Half amplitude means a smaller oscillation, not a slower one. A phase shift moves the peaks within each cycle. Different input frequencies can receive different gains and shifts, so a mixture can change shape even though none of its steady sinusoidal components changes frequency.

At a **response zero**, that frequency is cancelled completely and the output's phase is undefined. During startup, the stored history can add a transient, so measuring the first few output samples may give a misleading picture of steady-state response.

## Measure a simple response

A two-sample equal-weight average passes a constant input unchanged once its history is filled. Slow changes make neighbouring readings similar, so averaging changes them relatively little. At half the sample rate, the readings alternate positive and negative with equal magnitude; each neighbouring pair cancels exactly. Between these cases, gain and phase vary with frequency. These different outcomes are the same fixed filter acting on different inputs.

To investigate a filter, compare sustained test tones at several frequencies after startup, or evaluate its coefficients with a response tool. Record both amplitude and timing behaviour. A few measurements can illustrate the trend but do not prove that every frequency in a band meets a requirement.

## Specify useful and unwanted bands

The **passband** is the frequency region intended to pass within a specified gain tolerance. The **stopband** is intended to be sufficiently reduced. The **transition band** lies between them. A **low-pass filter** passes low frequencies and reduces higher ones, but no finite filter here makes an instantaneous jump between perfect passage and perfect rejection.

For a 100-sample-per-second sensor, an illustrative requirement might preserve 0–2 Hz within a chosen tolerance and strongly reduce frequencies above 15 Hz. The tolerated gain error and required reduction must also be stated before deciding whether a design succeeds.

A moving average has cancellation frequencies but also unwanted lobes between them. Increasing its length does not turn it into a universal frequency separator. It also cannot recover information already lost to aliasing, and it reduces useful signal components occupying the same frequencies as unwanted noise. Define the task before choosing the filter.

## Key takeaways
- Stable LTI filtering changes steady-state sinusoidal amplitude and phase, not frequency.
- Startup behaviour must be excluded or modelled when measuring response.
- Passband, stopband, tolerances and timing requirements guide filter choice.

## Further reading
- [Julius O. Smith: frequency response](https://www.dsprelated.com/freebooks/filters/Frequency_Response.html)
- [Julius O. Smith: steady sinusoidal response](https://www.dsprelated.com/freebooks/filters/Finding_Frequency_Response.html)
- [Smith: moving average frequency behaviour, Chapter 15](https://www.dspguide.com/CH15.PDF)
