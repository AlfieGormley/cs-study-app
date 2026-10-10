---
id: auto-regex-engines
title: Practical regex engines and ReDoS
level: advanced
minutes: 16
summary: How Perl-style backtracking engines and automaton-based engines like RE2 actually match, why one can take exponential time on a 30-character input, the outages this caused, and how to defend against it.
---

Two engines can recognise the same language while doing very different amounts of work. A path-enumerating backtracker can revisit the same state and input position exponentially many times; a set-based simulation merges those repeated situations.

## Matching strategies and guarantees

Costs in this lesson are given in Big O notation in terms of two sizes:

```formula
W = O(m × (n + 1))
where
W: the total work of one search by set simulation, in basic steps
O( ): Big O: an upper bound on growth that ignores constant factors
m: the compiled pattern size: roughly the number of NFA states or instructions, including expansions such as counted repetition
n: the length of the input text, in characters
In words: set simulation does at most a pattern-sized amount of work per input character, plus one extra round at the start, so doubling the input at most doubles the work.
```

For example, a 50-instruction pattern over a 1,000,000-character log is at most about 50 × 1,000,001 ≈ 5 × 10⁷ basic steps, times a constant.

| Strategy | Idea | Important limit |
|---|---|---|
| Unmemoized backtracking | Try choices depth-first and revisit alternatives after failure | Ambiguous patterns can take exponential time |
| Thompson/Pike simulation | Merge equivalent active states at each input position | Bounded-out-degree machines use O(m·(n + 1)) work |
| Lazy DFA | Caches sets of active states and their transitions | Full determinisation can require exponentially many states |

For a fixed pattern, m is a constant, so a documented O(m·n) single-search guarantee is linear in input size.

Production libraries combine strategies. Python re, Java's standard engine and default PCRE2 matching use backtracking; RE2, Go regexp and Rust regex provide input-linear single-search guarantees for their supported syntax. A bounded memoized backtracking implementation can also avoid repeated state/position work. Ruby 3.2 added memoization for many patterns; PCRE2 has a separate DFA-style API; GNU grep chooses methods according to options and syntax. Engine names alone do not specify every mode's behavior.

## How backtracking works

A backtracking engine walks the NFA **depth-first**. At every choice (an alternation, or "one more iteration or stop?"), it tries one option and remembers the other. If the path fails later, it returns to the most recent choice point and tries the alternative.

Here is the idea as code, run directly on a Thompson NFA like the one built in lesson 3:

```python
calls = 0

def bt(q, w, i):
    global calls
    calls += 1
    if q == acc and i == len(w):
        return True
    for r in delta.get((q, ""), ()):
        if bt(r, w, i):
            return True
    if i < len(w):
        for r in delta.get((q, w[i]), ()):
            if bt(r, w, i + 1):
                return True
    return False
```

This teaching function requires a supplied delta and accepting state. It has no memoization, recursion limit handling or epsilon-cycle guard; do not use it as a production matcher. A successful path may be found early, but other patterns can do extensive work before eventually succeeding. Failure may require exploring all remaining choices.

> [!note] Evidence gap
> Previous exact call counts and laptop timings are omitted: the original machine fixture and reproducible benchmark configuration were unavailable. The following combinatorial analysis explains growth without claiming measured runtime.

### Why it explodes

Consider full-string matching `(a+)+` against a run of n a's followed by one b (n at least 1), using an unoptimized path-enumerating backtracker.

The run of a's can be split among the inner `a+` iterations in many ways: for each of the gaps between neighbouring a's, choose whether to start a new inner iteration there.

```formula
g = n − 1
W_split = 2^{n − 1}
W_split = 2^3 = 8   for n = 4
where
n: the number of a's before the b
g: the number of gaps between neighbouring a's
W_split: the number of ways to cut the run of a's into non-empty consecutive pieces
2^{n − 1}: n − 1 copies of 2 multiplied together: each gap is independently "cut" or "no cut"
In words: every extra a adds one more gap and doubles the number of splits, so the work of trying them all doubles per character.
```

`aaaa` could be (aaaa), (a)(aaa), (aa)(aa), (a)(a)(aa), and so on: 8 splits in all. With 30 a's there are 2²⁹, over 500 million. Every split reaches the b and fails. The backtracker tries them all, because it does not remember that it has already been in this NFA state at this input position and failed.

That is the whole problem. The set simulation merges all those paths: it only asks *which states* are reachable after i characters, not *how*.

## Growth without a timing claim

