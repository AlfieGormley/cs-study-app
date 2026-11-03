---
id: dist-hybrid-clock-uncertainty
title: Hybrid logical clocks and uncertain reads
level: intermediate
minutes: 4
summary: Combine wall time with a counter and recognise when clock uncertainty requires a read restart.
sourceLesson: dist-time-ordering
---

Vector clocks expose causality but carry an entry per participant. Hybrid logical clocks keep a compact, time-like timestamp while retaining Lamport’s one-way causality guarantee.

## Hybrid logical clocks (HLC)

HLC (Kulkarni et al., 2014) combines physical time with a logical counter. Each timestamp is a pair `(l, c)`:

- `l` tracks the largest physical time seen,
- `c` is a counter that breaks ties when `l` doesn't advance.

The rule on a send or local event:

```formula reference
l′ = max(l, pt)
where
l: the HLC's current physical part: the largest physical time this node has seen, in the clock's time units
pt: the node's own physical (wall-clock) time right now, read from its time-of-day clock
l′: l-prime, the new physical part after the event
max: the larger of its inputs
In words: the physical part follows the wall clock, but never goes backwards and never falls behind a time it has already seen.
```

The counter then decides ties. If the new physical part is the same as before (the wall clock hasn't moved past what was already seen), the counter goes up by one; otherwise the physical part has advanced and the counter resets to 0.

On receive of a message stamped `(lm, cm)`, take the max of `l`, `lm` and `pt`. If the new physical part matches both the old local part and the message part, use one more than the larger counter. If only one matches, increment that input's counter. If physical time exceeds both, reset the counter to zero.

Properties:

- Respects happens-before like a Lamport clock (and, like one, can't detect concurrency).
- Stays close to physical-clock time under the paper's bounded clock-synchronisation assumptions, including limits on backwards movement, so timestamps remain time-like. It does not make incorrect physical clocks accurate or independently establish true time.
- Can use compact fixed-size encodings; exact timestamp widths and counter-overflow handling depend on the implementation.

The proximity argument assumes an earlier causal physical-clock reading cannot exceed a later reading by more than the bound. If all physical clocks jump far backwards together, pairwise skew can remain small while an HLC retains the old higher time; bounded pairwise skew alone is insufficient.

CockroachDB and YugabyteDB use HLCs for MVCC timestamps. CockroachDB adds a **maximum clock offset** (500 ms by default as of 2026, configurable with `--max-offset`) and an "uncertainty interval". In the simplified case with no observed-timestamp information narrowing the interval, a value inside that window may precede the read in physical time. CockroachDB tries to advance the transaction timestamp past the value and refresh earlier reads; a transaction retry is needed if it cannot refresh them.

```formula reference
r < w ≤ r + Δ_max
where
r: the read's timestamp
w: the timestamp of a value the read finds
Δ_max: delta-max, the maximum clock offset allowed between any two nodes; 500 milliseconds (ms) by default in CockroachDB
ms: millisecond, one thousandth of a second
In words: a value stamped later than the read, but by no more than the maximum clock offset, might really have been written before the read, so the read can't safely ignore it.
```

For example, a read at 10.000 s that finds a value stamped 10.200 s cannot tell which really came first, because 200 ms is within the 500 ms offset allowance; the transaction's timestamp moves past the value, and refreshing or retrying the read then includes it. A value stamped 10.600 s is beyond the allowance, so the read can treat it as definitely later and ignore it.

A node that detects its clock is too far from the rest of the cluster (by default, more than 80% of the maximum offset from at least half the other nodes) shuts itself down rather than risk violating the bound.

## Key takeaways
- An HLC pairs the largest physical time observed with a counter for ties, so timestamps keep moving forward.
- HLCs preserve happens-before but cannot detect concurrency; their encodings depend on the implementation.
- A write inside CockroachDB’s read uncertainty interval may precede the read in physical time, requiring a timestamp advance, read refresh or retry.

## Further reading
- [Logical Physical Clocks and Consistent Snapshots (HLC paper)](https://cse.buffalo.edu/tech-reports/2014-04.pdf)
- [CockroachDB transaction retries and refreshing](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer)
- [CockroachDB maximum offset setting](https://www.cockroachlabs.com/docs/stable/cockroach-start)
- [Living without atomic clocks (Cockroach Labs)](https://www.cockroachlabs.com/blog/living-without-atomic-clocks/)
