---
id: auto-nfa-simulator
title: Implementing set-based NFA simulation
level: intermediate
minutes: 3
sourceLesson: auto-nfa
summary: Take epsilon closure initially and after each consumed symbol.
---

In the preceding epsilon-NFA: s branches freely to p0 and r0, which are accepting. The p states form a two-step a-cycle and the r states a three-step a-cycle. Closure includes a state and all states reachable by free arrows; the simulator keeps this set for every input position.

## Simulating an NFA in Python

```python
def close(delta, S):
    # Copy so closure does not mutate
    # callers.
    S = set(S)
    todo = list(S)
    while todo:
        q = todo.pop()
        # Follow only free arrows.
        for r in delta.get((q, ""), ()):
            # Discover each state only once.
            if r not in S:
                # This guard terminates
                # epsilon cycles.
                S.add(r)
                todo.append(r)
    return S

def run_nfa(delta, start, accept, w):
    # Include free moves before any input.
    S = close(delta, {start})
    for c in w:
        T = set()
        for q in S:
            # Merge paths reaching the same
            # state.
            T |= delta.get((q, c), set())
        # Free moves also follow consumed
        # symbols.
        S = close(delta, T)
    # Any accepting complete path is enough.
    return bool(S & accept)
```

Here ε is the empty string `""`. Each step looks at every current state and every arrow out of it at most once, and there is one closure for the start plus one step per input symbol. That gives this cost:

```formula
T = O((n + 1) × (m + e))
T = O((n + 1) × m)   when e = O(m)
where
T: the running time of run_nfa, counted in basic steps
O( ): Big O: an upper bound on growth that ignores constant factors
n: the length of the input string, in symbols; an integer count, non-negative unless a positive lower bound is stated
m: the number of NFA states; an integer count, non-negative unless a positive lower bound is stated
e: the number of transitions (arrows) in the NFA; an integer count, non-negative unless a positive lower bound is stated
In words: the work is at most the input length plus one, times the size of the machine. When each state has a bounded number of arrows out of it, the number of arrows is proportional to the number of states, and the bound simplifies to input length plus one, times states.
```

It needs O(m) working memory for the current set, excluding the stored automaton. A Thompson-style NFA (the Thompson-construction units) has at most two arrows out of each state, so the second line applies. For example, a 200-state NFA scanning a 1,000,000-symbol input does at most about 200 × 1,000,001 ≈ 200 million state visits, times a constant. That bound is exactly what makes linear-time regex engines possible: Thompson's algorithm tracks reachable states; modern RE2 and Go regexp use related automaton techniques alongside other optimizations.

## Key takeaways
- Take epsilon closure initially and after each consumed symbol.
- A visited set terminates epsilon cycles; bounded out-degree gives work linear in input length for a fixed machine.

## Further reading
- [MIT: nondeterminism and closure properties](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
- [Rabin and Scott: finite automata (1959)](https://www.cse.chalmers.se/~coquand/AUTOMATA/rs.pdf)
