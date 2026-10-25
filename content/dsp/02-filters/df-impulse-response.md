---
id: df-impulse-response
title: Learn a system from one impulse
level: basic
minutes: 4
summary: Use an isolated unit impulse to reveal an LTI system's weights, memory and causality.
---

A **unit impulse** is a discrete sequence containing 1 at sample zero and 0 everywhere else, including negative sample indices. It is a single nonzero sample, rather than a narrow continuous-time spike of unspecified height.

The **impulse response** is the output produced by this input when a system starts at rest. For an LTI system, it tells us how every input sample contributes to future output. Each sample can be viewed as its own scaled, shifted impulse. Linearity lets us add their responses; time invariance lets us shift the same response to each arrival time.

## Reveal the weights

Consider a system that combines the present sample and the previous one. All input values before sample zero are zero.

```formula
y[n] = 0.75x[n] + 0.25x[n − 1]
where
y: the output sequence, with dimensionless sample values
x: the input sequence, with dimensionless sample values
n: the integer sample index; n starts at zero for this record
0.75: the dimensionless weight on the present input
0.25: the dimensionless weight on the previous input
In words: each output is three quarters of the current reading plus one quarter of the previous reading.
```

The impulse produces 0.75 at sample zero, 0.25 at sample one, then zeros. That two-sample response exposes the two weights directly. A pulse with amplitude 4 produces 3, then 1. A pulse arriving five samples later produces that same pair five samples later. The output depends on both the pulse and what the system remembers, so the system must start in zero state for this interpretation.

This complete Python example uses a list for the input and one variable for its remembered previous sample. It prints the first four response values.

```python
x = [1.0, 0.0, 0.0, 0.0]
previous = 0.0
y = []
for sample in x:
    y.append(0.75*sample + 0.25*previous)
    previous = sample
print(y)
# [0.75, 0.25, 0.0, 0.0]
```

## Causality is about available information

A **causal system** uses only present and past inputs. For a zero-state LTI system this means its impulse response is zero at every negative sample index. It cannot produce a response before the impulse arrives. A filter that needs tomorrow's sensor reading is noncausal in a live stream, although a saved recording may make that future sample available for offline processing.

> [!analogy] Real-world analogy: a single clap
> A clap in a room is followed by reflections that become quieter over time.
>
> **How it maps:** The isolated event is the test input; the sequence of reflections suggests how a system can spread one event through time.
>
> **Where it stops:** A clap is not an exact discrete unit impulse, and a real room measurement includes the microphone, source and background noise. It does not prove the room is LTI.

## What one experiment cannot establish

An impulse response fully characterises an already established LTI system under its initial-state assumptions. It does not prove an unknown system is linear or time invariant. A clipper may look like an unchanged connection for a small impulse yet distort larger signals. A changing system may respond differently tomorrow. A short measurement can also miss a long, quiet tail.

## Key takeaways
- A discrete unit impulse has one sample of amplitude 1 and zeros elsewhere.
- Its zero-state response characterises an LTI system.
- Causality excludes response before the input; one test cannot prove LTI behaviour.

## Further reading
- [Julius O. Smith: impulse-response representation](https://www.dsprelated.com/freebooks/filters/Impulse_Response_Representation.html)
- [Smith: convolution and impulse responses, Chapter 6](https://www.dspguide.com/CH6.PDF)
