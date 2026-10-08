---
id: cx-recurrences
title: Recurrences and the Master Theorem
level: advanced
minutes: 20
summary: Turning recursive code into recurrences, solving them with recursion trees, the three cases of the Master Theorem, where it fails, and the Akra–Bazzi generalisation for uneven splits.
---

Loops can be analysed by counting. Recursive algorithms, especially **divide and conquer** (split the problem, solve the pieces recursively, combine), need a different tool. Their running time is naturally described by a **recurrence**: an equation that defines T(n), the running time on an input of size n, in terms of T on smaller inputs.

This lesson is about writing those recurrences and solving them quickly. Throughout, n is the input size, O, Ω and Θ are the upper, lower and tight bounds from lesson 2, and log n is the base-2 logarithm of n unless another base is written.

## From code to recurrence

Every recursive function's cost splits into the calls it makes and the work it does itself:

```formula
T(n) = r × T(m) + w(n)
where
T(n): the running time on an input of size n, in basic steps
r: how many recursive calls one call makes
T(m): the running time of one recursive call
m: the input size each recursive call gets, smaller than n
w(n): the work one call does outside its recursive calls (splitting, comparing, merging)
n: the input size of the current call
In words: the cost of a call is the cost of all the calls it makes, plus the work it does itself.
```

```python
def bsearch(a, t, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if a[mid] == t:
        return mid
    if a[mid] < t:
        return bsearch(a, t, mid + 1, hi)
    return bsearch(a, t, lo, mid - 1)
```

Binary search makes one recursive call on half the range, plus a constant amount of work (O(1)). Merge sort calls itself on two halves and merges in linear time:

```formula
T_bs(n) = T_bs(n / 2) + O(1)
T_ms(n) = 2 × T_ms(n / 2) + Θ(n)
where
T_bs(n): the running time of binary search on a range of n items
T_ms(n): the running time of merge sort on n items
n: the input size
O(1): at most a constant amount of work, however large n is
Θ(n): work proportional to n (the merge step touches every item once)
In words: binary search does a constant amount of work and then searches one half; merge sort sorts both halves and then does a linear merge.
```

Some common recurrences and their solutions (the first column is T(n), shorthand for "T(n) = this expression"; 2^n is 2 multiplied by itself n times):

| Recurrence | Example | Solution |
|---|---|---|
| T(n/2) + 1 | binary search | Θ(log n) |
| T(n/2) + n | halving + scan | Θ(n) |
| 2T(n/2) + 1 | tree traversal | Θ(n) |
| 2T(n/2) + n | merge sort | Θ(n log n) |
| T(n-1) + 1 | linear recursion | Θ(n) |
| T(n-1) + n | selection sort | Θ(n^2) |
| 2T(n-1) + 1 | Towers of Hanoi | Θ(2^n) |

You'll be able to derive all of them by the end of the lesson. The **base case** (such as T(1) = Θ(1), the cost when the input is too small to split) is almost always constant, so it is usually left implicit. Floors and ceilings (n/2 versus n/2 rounded up) don't change the asymptotic answer, so we ignore them too.

## The recursion tree

The most intuitive method is to draw the tree of calls and add up the work at each level. For merge sort, T(n) = 2T(n/2) + n:

```
level 0:        n                 = n
             /     \
level 1:   n/2     n/2            = n
          /  \     /  \
level 2: n/4 n/4  n/4 n/4         = n
          ...
level k: 2^k nodes of n/2^k       = n
          ...
leaves:  n nodes of size 1        = n
```

Each level does n work in total, and the size halves at each level. Add the levels:

```formula
W_k = 2^k × (n / 2^k) = n
L = log_2(n) + 1
T(n) = L × n = Θ(n × log n)
where
W_k: the total work done on level k of the tree
k: the level number, 0 at the root
2^k: the number of calls on level k (it doubles each level)
n / 2^k: the input size of each call on level k
n: the input size of the original call
L: the number of levels, from size n down to size 1
log_2(n): the base-2 logarithm of n, the number of halvings from n to 1
T(n): the total running time
Θ: Big-Theta, a tight bound up to constant factors
log: logarithm (base 2 here; the base only changes a constant)
In words: every level does n work, and halving takes log_2(n) steps to reach size 1, so the total is about n log n.
```

