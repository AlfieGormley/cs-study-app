---
id: df-block-processing
title: Process blocks without losing history
level: intermediate
minutes: 5
summary: Preserve filter state between blocks and separate computation deadlines from total latency.
---

Devices and files often deliver samples in **processing blocks** rather than one at a time. A block boundary is a software boundary, not a break in the underlying signal. If coefficients, sample order and arithmetic stay the same, a sample-by-sample recurrence gives the same outputs regardless of how its input is divided into blocks, provided its **filter state** survives between them.

## Pass the state forward

This complete Python example processes the one-pole smoother with a previous-output weight of 0.5. The function accepts its initial state and returns its final state alongside the output list. It does not reset itself secretly.

```python
def smooth(block, state):
    output = []
    for sample in block:
        state = 0.5*sample + 0.5*state
        output.append(state)
    return output, state

x = [1.0, 1.0, 0.0, 0.0]
whole, _ = smooth(x, 0.0)
first, state = smooth(x[:2], 0.0)
second, state = smooth(x[2:], state)
assert whole == first + second
print(whole)
# [0.5, 0.75, 0.375, 0.1875]
```

Resetting the second block to zero produces two zeros there, losing the previous block's tail. This error often looks like a jump at every boundary. A direct FIR instead retains the required previous inputs; a library may store an equivalent transformed state. SciPy's `lfilter` exposes initial and final delay states as `zi` and `zf`. Retain its returned state in that API's representation; it is not generally just the last output sample.

> [!analogy] Real-world analogy: reading across pages
> Turning a page does not restart a story. You carry the relevant context into the next page.
>
> **How it maps:** Pages correspond to blocks; retained context corresponds to filter state. The amount printed on a page changes how the material is delivered, not its order or meaning.
>
> **Where it stops:** A digital filter needs a precisely defined finite state for these implementations, rather than a reader's flexible recollection.

## Decide what the end means

Zero state is one explicit startup policy. Another initial state may be justified by known earlier history. At the end of a finite recording, full convolution of an FIR can be obtained by appending enough zeros to flush the tail: one fewer zero than its number of taps. Keep only as many outputs as the chosen policy requires.

An IIR generally has no exact finite tail length. A finite application chooses a justified stopping tolerance or records a fixed additional duration. Do not flush with zeros between ordinary live blocks: the next block supplies the actual continuation. Startup, normal continuation and end-of-record handling are different decisions.

## A deadline is not total latency

For a regular incoming stream, one block's sample duration gives a recurring processing interval. At 48000 samples per second, each 64-sample block represents about 1.33 milliseconds of stream time. Larger blocks arrive less often but contain more work; raising the sample rate while keeping the block size fixed makes the interval shorter.

In a simple single-worker pipeline, sustained processing must keep up with this arrival interval, with margin for other work and scheduling variation. A worker that regularly takes longer accumulates a backlog even if each individual result is numerically correct. A host timing test cannot guarantee a real device will meet every deadline.

End-to-end **latency** also includes collecting samples into buffers, queues, computation, filter delay and output hardware. Smaller blocks reduce some buffering delay but increase call overhead. State continuity establishes numerical correctness; timing measurements and a complete pipeline model address separate requirements.

The Python example allocates lists and prints results to make state passing visible. It is a teaching example, not an audio callback to copy into a live device. Real-time callbacks need bounded work and must avoid operations such as allocation or console output that can take unpredictable time on their platform.

## Key takeaways
- Retain state across normal blocks and use explicit startup and tail policies.
- Processing block size should not alter the recurrence's numerical result.
- Processing budget, filter delay and end-to-end latency measure different things.

## Further reading
- [SciPy: lfilter initial and final states](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html)
- [Smith: convolution and output length, Chapter 6](https://www.dspguide.com/CH6.PDF)
- [PortAudio: processing callbacks and bounded work](https://portaudio.com/docs/v19-doxydocs/writing_a_callback.html)
- [PortAudio: streams, buffers and buffering latency](https://portaudio.com/docs/v19-doxydocs/api_overview.html)
- [PortAudio: buffering, scheduling and timing model](https://github.com/PortAudio/portaudio/wiki/BufferingLatencyAndTimingImplementationGuidelines)
