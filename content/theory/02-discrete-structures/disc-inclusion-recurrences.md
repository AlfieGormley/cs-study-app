---
id: disc-inclusion-recurrences
title: Inclusion–exclusion, recurrences and generating functions
level: intermediate
minutes: 20
summary: Counting overlapping cases with inclusion–exclusion, derangements and surjections, setting up and solving recurrences, and using generating functions to turn counting into polynomial multiplication.
---

The basic counting rules break down in two common situations. When cases **overlap**, the sum rule double-counts. When a problem is easiest to describe **in terms of smaller versions of itself**, a direct formula is hard to see. Inclusion–exclusion fixes the first; recurrences fix the second. Generating functions are a power tool that packages a whole sequence into one object, so that counting problems become algebra.

These are also the tools you need to analyse algorithms: recurrences describe the running time of recursive code, and the same "count the ways" reasoning is what dynamic programming computes.

## Inclusion–exclusion

When two groups overlap, adding their sizes counts everyone in the overlap twice, so subtract the overlap once:

```formula
|A ∪ B| = |A| + |B| − |A ∩ B|
|P ∪ J| = 18 + 15 − 8 = 25
where
A, B: two finite sets (collections of distinct items), here P and J
P, J: the engineers who know Python and the engineers who know Java
| |: the size of a set: how many elements it has
∪: union: the elements in at least one of the two sets
∩: intersection: the elements in both sets
In words: everyone in at least one group = the first group + the second group − those counted in both. With 18 Python, 15 Java and 8 who know both, 25 engineers know at least one.
```

> [!example] Two sets
> In a team of 30 engineers, 18 know Python, 15 know Java and 8 know both. Those who know at least one: 18 + 15 − 8 = 25. So 30 − 25 = 5 know neither.

For three sets, subtracting the pairwise overlaps removes the triple overlap one time too many, so add it back:

```formula
|A ∪ B ∪ C| = |A| + |B| + |C|
            − |A ∩ B| − |A ∩ C| − |B ∩ C|
            + |A ∩ B ∩ C|
where
A, B, C: three finite sets
| |: the size of a set (its number of elements)
∪: union: elements in at least one of the sets
∩: intersection: elements in all of the sets it joins
In words: add the three groups, subtract each pairwise overlap, then add back the part common to all three.
```

The general pattern alternates: add singles, subtract pairs, add triples, subtract quadruples, and so on. To see why it works, follow one element that lies in exactly m of the sets. It is counted once for every single set it is in, minus once for every pair, plus once for every triple, and so on:

```formula
C(m, 1) − C(m, 2) + C(m, 3)
  − … ± C(m, m) = 1
3 − 3 + 1 = 1   for m = 3
where
m: the number of the sets that contain this particular element, at least 1
C(m, j): "m choose j", the number of ways to pick j of those m sets: the number of j-fold intersections the element lies in
…: and so on, through every size from 1 to m
±: plus or minus: the signs keep alternating, so the last sign is + when m is odd and − when m is even
In words: however many sets an element is in, the alternating sum counts it once and only once. (It follows from the binomial theorem with x = −1 and y = 1.)
```

### Worked example: divisibility

How many integers from 1 to 1000 are divisible by 2, 3 or 5? The multiples of d up to 1000 number ⌊1000 / d⌋. The multiples of both 2 and 3 are the multiples of 6, and so on, because 2, 3 and 5 share no factors.

```formula
|A_d| = ⌊1000 / d⌋
|A_2| = 500  |A_3| = 333  |A_5| = 200
|A_6| = 166  |A_10| = 100  |A_15| = 66
|A_30| = 33
500 + 333 + 200 = 1033
1033 − 166 − 100 − 66 = 701
701 + 33 = 734
where
A_d: the set of integers from 1 to 1000 divisible by d
A_2, A_3, A_5: the singles: the multiples of 2, of 3 and of 5
A_6, A_10, A_15: the pairs: multiples of both 2 and 3 (that is, of 6), of both 2 and 5 (of 10), and of both 3 and 5 (of 15)
A_30: the triple: multiples of 2, 3 and 5 at once, which are the multiples of 30
d: the divisor, here 2, 3, 5, 6, 10, 15 or 30
| |: the size of a set (how many integers it contains)
⌊ ⌋: floor: round down to a whole number, so ⌊1000 / 3⌋ = ⌊333.3⌋ = 333
In words: add the three singles, subtract the three pairs, add back the triple: 734 integers are divisible by at least one of 2, 3 and 5.
```

