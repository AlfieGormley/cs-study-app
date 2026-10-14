---
id: cx-master-limits
sourceLesson: cx-recurrences
title: When the Master Theorem does not fit
level: advanced
minutes: 5
summary: Recognise unsupported recurrences and prove a guessed bound by induction.
---

Here n is input size. Check the theorem’s assumptions first; otherwise use a recursion tree and induction.

## Where the Master Theorem doesn't apply

**Subtract-and-conquer.** Subtracting from input size fails the required equal-fraction split. Unroll instead:

```formula
T(n) = T(n − 1) + n
T(n) = n + (n − 1) + … + 1
T(n) = n × (n + 1) / 2 = Θ(n^2)
T(0) = 0
where
T(n): counted scan work with zero cost at size zero
n: input item count, decreasing by one per call
…: "and so on" down to 1
Θ: a tight growth bound, up to constant factors
In words: size-proportional work across inputs decreasing by one sums to about half the squared input.
```

Two calls one item smaller plus a constant outside step double work per level:

```formula
T(n) = 1 + 2 + 4 + … + 2^{n−1}
T(n) = 2^n − 1 = Θ(2^n)
T(n) = 2T(n − 1) + 1
T(0) = 0
where
T(n): step count, here Towers of Hanoi disc moves
n: disc count
…: "and so on", doubling each time
Θ: Big-Theta, exactly this rate up to constants
In words: two calls one size smaller double the call count on each level.
```

For 10 discs that is 1,023 moves; for 64 discs, about 1.8 × 10^19.

**The gap between cases.** With critical exponent one, outside work is smaller by a logarithm instead of a fixed positive power:

```formula
f(n) = n / log(n)
f(n) / n^{1 − ε} = n^ε / log(n) → ∞
f(n) / n = 1 / log(n) → 0
T(n) = 2T(n/2) + n/log(n)
a = 2, b = 2, c = log_2(2) = 1
where
f(n): outside-call work, in steps
n: the input size
log: the base-two logarithm
ε: epsilon, any fixed positive number
→: "tends to", as n grows
∞: infinity, growing without limit
T(n): the recurrence’s running time
a: the number of child calls
b: the shrink factor
c: the critical exponent
log_2: the base-2 logarithm
In words: outside work exceeds every fixed sublinear power, failing case 1; its logarithmic deficit also fails standard case 2.
```

So it falls between case 1 and case 2 of the standard statement. (The answer is Θ(n log log n), as the later Akra–Bazzi examples show. Some textbooks state an extended case 2 that allows negative k and covers this directly.)

**Uneven splits.** Different-size children fail the equal-size assumption.

**Non-constant branching or shrink factors.** Square-root-sized children with square-root branching need another technique. Rewriting input as a power of two halves its exponent:

```formula
T(n) = T(n/3) + T(2n/3) + n
T(n) = √(n) T(√(n)) + n
n = 2^m, √(n) = 2^{m/2}
where
T(n): the cost in each independent recurrence
n: the input size
m: the exponent used as the transformed input
√: the nonnegative square root
In words: unequal fractions fail equal splitting. The square-root example has size-dependent parameters; the exponent substitution turns its split into halving.
```

## Substitution: guess and prove

When no theorem fits, guess from a recursion tree and prove the bound by **mathematical induction**. For merge sort on powers of two, start at two items and choose a fixed multiplier covering that base case. Handle one item separately: its logarithm is zero:

```formula
T(n) = 2T(n/2) + n
T(n) ≤ 2c(n/2)log_2(n/2) + n
T(n) ≤ cn(log_2(n) − 1) + n
T(n) ≤ cn log_2(n) − cn + n
T(n) ≤ cn log_2(n)   when c ≥ 1
log_2(1) = 0
where
T(n): merge sort step count
n: a power-of-two input of at least 4 in the inductive step; size 2 is the base case
c: one fixed positive multiplier in the guessed bound
log_2: the base-two logarithm
≤, ≥: less than or equal to, greater than or equal to
In words: assuming the bound for half-size inputs, the bound for size n follows with the same c, as long as c is at least 1.
```

The second line assumes the bound for half-size input. The final subtraction cancels the added linear work because the fixed multiplier is at least one.

> [!warning] The classic induction bug
> A linear growth class does not prove the same fixed multiplier works. The failed step increases the coefficient; hiding it inside Big-O incorrectly makes the induction appear to close.

```formula
T(n) = 2T(n/2) + n
T(n) ≤ 2c(n/2) + n = cn + n
cn + n = O(n)
cn + n > cn for n > 0
where
T(n): step count under the attempted linear bound
n: the positive input size
c: one fixed positive multiplier used in the induction
O: an eventual upper growth bound
>: greater than
In words: the expression has linear growth, but the same fixed multiplier cannot absorb its extra linear term.
```

## Key takeaways
- Subtracting from input size, uneven splits and some gap functions need other techniques.
- A substitution proof must preserve the same chosen constant through the induction.
- A loose asymptotic simplification inside the proof does not establish the required inequality.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Akra–Bazzi method — Wikipedia](https://en.wikipedia.org/wiki/Akra%E2%80%93Bazzi_method)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
