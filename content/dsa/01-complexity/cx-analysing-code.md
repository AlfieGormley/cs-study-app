---
id: cx-analysing-code
title: Analysing code
level: intermediate
minutes: 12
summary: How to read the complexity off real code, including dependent and logarithmic loops, recursion, hidden library costs, and best, average and worst case.
---

You now have the notation. This lesson is about using it: looking at a piece of code and working out its time complexity quickly and correctly. Most code reduces to a handful of patterns, plus a few traps that catch even experienced engineers.

Throughout, n is the input size (for example the length of the list), and m is the size of a second input when there is one. O(...) is Big-O, an upper bound on growth; Θ(...) is Big-Theta, a tight bound; and log n is the base-2 logarithm of n, roughly how many times you can halve n before reaching 1.

## The basic rules

1. **Cost model.** Treat fixed-size arithmetic, comparison and indexing as O(1). Python arbitrary-precision integers, long strings, user-defined comparisons and output can cost more; the counts below abstract those costs unless stated otherwise.
2. **Sequential blocks add.** O(n) followed by O(n^2) is O(n + n^2) = O(n^2), because the n × n term dominates.
3. **Nested loops multiply**, if the inner loop's length doesn't depend on the outer variable. n iterations of an O(m) body is O(n × m).
4. **Branches take the worse side** for worst-case analysis. `if cond: O(n) else: O(1)` is O(n) in the worst case.
5. **Function calls cost whatever the function costs.** A one-line call to `sorted()` is O(n log n), not O(1).

Those cover simple code. The interesting cases are loops whose bounds change.

## Dependent nested loops

When the inner loop depends on the outer variable, you have to **sum** rather than multiply.

```python
for i in range(n):
    for j in range(i):
        work()
```

The inner loop runs 0, 1, 2, ..., n − 1 times, so add those up:

```formula
W(n) = 0 + 1 + 2 + … + (n − 1)
W(n) = Σ_{i=0}^{n−1} i
W(n) = n × (n − 1) / 2 = Θ(n^2)
W(10) = 10 × 9 / 2 = 45
where
W(n): the number of times work() runs
n: the input size, the bound of the outer loop
i: the outer loop's counter; on pass i the inner loop runs i times
Σ_{i=0}^{n−1}: capital sigma, "sum of": add up the expression after it for every whole number i from 0 to n − 1
…: "and so on" up to the last term
Θ(n^2): Big-Theta of n squared: grows at exactly the rate of n × n, up to a constant factor
In words: the inner loop runs once more on each pass, the runs add up to about half of n squared, and halving does not change the growth class.
```

Halving the work does not change the class.

Three nested loops over `i < j < k` do one step per triple of different positions:

```formula
W_3(n) = n × (n − 1) × (n − 2) / 6
W_3(n) ≈ n^3 / 6 = Θ(n^3)
where
W_3(n): the number of steps the three nested loops take
n: the input size
n^3: n cubed, n × n × n
≈: approximately equal to, for large n
Θ(n^3): Big-Theta of n cubed: grows at exactly the rate of n × n × n, up to a constant factor
In words: there are about a sixth of n cubed ways to choose three positions in order, which is still cubic.
```

> [!tip] A quick sanity check
> For nested loops, ask "roughly how many times does the innermost line run, as a fraction of the full box?" If it's a constant fraction (a half, a sixth), the class is the same as the full product.

## Logarithmic loops

A loop whose variable is **multiplied or divided** by a constant each step runs a logarithmic number of times.

```python
i = 1
while i < n:
    i *= 2
```

`i` takes the values 1, 2, 4, 8, ..., stopping once it reaches n. Count the steps:

```formula
i = 2^k
2^k ≥ n
k = ⌈log_2(n)⌉
k = ⌈log_2(16)⌉ = 4
k = ⌈log_2(17)⌉ = ⌈4.09⌉ = 5
where
i: the loop variable, which doubles every pass, so after k passes it equals 2^k
k: the number of loop iterations; the loop stops at the first k with 2^k ≥ n
n: the input size, the value the loop counts up to
2^k: 2 multiplied by itself k times
log_2(n): the base-2 logarithm of n, the power you raise 2 to in order to get n
⌈x⌉: ceiling: round x up to the next whole number
≥: greater than or equal to
In words: doubling from 1 reaches n after about log_2(n) steps, rounded up.
```

For n = 16 that's 4 iterations (1, 2, 4, 8); for n = 17 it's 5.

