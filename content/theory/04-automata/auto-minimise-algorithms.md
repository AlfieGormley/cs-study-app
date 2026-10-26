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

```formula reference
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
In words: Moore's worst-case bound grows with the square of the state count and with the alphabet size. Hopcroft's bound grows with the state count times its slowly growing logarithm, again scaled by alphabet size. Careful scheduling limits repeated scanning.
```

The practical distinction is repeated work. Moore's method may rescan states over many rounds. Hopcroft schedules carefully chosen splitters so large blocks do not keep causing the same work. These bounds describe growth, not measured speed on a particular machine. Table filling with a dependency worklist has the same quadratic worst-case growth as Moore; repeated full passes can be slower.

**Hopcroft's algorithm** is the standard choice for large automata. Its worklist rule matters: if a split block is already pending, replace it with both pieces; otherwise schedule only the smaller piece. With reverse transition lists, each transition can be charged only logarithmically many times in the number of states: each newly scheduled smaller piece is at most half its previous block's size.

**Brzozowski's algorithm** is strange and elegant: reverse the automaton, determinise, reverse again, determinise again.

```flow
Reverse the automaton
Build reachable subset states
Reverse the result
Build reachable subset states again
```

Reversal flips every arrow and exchanges initial and accepting roles. Several initial states may result; represent them with a fresh start and epsilon arrows if a single start is required. Each determinisation keeps only reachable subsets.

The result is always the minimal DFA. Its worst case is exponential because each determinisation can blow up, but it can be fast in practice and works directly on NFAs.

## Key takeaways
- Smaller-half scheduling limits repeated transition work in Hopcroft refinement.
- Double reversal and reachable determinisation give a minimal DFA, with exponential worst-case intermediates.

## Further reading
- [Minimization of Automata — Berstel, Boasson, Carton and Fagnot](https://arxiv.org/abs/1010.5318)
