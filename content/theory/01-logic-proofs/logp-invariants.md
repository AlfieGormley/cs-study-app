---
id: logp-invariants
title: Invariants for proving algorithms correct
level: intermediate
minutes: 15
summary: Loop invariants and variants, the initialise–maintain–terminate recipe, worked proofs for binary search, fast exponentiation, Euclid's algorithm and insertion sort, and how invariants show up in assertions, data structures and verified systems.
---

Induction proves facts about recursive definitions. Many algorithms use loops that update variables. How do you prove a `while` loop is correct, for every input, without running it on every input?

The answer is a **loop invariant**: a statement about the program's variables that is true every time execution reaches the top of the loop. If it is true on entry, stays true after each iteration, and combined with the exit condition gives you what you wanted, the loop is correct. That is induction on the number of iterations, packaged for code.

Invariants are also the most practical piece of theory in this module. They are how you write binary search without off-by-one errors, what `assert` statements should check, and what keeps a heap a heap.

## The recipe

To prove a loop correct with invariant I:

1. **Initialisation**: I holds before the first iteration.
2. **Maintenance**: if I holds at the start of an iteration (and the loop condition is true), it holds at the end.
3. **Termination**: when the loop exits, I plus the negated loop condition imply the goal.

Steps 1 and 2 are the base case and inductive step. Step 3 is where you cash in.

This proves **partial correctness**: *if* the loop stops, the answer is right. You also need **total correctness**: the loop *does* stop. For that, find a **variant** (or ranking function): an integer expression that is always ≥ 0 and strictly decreases each iteration. A non-negative integer cannot decrease forever. Assuming each loop test and body execution finishes normally, this proves loop termination. More general well-founded orders can also supply ranking functions.

## A first example

Assume a finite list of integers that is not modified concurrently, exact arithmetic and normal execution without resource failures. Include 0 ≤ i ≤ len(a) in the invariant.

```python
def total(a):
    s, i = 0, 0
    # I: s == sum(a[:i])
    while i < len(a):
        s += a[i]
        i += 1
    return s
```

- **Init**: s = 0 and a[:0] is empty, whose sum is 0. ✓
- **Maintain**: if s = sum(a[:i]), then after the body s' = sum(a[:i]) + a[i] = sum(a[:i+1]) and i' = i + 1. ✓
- **Terminate**: on exit i = len(a), so s = sum(a). ✓
- **Variant**: len(a) − i, which is ≥ 0 and falls by 1 each time.

Notice where the invariant came from: it is the goal s = sum(a) with the constant len(a) **replaced by the loop variable** i. That is the single most useful trick for finding invariants.

## Binary search, done properly

Binary search is famous for being easy to describe and hard to get right. An invariant makes it mechanical. This version returns the first index whose element is ≥ x (the bisect_left insertion position), assuming a stable ascending list and a total order shared with x. NaNs and inconsistent custom comparisons are excluded. The invariant also includes 0 ≤ lo ≤ hi ≤ len(a):

```python
def bsearch(a, x):
    # a is sorted ascending
    lo, hi = 0, len(a)
    # I: all of a[:lo]  <  x
    #    all of a[hi:] >= x
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

```
 index: 0    lo         hi     n
        [ <x ][  unknown  ][ >=x ]
