---
id: dp-interpolation
title: Increase sample rate with interpolation
level: intermediate
minutes: 4
summary: Follow zero insertion, spectral images and the low-pass gain needed to reconstruct between samples.
---

**Interpolation** estimates samples at new time positions from an existing record. Increasing the output sample rate gives more values to pass to another system, but they are computed estimates, not extra physical measurements. It cannot recover frequency distinctions already lost to aliasing.

Integer-rate interpolation has two conceptual steps: insert zero placeholders between the original samples, then apply a reconstruction low-pass filter. Efficient implementations can combine these steps without explicitly calculating every zero.

## New positions preserve the original times

To double the rate, put each original sample in every other output position. Interpret the result at twice the original sample rate. Original values then retain their original time positions; the extra positions fall between them.

For a constant sequence of ones, the intermediate sequence alternates ones and zeros. Those zeros do not claim the physical signal stopped between observations. They reserve positions for the filtering step.

> [!analogy] Real-world analogy: filling a timetable
> Put the known appointments into a timetable with twice as many time slots. Empty slots reserve positions; they do not mean the activity stopped.
>
> **How it maps:** Original samples retain their timing while zero placeholders create new positions. The filter estimates values at and around those positions.
>
> **Where it stops:** Signal interpolation depends on a bandwidth assumption and a numerical filter, not judgement about appointments. It cannot invent unknown high-frequency information.

## Filter images and restore the scale

Zero insertion produces **spectral images**: copies of the original baseband spectrum within the enlarged frequency range. A reconstruction low-pass retains the wanted band and suppresses those images. They are still separated from the wanted baseband, so filtering can remove them before any later reduction folds them together.

The filter must also have appropriate gain. With one zero after every original sample, the constant sequence's average is halved. A unity-DC-gain low-pass would keep that reduced average. If no other scale correction is present, a factor-two interpolator needs a filter with DC gain two. More generally, the required DC gain equals the zero-insertion factor, with corresponding passband gain where faithful reconstruction is wanted.

A three-coefficient filter with weights `[0.5, 1.0, 0.5]` illustrates this for doubling. Their sum is two. It fills the interior constant sequence back to one and provides linear interpolation between successive original values after accounting for delay. Its image suppression is too gradual for demanding applications; it is a useful model rather than a production specification.

## Compare implementations fairly

That toy filter used causally has one high-rate-sample delay and edge transients. An offline centred API can produce different timing and edge values while still performing its documented operation. Match the filter, scaling, output-length and boundary conventions before comparing arrays.

**Resampling** can increase by one integer factor and decrease by another. SciPy's `resample_poly` combines zero insertion, FIR filtering and reduction using **polyphase** computation. It supplies the required internal amplitude scaling, so do not multiply its default output by the insertion factor again.

Its default boundary model assumes zeros beyond the finite input. A filter for the intermediate increased rate must both suppress interpolation images and protect the final reduced rate from aliasing. Inspect timing and boundary behaviour as well as the interior frequency response.

## Key takeaways

- Zero placeholders reserve time positions; low-pass filtering forms the interpolated signal.
- Reconstruction needs the right gain as well as image suppression.
- More output values cannot undo original aliasing or replace new measurements.

## Further reading

- [SciPy: upsample, FIR filter and downsample](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.upfirdn.html)
- [SciPy: polyphase resampling](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html)
