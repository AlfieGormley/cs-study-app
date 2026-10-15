---
id: auto-minimise-algorithms
title: Hopcroft and double reversal
level: advanced
minutes: 3
sourceLesson: auto-minimisation
summary: Smaller-half scheduling limits repeated transition work in Hopcroft refinement.
---

Moore refinement repeatedly splits states by their successor blocks until the partition stops changing. Here we compare its cost with two other minimisation methods.

## How fast?

The running times below are written in Big O notation, in terms of two sizes of the DFA:

```formula
T_Moore = O(k n²)
T_Hopcroft = O(k n log_2(n))
where
T_Moore: the worst-case running time of Moore's partition refinement
T_Hopcroft: the worst-case running time of Hopcroft's algorithm
O( ): Big O: an upper bound on growth that ignores constant factors
n: the number of states in the DFA; an integer count, non-negative unless a positive lower bound is stated
k: the size of the alphabet (the number of different input symbols); an integer count, non-negative unless a positive lower bound is stated
n²: n squared, n × n
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1, so log_2(1024) = 10
In words: Moore's algorithm can take time proportional to the alphabet size times the square of the state count; Hopcroft's replaces one factor of n with the much smaller log of n.
```

For a 1,000-state DFA over 2 symbols, the alphabet size times the squared state count is 2,000,000, while the alphabet size times the state count times its base-two logarithm is about 20,000: a hundredfold difference before constant factors.

| Algorithm | Worst case | Notes |
|---|---|---|
| Table filling | O(k n²) with a dependency worklist | repeated full passes can be slower |
| Moore | O(k n²) | rounds of refinement |
| Hopcroft (1971) | O(k n log n) | split by smaller half |
| Brzozowski | exponential | det(rev(det(rev(A)))) |

**Hopcroft's algorithm** is the standard choice for large automata. Its worklist rule matters: if a split block is already pending, replace it with both pieces; otherwise schedule only the smaller piece. Smaller-piece scheduling and reverse transition lists let each of the transitions be charged O(log n) times: a state can only be in a scheduled "smaller half" about log₂ n times, because each time the piece containing it at least halves.

**Brzozowski's algorithm** is strange and elegant: reverse the automaton, determinise, reverse again, determinise again.

```formula
A_min = det(rev(det(rev(A))))
where
A: the input automaton (a DFA or an NFA)
rev: reversal: flip every arrow, make the accepting states the start states and the start state the accepting state. The result recognises every string of the language written backwards
det: determinisation by the subset construction, keeping only reachable sets
A_min: the result, a minimal DFA for the same language as A
In words: reverse, determinise, reverse, determinise, reading the functions from the inside out; the result is always the minimal DFA.
```

The result is always the minimal DFA. Its worst case is exponential because each determinisation can blow up, but it can be fast in practice and works directly on NFAs.

## Key takeaways
- Smaller-half scheduling limits repeated transition work in Hopcroft refinement.
- Double reversal and reachable determinisation give a minimal DFA, with exponential worst-case intermediates.

## Further reading
- [Minimization of Automata — Berstel, Boasson, Carton and Fagnot](https://arxiv.org/abs/1010.5318)
- [Hopcroft: minimising finite automata (1971)](http://i.stanford.edu/pub/cstr/reports/cs/tr/71/190/CS-TR-71-190.pdf)