So 734 are divisible by at least one, and 1000 − 734 = 266 by none. Each term is one integer division (constant time in a fixed-width arithmetic model), so inclusion–exclusion counts without iterating. The same idea computes Euler's totient function (written with the Greek letter phi), which you'll meet in the number theory lesson.

### Derangements

A **derangement** is a permutation where nothing stays in its original place: every guest leaves with someone else's coat, or every reviewer gets someone else's pull request.

Let Aᵢ be the permutations that fix item i (leave it in its original position). Fixing any particular k items leaves (n − k)! permutations of the rest, and there are C(n, k) ways to choose which k. Inclusion–exclusion over "at least one fixed point" gives:

```formula
D(n) = n! − C(n, 1) × (n − 1)!
     + C(n, 2) × (n − 2)! − …
D(n) = n! × (1 − 1/1! + 1/2! − … ± 1/n!)
D(4) = 24 × (1 − 1 + 1/2 − 1/6 + 1/24)
D(4) = 24 − 24 + 12 − 4 + 1 = 9
where
D(n): the number of derangements of n items: orderings with no item in its original position
n: the number of items, 0 or more
k: the number of items forced to stay in their original positions in one term, from 0 to n
C(n, k): "n choose k", the number of ways to pick which k items stay put
!: factorial: the product of every whole number from that number down to 1, with 0! = 1
…: and so on, one term for each k up to n
±: the sign of the last term: + when n is even, − when n is odd
In words: start from all n! orderings, subtract those fixing some item, add back those fixing two, and so on. Since C(n, k) × (n − k)! = n! / k!, each term is n! divided by k!, which gives the bracketed form.
```

