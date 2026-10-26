---
id: dp-downsampling
title: Reduce sample rate without folding signals
level: intermediate
minutes: 4
summary: Set a new Nyquist limit, low-pass first and understand why keeping every second sample is insufficient.
---

Keeping every second or third sample lowers the sample rate. It also lowers the range of frequencies that can be represented without ambiguity. A tone that was safe at the original rate can exceed the new Nyquist limit and appear as a different, lower-frequency tone.

**Decimation** combines low-pass filtering with retaining samples at a lower rate. The order matters: suppress the unwanted high frequencies before discarding samples.

## Design for the output rate

Reducing a 1200-sample-per-second signal by a factor of three gives 400 samples per second. Its new Nyquist boundary is 200 Hz, even though the original boundary was 600 Hz. Design the prefilter for the reduced rate.

```formula reference
F_o = F_i / D
f_N = F_o / 2
where
F_o: output sample rate, in samples per second, expressed in hertz
F_i: input sample rate, in samples per second, expressed in hertz
D: positive integer reduction factor
f_N: output Nyquist boundary, in hertz
In words: divide the input sample rate by the reduction factor, then halve the output rate to find its Nyquist boundary.
```

Wanted baseband content must lie strictly below that boundary. A practical low-pass also needs a transition band in which its response falls from passing wanted content to rejecting unwanted content. Do not put the wanted passband edge exactly at Nyquist and expect an instantaneous cut-off. Choose enough stopband attenuation for the alias level the application can tolerate.

## Why filtering afterwards is too late

A 350 Hz cosine is below the original Nyquist boundary in this example. Keep every third sample without filtering, and it appears as a 50 Hz cosine at the output. Discarding samples has folded the unwanted tone into the useful band; it has not erased it.

Now an actual 50 Hz input and the aliased 350 Hz input can be indistinguishable from the output samples alone. A later low-pass cannot selectively remove the alias while preserving every genuine 50 Hz component. Filter before the ambiguity occurs.

> [!analogy] Real-world analogy: checking before a narrow doorway
> Remove oversized items before sending a mixed delivery through a narrow doorway. Sorting afterwards cannot recover information lost when items were forced together.
>
> **How it maps:** The new rate has a smaller unambiguous frequency range. The prefilter suppresses components outside it before samples are discarded.
>
> **Where it stops:** Aliasing is an exact ambiguity between sampled oscillations, not physical damage or a queue. A real filter only attenuates unwanted components by a finite amount.

## Specify the whole rate-change operation

SciPy's `decimate` filters before reducing. `resample_poly` also combines FIR filtering and rate conversion efficiently. An API is useful, but its default filter is not evidence that your required passband and stopband specification has been met. Test across the unwanted band and inspect finite-record edges.

Record the timing convention too. A causal streaming filter has delay and startup behaviour; an offline centred or zero-phase operation has different alignment and boundary assumptions. Neither should silently substitute for the other when event times matter.

This digital prefilter protects a later digital rate reduction. It cannot repair aliasing that already happened at the original analogue-to-digital conversion, which needs its own anti-alias protection.

## Key takeaways

- The output rate sets the relevant Nyquist boundary.
- Filter before reducing, leaving a transition band and enough unwanted-band rejection.
- Record timing and edge assumptions, and keep original ADC aliasing separate from later decimation.

## Further reading

- [SciPy: decimation includes an anti-alias filter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.decimate.html)
- [SciPy: polyphase resampling and boundary assumptions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample_poly.html)
