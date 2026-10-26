---
id: auto-regex-backtracking
title: Matching strategies and repeated paths
level: advanced
minutes: 5
sourceLesson: auto-regex-engines
summary: Path enumeration can revisit the same state and input position through many decompositions.
---

Two engines can recognise the same language while doing very different amounts of work. A path-enumerating backtracker can revisit the same state and input position exponentially many times; a set-based simulation merges those repeated situations.

## Matching strategies and guarantees

In the cost discussion, m is the compiled pattern size, including counted-repeat expansion, and n is the input length. Set simulation performs at most a machine-sized amount of work per input symbol, plus initialisation. The optional bound records that relationship:

```formula reference
W = O(m × (n + 1))
where
W: the total work of one search by set simulation, in basic steps
O( ): Big O: an upper bound on growth that ignores constant factors
m: the compiled pattern size: roughly the number of NFA states or instructions, including expansions such as counted repetition; an integer count, non-negative unless a positive lower bound is stated
n: the length of the input text, in characters; an integer count, non-negative unless a positive lower bound is stated
In words: set simulation does at most a pattern-sized amount of work per input character, plus one extra round at the start, so this upper bound grows linearly with input length for a fixed compiled pattern; it does not predict an exact time.
```

Set simulation limits each input step to work bounded by the compiled machine size. For a fixed pattern this gives input-linear growth. Changing the pattern size or repeatedly calling the search API changes the total workload.

| Strategy | Idea | Important limit |
|---|---|---|
| Unmemoized backtracking | Try choices depth-first and revisit alternatives after failure | Ambiguous patterns can take exponential time |
| Thompson/Pike simulation | Merge equivalent active states at each input position | Bounded-out-degree machines use O(m·(n + 1)) work |
| Lazy DFA | Caches sets of active states and their transitions | Full determinisation can require exponentially many states |

For a fixed pattern, m is a constant, so a documented O(m·n) single-search guarantee is linear in input size.

Production libraries combine strategies. Python re, Java's standard engine and default PCRE2 matching use backtracking; RE2, Go regexp and Rust regex provide input-linear single-search guarantees for their supported syntax. A bounded memoized backtracking implementation can also avoid repeated state/position work. Ruby 3.2 added memoization for many patterns; PCRE2 has a separate DFA-style API; GNU grep chooses methods according to options and syntax. Engine names alone do not specify every mode's behavior.

## How backtracking works

A backtracking engine walks the NFA **depth-first**. At every choice (an alternation, or "one more iteration or stop?"), it tries one option and remembers the other. If the path fails later, it returns to the most recent choice point and tries the alternative.

Here is the idea as code, run directly on a Thompson NFA like the one built in the Thompson-construction units:

```python
calls = 0

def bt(q, w, i):
    global calls
    # Count visits, including revisited
    # states.
    calls += 1
    if q == acc and i == len(w):
        return True
    # Try free moves before consuming a
    # symbol.
    for r in delta.get((q, ""), ()):
        if bt(r, w, i):
            return True
    if i < len(w):
        for r in delta.get((q, w[i]), ()):
            # This branch consumes exactly
            # one symbol.
            if bt(r, w, i + 1):
                return True
    return False
```

This teaching function requires a supplied delta and accepting state. It has no memoization, handling of excessive call nesting or epsilon-cycle guard; do not use it as a production matcher. A successful path may be found early, but other patterns can do extensive work before eventually succeeding. Failure may require exploring all remaining choices.

### Why it explodes

Consider full-string matching `(a+)+` against a run of n a's followed by one b (n at least 1), using an unoptimized path-enumerating backtracker.

The run of a's can be split among the inner `a+` iterations in many ways: for each of the gaps between neighbouring a's, choose whether to start a new inner iteration there.

Every gap between neighbouring a characters can either separate two inner repetitions or stay inside one. Adding another a adds a new independent cut-or-no-cut choice, doubling the number of decompositions. A matcher that retries each decomposition repeats work exponentially.

`aaaa` could be (aaaa), (a)(aaa), (aa)(aa), (a)(a)(aa), and so on: 8 splits in all. With 30 a's there are two to the power twenty-nine, over 500 million. Every split reaches the b and fails. The backtracker tries them all, because it does not remember that it has already been in this NFA state at this input position and failed.

That is the whole problem. The set simulation merges all those paths: it only asks *which states* are reachable after i characters, not *how*.

## Key takeaways
- Path enumeration can revisit the same state and input position through many decompositions.
- A fixed-pattern input-linear guarantee is different from a bound that also includes pattern size.

## Further reading
- [Russ Cox: simple and fast regular-expression matching](https://swtch.com/~rsc/regexp/regexp1.html)
- [MIT: regexes to finite automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
