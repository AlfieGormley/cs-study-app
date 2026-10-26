---
id: auto-state-elimination
title: Turning an automaton back into a regex
level: intermediate
minutes: 3
sourceLesson: auto-thompson
summary: Eliminating a state preserves routes through it by concatenating entry, starred loop and exit labels.
---

## The other direction: automaton to regex

To show every DFA has a regex, use **state elimination**:

1. Add a new start state with an ε-arrow to the old start, and a new single accept state with ε-arrows from the old accepting states.
2. Allow arrows to be labelled with regexes, not just symbols.
3. Remove the other states one by one. When you remove a state, replace every two-step path through it with a direct arrow whose label is given by the rule below, and union it with any existing direct arrow.
4. When only the new start and accept remain, the label between them is the regex.

The rule for step 3, when removing state q:

```formula essential
R_{pr}′ = R_{pq} · (R_{qq})* · R_{qr}
          | R_{pr}
where
q: the state being removed
p: a state with an arrow into q
r: a state with an arrow out of q
R_{pq}: the regex label on the arrow from p to q
R_{qq}: the label on q's self-loop (use ∅, the empty language, if there is none; its star matches ε)
R_{qr}: the label on the arrow from q to r
R_{pr}: the label already on the direct arrow from p to r (use ∅, the empty set, if there is none)
R_{pr}′: the new label on the direct arrow from p to r
·: concatenation: one part straight after the other
*: the Kleene star: zero or more repetitions
|: union (alternation): either side
In words: to get from p to r without q, you can go into q, loop round q any number of times, and come out to r, or you can take the direct arrow that was already there.
```

For the "even number of 1s" DFA from the DFA units (E loops on 0, 1 goes to O, O loops on 0, 1 goes back to E), eliminate O. The arrow into O is `1`, O's loop is `0` and the arrow out is `1`, so the path E → O → E becomes `10*1`. With E's own `0` loop the answer is `(0|10*1)*`.

Regexes produced this way can be exponentially longer than the DFA, and different elimination orders give different (equivalent) regexes. That is why tools go regex → automaton all the time and rarely the other way.

## Key takeaways
- Eliminating a state preserves routes through it by concatenating entry, starred loop and exit labels.
- Union preserves any existing direct route; the final regex may be much larger than the original DFA.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
