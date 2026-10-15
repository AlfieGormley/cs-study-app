---
id: compu-tm-increment
title: Tracing and simulating binary increment
level: intermediate
minutes: 3
summary: Binary increment scans right and propagates a carry back through trailing ones.
sourceLesson: compu-turing-machines
---

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
    # Unstored positions contain the blank.
    tape = dict(enumerate(w))
    s, head, steps = start, 0, 0
    while s not in halt:
        if steps == max_steps:
            return "timeout", steps, tape
        sym = tape.get(head, blank)
        if (s, sym) not in delta:
            # no rule: implicit reject
            return "reject", steps, tape
        # Apply exactly one transition.
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

Notice the `max_steps` cap. If the simulation reaches that cap, you know only that it did not halt within that budget; the timeout alone does not settle eventual halting. You will meet that problem again.

## Key takeaways

- Binary increment scans right and propagates a carry back through trailing ones.
- A dictionary keyed by tape position models the finitely visited portion of an unbounded tape.
- A simulation timeout establishes only that the budget was exceeded.

## Further reading

- [Sipser: TM variants and the Church–Turing thesis](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec6-1/)