For a path-enumerating matcher without memoization or simplifying optimizations, (a|aa)* on a failing run has Fibonacci-many decompositions: the first part has length one or two.

```formula
W(n) = W(n − 1) + W(n − 2)
W(0) = W(1) = 1
W(n + 1) / W(n) → φ
φ = (1 + √5) / 2 ≈ 1.618
where
n: the number of a's in the run
W(n): the number of ways to write n as an ordered sum of 1s and 2s, one way per path the backtracker explores
→: approaches, as n grows larger and larger
φ: Greek phi: the golden ratio
√5: the square root of 5, about 2.236
≈: is approximately equal to
In words: a run of n a's starts with a part of length 1 (leaving n − 1) or length 2 (leaving n − 2), so the counts follow the Fibonacci numbers 1, 1, 2, 3, 5, 8, …, and each extra a multiplies the count by about 1.618.
```

For example, four a's have 3 + 2 = 5 decompositions (three for a run of three, plus two for a run of two): aaaa splits as 1+1+1+1, 2+1+1, 1+2+1, 1+1+2 and 2+2. This grows asymptotically by a factor approaching 1.618 per additional a. It is a count of possible decompositions, not an exact CPU-instruction count or a universal runtime prediction.

## The danger patterns

Exponential blow-up needs **ambiguity**: several different paths through the pattern that consume the same text. Look for:

- **Nested regex quantifiers**: `(a+)+`, `(a*)*`, `(\w+\s?)*`.
- **Overlapping alternatives under a quantifier**: `(a|a)*`, `(\w|\d)+`, `(.|\s)*`.
- **Adjacent quantified parts that can match the same characters**: `.*.*=`, `\d+\d+`. On their own these are usually polynomial, but repeated or nested inside another quantifier they compound.

There is also a **polynomial** form, which is less dramatic per character but easier to trigger:

- An unoptimized search for \s+$ on a run of spaces followed by x tries every space as a starting position, and from each start scans the remaining spaces before failing at the x. That is quadratic work; the sum is worked out below.

```formula
S = n + (n − 1) + … + 1
S = n × (n + 1) / 2
S = 10 × 11 / 2 = 55   for n = 10
where
n: the number of spaces before the x
S: the total number of spaces scanned over all starting positions
…: the terms in between, counting down by one
In words: the first start scans n spaces, the next n − 1, and so on down to 1. That triangular sum is about half of n squared, so doubling the spaces roughly quadruples the work.
```

Actual engine optimizations and constants determine runtime.

## Real outage

> [!note] Evidence gap
> Detailed Stack Overflow outage timings and remediation claims are omitted because its original postmortem could not be retrieved during this review. This is a source-access limitation, not evidence that the event did not happen.

> [!example] Cloudflare, 2 July 2019
> A new web application firewall rule contained `.*(?:.*=.*)` inside a larger pattern. Deployed globally at once, it drove CPUs serving HTTP traffic to nearly 100% and took down Cloudflare's proxy and CDN for 27 minutes. Cloudflare's postmortem shows the simplified `.*.*=.*;` taking 5,353 steps to fail on `x=` followed by 20 x's. Among the follow-ups: switching the WAF to RE2 or Rust's regex engine, "which both have run-time guarantees".

The common thread: a pattern that looked fine, an input nobody had tested, and a regex evaluated on a hot path.

## How automaton engines avoid it

RE2, Go regexp and Rust regex prevent unrestricted repeated exploration for their supported single searches. Implementations can combine several methods, including bounded memoized path exploration. The main ideas:

1. **Thompson NFA simulation** (lessons 2 and 3): track the set of active states. O(m) per character, where m is the compiled pattern size.
2. **Pike VM**: the same, but each active state carries its capture-group positions, with a priority order so results match Perl's leftmost-first semantics.
3. **Lazy DFA**: cache subset-construction states as they are discovered. A cached transition can be followed with a table lookup; the hit rate is workload-dependent. RE2 bounds the cache's memory; if it fills too often, it falls back to the NFA.
4. **Literal prefilters**: scan for a required fixed string (say `ERROR` in `ERROR.*timeout`) with fast substring search, and only run the automaton near hits.

Go's documentation states the guarantee directly: matching is "guaranteed to run in time linear in the size of the input". Rust's says searches are worst case O(m · n), with m the pattern size and n the input length.

### The price

Features that are not regular, or are expensive to simulate, are left out:

