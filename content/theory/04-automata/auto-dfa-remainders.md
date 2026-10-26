---
id: auto-dfa-remainders
title: Recognising binary remainders
level: basic
minutes: 4
sourceLesson: auto-dfa
summary: Appending a bit doubles a binary value and adds the bit; remainders can be updated directly.
---

## Remember the remainder, not the number

Read a binary number left to right, most significant bit first. Appending a bit to the right of a binary number doubles its value and adds the new bit, just as appending a digit in decimal multiplies by 10 and adds it. The machine cannot store the whole value, which grows without limit, but it does not need to: the remainder after dividing by 3 can be updated from the old remainder alone.

```formula essential
r′ = (2r + b) mod 3
where
r: the remainder of the binary prefix after division by three, initially zero
b: the next bit read, 0 or 1
r′: the new remainder, one of zero, one and two
mod: the remainder after whole-number division, so 7 mod 3 = 1 and 9 mod 3 = 0
In words: the new remainder depends only on the old remainder and the new bit, never on the full value. So three states, one per possible remainder (0, 1 or 2), are enough.
```

For example, after reading `100` the value is 4 and the remainder is 1. Reading a 1 doubles four and adds one, giving nine. Updating just the remainder doubles one and adds one, giving three and therefore remainder zero: the same answer, because nine is divisible by three. This works because multiples of 3 contribute nothing to a remainder after doubling, so they can be thrown away at every step.

| Remainder | on 0 | on 1 |
|---|---|---|
| → 0 (accept) | 0 | 1 |
| 1 | 2 | 0 |
| 2 | 1 | 2 |

Trace `1001` using the table: the remainders are 0, 1, 2, 1, 0. The final remainder is zero, so the machine accepts. There is no need to convert the whole input to an integer first, even when it is too long to fit in a fixed-width integer.

And `101` (5) goes 0 → 1 → 2 → 2, ending in 2: reject. The same trick builds a DFA for "divisible by k" with k states, in any base.

> [!note] What about the empty string?
> This DFA accepts the empty string, because the start state is accepting. Whether the empty string "is divisible by 3" is a design decision. If you want to reject it, add a separate start state. Edge cases like this are where hand-built automata most often go wrong.

## Running a DFA in Python

A DFA is just a lookup table and a loop. This is the whole simulator:

```python
def run_dfa(delta, start, accept, w):
    # Reset each independent membership run.
    q = start
    for c in w:
        if (q, c) not in delta:
            return False   # no move: reject
        # Keep only the state for this
        # prefix.
        q = delta[(q, c)]
    # Acceptance is tested after all input.
    return q in accept

# Store only each prefix remainder.
D3 = {(r, b): (2 * r + int(b)) % 3
      for r in range(3) for b in "01"}

print(run_dfa(D3, 0, {0}, "1001"))  # True
print(run_dfa(D3, 0, {0}, "101"))   # False
```

The cost is O(n) time for a string of length n, for a fixed machine with O(1) transition lookup, using constant auxiliary state storage beyond the stored machine and input. That is the defining property of finite automata and the reason they are used for high-throughput scanning: they never need to look back, buffer or backtrack.

## Key takeaways
- Appending a bit doubles a binary value and adds the bit; remainders can be updated directly.
- The remainder construction gives a sufficient state count, which may shrink through equivalent states.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
