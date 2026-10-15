---
id: auto-nfa-state-explosion
title: Why determinisation can grow exponentially
level: intermediate
minutes: 4
sourceLesson: auto-nfa
summary: An NFA with m states has at most two to the power m subset states.
---

## The exponential blow-up

Back to "the n-th symbol from the end is 1", where n is a fixed positive whole number such as 3. The NFA has one looping start state, one state for the guess on 1, then one state for each of the n − 1 "any symbol" steps that must follow. The subset construction produces:

| n | NFA states | DFA states |
|---|---|---|
| 1 | 2 | 2 |
| 2 | 3 | 4 |
| 3 | 4 | 8 |
| 4 | 5 | 16 |
| 6 | 7 | 64 |

The pattern in the table, in symbols:

```formula
m = n + 1
d = 2^n = 2^{m − 1}
where
n: which position from the end must be 1 (n = 3 means third from the end); a positive integer
m: the number of NFA states; an integer count, non-negative unless a positive lower bound is stated
d: the number of states in the minimal DFA
2^n: 2 to the power n: the number of different bit strings of length n
In words: the NFA grows by one state each time n goes up by one, but the DFA doubles. For n = 6 the NFA has 7 states and the DFA has 2^6 = 64.
```

These DFAs are already minimal DFAs; you cannot do better. The reason is that the DFA must remember the last n symbols. Take two different strings u and v of length n. They differ at some position, say u has 1 and v has 0 at position i, counting from the left. Append i − 1 more symbols: now that position is n-th from the end, so one string is accepted and the other is not. So all two to the power n strings of length n need different states.

For example, with n set to 3, take u as `110` and v as `100`. They differ at position 2, so append one symbol, say `0`: `1100` has 1 third from the end (accept) and `1000` has 0 there (reject).

> [!warning] Worst case is real
> The general subset bound is exponential in the number of NFA states, and this family comes close to it. Full determinisation can be manageable for a given workload, but engines that build full DFAs ahead of time must guard against patterns like `(a|b)*a(a|b){20}`, which needs over a million states.

The general bound against this family:

```formula
d ≤ 2^m
d_L = 2^{m − 1}
2^{21} = 2,097,152
where
d: the number of states of the DFA built from the NFA
d_L: the minimal DFA size for the language "n-th symbol from the end is 1", whose NFA has m states
m: the number of NFA states; an integer count, non-negative unless a positive lower bound is stated
2^m: 2 to the power m: the number of subsets of m states, the most the subset construction can ever produce
≤: is less than or equal to
In words: an m-state NFA never needs more than 2^m DFA states. The n-th-from-the-end family needs exactly half that, 2^(m − 1): exponential, but not the full bound. The pattern (a|b)*a(a|b){20} asks for "21st from the end is a", so its minimal DFA has 2^21, about 2.1 million, states.
```

## Key takeaways
- An NFA with m states has at most two to the power m subset states.
- The n-th-from-end family has pairwise distinguishable length-n prefixes and needs exponentially many DFA states.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
