---
id: compu-turing-machines
title: Turing machines
level: intermediate
minutes: 13
summary: The simplest model of a general-purpose computer, a finite control with a read-write tape, and why it can do what PDAs cannot, simulated in Python down to the busy beaver.
---

A PDA's memory is a stack: unbounded, but you can only touch the top. Remove that restriction, so the machine can move freely over its memory and rewrite any cell, and you get a **Turing machine** (TM).

Alan Turing described it in 1936 by imagining a human clerk working with pencil and paper. The clerk has a finite rule book (states), looks at one square at a time, may write or erase a symbol, and may move one square left or right. Everything you would call "an algorithm" can be carried out this way. That claim is the subject of the next lesson. This lesson is about the machine itself.

## The machine

```
   ... _  _  1  0  1  1  _  _ ...   tape
                ▲
             ┌──┴──┐
             │  q  │  finite control
             └─────┘
```

- An **infinite tape** divided into cells. The input is written on it at the start; every other cell holds the blank `_`.
- A **head** that reads one cell, writes a symbol there, and moves one cell left (L) or right (R).
- A **finite control**: the current state.

Formally, a TM is a 7-tuple (Q, Σ, Γ, δ, q₀, q_accept, q_reject):

- **Q**: finite set of states, including the start q₀ and two halting states q_accept ≠ q_reject.
- **Σ**: finite input alphabet (not containing the blank).
- **Γ**: finite tape alphabet, with Σ ⊆ Γ and `_` ∈ Γ. Γ can include extra marker symbols such as X.
- **δ: (Q − {q_accept, q_reject}) × Γ → Q × Γ × {L, R}**: in state q reading symbol a, write b, move, and enter a new state.

A **configuration** is a snapshot: state, tape contents and head position. It is often written `1 0 q 1 1`, meaning the tape is `1011`, the machine is in state q, and the head is on the third symbol.

> [!note] Three outcomes, not two
> On a given input a TM can **accept**, **reject**, or **loop forever**. A DFA completes one transition per input symbol. A PDA can have infinite epsilon-move branches; a decision algorithm for CFL membership still exists. A TM has no such guarantee. That third outcome is the source of every undecidability result in this module.

## Recognisers and deciders

- A TM M **recognises** language L if M accepts exactly the strings in L. On strings outside L it may reject *or loop*. Such languages are **Turing-recognisable** (also called recursively enumerable).
- M **decides** L if it recognises L *and* halts on every input. Such languages are **decidable** (recursive).

Every decidable language is recognisable. Whether the reverse holds is the big question of lesson 5. (It does not.)

## Example 1: binary increment

Add 1 to a binary number. Strategy: run to the right end, then move left turning trailing 1s into 0s (the carry), and turn the first 0 or blank into 1.

```
state  read  write move next
R      0     0     R    R
R      1     1     R    R
R      _     _     L    C
C      1     0     L    C    carry
C      0     1     L    H    done
C      _     1     L    H    new digit
```

Trace on `1011`, writing each configuration with the state just left of the cell under the head:

```
R1011     scan right (4 steps)
1011R_    blank: move L, go to C
101C1     1 → 0, carry, move L
10C10     1 → 0, carry, move L
1C000     0 → 1, halt
H1100     11 + 1 = 12, in 8 steps
```

## Simulating a Turing machine in Python

A dictionary from position to symbol models the infinite tape: missing keys are blank, and negative positions work for free.

