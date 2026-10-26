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

The first repetition consumes either one a or two. Each choice leaves a shorter run with the same problem, so alternatives branch repeatedly. The decomposition counts begin 1, 1, 2, 3, 5, 8: each count combines the previous two. This is exponential growth even though it does not double with every character.

For example, four a characters can be consumed as four singles, two doubles, or one double with two singles in three different orders. These are different paths over the same text. Path counts explain potential repeated work; they are not exact CPU instruction counts or universal timing predictions.

## The danger patterns

Exponential blow-up needs **ambiguity**: several different paths through the pattern that consume the same text. Look for:

- **Nested regex quantifiers**: `(a+)+`, `(a*)*`, `(\w+\s?)*`.
- **Overlapping alternatives under a regex repetition operator**: `(a|a)*`, `(\w|\d)+`, `(.|\s)*`.
- **Adjacent repeated parts that can match the same characters**: `.*.*=`, `\d+\d+`. On their own these are usually polynomial, but repeated or nested inside another regex repetition operator they compound.

There is also a **polynomial** form, which is less dramatic per character but easier to trigger:

- An unoptimised search for `\s+$` on a run of spaces followed by x tries every space as a starting position, and from each start scans the remaining spaces before failing at the x.

The first starting position scans all the spaces. The next scans almost all of them, and so on. Doubling the run creates roughly twice as many starting positions, each with roughly twice as much scanning available: quadratic growth. Faster scanning at a single start does not remove the repeated-start cost.

Actual engine optimizations and constants determine runtime.

## Real outage

> [!example] Cloudflare, 2 July 2019
> A new web application firewall rule contained `.*(?:.*=.*)` inside a larger pattern. Deployed globally at once, it drove CPUs serving HTTP traffic to nearly 100% and took down Cloudflare's proxy and CDN for 27 minutes. Cloudflare's postmortem shows the simplified `.*.*=.*;` taking 5,353 steps to fail on `x=` followed by 20 x's. Among the follow-ups: switching the WAF to RE2 or Rust's regex engine, both documented as providing runtime guarantees.

The shared cause: a pattern that looked fine, an input nobody had tested, and a regex evaluated on a hot path.

## Key takeaways
- Nested repetition and overlapping alternatives can create exponentially many paths.
- Repeated-start searches may also have polynomial worst cases; failing almost-matches expose the work.

## Further reading
- [Cloudflare: details of the July 2019 outage](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [Russ Cox: simple and fast matching](https://swtch.com/~rsc/regexp/regexp1.html)
