---
id: df-fir-design
title: Design and inspect a small FIR filter
level: intermediate
minutes: 4
summary: Design a low-pass FIR, check its actual response, and account for symmetric-filter delay.
---

A **finite impulse response**, or **FIR**, filter has an impulse response that becomes exactly zero after a finite number of samples. A direct FIR implementation multiplies present and past inputs by fixed **filter coefficients** and adds them. Each coefficient is often called an **FIR tap**. A moving average is an FIR with equal taps; useful FIR filters need not use equal or positive coefficients.

## Ask a design tool a precise question

Begin with requirements: which frequencies matter, how much their gain may vary, how strongly unwanted frequencies must be reduced, and how much delay is acceptable. A filter that makes a graph look smooth may still erase useful changes or delay an alarm too much.

SciPy's `signal.firwin` designs FIR coefficients using the **window method**: it limits and shapes an ideal response's coefficient sequence. For example, you can request 31 taps, a Hamming window, a low-pass response and an explicit sample rate of 100 samples per second. The sample rate tells the tool how to interpret frequencies; this filter does not change how many samples arrive each second.

The `cutoff` of 10 Hz is this API's half-amplitude point, approximately minus 6 dB, rather than a promise that every frequency below 10 Hz has gain 1. `scale=True` normalises this low-pass design to unity gain at DC. Always check an API's convention before treating a parameter as a passband edge.

## Inspect what was actually designed

Use a tool such as `freqz` to evaluate the returned coefficients, then compare the measured gains with the requirements. Check the passband, transition and stopband rather than inspecting only the named cutoff. Four chosen frequencies establish the response at those points; they do not prove that the whole band meets a tolerance. Peaks between checked points can matter.

**Filter ripple** is the unwanted variation of gain within a band. Increasing tap count with a comparable window usually narrows the transition; window choice trades transition width against ripple and stopband attenuation. More taps also require more work in a direct implementation and, for this symmetric design, introduce more delay. If a design fails, change the design choices and recheck; a reassuring parameter name is not evidence of success.

## Symmetry gives a specific delay

Real, symmetric FIR coefficients give linear phase. Their **group delay** is constant wherever the response is nonzero and the phase can be followed continuously. This describes the slope of phase with frequency: frequency components locally share the same delay. It does not say their amplitudes are unchanged. Phase can jump when the corresponding zero-phase response changes sign, and phase is undefined at exact response zeros.

The symmetry centre sets the delay. A causal symmetric 31-tap filter has a delay of 15 sample intervals, or 0.15 seconds at 100 samples per second. Adding more symmetric taps moves that centre farther into the past. The optional reference gives the general relationship.

```formula reference
D = (M − 1) / 2
τ = D / F_s
where
D: the group delay in sample intervals for a causal real symmetric FIR with nonzero response at the frequency considered
M: the number of coefficients, here 31
τ: the corresponding delay in seconds (s)
F_s: the sample rate in sample intervals per second, here 100
s: second, the unit of time; s to the power minus one means per second
In words: a causal symmetric FIR's delay is set by the centre of its coefficient sequence; more taps increase that delay, while a higher sample rate makes each sample interval shorter.
```

An even number of symmetric taps gives a half-integer delay in sample intervals, which is valid. Arbitrary FIR coefficients need not have constant group delay. Nor does “FIR” mean “zero delay”. Shifting a saved output backwards can align a recording, but cannot make future samples available to a live system or undo changed amplitudes. Startup and the finite tail still need a policy.

## Key takeaways
- FIR taps describe finite memory; a design parameter needs an API convention.
- Inspect response, including transition and ripple, against actual requirements.
- Real symmetric FIRs have a known group delay where their response is nonzero.

## Further reading
- [SciPy: firwin design and cutoff convention](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html)
- [SciPy: freqz response evaluation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.freqz.html)
- [Julius O. Smith: symmetric linear-phase filters](https://www.dsprelated.com/freebooks/filters/Symmetric_Linear_Phase_Filters.html)