```python
def run(delta, w, start, halt,
        blank="_", max_steps=10_000):
    if (type(max_steps) is not int
            or max_steps < 0):
        raise ValueError("invalid cap")
    tape = dict(enumerate(w))
    s, head, steps = start, 0, 0
    while s not in halt:
        if steps == max_steps:
            return "timeout", steps, tape
        sym = tape.get(head, blank)
        if (s, sym) not in delta:
            # no rule: implicit reject
            return "reject", steps, tape
        write, move, s = delta[(s, sym)]
        tape[head] = write
        if move not in {"L", "R"}:
            raise ValueError("invalid move")
        head += 1 if move == "R" else -1
        steps += 1
    return s, steps, tape

INC = {
  ("R", "0"): ("0", "R", "R"),
  ("R", "1"): ("1", "R", "R"),
  ("R", "_"): ("_", "L", "C"),
  ("C", "1"): ("0", "L", "C"),
  ("C", "0"): ("1", "L", "H"),
  ("C", "_"): ("1", "L", "H"),
}
s, n, tape = run(INC, "1011", "R", {"H"})
print("".join(tape[i] for i in
              sorted(tape)).strip("_"), n)
# 1100 8
```

Notice the `max_steps` guard. If the simulation times out, you know only that it did not halt within that budget; the timeout alone does not settle eventual halting. You will meet that problem again.

## Example 2: aⁿbⁿcⁿ, beyond any PDA

The last lesson proved aⁿbⁿcⁿ is not context-free. A TM decides it easily by **crossing off**: on each pass, mark one a as X, one b as Y and one c as Z, then return to the left.

```
q0: a→X R q1 | Y→R q4 | _→accept
q1: skip a,Y right; b→Y R q2
q2: skip b,Z right; c→Z L q3
q3: skip a,b,Y,Z left; X→R q0
q4: skip Y,Z right; _→accept
anything else: reject
```

Trace on `aabbcc` (one pass shown):

```
aabbcc → Xabbcc → XaYbcc
→ XaYbZc  then back left to X
→ XXYYZc → XXYYZZ
q0 sees Y → q4 checks only Y,Z
→ blank: accept
```

```python
ABC = {
 ("q0","a"):("X","R","q1"),
 ("q0","Y"):("Y","R","q4"),
 ("q0","_"):("_","R","acc"),
 ("q1","a"):("a","R","q1"),
 ("q1","Y"):("Y","R","q1"),
 ("q1","b"):("Y","R","q2"),
 ("q2","b"):("b","R","q2"),
 ("q2","Z"):("Z","R","q2"),
 ("q2","c"):("Z","L","q3"),
 ("q3","X"):("X","R","q0"),
 ("q4","Y"):("Y","R","q4"),
 ("q4","Z"):("Z","R","q4"),
 ("q4","_"):("_","R","acc"),
}
for sym in "abYZ":     # q3 sweeps left
    ABC[("q3", sym)] = (sym, "L", "q3")

for w in ["abc", "aabbcc", "aabbc",
          "abcabc", "aaabbbccc"]:
    r = run(ABC, w, "q0", {"acc"})
    print(w, r[0], r[1])
# abc acc 8
# aabbcc acc 23
# aabbc reject 13
# abcabc reject 7
# aaabbbccc acc 46
```

Each pass walks across the string, and there are n passes, so the machine takes **O(n²)** steps (8, 23, 46 for n = 1, 2, 3). A two-tape TM could do it in O(n): copy the a's to tape 2, then match them against the b's and c's.

## Robustness: the variants are all equivalent

The definition seems arbitrary. Why one tape? Why not stay put? The remarkable fact is that the reasonable variants all recognise exactly the same languages:

| Variant | Simulated by 1-tape TM |
|---|---|
| Stay-put moves | trivially (R then L) |
| Two-way infinite tape | fold it in half |
| A fixed number k of tapes | Standard O(t²) simulation when t ≥ input length |
| Nondeterministic | Fair search; exponential upper bound in a branch-time bound |
| RAM with suitable bit-cost or bounded-word operations | polynomial slowdown |

The multi-tape simulation stores all k tapes on one, separated by markers, with a dot over each simulated head. Each simulated step sweeps the used tape once, which is O(t) cells after t steps, giving O(t²) total.

Nondeterministic TMs are simulated by trying all branches **breadth-first**. Depth-first would be wrong: it could follow an infinite branch forever while an accepting branch sits elsewhere. This matters for power, not just speed. This simulation establishes an upper bound, not a proof that exponential slowdown is necessary. Whether every language accepted in nondeterministic polynomial time has a deterministic polynomial-time decider is P versus NP.