The same holds for halving (`n //= 2`), and for any constant factor: multiplying by 3 gives log_3(n) steps (the base-3 logarithm), still Θ(log n), because logarithms in different bases differ only by a constant factor. This is the shape behind binary search and balanced trees.

A loop that stops at a square root is different again:

```python
i = 1
while i * i <= n:
    i += 1
```

This runs about √n times (the square root of n): the loop stops when i × i passes n, so i only gets as far as √n. For n = 1,000,000 that is about 1,000 iterations.

## Mixed loops and two classic traps

A linear outer loop around a logarithmic inner loop gives n × log_2(n) ("n log n") steps:

```python
for i in range(n):        # n times
    j = 1
    while j < n:          # log n times
        j *= 2
```

Now the trap. What about an outer loop that **doubles** with an inner loop that runs `i` times?

```python
i = 1
while i < n:
    for j in range(i):
        work()
    i *= 2
```

It looks like "log n outer times n inner", so n log n. But the inner loop runs 1, then 2, then 4 times, and so on up to the last power of 2 below n. Adding these is a **geometric series** (each term is double the last), and a geometric series is dominated by its last term:

```formula
W = 1 + 2 + 4 + … + 2^k
W = 2^{k+1} − 1
2^k < n,  so  W < 2 × n
n = 100:  W = 1 + … + 64 = 127
where
W: the total number of work() calls
k: the number of the last outer pass; on that pass i = 2^k, the largest power of 2 below n
2^k: 2 multiplied by itself k times
2^{k+1}: 2 multiplied by itself k + 1 times
n: the input size
…: "and so on"
In words: each power of 2 is one more than the sum of all the smaller ones, so the whole sum is just under twice the last term, and the last term is less than n.
```

So the whole thing is **Θ(n)**. Always sum the actual counts.

The second trap is the **harmonic** loop:

```python
for i in range(1, n + 1):
    for j in range(0, n, i):
        work()
```

The inner loop steps through 0 to n in jumps of i, so it runs about n / i times. Add up all the passes:

```formula
W(n) ≈ n/1 + n/2 + n/3 + … + n/n
W(n) ≈ n × H(n)
H(n) = 1 + 1/2 + … + 1/n ≈ ln(n)
W(1000) ≈ 1000 × 7.5 = 7500
where
W(n): the total number of work() calls
n: the input size
H(n): the n-th harmonic number, the sum of the fractions 1/1 to 1/n
ln(n): the natural logarithm of n (base e ≈ 2.718); about 0.69 × log_2(n)
…: "and so on"
≈: approximately equal to (each pass runs n / i times rounded up; H(1000) ≈ 7.49)
In words: the inner loop shrinks as 1/i, and those fractions add up to only about the logarithm of n, so the total is about n log n, not n squared.
```

So this is **Θ(n log n)**, not n^2. It appears in sieves (such as the Sieve of Eratosthenes, which is even tighter at n log log n, where log log n is the logarithm of the logarithm) and in some graph and number theory problems.

| Pattern | Count |
|---|---|
| inner to i | n^2 / 2 |
| i *= 2 | log n |
| i*i <= n | √n |
| doubling outer, inner to i | < 2n |
| inner step i | n ln n |

## Recursion

For recursive code, count **how many calls** happen and **how much work each does** outside the recursive calls.

Linear recursion makes one call per level:

```python
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
```

Θ(n) calls and multiplications in the unit-cost model. Actual Python integer multiplications become more expensive as n! (n factorial, n × (n − 1) × … × 1) grows.

Branching recursion is where things explode. Naive Fibonacci makes two calls per level:

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

Draw the **recursion tree**:

```
                 f5
           /            \
         f4              f3
       /    \          /    \
     f3      f2      f2      f1
    /  \    /  \    /  \
   f2  f1  f1  f0  f1  f0
  /  \
 f1  f0
```

(Here `f5` means `fib(5)`.) `fib(5)` makes 15 calls. In general:

```formula
calls(n) = 2 × F(n + 1) − 1
calls(5) = 2 × F(6) − 1 = 2 × 8 − 1 = 15
calls(n) = Θ(φ^n)
φ = (1 + √5) / 2 ≈ 1.618
where
calls(n): the total number of calls made by fib(n), counting the first one
F(n): the n-th Fibonacci number: 0, 1, 1, 2, 3, 5, 8, … (each is the sum of the two before; F(0) = 0, F(1) = 1, F(6) = 8)
n: the argument passed to fib
φ: phi, the golden ratio, about 1.618
φ^n: φ multiplied by itself n times
√5: the square root of 5, about 2.236
Θ: Big-Theta: grows at exactly this rate, up to a constant factor
≈: approximately equal to
In words: the number of calls is itself almost twice a Fibonacci number, and Fibonacci numbers grow by a factor of about 1.618 each step, so the call count grows exponentially.
```

