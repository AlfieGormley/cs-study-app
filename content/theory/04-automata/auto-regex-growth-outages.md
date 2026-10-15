---
id: auto-regex-growth-outages
title: Ambiguous patterns, growth and outages
level: advanced
minutes: 4
sourceLesson: auto-regex-engines
summary: Nested repetition and overlapping alternatives can create exponentially many paths.
---

A path-enumerating backtracker retries alternatives after a path fails. Here the input length counts the repeated a characters before the final failing symbol, unless stated otherwise.

## Growth without a timing claim

For a path-enumerating matcher without memoization or simplifying optimizations, (a|aa)* on a failing run has Fibonacci-many decompositions: the first part has length one or two.

```formula
W(n) = W(n − 1) + W(n − 2) for n ≥ 2
W(0) = W(1) = 1
W(n + 1) / W(n) → φ
φ = (1 + √(5)) / 2 ≈ 1.618
where
n: the number of a's in the run; an integer count, non-negative unless a positive lower bound is stated
W(n): the number of ways to write n as an ordered sum of 1s and 2s, one way per path the backtracker explores
→: approaches, as n grows larger and larger
φ: Greek phi: the golden ratio
√( ): the non-negative square-root function; the square root of 5 is about 2.236
≥: is greater than or equal to
≈: is approximately equal to
In words: a run of n a's starts with a part of length 1 (leaving n − 1) or length 2 (leaving n − 2), so the counts follow the Fibonacci numbers 1, 1, 2, 3, 5, 8, …, and each extra a multiplies the count by about 1.618.
```

For example, four a's have 3 + 2 = 5 decompositions (three for a run of three, plus two for a run of two): aaaa splits as 1+1+1+1, 2+1+1, 1+2+1, 1+1+2 and 2+2. This grows asymptotically by a factor approaching 1.618 per additional a. It is a count of possible decompositions, not an exact count of executed CPU instructions or a universal runtime prediction.

## The danger patterns

Exponential blow-up needs **ambiguity**: several different paths through the pattern that consume the same text. Look for:

- **Nested regex quantifiers**: `(a+)+`, `(a*)*`, `(\w+\s?)*`.
- **Overlapping alternatives under a regex repetition operator**: `(a|a)*`, `(\w|\d)+`, `(.|\s)*`.
- **Adjacent repeated parts that can match the same characters**: `.*.*=`, `\d+\d+`. On their own these are usually polynomial, but repeated or nested inside another regex repetition operator they compound.

There is also a **polynomial** form, which is less dramatic per character but easier to trigger:

- An unoptimized search for \s+$ on a run of spaces followed by x tries every space as a starting position, and from each start scans the remaining spaces before failing at the x. That is quadratic work; the sum is worked out below.

```formula
S = n + (n − 1) + … + 1
S = n(n + 1) / 2
S = 10 × 11 / 2 = 55   for n = 10
where
n: the number of spaces before the x; an integer count, non-negative unless a positive lower bound is stated
S: the total number of spaces scanned over all starting positions
…: the terms in between, counting down by one
In words: the first start scans n spaces, the next n − 1, and so on down to 1. That triangular sum is about half of n squared, so doubling the spaces roughly quadruples the work.
```

Actual engine optimizations and constants determine runtime.

## Real outage

> [!note] Evidence gap
> Detailed Stack Overflow outage timings and remediation claims are omitted because its original postmortem could not be retrieved during this review. This is a source-access limitation, not evidence that the event did not happen.

> [!example] Cloudflare, 2 July 2019
> A new web application firewall rule contained `.*(?:.*=.*)` inside a larger pattern. Deployed globally at once, it drove CPUs serving HTTP traffic to nearly 100% and took down Cloudflare's proxy and CDN for 27 minutes. Cloudflare's postmortem shows the simplified `.*.*=.*;` taking 5,353 steps to fail on `x=` followed by 20 x's. Among the follow-ups: switching the WAF to RE2 or Rust's regex engine, both documented as providing runtime guarantees.

The shared cause: a pattern that looked fine, an input nobody had tested, and a regex evaluated on a hot path.

## Key takeaways
- Nested repetition and overlapping alternatives can create exponentially many paths.
- Repeated-start searches may also have polynomial worst cases; failing almost-matches expose the work.

## Further reading
- [Cloudflare: details of the July 2019 outage](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [Russ Cox: simple and fast matching](https://swtch.com/~rsc/regexp/regexp1.html)