The bracket is the start of the series for e⁻¹ (1 divided by Euler's number e ≈ 2.718), which gives a shortcut:

```formula
D(n) = ⌊n! / e + 1/2⌋   for n ≥ 1
D(4) = ⌊24 / 2.718 + 0.5⌋ = ⌊9.33⌋ = 9
D(n) / n! → 1 / e ≈ 0.368
where
D(n): the number of derangements of n items
n!: n factorial, the number of all orderings of n items
e: Euler's number, about 2.71828, the base of natural logarithms
⌊ ⌋: floor: round down to a whole number. Adding 1/2 first turns this into rounding to the nearest whole number
→: tends to, as n grows larger and larger
≈: approximately equal to
In words: the number of derangements is n! / e rounded to the nearest whole number, and the chance that a random ordering moves every item approaches about 36.8%.
```

The values run 0, 1, 2, 9, 44, 265, … for 1 to 6 items. The limit is approached quickly, but small cases differ substantially: for 1 item the probability is 0, and for 2 items it is 1/2.

### Counting onto functions

How many ways can you assign 5 distinct jobs to 3 servers so every server gets at least one? There are 3⁵ assignments in all. Subtract those missing a given server, add back those missing two:

```formula
S = 3^5 − C(3, 1) × 2^5 + C(3, 2) × 1^5
S = 243 − 3 × 32 + 3 × 1
S = 243 − 96 + 3 = 150
where
S: the number of assignments of 5 distinct jobs to 3 servers that leave no server idle (onto, or surjective, functions)
3^5: all assignments: each of the 5 jobs independently picks one of 3 servers
C(3, 1) × 2^5: choose 1 server to leave idle (3 ways), then send all 5 jobs to the other 2
C(3, 2) × 1^5: choose 2 servers to leave idle (3 ways), then all jobs go to the last one
C(a, b): "a choose b", the number of ways to choose b items from a
In words: 150 of the 243 assignments use every server. Assignments missing two servers were subtracted twice, so they are added back once.
```

The same pattern counts onto functions from an m-element set to an n-element set: add or subtract, for each number j of excluded targets, C(n, j) × (n − j)ᵐ, with the sign + for even j and − for odd j.

Inclusion–exclusion is the go-to method whenever the condition is "every X is covered" or "no X is bad": count the complement events, which are often easier, and alternate.

## Recurrences

A **recurrence** defines each term of a sequence from earlier terms, plus base cases. Setting one up is often easier than finding a formula directly, because it mirrors how you'd *build* the objects.

### Setting up a recurrence

> [!example] Binary strings with no two adjacent 1s
> Count the binary strings of a given length that never contain "11". Look at the first character. If it's 0, the rest is any valid string one character shorter. If it's 1, the next must be 0, and then any valid string two characters shorter follows. The two cases don't overlap, so the count is the sum of the two shorter counts.

```formula
a(n) = a(n − 1) + a(n − 2)
a(1) = 2,  a(2) = 3
a(3) = 3 + 2 = 5,  a(4) = 5 + 3 = 8
where
a(n): the number of binary strings of length n with no two adjacent 1s
n: the string length, a whole number; the recurrence applies for n ≥ 3
a(n − 1), a(n − 2): the counts for strings one and two characters shorter
In words: valid strings starting with 0, plus valid strings starting with 10. The values 2, 3, 5, 8, 13, … are the Fibonacci numbers.
```

The skill is finding the right **first decision** that splits the objects into disjoint cases, each a smaller instance of the same problem. It is exactly the step you take when designing a dynamic-programming solution.

The **Tower of Hanoi** is the classic: to move n discs, move n − 1 out of the way, move the biggest, then move the n − 1 back on top.

```formula
T(n) = 2 × T(n − 1) + 1,   T(0) = 0
T(1), T(2), … = 1, 3, 7, 15, 31, …
T(n) = 2^n − 1
2 × (2^{n−1} − 1) + 1 = 2^n − 1
where
T(n): the minimum number of single-disc moves to move a tower of n discs
n: the number of discs, 0 or more
T(n − 1): the moves for the smaller tower, needed twice (off, then back on)
2^n: n copies of 2 multiplied together
…: and so on
In words: the first line is the recurrence, the second its first few values, the third a guessed closed form, and the fourth checks the guess: putting 2^{n−1} − 1 into the right-hand side gives back 2^n − 1.
```

Guessing a formula from small values and proving it by induction is a perfectly good method. For 10 discs it gives 2¹⁰ − 1 = 1,023 moves.

### Solving linear recurrences

A **linear homogeneous recurrence with constant coefficients** makes each term a fixed weighted sum of the previous terms, with nothing else added. For the second-order case, guess a solution of the form rⁿ. Substituting and dividing by rⁿ⁻² gives the **characteristic equation**:

```formula
a(n) = c_1 × a(n − 1) + c_2 × a(n − 2)
a(n) = r^n  gives  r^2 = c_1 × r + c_2
a(n) = α × r_1^n + β × r_2^n
where
a(n): the nth term of the sequence
n: the position in the sequence, a whole number
c_1, c_2: fixed numbers (the constant coefficients), with c_2 not zero
r: a candidate growth factor; r^n means n copies of r multiplied together
r_1, r_2: the two different roots (solutions) of the characteristic equation
α, β: alpha and beta, constants fixed by the base cases (the first two terms)
In words: try a pure exponential, find which growth factors fit, then mix them to match the starting values. This form of the solution needs the two roots to be distinct.
```

A full example, with a(0) = 2 and a(1) = 5:

```formula
a(n) = 5 × a(n − 1) − 6 × a(n − 2)
r^2 − 5 × r + 6 = 0
(r − 2) × (r − 3) = 0,  so r = 2, 3
a(n) = α × 2^n + β × 3^n
α + β = 2   (n = 0)
2 × α + 3 × β = 5   (n = 1)
α = 1,  β = 1
a(n) = 2^n + 3^n
where
a(n): the nth term; a(0) = 2 and a(1) = 5 are the base cases
n: the position in the sequence
r: a root of the characteristic equation
α, β: alpha and beta, the constants fixed by the base cases
In words: the roots are 2 and 3, the two starting values force both constants to be 1, and the answer is 2^n + 3^n. Check: a(2) = 5 × 5 − 6 × 2 = 13 = 4 + 9.
```

Fibonacci, where each number is the sum of the two before it, works the same way:

```formula
r^2 = r + 1
r = (1 ± √5) / 2
φ = (1 + √5) / 2 ≈ 1.618
F(n) ≈ φ^n / √5
where
r: a root of the characteristic equation of the Fibonacci recurrence
±: plus or minus: one root uses +, the other −
√: square root, so √5 ≈ 2.236
φ: phi, the golden ratio: the larger root
F(n): the nth Fibonacci number, with F(0) = 0 and F(1) = 1
≈: approximately equal to; for n ≥ 0, F(n) is φ^n / √5 rounded to the nearest whole number
In words: Fibonacci numbers grow by a factor of about 1.618 each step. F(10) = 55, and 1.618^10 / 2.236 ≈ 55.0.
```

This is why naive recursive Fibonacci, whose call count obeys a Fibonacci-like recurrence, takes exponential time, and why memoisation reduces it to O(n) additions, where n is the index of the Fibonacci number. Exact Fibonacci values grow to about 0.69 × n bits, so this is not a linear bit-complexity bound.

### Divide-and-conquer recurrences

Recursive algorithms that split the input into equal parts give recurrences of a standard shape. Merge sort splits into two halves and merges in linear time. Unrolling its recursion tree shows the same work on every level:

```formula
T(n) = a × T(n / b) + f(n)
T(n) = 2 × T(n / 2) + n
W_i = 2^i × (n / 2^i) = n
L = log_2(n)
T(n) ≈ W_i × L = n × log_2(n)
where
T(n): the running time on an input of size n
n: the input size
a: the number of recursive calls (subproblems), 2 for merge sort
b: the factor by which each subproblem is smaller, 2 for merge sort
f(n): the work done outside the recursive calls (splitting and combining), n for merge sort
W_i: the total work on level i of the recursion tree: 2^i subproblems of size n / 2^i each
i: the level, 0 at the top
L: the number of levels before the subproblems reach size 1
log_2: logarithm base 2: how many times you can halve n before reaching 1
≈: approximately (ignoring constant factors and rounding)
In words: merge sort does about n work on each of about log_2(n) levels. For n = 1024 that is 1024 × 10 = 10,240 units of work.
```

The **master theorem** packages this. Compare the outside work f(n) with the work at the leaves of the tree:

```formula
N_leaf = n^{log_b(a)}
n^{log_2(1)} = n^0 = 1
n^{log_2(2)} = n^1 = n
n^{log_2(3)} ≈ n^{1.585}
where
N_leaf: the number of leaves of the recursion tree, which sets the work done at the bottom
n: the input size
a: the number of recursive calls
b: the factor by which each call's input shrinks
log_b: logarithm base b: the power you raise b to in order to get its argument
log_2: logarithm base 2; log_2(1) = 0, log_2(2) = 1 and log_2(3) ≈ 1.585
≈: approximately equal to
In words: the last three lines are binary search (a = 1, b = 2), merge sort (a = 2, b = 2) and Karatsuba multiplication (a = 3, b = 2). Roughly, if f(n) grows more slowly than N_leaf, the leaves dominate and the time is about N_leaf; if f(n) matches it, multiply by a factor of log n; if f(n) grows faster, f(n) dominates (each case has technical conditions).
```

So binary search (constant outside work, which matches its single leaf) is O(log n); merge sort (linear outside work, matching its n leaves) is O(n log n); Karatsuba multiplication (linear outside work, less than its n^1.585 leaves) is O(n^1.585), where O(…) means "grows at most proportionally to" and n is the input size. The DSA subject covers it in depth.

## Generating functions

A **generating function** stores a sequence a₀, a₁, a₂, … as the coefficients of a power series:

```formula
A(x) = a_0 + a_1 × x + a_2 × x^2 + …
where
A(x): the generating function of the sequence
a_0, a_1, a_2: the terms of the sequence being stored (counts, for example)
x: a placeholder variable; x^n marks position n
…: and so on, one term for every position
In words: the number of ways for size n is stored as the number in front of x^n.
```

For the formal counting manipulations here we do not need to evaluate x; it is just a clothes line to hang the numbers on. The magic is that **multiplying two generating functions convolves the sequences**: the coefficient of xⁿ in the product adds up every way to split n into a part from the first factor and a part from the second. That is exactly how "split n into a part from here and a part from there" counts combine.

The building block is the geometric series:

```formula
1 / (1 − x) = 1 + x + x^2 + x^3 + …
where
x: the placeholder variable (as a real number the series only adds up when x is between −1 and 1, but formal counting never evaluates it)
x^2, x^3: x multiplied by itself 2 and 3 times
…: and so on forever
In words: every coefficient is 1: "one way to choose any number of something". Multiply both sides by 1 − x and every term cancels except the 1.
```

### Example: making change

How many ways can you make n pence from 1p, 2p and 5p coins (order doesn't matter)? Any number of 1p coins is allowed, with one way to use each number, which is the geometric series. 2p coins can only make even amounts, and 5p coins multiples of 5. Each term in the product picks one power from each factor, so the coefficient of xⁿ counts the combinations:

```formula
G(x) = 1 / ((1 − x) × (1 − x^2) × (1 − x^5))
1 / (1 − x^2) = 1 + x^2 + x^4 + …
1 / (1 − x^5) = 1 + x^5 + x^10 + …
where
G(x): the generating function for making change; the coefficient of x^n is the number of ways to make n pence
x: the placeholder variable; x^k stands for k pence
1 − x, 1 − x^2, 1 − x^5: one factor per coin; 1 / (1 − x^c) lists the amounts 0, c, 2c, … that coins worth c pence can make
…: and so on forever
In words: multiply one series per coin; the number in front of x^10 counts the ways to make 10p, which is 10.
```

Multiplying the polynomials (truncated at degree n) is precisely the classic coin-change dynamic programme. In this code, n is a non-negative integer and coins contains distinct positive integer denominations:

```python
def ways(n, coins):
    w = [1] + [0] * n
    for c in coins:          # multiply by
        for v in range(c, n + 1):
            w[v] += w[v - c]  # 1/(1-x^c)
    return w[n]

ways(10, [1, 2, 5])   # 10
```

The inner loop multiplies the series in w by one coin's factor. Because w[v − c] has already been updated when w[v] uses it, the loop computes:

```formula
w′(x) = w(x) + x^c × w′(x)
w′(x) = w(x) / (1 − x^c)
where
w(x): the generating function held in the list w before this coin's loop: w[v] is the coefficient of x^v
w′(x): the same list after the loop (the prime mark means "new")
c: the value of the current coin, in pence
x^c: shifting every coefficient up c places, which is what w[v - c] does
In words: the new count for v pence is the old count plus the new count for v − c pence (use at least one more of this coin), which is division by 1 − x^c.
```

Generating functions give a way to *derive* DP algorithms and prove them correct, and with more algebra they give closed forms. For Fibonacci:

```formula
F(x) = x / (1 − x − x^2)
where
F(x): the generating function of the Fibonacci numbers F(0), F(1), F(2), … = 0, 1, 1, 2, 3, 5, …
x: the placeholder variable
x^2: x multiplied by itself
In words: the Fibonacci numbers are the coefficients of this fraction's series. Splitting it into partial fractions recovers the golden-ratio formula above.
```

> [!note] Catalan numbers
> The Catalan numbers 1, 1, 2, 5, 14, 42, … count balanced bracket strings (by the number of bracket pairs), ordered rooted binary-tree shapes (by the number of nodes, left/right distinguished) and, from size 1 upwards, triangulations of a convex polygon with two more vertices than the size. They satisfy a convolution recurrence, and the generating function solves to a closed form (both below). There are 14 balanced strings of 4 bracket pairs.

```formula
Cat_{n+1} = Σ Cat_i × Cat_{n−i}
Cat_n = C(2n, n) / (n + 1)
Cat_4 = C(8, 4) / 5 = 70 / 5 = 14
where
Cat_n, Cat_{n+1}, Cat_i, Cat_{n−i}, Cat_4: Catalan numbers (the subscript is the size); Cat_n counts, for example, balanced strings of n bracket pairs, with Cat_0 = 1
n: the size, a whole number 0 or more
i: the summation index
Σ: sigma, "sum of": add the term after it for every i from 0 to n
C(2n, n): "2n choose n", the number of ways to choose n items from 2n
In words: a balanced string splits into a first bracket pair enclosing i pairs, followed by the other n − i pairs, which gives the convolution. The closed form gives 14 for n = 4.
```

## Pitfalls

- **Forgetting the intersections.** Adding counts of overlapping cases is the most common counting bug. If cases can overlap, you need inclusion–exclusion or a disjoint reformulation.
- **Wrong base cases.** The recurrence "each term is the sum of the two before" gives Fibonacci numbers, Lucas numbers or something else entirely, depending on the first two values. Check the recurrence against brute force for lengths 1, 2 and 3.
- **Non-disjoint cases in a recurrence.** If your first-step cases overlap, you overcount, just as with the sum rule.
- **Repeated roots.** For a genuine second-order recurrence whose characteristic equation has a nonzero double root, the solution needs an extra factor of n (below).

```formula
a(n) = (α + β × n) × r^n
a(n) = (1 + n) × 2^n
where
a(n): the nth term of a second-order linear recurrence whose characteristic equation has the same root twice
n: the position in the sequence
r: the repeated (double) root, not zero
α, β: alpha and beta, constants fixed by the first two terms
In words: with a double root, α × r^n + β × r^n is really just one constant times r^n and can't fit two starting values, so the second solution is n × r^n. For a(n) = 4 × a(n − 1) − 4 × a(n − 2) with a(0) = 1 and a(1) = 4, the double root is 2 and a(n) = (1 + n) × 2^n, so a(5) = 192.
```

## Key takeaways
- Inclusion–exclusion corrects overlapping counts: add singles, subtract pairs, add triples, and so on.
- It counts derangements (about n!/e of the n! orderings of n items) and onto functions, and anything phrased as "none bad" or "every one covered".
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
