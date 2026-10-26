---
id: compu-halting-reductions
title: Reducing acceptance and blank-tape halting
level: advanced
minutes: 3
summary: Replacing rejection with divergence reduces acceptance to halting.
sourceLesson: compu-reductions-rice
---

## From acceptance to halting

The input is ⟨M, w⟩. Build a machine M′ that halts exactly when M accepts w:

```
M′(x):
  run M on x
  if M accepts: accept (halt)
  if M rejects: loop forever
```

Map ⟨M, w⟩ to ⟨M′, w⟩. Then:

- If M accepts w, the edited machine halts on w.
- If M rejects w, the edited machine loops on w.
- If M loops on w, the edited machine also loops on w.

```formula essential
f(⟨M, w⟩) = ⟨M′, w⟩
⟨M, w⟩ ∈ A_TM  ⇔  ⟨M′, w⟩ ∈ HALT_TM
where
f: the mapping reduction, a total computable function on encodings
M: any Turing machine
M′: M-prime, the edited copy of M built by the mapping reduction
w: any input string
⟨M, w⟩: angle brackets: one string encoding a machine and an input
A_TM: the acceptance problem: pairs where M accepts w
HALT_TM: the halting problem: pairs where the machine halts on w
∈: is a member of
⇔: if and only if
In words: M accepts w exactly when the edited machine M′ halts on w, so a halting decider would decide acceptance.
```

The function f is computable: it just edits the machine’s transition rules, it never *runs* M. Programs that build programs are the whole technique. In Python, with a "machine" as a function that returns True (accept), False (reject) or never returns:

```python
def f(M, w):
    # A_TM ≤ₘ HALT_TM
    def M2(x):
        if M(x):        # may never return
            return True # accepted: halt
        while True:     # rejected: hang
            pass
    return M2, w        # build, don't run
```

## Example 2: the blank-tape halting problem

```formula essential
HALT_ε = { ⟨M⟩ : M(ε)↓ }
f(⟨M, w⟩) = ⟨M_w⟩
where
HALT_ε: the blank-tape halting problem
M: any Turing machine
⟨M⟩: angle brackets: the encoding of M as a string
ε: epsilon, the empty input, so the tape starts blank
M(ε)↓: M, started on a blank tape, eventually halts
f: the mapping reduction from HALT_TM, a total computable function
w: any input string
M_w: a new machine that erases its input, writes w, then runs M
In words: HALT_ε holds the machines that halt when started on a blank tape; the map f sends ⟨M, w⟩ to ⟨M_w⟩, and M_w halts on blank input exactly when M halts on w.
```

Reduce HALT_TM to it. Given ⟨M, w⟩, build M_w, which erases its input, writes w on the tape, then runs M. M_w halts on blank input (indeed on any input) iff M halts on w. In Python: `lambda _: M(w)`.

This is the problem the busy beaver function would solve, which is why S(n) is uncomputable.

## Key takeaways

- Replacing rejection with divergence reduces acceptance to halting.
- Embedding an input in a new finite machine reduces arbitrary-input halting to blank-tape halting.
- The map emits a machine description without waiting for the simulated run.

## Further reading

- [Lynch: mapping reductions and Rice’s theorem](https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/resources/mit6_045js11_lec09/)
