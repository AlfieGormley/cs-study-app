---
id: cx-master-limits
sourceLesson: cx-recurrences
title: When the Master Theorem does not fit
level: advanced
minutes: 5
summary: Recognise unsupported recurrences and prove a guessed bound by induction.
---

Here n is the input size. First check a theorem’s assumptions; when they fail, a recursion tree and an explicit induction can provide a different route.

## Where the Master Theorem doesn't apply

**Subtract-and-conquer.** Recurrences where the input shrinks by subtracting rather than dividing aren't of the form a × T(n/b). Unroll them instead:

```formula
T(n) = T(n − 1) + n
T(n) = n + (n − 1) + … + 1
T(n) = n × (n + 1) / 2 = Θ(n^2)
where
T(n): the running time on input size n
n: the input size, which drops by 1 per call
…: "and so on" down to 1
Θ(n^2): Big-Theta of n squared, growing like n × n
In words: each call does work equal to its size and passes on a problem only one smaller, so the work adds up to about half of n squared.
```

Likewise T(n) = 2T(n − 1) + 1 doubles at every level for n levels:

```formula
T(n) = 1 + 2 + 4 + … + 2^{n−1}
T(n) = 2^n − 1 = Θ(2^n)
where
T(n): the number of steps (for Towers of Hanoi, the number of disc moves)
n: the input size (the number of discs)
2^{n−1}: n − 1 copies of 2 multiplied together, the number of calls on the deepest level
2^n: n copies of 2 multiplied together
…: "and so on", doubling each time
Θ: Big-Theta, exactly this rate up to constants
In words: two calls each one size smaller makes the call count double on every one of n levels.
```

For 10 discs that is 1,023 moves; for 64 discs, about 1.8 × 10^19.

**The gap between cases.** T(n) = 2T(n/2) + n / log n has log_b(a) = log_2(2) = 1, so compare f(n) = n / log n with n^1 = n:

```formula
f(n) = n / log(n)
f(n) / n^{1 − ε} = n^ε / log(n) → ∞
f(n) / n = 1 / log(n) → 0
where
f(n): the work outside the recursive calls
n: the input size
log(n): the logarithm of n
ε: epsilon, any fixed positive number
n^ε: n to the power ε, which outgrows log(n) for any ε > 0
→: "tends to", as n grows
∞: infinity, growing without limit
In words: n over log n is bigger than any n^(1 − ε), so case 1 fails, but smaller than n by a log factor, so case 2 (with k ≥ 0) fails too.
```

So it falls between case 1 and case 2 of the standard statement. (The answer is Θ(n log log n), as the later Akra–Bazzi examples show. Some textbooks state an extended case 2 that allows negative k and covers this directly.)

**Uneven splits.** T(n) = T(n/3) + T(2n/3) + n has two subproblems of different sizes. The Master Theorem needs every subproblem to be n/b.

**Non-constant a or b.** T(n) = √n × T(√n) + n (√n is the square root of n) needs other techniques, such as a change of variables: substitute n = 2^m, so that √n = 2^(m/2) and the recurrence becomes one in m.

## Substitution: guess and prove

When no theorem fits, guess the answer (from a recursion tree) and prove it by **mathematical induction**: assume the bound holds for smaller inputs and show it then holds for n. For merge sort, prove T(n) ≤ c × n × log_2(n) for powers of two n ≥ 2, choosing c large enough to cover T(2). Treat T(1) separately, since log_2(1) = 0:

```formula
T(n) = 2 × T(n/2) + n
T(n) ≤ 2 × c × (n/2) × log_2(n/2) + n
T(n) ≤ c × n × (log_2(n) − 1) + n
T(n) ≤ c × n × log_2(n) − c × n + n
T(n) ≤ c × n × log_2(n)   when c ≥ 1
where
T(n): merge sort's running time on n items
n: the input size, a power of 2 of at least 2
c: the constant in the guessed bound, chosen once and kept fixed
log_2(n): the base-2 logarithm of n; log_2(n/2) = log_2(n) − 1
≤, ≥: less than or equal to, greater than or equal to
In words: assuming the bound for half-size inputs, the bound for size n follows with the same c, as long as c is at least 1.
```

The second line uses the assumption for n/2; the last line drops − c × n + n, which is at most 0 when c is at least 1.

> [!warning] The classic induction bug
> "Guess T(n) = O(n). Then T(n) = 2T(n/2) + n ≤ 2c(n/2) + n = cn + n = O(n)." This is wrong. You must prove the *exact* form T(n) ≤ c × n with the same constant c, and c × n + n is not ≤ c × n. Hiding constants inside O during an induction lets you "prove" anything.

## Key takeaways
- Subtracting from input size, uneven splits and some gap functions need other techniques.
- A substitution proof must preserve the same chosen constant through the induction.
- A loose asymptotic simplification inside the proof does not establish the required inequality.

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Akra–Bazzi method — Wikipedia](https://en.wikipedia.org/wiki/Akra%E2%80%93Bazzi_method)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
