---
id: cplx-input-cost
title: "Decision problems and input cost"
level: basic
minutes: 4
summary: "Measure input size in bits, so large values can have short encodings."
sourceLesson: cplx-p-np
---

Computability asks whether a problem can be solved by an algorithm at all. **Complexity theory** asks a sharper question: how much time or memory does it take, as the input grows?

The headline result of the field is a question nobody has answered. Is every problem whose solutions are easy to **check** also easy to **solve**? That is the **P vs NP** problem, and this lesson sets up exactly what it means.

## Measuring cost

Three conventions make the theory work.

1. **Decision problems.** We mostly study yes/no questions: "does this graph have a route of length at most 100?" rather than "find the shortest route". A yes/no problem is just a set of inputs (a **formal language**) whose answer is yes.
2. **Input size n is measured in bits.** A positive integer takes roughly its base-two logarithm in bits to write down; its numeric value is not its encoded length.
3. **Worst case, asymptotically.** We count the steps an algorithm takes on its *worst* input of a given size, and only care how that count grows as the size grows.

Convention 2 in symbols: the number of bits needed to write a whole number grows with its logarithm, not with its value.

```formula
b ≈ log_2(N)
b ≈ log_2(1000) ≈ 10 bits   for N = 1000
where
b: the number of bits (binary digits) needed to write the number down
N: the number itself, a positive whole number
log_2: logarithm base 2: log_2(N) is the power you must raise 2 to in order to get N, so log_2(1024) = 10
≈: approximately equal to (the exact count is log_2(N) rounded down, plus 1)
bits: the unit of the result: binary digits, each 0 or 1
In words: a number about a thousand needs only about 10 bits. Doubling N adds just one bit, so an input's size in bits can be tiny compared with the values written in it.
```

Convention 3 in symbols is **Big O** notation. It is how the rest of this module states running times.

```formula
T(n) = O(f(n))   means
T(n) ≤ cf(n)   for all n ≥ n_0
where
T(n): the worst-case number of steps the algorithm takes on any input of n bits
n: the input size, in bits
f(n): the growth benchmark function, such as n^2 or 2^n
O(f(n)): Big O of f(n): "grows at most as fast as a constant times f(n), once n is large enough"
c: a fixed positive constant that does not depend on n
n_0: a threshold size; the bound only has to hold for inputs at least this big
≤: is less than or equal to
≥: is greater than or equal to
In words: the running time is O(f(n)) when, beyond some input size, it never exceeds a fixed constant times f(n). An algorithm that takes 3 × n^2 + 5 × n steps is O(n^2), because with c = 4 the bound holds for every n ≥ 5.
```

Big O ignores constant factors and small inputs on purpose: it describes the shape of the growth, not the exact time on a particular machine.

For problems such as integer-weight TSP with a known finite cost range, a threshold decision procedure lets you recover the optimum cost by binary search. Each answer halves the remaining range: costs from zero to one million require at most twenty calls. This uses a polynomial number of calls when the cost bound has polynomial bit length. Finding an actual solution additionally needs a suitable self-reduction; the statement is not a universal equivalence for arbitrary optimisation problems.

## Key takeaways

- Measure input size in bits, so large values can have short encodings.
- Big O bounds eventual worst-case growth, ignoring fixed factors.
- Binary search can recover an integer optimum cost from a threshold decision procedure.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
