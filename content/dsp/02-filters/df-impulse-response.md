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

Consider a system that takes three quarters of the present reading and one quarter of the previous reading, then adds them. All input values before sample zero are zero.

The impulse produces 0.75 at sample zero, 0.25 at sample one, then zeros. That two-sample response exposes the two weights directly. A pulse with amplitude 4 produces 3, then 1. A pulse arriving five samples later produces that same pair five samples later. The output depends on both the pulse and what the system remembers, so the system must start in zero state for this interpretation.

This reveals **filter memory** without a long test signal. The first response value tells you how much acts immediately; later values show how an input continues to matter. Here the influence ends after two outputs. Other systems have longer responses, including tails that decay without reaching exact zero in the mathematical model.

For an established LTI system, doubling a pulse doubles its whole response, and delaying the pulse delays the whole response. If either prediction fails, the measured response cannot serve as one fixed description of all its behaviour.

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