## The busy beaver: how strange small machines get

For the standard two-way tape, two-symbol busy-beaver model, count n working states separately from a halt state. Among machines that halt from a blank tape, which runs longest? That maximum step count is the **busy beaver** number S(n). The 2-state champion:

```python
BB2 = {
  ("A", "0"): ("1", "R", "B"),
  ("A", "1"): ("1", "L", "B"),
  ("B", "0"): ("1", "L", "A"),
  ("B", "1"): ("1", "R", "H"),
}
s, n, tape = run(BB2, "", "A", {"H"},
                 blank="0")
ones = sum(v == "1" for v in tape.values())
print(n, ones)   # 6 4
```

| n | S(n) steps | Σ(n) ones |
|---|---|---|
| 2 | 6 | 4 |
| 3 | 21 | 6 |
| 4 | 107 | 13 |
| 5 | 47,176,870 | 4,098 |

S(5) was only proved in 2024, by the online bbchallenge collaboration with a Coq-verified proof. Doing so meant showing that every one of the many millions of 5-state machines either halts within 47,176,870 steps or never halts. The proof combines exhaustive reduction of machine cases with certified reasoning about non-halting.

> [!note] Evidence gap
> The previous unspecific claim about six-state machines encoding open Collatz-like problems is omitted: no particular machine, encoding convention and unresolved mathematical statement were identified for verification.

S(n) eventually exceeds every total computable function of n. This stronger growth theorem needs a separate argument. Its uncomputability follows from a simpler observation: if you could compute S(n), you could decide blank-tape halting for an n-state machine by running it for S(n) steps. An arbitrary finite input can be built into a machine’s finite control.

## Why this model, when no one builds one

Turing-machine notation is mainly a mathematical and educational model rather than an ordinary application language. The model's value is that it is **simple enough to prove things about** and **expressive enough to model effective computation**. A modern CPU is a finite-state machine (registers, caches) attached to a large memory. With an effective instruction set and suitably costed operations, unbounded memory gives a model equivalent in computability to a TM; polynomial simulation claims also require an appropriate cost model. So a theorem like "no TM can decide X" becomes "no effective procedure can decide X for all inputs in the unbounded model", using the Church–Turing thesis.

## Pitfalls

- **Reject is not loop.** A recogniser may never answer "no". If you want a decider, you must prove it halts on every input.
- **The tape is infinite, but each halting run uses finitely much.** In t single-cell moves the head visits at most t + 1 cells; counting initially stored input as well gives at most |input| + t + 1 cells involved.
- **Implicit reject** (no matching rule) is a common convention, as in the simulator above. Be clear which convention a textbook uses.

## Key takeaways
- A TM is a finite control plus an unbounded read-write tape; transitions read/write a symbol and move one cell, with no outgoing transitions from halting states.
- On each input it accepts, rejects or loops. Deciders always halt; recognisers need only accept the right strings.
- TMs decide non-context-free languages like aⁿbⁿcⁿ by crossing off symbols in O(n²) steps.
- Multi-tape, nondeterministic and RAM variants all recognise the same languages; only running time changes.
- Busy beaver values explode (S(5) = 47,176,870) and S(n) is uncomputable.

## Further reading
- [Turing machine (Wikipedia)](https://en.wikipedia.org/wiki/Turing_machine)
- [Turing machines (Stanford Encyclopedia of Philosophy)](https://plato.stanford.edu/entries/turing-machine/)
- [Busy beaver (Wikipedia)](https://en.wikipedia.org/wiki/Busy_beaver)
- [The Busy Beaver Challenge (bbchallenge.org)](https://bbchallenge.org/)
- [Recursively enumerable language (Wikipedia)](https://en.wikipedia.org/wiki/Recursively_enumerable_language)

- [Determination of the fifth Busy Beaver value — proof authors](https://arxiv.org/abs/2509.12337)
