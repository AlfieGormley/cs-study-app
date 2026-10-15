---
id: auto-nfa-lazy-tradeoffs
title: Lazy determinisation and model trade-offs
level: intermediate
minutes: 3
sourceLesson: auto-nfa
summary: Caching reached subsets can give table lookups without constructing every subset first.
---

The subset construction represents an NFA by reachable sets of states. A set accepts whenever it contains an accepting NFA state; this existential rule is why complementing an NFA requires care.

## Why both models matter

- **NFAs are easy to build.** Union, concatenation and star are almost trivial with ε-arrows. That is why the regex-to-automaton construction (the following Thompson-construction units) produces an NFA.
- **DFAs are fast to run.** One table lookup per symbol, no sets.
- **Practical engines mix the two.** RE2 and Rust's `regex` do a **lazy subset construction**: they build DFA states on demand during matching and cache them. If the cache gets too big, they flush it or fall back to NFA simulation. You get DFA speed on typical inputs without paying the exponential cost up front.

In this comparison, m is the number of NFA states and e is the number of transitions (arrows).

| | NFA simulation | Full DFA |
|---|---|---|
| Build cost | O(m) for a Thompson-style NFA | potentially exponential, including transition computation |
| Time per symbol | O(m) for bounded out-degree | O(1) with a precomputed transition table |
| Memory | O(m + e), including transitions | O(2ᵐ) states; transition storage also depends on alphabet size |

## Pitfalls

- **Forgetting ε-closure.** Take the closure of the start state and after every step. Missing it makes ε-arrows invisible, and strings are wrongly rejected.
- **Complementing an NFA by swapping F.** This does not work. An NFA accepts if *some* path accepts, so after swapping, a string with one accepting and one rejecting path is accepted by both machines. Determinise first, then swap.
- **Treating nondeterminism as randomness.** An NFA does not flip coins. It accepts if an accepting path *exists*. It is an existence statement, like the "certificate" view of NP you will meet later.

## Key takeaways
- Caching reached subsets can give table lookups without constructing every subset first.
- Cache limits control memory; nondeterministic acceptance cannot be complemented by swapping accepting states.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
- [Russ Cox: matching in the wild](https://swtch.com/~rsc/regexp/regexp3.html)
