---
id: ds-signal-operations
title: Gain, mixing and delay
level: basic
minutes: 3
summary: Change values and timing while stating what happens at record edges.
---

Many DSP tasks begin with simple operations: scale one record, add two records, or shift a record in time. Specify units and timing before combining arrays. Adding a temperature in degrees to an acceleration in metres per second squared has no physical meaning without an explicit model or conversion.

## Scale and mix aligned records

**Gain** multiplies every sample by a factor. A negative gain reverses polarity, swapping positive and negative values. **Mixing** here means adding aligned samples, possibly with separate gains. It does not mean interleaving two arrays or appending one after another.

For the unitless records `[1, -1]` and `[1, 1]`, adding corresponding values gives `[2, 0]`. Equal positive samples reinforce; opposite samples cancel. Two records each within a normalised limit of 1 can therefore sum beyond that limit. Scaling before a range-limited output provides **headroom**, a margin below the allowed peak.

For example, reducing both inputs before mixing can leave room for aligned peaks. Reducing gain after a range-limited stage has already clipped does not restore the original sum. The point at which gain is applied matters.

Equal array lengths alone do not establish that timestamps agree. Two sensors can store the same number of values at different rates or with different starting times. Align what each position represents before adding it. Appending one record after another is concatenation, a different operation from mixing.

## Delay with explicit boundaries

A **sample delay** makes an event occur later. For an integer delay, retrieve an earlier input value at each output index. This lesson treats values outside the finite input record as zero, called **zero extension**.

For input `[1, 2, 3]` and a two-sample delay, retaining only three output samples gives `[0, 0, 1]`. Retaining the complete delayed finite record gives `[0, 0, 1, 2, 3]`. This is a storage choice: the last two original values were cropped in the short output, not destroyed by the delay itself.

A delay measured in samples needs a sample rate to become a time. At a higher rate, the same number of delayed samples represents a shorter wait. A pure delay changes when events occur without changing their order or playing them more slowly.

> [!analogy] Real-world analogy: A recording with a later start
> Imagine placing a recorded announcement two seconds later on a timeline.
>
> **How it maps:** A delay changes the announcement’s position. Saving only the original time window can crop the end, while extending the timeline retains it.
>
> **Where it stops:** This models a pure shift, not echoes, speed changes or the physical propagation of sound.

Shifting values from the end back to the start would be a **circular shift**, a different boundary convention. It can create a value at the beginning where a delayed recording should still be silent. Fractional-sample delay requires estimating values between sample positions and is outside this lesson.

## Key takeaways
- Mixing adds aligned compatible samples; gains control their contributions.
- Sample addition can exceed individual input peaks.
- State the delay’s boundary convention and whether the output retains its tail.

## Further reading
- [Steven W. Smith: relevant chapter](https://www.dspguide.com/CH5.PDF)