- **Backreferences** like `(\w+) \1`. General backreferences can express non-regular languages, although individual backreference patterns can still be regular; `^(..+)\1+$` on a string of a's matches exactly when the length is composite. General backreferences cannot be implemented by ordinary finite automata. This does not mean every individual backreference pattern is slow or non-regular.
- **Lookaround** (`(?=...)`, `(?<=...)`) is unsupported in RE2, Go and Rust's `regex`. .NET's NonBacktracking mode also excludes lookarounds and backreferences.
- **Atomic groups and possessive quantifiers** can change which strings match. They have meaning beyond a particular execution algorithm: PCRE2’s DFA-style matcher supports them with documented semantics. RE2, Go and Rust regex omit this syntax.

Linear time is per search. Rust's documentation notes that iterating over **all** matches can be O(m · n²) in the worst case, where m is the pattern size and n the input length: up to n searches, each linear. And large patterns cost memory: counted repetition of a Unicode class, such as `\w{200}`, compiles to a big automaton, which is why these libraries enforce size limits on compiled patterns.

## Defences

1. **Use a linear-time engine for untrusted input or untrusted patterns.** Python has the `google-re2` bindings; Java has RE2/J; .NET 7+ has `RegexOptions.NonBacktracking`; V8 described an experimental linear engine and /l flag in a 2021 article; availability depends on runtime version and build flags, so this is not a portable JavaScript feature. Bound pattern size, compilation resources and input volume even with linear matching.
2. **Remove ambiguity.** `(a+)+` is just `a+`. `(\w+\s?)*` has the same full-match language as `(\w+\s)*\w*`, but in the second form every word must end at a space, so each string can be matched only one way. Captured-group results can differ. Unanchored searches also need separate complexity analysis.
3. **Use atomic groups or possessive quantifiers** where the engine has them. Python 3.11 added both: `(?>a+)+$` and `(a++)+$` eliminate that nested pattern’s repeated splitting because the inner group cannot give back characters. Atomicity does not make every surrounding search safe and can change accepted input.
4. **Bound the input.** Cap field lengths before matching. Reject overlong values rather than validating only a truncated prefix: truncation can hide an invalid suffix.
5. **Set timeouts** where supported: .NET's `Regex` accepts a match timeout. Python's `re` and Java's `java.util.regex` have none built in, so use a killable process or an execution boundary that actually stops the work on deadline. Timing out a waiting thread does not necessarily stop the underlying match.
6. **Test with failing inputs.** Long almost-matches (many a's then a wrong character) are what expose backtracking. Static analysers and fuzzers for ReDoS exist for several languages.
7. **Don't use regex for nested structure.** Formal regular expressions cannot recognise arbitrary nesting. Bounded nesting and richer engine features are different cases; use a suitable parser for general structured formats.

## Choosing an engine

- **Backtracking** is right when you need backreferences or lookaround, patterns are written by your own developers, and inputs are bounded. Check the chosen implementation, input limits and required features; developer-authored patterns can also be vulnerable.
- **Automaton-based** is right when patterns or inputs come from users (search boxes, WAF rules, log filters, user-supplied validation), when inputs are large (grep over gigabytes), or when predictable scaling matters. This still requires resource limits and workload testing.

## Key takeaways
- Backtracking engines (Perl, PCRE, Python, Java, JavaScript, .NET default) search NFA paths depth-first; ambiguous patterns make the number of paths exponential.
- Long almost-matching failures expose many vulnerabilities; success can also require substantial backtracking in other patterns.
- Ambiguous repetition can cause excessive work in path-enumerating engines. A naive repeated-start search for \s+$ has quadratic work on a failing whitespace run.
- Cloudflare’s primary postmortem documents a 27-minute regex-related outage in July 2019.
- RE2, Go and Rust simulate the automaton (set simulation, Pike VM, lazy DFA) for O(m · n) worst case, for pattern size m and input length n, at the cost of backreferences and lookaround.
- Defend with linear-time engines for untrusted input, unambiguous patterns, atomic groups, input length caps and timeouts.

## Further reading
- [Regular Expression Matching Can Be Simple And Fast — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Regular Expression Matching in the Wild (RE2) — Russ Cox](https://swtch.com/~rsc/regexp/regexp3.html)
- [Details of the Cloudflare outage on July 2, 2019 — Cloudflare blog](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [Regular expression Denial of Service (ReDoS) — OWASP](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [An additional non-backtracking RegExp engine — V8 blog](https://v8.dev/blog/non-backtracking-regexp)
- [regex crate documentation — docs.rs](https://docs.rs/regex/latest/regex/)