For n = 1,024 that is 11 levels of 1,024 work each, about 11,000 steps. Total: **Θ(n log n)**.

Now try T(n) = 3T(n/2) + n (the shape of Karatsuba's multiplication algorithm). The work per level now changes from level to level:

```formula
W_k = 3^k × (n / 2^k) = n × (3/2)^k
leaves = 3^{log_2(n)} = n^{log_2(3)}
n^{log_2(3)} ≈ n^{1.585}
where
W_k: the total work on level k
k: the level number, 0 at the root
3^k: the number of calls on level k (it triples each level)
n / 2^k: the input size of each call on level k
(3/2)^k: 1.5 multiplied by itself k times
leaves: the number of calls at the bottom level, size 1
log_2(n): the base-2 logarithm of n, the depth of the tree
log_2(3): the base-2 logarithm of 3, about 1.585
n: the input size
≈: approximately equal to
In words: each level does 1.5 times the work of the level above, so the bottom level, with n^1.585 tiny calls, outweighs everything above it.
```

The second line uses the identity a^(log_b n) = n^(log_b a): both sides equal b to the power log_b(a) × log_b(n) (here b = 2 and a = 3). A *growing* geometric series is dominated by its **last** term, the leaves, so T(n) = Θ(n^(log_2 3)), an exponent of about 1.585.

And T(n) = 2T(n/2) + n^2:

```formula
W_k = 2^k × (n / 2^k)^2 = n^2 / 2^k
T(n) ≤ n^2 × (1 + 1/2 + 1/4 + …) = 2 × n^2
where
W_k: the total work on level k
k: the level number, 0 at the root
2^k: the number of calls on level k
n / 2^k: the input size of each call on level k
n^2: n squared, n × n, the root's own work
T(n): the total running time
…: "and so on", halving each time
≤: less than or equal to
In words: each level does half the work of the level above, so the whole tree costs less than twice the root.
```

The work *shrinks* by half per level. A shrinking geometric series is dominated by its **first** term, the root: T(n) = Θ(n^2).

These three behaviours are the whole idea behind the Master Theorem.

> [!tip] The three shapes
> - Work per level **shrinks** geometrically: the root dominates. T(n) = Θ(f(n)), where f(n) is the root's own work.
> - Work per level is **equal**: multiply one level by the number of levels, log n.
> - Work per level **grows** geometrically: the leaves dominate. T(n) = Θ(number of leaves).

## The Master Theorem

The Master Theorem solves recurrences of this shape, where every recursive call gets the same fraction of the input:

```formula
T(n) = a × T(n / b) + f(n)
a ≥ 1,  b > 1
where
T(n): the running time on an input of size n
a: the number of recursive calls (subproblems) each call makes; a constant of at least 1
b: the factor by which the input shrinks; each subproblem has size n / b; a constant greater than 1
f(n): the work done in one call outside its recursive calls (splitting and combining)
n: the input size
≥: greater than or equal to
In words: a call splits its input into a pieces of size n / b, recurses on each, and does f(n) work of its own.
```

The key quantity is the **critical exponent**. It comes from counting the leaves of the recursion tree:

```formula
depth = log_b(n)
leaves = a^{log_b(n)} = n^{log_b(a)}
c = log_b(a)
where
depth: the number of levels before the input size reaches 1 (n divided by b that many times)
log_b(n): the logarithm of n to base b, the power you raise b to in order to get n
leaves: the number of size-1 calls at the bottom of the tree
a: the number of subproblems per call
b: the shrink factor
n: the input size
c: the critical exponent, log_b(a): the power you raise b to in order to get a
log_b(a): the logarithm of a to base b
In words: the tree branches a ways at each of log_b(n) levels, which makes n^c leaves; n^c is the total cost of the leaf level.
```

The leaf level costs n^c in total, and the root costs f(n). The theorem compares them. Each case says which end of the tree wins.

**Case 1: f is polynomially smaller than n^c.** The leaves dominate:

```formula
f(n) = O(n^{c − ε})  for some ε > 0
T(n) = Θ(n^c)
where
f(n): the work outside the recursive calls
n: the input size
c: the critical exponent, log_b(a)
ε: epsilon, some fixed positive number, however small (0.1 will do if it works)
O: Big-O, at most a constant times
Θ: Big-Theta, exactly this rate up to constants
T(n): the running time on input size n
In words: if the root's work is smaller than the leaf count by at least a fixed power of n, the leaves dominate and the answer is the number of leaves.
```

**Case 2: f is about the same as n^c.** Every level does roughly equal work, so you multiply by the number of levels, which adds a log factor:

```formula
f(n) = Θ(n^c × (log n)^k)  for some k ≥ 0
T(n) = Θ(n^c × (log n)^{k+1})
where
f(n): the work outside the recursive calls
n: the input size
c: the critical exponent, log_b(a)
log: the logarithm (any fixed base; it only changes a constant)
k: a fixed number of at least 0; k = 0 is the common case, f(n) = Θ(n^c)
Θ: Big-Theta, exactly this rate up to constants
T(n): the running time on input size n
≥: greater than or equal to
In words: if the root's work matches the leaf count (up to log factors), every level costs about the same and the answer gains one more log factor.
```

(Levels are exactly equal only when k = 0; for larger k, summing the slowly changing level costs still adds one log power.)

**Case 3: f is polynomially larger than n^c**, *and* a **regularity condition** holds. Then the root dominates:

```formula
f(n) = Ω(n^{c + ε})  for some ε > 0
a × f(n / b) ≤ q × f(n),  q < 1
T(n) = Θ(f(n))
where
f(n): the work outside the recursive calls
f(n / b): the work outside the calls in one child call
a: the number of subproblems
b: the shrink factor
n: the input size (the regularity inequality must hold for all large n)
c: the critical exponent, log_b(a)
ε: epsilon, some fixed positive number
q: some fixed constant below 1 (written k in some textbooks)
Ω: Big-Omega, at least a constant times
Θ: Big-Theta, exactly this rate up to constants
T(n): the running time on input size n
≤: less than or equal to
In words: if the root's work beats the leaf count by a fixed power of n, and the children together always do a fixed fraction less work than their parent, the root's own work dominates.
```

The regularity condition says that the work really does shrink from one level to the next. It holds automatically for ordinary polynomial f, such as f(n) = n^2 with a = 2, b = 2 (two children do 2 × (n/2)^2 = n^2 / 2, half the parent's work); it exists to rule out pathological, wildly oscillating functions.

### The simple version

Most recurrences you'll meet have f(n) = Θ(n^d), a plain power of n. Then just compare d with log_b(a):

```formula
T(n) = a × T(n / b) + Θ(n^d)
where
T(n): the running time on input size n
a: the number of subproblems
b: the shrink factor; each subproblem has size n / b
d: the power of n in the outside work, a constant of at least 0 (d = 1 for a linear merge)
n: the input size
Θ: Big-Theta, exactly this rate up to constants
In words: the special case where the work outside the calls is a simple power of n, which covers almost every textbook recurrence.
```

| Compare | Result |
|---|---|
| d < log_b a | Θ(n^(log_b a)) |
| d = log_b a | Θ(n^d log n) |
| d > log_b a | Θ(n^d) |

Equivalently, compare a with b^d: the ratio a / b^d is exactly how fast the work per level grows. Above 1, the leaves win; equal to 1, every level ties; below 1, the root wins.

### Worked examples

In the table, the first column is the right-hand side of T(n) = …, and log_b a is the critical exponent:

| Recurrence | a, b | log_b a | f | Case | T(n) |
|---|---|---|---|---|---|
| T(n/2) + 1 | 1, 2 | 0 | 1 | 2 | log n |
| 2T(n/2) + n | 2, 2 | 1 | n | 2 | n log n |
| 3T(n/2) + n | 3, 2 | 1.585 | n | 1 | n^1.585 |
| 7T(n/2) + n^2 | 7, 2 | 2.807 | n^2 | 1 | n^2.807 |
| 4T(n/2) + n^2 | 4, 2 | 2 | n^2 | 2 | n^2 log n |
| 2T(n/2) + n^2 | 2, 2 | 1 | n^2 | 3 | n^2 |
| T(n/2) + n | 1, 2 | 0 | n | 3 | n |
| 2T(n/2) + n log n | 2, 2 | 1 | n log n | 2, k=1 | n log^2 n |

Here is the Strassen row worked through in full:

```formula
T(n) = 7 × T(n / 2) + Θ(n^2)
c = log_2(7) ≈ 2.807
d = 2 < 2.807
T(n) = Θ(n^{log_2(7)}) ≈ Θ(n^{2.807})
where
T(n): the time to multiply two n-by-n matrices
n: the side length of the matrices
a = 7: seven half-size matrix multiplications per call
b = 2: each subproblem has half the side length
c: the critical exponent, log_b(a)
log_2(7): the base-2 logarithm of 7, about 2.807
d: the power of n in the outside work (adding matrices of side n costs about n^2)
Θ: Big-Theta, exactly this rate up to constants
≈: approximately equal to
In words: the outside work grows more slowly than the leaf count, so case 1 applies and the leaves set the cost at about n^2.807.
```

Two of these are famous. 7T(n/2) + n^2 is **Strassen's** matrix multiplication: by using 7 half-size multiplications instead of 8, it beats the naive Θ(n^3). 3T(n/2) + n is **Karatsuba's** integer multiplication, which uses 3 half-size products instead of 4 and beats the schoolbook Θ(n^2). In both, cutting the number of subproblems lowers log_b(a), which is the exponent that matters in case 1: with 8 products Strassen's recurrence would give log_2(8) = 3, no better than naive.

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
2^{n−1}: 2 multiplied by itself n − 1 times, the number of calls on the deepest level
2^n: 2 multiplied by itself n times
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

So it falls between case 1 and case 2 of the standard statement. (The answer is Θ(n log log n), as Akra–Bazzi shows below. Some textbooks state an extended case 2 that allows negative k and covers this directly.)

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

## Akra–Bazzi: the general case

The **Akra–Bazzi** method handles recurrences with several subproblem sizes under regularity assumptions: nonnegative g with suitable polynomial growth, bounded positive base cases, and sufficiently small perturbations of the subproblem sizes. The smooth polynomial/logarithmic examples here satisfy these conditions. The recurrence looks like this:

```formula
T(n) = g(n) + Σ_{i=1}^{m} a_i × T(b_i × n)
a_i > 0,  0 < b_i < 1
where
T(n): the running time on input size n
g(n): the work done outside the recursive calls (the Master Theorem's f(n))
Σ_{i=1}^{m}: capital sigma, "sum of": add up the term for every kind of subproblem i from 1 to m
m: the number of different subproblem sizes
a_i: how many subproblems of kind i each call makes, a positive constant
b_i: the fraction of n that each subproblem of kind i gets, between 0 and 1
i: which kind of subproblem
n: the input size
In words: a call does g(n) work and recurses on several groups of subproblems, each group with its own count and its own fraction of the input.
```

1. Find the unique p that balances the subproblems' total weight:

```formula
Σ_{i=1}^{m} a_i × (b_i)^p = 1
where
Σ_{i=1}^{m}: "sum of" over every kind of subproblem i from 1 to m
a_i: the number of subproblems of kind i
b_i: the fraction of the input each one gets
(b_i)^p: b_i raised to the power p
p: the unknown exponent being solved for
m: the number of kinds of subproblem
i: which kind
In words: p is the power at which the subproblems' sizes, weighted by how many there are, add up to exactly 1.
```

2. Then:

```formula
T(n) = Θ(n^p × (1 + I))
I = ∫_1^n g(u) / u^{p+1} du
where
T(n): the running time on input size n
n: the input size
p: the balancing exponent from step 1
I: an integral that measures how much the outside work g adds across all scales
∫_1^n … du: the integral from 1 to n with respect to u: the area under the curve between u = 1 and u = n, a continuous version of summing
g(u): the outside work at input size u
u: a stand-in variable for the input size, running from 1 to n
u^{p+1}: u raised to the power p + 1
Θ: Big-Theta, exactly this rate up to constants
In words: start from n^p, the cost if the leaves dominated, and multiply by a correction that grows when the outside work is comparable to or bigger than n^p.
```

The intuition: p plays the role of log_b(a). It is the exponent at which the subproblems' total "weight" exactly balances. Then you compare g with n^p, much like the Master Theorem, but the integral handles the in-between cases smoothly. (It also tolerates small perturbations such as floors and ceilings in the subproblem sizes.)

**Example 1: uneven split.** T(n) = T(n/3) + T(2n/3) + n.

```formula
(1/3)^p + (2/3)^p = 1  gives  p = 1
I = ∫_1^n u / u^2 du = ∫_1^n 1/u du = ln(n)
T(n) = Θ(n × (1 + ln(n))) = Θ(n × log n)
where
p: the balancing exponent; at p = 1 the fractions 1/3 and 2/3 add up to exactly 1
I: the Akra–Bazzi integral
∫_1^n … du: the integral from 1 to n with respect to u, the area under the curve
u: a stand-in for the input size, from 1 to n
ln(n): the natural logarithm of n (base e ≈ 2.718)
log: the logarithm in any base; it differs from ln by a constant factor
T(n): the running time
n: the input size
Θ: Big-Theta, exactly this rate up to constants
In words: the two pieces add up to the whole input, so every level does about n work, and there are about log n levels.
```

The recursion tree agrees: no level does more than n work, the first log_3(n) levels are complete and do exactly n each, and the deepest path (always taking 2/3) has log_{3/2}(n) levels (the logarithm of n to base 1.5). Both counts are Θ(log n).

**Example 2: median of medians.** The linear-time selection algorithm satisfies T(n) = T(n/5) + T(7n/10) + n.

```formula
(1/5)^1 + (7/10)^1 = 0.9 < 1
(1/5)^p + (7/10)^p = 1  gives  p ≈ 0.84
I ≈ n^{1−p} / (1 − p)
T(n) = Θ(n^p × n^{1−p}) = Θ(n)
where
p: the balancing exponent; since the sum is below 1 at p = 1, p must be smaller than 1
I: the Akra–Bazzi integral, here ∫ of u / u^(p+1) = u^(−p) from 1 to n
n^{1−p}: n raised to the power 1 − p
T(n): the running time of median-of-medians selection on n items
n: the input size
Θ: Big-Theta, exactly this rate up to constants
≈: approximately equal to
In words: the two subproblems together are only 90% of the input, so the work per level shrinks geometrically and the root's linear work dominates.
```

**Example 3: the gap case.** T(n) = 2T(n/2) + n / log n. Here p = 1, since 2 × (1/2)^1 = 1:

```formula
I = ∫_2^n 1 / (u × ln(u)) du = ln(ln(n)) + C
T(n) = Θ(n × (1 + ln(ln(n))))
T(n) = Θ(n × log log n)
where
I: the Akra–Bazzi integral with g(u) = u / ln(u) and p = 1
∫_2^n … du: the integral from 2 to n with respect to u, the area under the curve
u: a stand-in for the input size
ln: the natural logarithm (base e ≈ 2.718)
C: a constant from the lower limit, which disappears inside Θ
T(n): the running time
n: the input size
log log n: the logarithm of the logarithm of n, which grows extremely slowly (log_2 log_2 of a billion is about 5)
Θ: Big-Theta, exactly this rate up to constants
In words: the outside work is just a log factor below n, and summed over all levels that adds only a log-log factor.
```

The integral starts at 2 rather than 1 to avoid dividing by ln(1) = 0; the lower limit only changes constants.

## Key takeaways
- Write a recurrence as (number of calls) × T(subproblem size) + (work outside the calls).
- Recursion trees show the three shapes: shrinking levels (root dominates), equal levels (multiply by log n), growing levels (leaves dominate).
- Master Theorem for T(n) = a × T(n/b) + f(n): compare f with n^(log_b a), the number of leaves. Smaller: Θ(n^(log_b a)). Equal: add a log factor. Larger (with regularity): Θ(f).
- Strassen and Karatsuba win by reducing a, the number of subproblems.
- The Master Theorem does not cover T(n − 1) recurrences, uneven splits, or f in the gap between cases.
- Akra–Bazzi finds p with Σ a_i × (b_i)^p = 1 and handles uneven splits like T(n/5) + T(7n/10) + n = Θ(n).

## Further reading
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Akra–Bazzi method — Wikipedia](https://en.wikipedia.org/wiki/Akra%E2%80%93Bazzi_method)
- [Divide-and-conquer algorithm — Wikipedia](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Algorithms by Jeff Erickson, chapter 1: Recursion](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [Strassen algorithm — Wikipedia](https://en.wikipedia.org/wiki/Strassen_algorithm)
- [Karatsuba algorithm — Wikipedia](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