`fib(30)` makes about 2.7 million calls; `fib(50)` would make about 4 × 10^10.

The waste is visible in the tree: `fib(3)` is computed twice, `fib(2)` three times. Caching results (**memoisation**, covered with dynamic programming later) reduces this to n distinct calls: Θ(n).

Divide-and-conquer recursion (halving the problem) needs the tools in lesson 6, but a rough guide:

- One call on half the input, O(1) extra work: Θ(log n) (binary search).
- Two calls on halves, O(n) extra work: Θ(n log n) (merge sort).

## Hidden costs

Many "one-line" operations aren't O(1). In Python (CPython):

| Operation | Cost |
|---|---|
| `x in some_list` | O(n) |
| `x in some_set` | O(1) average |
| `lst.append(x)` | O(1) amortised |
| `lst.insert(0, x)` | O(n) |
| `lst.pop(0)` | O(n) |
| `lst[a:b]` | O(b - a) copy |
| `sorted(lst)` | O(n log n) |
| `len(lst)` | O(1) |

This turns innocent-looking code quadratic:

```python
def unique(items):
    seen = []
    out = []
    for x in items:
        if x not in seen:   # O(n) scan
            seen.append(x)
            out.append(x)
    return out
```

The membership test scans `seen`, so the function is Θ(n^2) when most items are distinct. Changing `seen` to a `set` makes it Θ(n) on average. The algorithm didn't change; the data structure did.

> [!warning] Slicing in recursion
> `binary_search(arr[mid:], target)` looks logarithmic, but each slice copies up to half the array. For an array of n items the total copying is n/2 + n/4 + n/8 + …, which adds up to just under n, so the "O(log n)" search is actually O(n). Pass indices (`lo`, `hi`) instead of slices.

## Best, average and worst case

The same algorithm can take very different time on different inputs of the same size. Linear search shows this:

```python
def find(xs, target):
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1
```

- **Best case:** target is first. 1 comparison, Θ(1).
- **Worst case:** target is last or absent. n comparisons, Θ(n).
- **Average case:** if the target is present and equally likely to be at any position, average the comparison counts over all n positions:

```formula
E = (1 + 2 + … + n) / n
E = (n × (n + 1) / 2) / n
E = (n + 1) / 2 = Θ(n)
where
E: the expected (average) number of comparisons
n: the number of items in the list
…: "and so on" up to n
Θ(n): Big-Theta of n: grows in proportion to n
In words: on average you look through about half the list, which is still linear.
```

For a list of 1,001 items that is 501 comparisons on average.

Which one should you report?

- **Worst case** is the default. It's a guarantee, it's usually easiest to analyse, and adversarial inputs exist (users and attackers will find your slow path).
- **Average case** describes typical behaviour, but it depends on an assumption about the input distribution, which may be wrong for your data.
- **Best case** is rarely useful on its own. Any algorithm can be given a fast best case by checking for one special input.

A related term is **expected time** for **randomised** algorithms. For distinct keys with uniformly random pivots, randomised quicksort is expected Θ(n log n) on every fixed input, because the randomness is in the algorithm, not the input. For distinct keys, quicksort with a first- or last-element pivot is average Θ(n log n) over uniformly random permutations but Θ(n²) on sorted input, which real data often is.

> [!example] Early exits
> An early return can improve best or average time. Whether it changes the worst case depends on whether any inputs still force the original expensive path. Ask which inputs attain the maximum after adding the check.

## Key takeaways
- Sequential code adds, nested loops multiply, dependent loops need an actual sum.
- Multiplying or dividing the loop variable by a constant gives Θ(log n) iterations.
- A geometric series is dominated by its largest term: doubling outer loops often give Θ(n), not n log n.
- The harmonic loop, n/1 + n/2 + ... + n/n steps for input size n, is Θ(n log n).
- For recursion, count calls times work per call. Two calls per level with little shrinkage is exponential.
- Library calls have costs: `in` on a list, `pop(0)` and slicing are all O(n).
- Report worst case by default; average case depends on assumptions about input.

## Further reading
- [TimeComplexity — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Best, worst and average case — Wikipedia](https://en.wikipedia.org/wiki/Best,_worst_and_average_case)
- [Harmonic series — Wikipedia](https://en.wikipedia.org/wiki/Harmonic_series_(mathematics))
- [Memoization — Wikipedia](https://en.wikipedia.org/wiki/Memoization)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
