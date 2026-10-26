---
id: prob-average-transfer-times
title: Average transfer times rather than rates
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Compute the duration in each outcome before averaging.
---

A fast transfer cannot cancel a slow transfer simply because their speeds average neatly. First decide what you are averaging: speed at a moment, speed per transfer, or the duration of a fixed job.

## Average the quantity you need

Each 100-megabyte download independently chooses either 10 or 90 megabytes per second with equal probability and keeps that speed throughout. Ignore overhead. The slow download lasts 10 seconds and the fast one about 1.11 seconds, giving a mean duration about 5.56 seconds.

The mean of the two chosen speeds is 50 megabytes per second. Dividing the file size by that mean gives two seconds, which does not describe the expected duration. The reciprocal relationship between speed and time is non-linear: calculate time in each outcome before averaging.

## Why slow transfers matter so much

Halving a speed doubles the time for the same file. A very slow possibility can therefore add substantial waiting time, even when a fast possibility makes the average speed look attractive. For positive speeds and finite relevant expectations, **Jensen’s inequality** formalises why dividing by the expected speed underestimates or equals the expected duration.

A single transfer spending equal amounts of time at the two rates is a different model. Likewise, averaging throughput over elapsed time weights observations differently from averaging one chosen speed per fixed-size transfer. State the sampling unit before combining rates.

## Key takeaways
- Convert each outcome to the required quantity before averaging.
- Per-transfer and per-time rate averages answer different questions.
- Non-linear transformations do not generally commute with expectation.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
