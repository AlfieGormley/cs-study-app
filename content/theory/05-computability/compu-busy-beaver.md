---
id: compu-busy-beaver
title: Busy beavers and uncomputable runtime bounds
level: intermediate
minutes: 3
summary: Busy-beaver maxima range only over machines that halt on the blank tape.
sourceLesson: compu-turing-machines
---

## The busy beaver: how strange small machines get

Fix the standard two-way tape, two-symbol busy-beaver model, counting working states separately from one halt state. Among machines of a given size that halt from a blank tape, which runs longest? That maximum step count is the **busy beaver** runtime. Machines that never halt are excluded, rather than assigned an infinite score. For any fixed size there are finitely many transition tables, so the maximum over halting machines exists.

Conventionally S(n) names this maximum for n working states. A different function, Σ(n), counts the greatest number of ones left by such a halting machine. These are separate maxima; the definition does not require one machine to attain both. Here Σ is a function name, not an alphabet.

The 2-state champion:

Reuse `run` from the binary-increment unit. Its blank symbol is set to zero here; H is a halting state.

```python
# States A and B work; H alone halts.
BB2 = {
  ("A", "0"): ("1", "R", "B"),
  ("A", "1"): ("1", "L", "B"),
  ("B", "0"): ("1", "L", "A"),
  ("B", "1"): ("1", "R", "H"),
}
s, n, tape = run(BB2, "", "A", {"H"},
                 blank="0")
# Count the output symbols, not visited
# cells.
ones = sum(v == "1" for v in tape.values())
print(n, ones)   # 6 4
```

| n | S(n) steps | Σ(n) ones |
|---|---|---|
| 2 | 6 | 4 |
| 3 | 21 | 6 |
| 4 | 107 | 13 |
| 5 | 47,176,870 | 4,098 |

S(5) was only proved in 2024, by the online bbchallenge collaboration with a Coq-verified proof. Doing so meant showing that every one of the many millions of 5-state machines either halts within 47,176,870 steps or never halts. The proof combines a case-by-case check covering every machine with certified reasoning about non-halting.

S(n) eventually exceeds every total computable function of n. This stronger growth theorem needs a separate argument. Its uncomputability follows from a simpler observation: if you could compute S(n), you could decide blank-tape halting for an n-state machine by running it for S(n) steps. An arbitrary finite input can be built into a machine’s finite control.

## Key takeaways

- Busy-beaver maxima range only over machines that halt on the blank tape.
- The two-state champion runs six steps and leaves four ones.
- A computable busy-beaver runtime bound would decide blank-tape halting, which is impossible.

## Further reading

- [Busy Beaver Challenge: the certified five-state result](https://bbchallenge.org/)
- [Determination of the fifth Busy Beaver value — proof authors](https://arxiv.org/abs/2509.12337)