```

- **Init**: a[:0] and a[n:] are both empty, so I holds vacuously. ✓
- **Maintain**: since lo ≤ mid < hi, mid is in the unknown zone.
  - If a[mid] < x, then because a is sorted, everything up to mid is < x. Setting lo = mid + 1 keeps "a[:lo] < x". ✓
  - Otherwise a[mid] ≥ x, so everything from mid on is ≥ x. Setting hi = mid keeps "a[hi:] ≥ x". ✓
- **Terminate**: exit means lo == hi. The unknown zone is empty: everything before lo is < x and everything from lo on is ≥ x. So lo is exactly the first index with a[lo] ≥ x (or n if there is none). ✓
- **Variant**: hi − lo. Because lo ≤ mid < hi, either lo grows or hi shrinks, by at least 1. ✓

Each choice is now forced by the invariant. Write `hi = mid - 1` and you could skip the answer; write `lo = mid` and when hi = lo + 1 the loop spins forever, because mid = lo. The invariant tells you which is right instead of guessing.

> [!warning] Proofs over ideal numbers
> In 2006 Joshua Bloch reported that the JDK's `binarySearch` had been broken for about nine years. The line `mid = (low + high) / 2` overflows a 32-bit `int` once low + high exceeds 2³¹ − 1, giving a negative index. The invariant proof was right *for mathematical integers*. Python integers have arbitrary precision, subject to memory limits. For nonnegative in-range indices low ≤ high in Java or C, use low + (high - low) / 2. C signed overflow is undefined behavior, whereas Java int arithmetic wraps.

## Fast exponentiation

Computing xⁿ with n multiplications is slow for large n. For integer n ≥ 0, repeated squaring uses O(log(n + 1)) multiplications. This is not a bit-operation bound: large-integer multiplication costs depend on operand size. The proof assumes exact arithmetic:

```python
def power(x, n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be >= 0")
    result, base, e = 1, x, n
    # I: result * base**e == x**n
    while e > 0:
        if e % 2 == 1:
            result *= base
        base *= base
        e //= 2
    return result
```

The invariant is not obvious from the code; it is what makes the code make sense.

- **Init**: 1 · xⁿ = xⁿ. ✓
- **Maintain**, if e is even: the new values give result · (base²)^(e/2) = result · baseᵉ. ✓
- **Maintain**, if e is odd: result' = result · base and e' = (e − 1)/2, so result · base · (base²)^((e−1)/2) = result · baseᵉ. ✓
- **Terminate**: e = 0, so result · base⁰ = result = xⁿ. ✓
- **Variant**: e, which at least halves and stays ≥ 0.

Trace x = 3, n = 13; the last column never changes:

```
result  base       e   result·baseᵉ
1       3          13  1594323
3       9          6   1594323
3       81         3   1594323
243     6561       1   1594323
1594323 43046721   0   1594323
```

3¹³ = 1,594,323. Modular variants of repeated squaring are used in modular exponentiation. Real cryptographic implementations also need side-channel protections; this branching teaching code is not a production RSA implementation.

> [!note] Evidence gap
> A previous fixed RSA runtime claim is omitted because no reproducible implementation, exponent, hardware or benchmark was supplied.

## Euclid's algorithm

```python
def gcd(a, b):
    # integers a, b >= 0; gcd(0, 0) = 0
    # I: gcd(a, b) == gcd(a0, b0)
    while b != 0:
        a, b = b, a % b
    return a
```

- **Init**: trivially, with a0, b0 the inputs. ✓
- **Maintain**: the key fact gcd(a, b) = gcd(b, a mod b). Any common divisor of a and b divides a − qb = a mod b, and any common divisor of b and a mod b divides a = qb + (a mod b). Same divisors, same greatest one. ✓
- **Terminate**: b = 0 and gcd(a, 0) = a. ✓
- **Variant**: b, since 0 ≤ a mod b < b.

```
a    b
252  105
105  42
42   21
21   0     -> gcd = 21
```

## Insertion sort and nested loops

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        # I: a[:i] is sorted and holds
        #    the original a[:i]'s items
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a
```

The outer invariant says the prefix is a sorted rearrangement of the original prefix. The inner loop needs its own invariant (roughly: a[j+2 .. i] holds the elements greater than key, shifted right by one). After the last iteration, the processed prefix has length len(a), so the whole array is sorted. Python’s for-loop variable does not advance to len(a); it remains at its last assigned value, or is never assigned if there are no iterations.

Two-part invariants are common. "Sorted" alone is not enough: the empty array is sorted too. You also need "is a permutation of the input", or a buggy sort that overwrites everything with zeros would pass.

## Hoare logic in one paragraph

Tony Hoare (1969) wrote correctness claims as **triples** {P} S {Q}: if precondition P holds before running statement S, and S terminates, then postcondition Q holds after. The rule for loops is the recipe above:

```
       {I ∧ B}  body  {I}
------------------------------
{I}  while B: body  {I ∧ ¬B}
```

If the body preserves I whenever the condition B is true, then the loop as a whole preserves I and exits with ¬B. Tools such as **Dafny** ask you to write invariants and then check these obligations automatically with an SMT solver.

## Invariants beyond loops

The same idea scales up from loops to whole systems.

- **Data structure (representation) invariants**: a binary heap's parent ≤ children; a red-black tree's equal black height on every path; a chained hash table's "key k is in bucket hash(k) mod m". Every public method must restore them before returning.
- **Class invariants**: a bank `Account` with balance ≥ 0. Constructors establish it; methods preserve it.
- **Database constraints** enforce their defined conditions at specified checking points. Deferrable constraints may be checked at commit; PostgreSQL CHECK accepts TRUE or NULL, and default UNIQUE handling permits multiple NULLs. Add NOT NULL when required.
- **Distributed systems**: "at most one leader per term" in Raft. Amazon engineers used TLA+ to model-check invariants like these and reported finding subtle bugs in systems including DynamoDB that testing had missed.

> [!tip] Put the invariant in the code
> Write the invariant as a comment, and in debug builds as an `assert`. An assertion detects a violation when execution reaches that check; the underlying bug may have occurred earlier. Python can disable assert statements under optimization, so do not use them as mandatory input validation.

## Finding invariants

There is no algorithm for this in general, but a few heuristics cover most loops:

1. **Replace a constant with a variable** in the postcondition (sum(a) → sum(a[:i])).
2. **Describe the regions** of the array the loop has partitioned (binary search, partition in quicksort, Dutch national flag).
3. **Find the conserved quantity**: something that stays fixed while the variables change (result · baseᵉ, gcd(a, b)).
4. **Strengthen if stuck**: if maintenance can't be proved, the invariant is usually missing a fact, just like strengthening an induction hypothesis.

## Key takeaways
- A loop invariant is true at the top of every iteration; prove initialisation, maintenance, and that it plus the exit condition gives the goal.
- That gives partial correctness; add a variant (a non-negative integer that strictly decreases) for termination.
- Binary search becomes mechanical with the invariant "a[:lo] < x and a[hi:] ≥ x".
- Good invariants often come from generalising the postcondition or spotting a conserved quantity.
- Proofs over ideal integers miss overflow; check the machine model.
- The same idea underlies data-structure invariants, database constraints and verified distributed systems.

## Further reading
- [Loop invariant — Wikipedia](https://en.wikipedia.org/wiki/Loop_invariant)
- [Hoare logic — Wikipedia](https://en.wikipedia.org/wiki/Hoare_logic)
- [Loop variant — Wikipedia](https://en.wikipedia.org/wiki/Loop_variant)
- [Nearly all binary searches and mergesorts are broken — Google Research blog](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)
- [How Amazon Web Services uses formal methods (PDF)](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf)
- [Dafny](https://dafny.org/)
