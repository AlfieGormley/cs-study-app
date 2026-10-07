---
id: disc-inclusion-recurrences
title: Inclusion–exclusion, recurrences and generating functions
level: intermediate
minutes: 15
summary: Counting overlapping cases with inclusion–exclusion, derangements and surjections, setting up and solving recurrences, and using generating functions to turn counting into polynomial multiplication.
---

The basic counting rules break down in two common situations. When cases **overlap**, the sum rule double-counts. When a problem is easiest to describe **in terms of smaller versions of itself**, a direct formula is hard to see. Inclusion–exclusion fixes the first; recurrences fix the second. Generating functions are a power tool that packages a whole sequence into one object, so that counting problems become algebra.

These are also the tools you need to analyse algorithms: recurrences describe the running time of recursive code, and the same "count the ways" reasoning is what dynamic programming computes.

## Inclusion–exclusion

For two sets, adding |A| and |B| counts the overlap twice, so subtract it once:

```
|A ∪ B| = |A| + |B| - |A ∩ B|
```

> [!example] Two sets
> In a team of 30 engineers, 18 know Python, 15 know Java and 8 know both. Those who know at least one: 18 + 15 − 8 = 25. So 5 know neither.

For three sets, subtracting the pairwise overlaps removes the triple overlap one time too many, so add it back:

```
|A ∪ B ∪ C| = |A| + |B| + |C|
            - |A∩B| - |A∩C| - |B∩C|
            + |A∩B∩C|
```

The general pattern alternates: add singles, subtract pairs, add triples, subtract quadruples, and so on. An element that lies in exactly m of the sets gets counted C(m,1) − C(m,2) + C(m,3) − … = 1 time, which is why the formula works.

### Worked example: divisibility

How many integers from 1 to 1000 are divisible by 2, 3 or 5? Let A₂, A₃, A₅ be the multiples. The multiples of both 2 and 3 are the multiples of 6, and so on.

```
|A2| = 500  |A3| = 333  |A5| = 200
|A6| = 166  |A10| = 100 |A15| = 66
|A30| = 33

500 + 333 + 200        = 1033
     - 166 - 100 - 66  =  701
     + 33              =  734
```

So 734 are divisible by at least one, and 1000 − 734 = 266 by none. Each term is one integer division ⌊1000/d⌋ (constant time in a fixed-width arithmetic model), so inclusion–exclusion counts without iterating. The same idea computes Euler's totient φ(n), which you'll meet in the number theory lesson.

### Derangements

A **derangement** is a permutation where nothing stays in its original place: every guest leaves with someone else's coat, or every reviewer gets someone else's pull request.

Let Aᵢ be the permutations that fix item i. Fixing any particular k items leaves (n − k)! permutations of the rest, and there are C(n, k) ways to choose which k. Inclusion–exclusion over "at least one fixed point" gives:

```
D(n) = n! - C(n,1)(n-1)! + C(n,2)(n-2)!
       - ... 
     = n! (1 - 1/1! + 1/2! - ... ± 1/n!)
```

The bracket is the start of the series for e⁻¹, so D(n) is the nearest integer to n!/e for n ≥ 1. The values run 0, 1, 2, 9, 44, 265, … and the probability that a random permutation is a derangement is about 1/e ≈ 36.8%, approaching that limit as n grows; small cases differ substantially, for example D(1)/1! = 0 and D(2)/2! = 1/2.

### Counting onto functions

How many ways can you assign 5 distinct jobs to 3 servers so every server gets at least one? There are 3⁵ assignments in all. Subtract those missing a given server (C(3,1) · 2⁵), add back those missing two (C(3,2) · 1⁵):

```
3^5 - 3*2^5 + 3*1^5
= 243 - 96 + 3 = 150
```

Inclusion–exclusion is the go-to method whenever the condition is "every X is covered" or "no X is bad": count the complement events, which are often easier, and alternate.

## Recurrences

A **recurrence** defines each term of a sequence from earlier terms, plus base cases. Setting one up is often easier than finding a formula directly, because it mirrors how you'd *build* the objects.

### Setting up a recurrence

> [!example] Binary strings with no two adjacent 1s
> Let a(n) count length-n binary strings without "11". Look at the first character. If it's 0, the rest is any valid string of length n − 1. If it's 1, the next must be 0, and then any valid string of length n − 2 follows. So a(n) = a(n−1) + a(n−2), with a(1) = 2 and a(2) = 3. That gives 2, 3, 5, 8, 13, …: the Fibonacci numbers.

The skill is finding the right **first decision** that splits the objects into disjoint cases, each a smaller instance of the same problem. It is exactly the step you take when designing a dynamic-programming solution.

The **Tower of Hanoi** is the classic: to move n discs, move n − 1 out of the way, move the biggest, then move the n − 1 back on top.

```
T(n) = 2 T(n-1) + 1,  T(0) = 0
T: 1, 3, 7, 15, 31, ...
guess T(n) = 2^n - 1
check: 2(2^(n-1) - 1) + 1 = 2^n - 1
```

Guessing a formula from small values and proving it by induction is a perfectly good method.

### Solving linear recurrences

A **linear homogeneous recurrence with constant coefficients** looks like a(n) = c₁a(n−1) + c₂a(n−2). Try a(n) = rⁿ. Substituting and dividing by rⁿ⁻² gives the **characteristic equation**:

```
r^2 = c1 r + c2
```

If it has distinct roots r₁ and r₂, every solution is a(n) = α r₁ⁿ + β r₂ⁿ, with α and β fixed by the base cases.

```
a(n) = 5a(n-1) - 6a(n-2)
a(0) = 2, a(1) = 5

r^2 - 5r + 6 = 0  -> r = 2, 3
a(n) = α 2^n + β 3^n
n=0: α + β   = 2
n=1: 2α + 3β = 5  -> α = 1, β = 1
a(n) = 2^n + 3^n
```

For Fibonacci, r² = r + 1 gives r = (1 ± √5)/2. The larger root is the golden ratio φ ≈ 1.618, so F(n) grows like φⁿ/√5. This is why naive recursive Fibonacci, whose call count obeys a Fibonacci-like recurrence, takes exponential time, and why memoisation reduces it to O(n) additions. Exact Fibonacci values have Θ(n) bits, so this is not a linear bit-complexity bound.

### Divide-and-conquer recurrences

Recursive algorithms that split the input give recurrences of the form T(n) = a T(n/b) + f(n). Merge sort is T(n) = 2T(n/2) + n. Unrolling it:

```
level 0:  n             = n
level 1:  2 * (n/2)     = n
level 2:  4 * (n/4)     = n
...       log2(n) levels
total ≈ n log2 n
```

The **master theorem** packages this: compare f(n) with n^(log_b a). Binary search (a = 1, b = 2, f = 1) is O(log n); merge sort is O(n log n); Karatsuba multiplication (a = 3, b = 2, f = n) is O(n^1.585). The DSA subject covers it in depth.

## Generating functions

A **generating function** stores a sequence a₀, a₁, a₂, … as the coefficients of a power series:

```
A(x) = a0 + a1 x + a2 x^2 + ...
```

For the formal counting manipulations here we do not need to evaluate x; it is just a clothes line to hang the numbers on. The magic is that **multiplying two generating functions convolves the sequences**, and convolution is exactly how "split n into a part from here and a part from there" counts combine.

The building block is the geometric series:

```
1/(1-x) = 1 + x + x^2 + x^3 + ...
```

Its coefficients are all 1: "one way to choose any number of something".

### Example: making change

How many ways can you make n pence from 1p, 2p and 5p coins (order doesn't matter)? The number of 1p coins is any k ≥ 0, giving 1 + x + x² + …; 2p coins contribute 1 + x² + x⁴ + …; 5p coins 1 + x⁵ + x¹⁰ + …. Each term in the product picks one power from each factor, so the coefficient of xⁿ counts the combinations:

```
G(x) = 1 / ((1-x)(1-x^2)(1-x^5))
```

Multiplying the polynomials (truncated at degree n) is precisely the classic coin-change DP:

Assume n is a non-negative integer and coins contains distinct positive integer denominations.

```python
def ways(n, coins):
    w = [1] + [0] * n
    for c in coins:          # multiply by
        for v in range(c, n + 1):
            w[v] += w[v - c]  # 1/(1-x^c)
    return w[n]

ways(10, [1, 2, 5])   # 10
```

The inner loop is multiplication by 1/(1 − xᶜ): w(x) becomes w(x) + xᶜ · (new w(x)). Generating functions give a way to *derive* DP algorithms and prove them correct, and with more algebra they give closed forms. For Fibonacci, F(x) = x/(1 − x − x²), and partial fractions on this recover the φⁿ formula.

> [!note] Catalan numbers
> 1, 1, 2, 5, 14, 42, … count balanced strings of n bracket pairs, ordered rooted binary-tree shapes with n nodes (left/right distinguished), and, for n ≥ 1, triangulations of a convex polygon with n + 2 vertices. They satisfy C(n+1) = Σ C(i) C(n−i), a convolution, and the generating function solves to C(n) = (2n choose n)/(n + 1). There are 14 balanced strings of 4 bracket pairs.

## Pitfalls

- **Forgetting the intersections.** Adding counts of overlapping cases is the most common counting bug. If cases can overlap, you need inclusion–exclusion or a disjoint reformulation.
- **Wrong base cases.** a(n) = a(n−1) + a(n−2) gives Fibonacci, Lucas numbers or something else entirely, depending on a(0) and a(1). Check the recurrence against brute force for n = 1, 2, 3.
- **Non-disjoint cases in a recurrence.** If your first-step cases overlap, you overcount, just as with the sum rule.
- **Repeated roots.** For a genuine second-order recurrence with a nonzero double root r, the solution is (α + βn) rⁿ, not α rⁿ + β rⁿ.

## Key takeaways
- Inclusion–exclusion corrects overlapping counts: add singles, subtract pairs, add triples, and so on.
- It counts derangements (about n!/e) and onto functions, and anything phrased as "none bad" or "every one covered".
- Recurrences come from a first decision that splits the objects into smaller instances, which is the same step as designing a DP.
- Linear recurrences are solved with the characteristic equation; divide-and-conquer ones by unrolling or the master theorem.
- Generating functions turn sequences into power series, so combining choices becomes polynomial multiplication; the coin-change DP is that multiplication.

## Further reading
- [Inclusion–exclusion principle — Wikipedia](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
- [Derangement — Wikipedia](https://en.wikipedia.org/wiki/Derangement)
- [Recurrence relation — Wikipedia](https://en.wikipedia.org/wiki/Recurrence_relation)
- [Generating function — Wikipedia](https://en.wikipedia.org/wiki/Generating_function)
- [Master theorem — Wikipedia](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Catalan number — Wikipedia](https://en.wikipedia.org/wiki/Catalan_number)
