---
id: cx-growth-rates
title: Algorithms and why efficiency matters
level: basic
minutes: 9
summary: What an algorithm is, how to count the work it does, and why the growth rate of that count matters far more than the speed of your computer.
---

An **algorithm** is a finite, precise sequence of steps that takes some input and produces an output. "Sort this list", "find the shortest route", "check whether this password matches" all have algorithms behind them.

For this introductory discussion, a deterministic algorithm that correctly solves a total problem should be:

- **Well defined**: every step is unambiguous. "Pick a good pivot" is not a step; "pick the middle element" is.
- **Finite**: it terminates on every valid input.
- **Correct**: it produces the right output for every valid input, not just the ones you tried.

There are usually many correct algorithms for the same problem. This module is about how to compare them, and the main currency is **how the amount of work grows as the input grows**.

## Why not just time it?

The obvious way to compare two programs is to run them and use a stopwatch. That is useful (lesson 7 is about doing it well), but on its own it tells you little:

- The result depends on the machine, the language, the compiler and what else was running.
- It tells you about the input you tried, not the input you will get next year.
- It does not tell you *why* one is faster, so it does not tell you how to make it faster.

Instead, we **count the basic operations** an algorithm performs as a function of the input size, usually called **n**. A basic operation is anything that takes a fixed amount of time regardless of n: an arithmetic step, a comparison, reading or writing one array element, the overhead of a function call (its body must be counted separately). Arithmetic and comparisons are constant-cost only for bounded-size values in this model.

This simplified machine, where each basic step costs one unit and memory access is uniform, is called the **RAM model**. It is not perfectly true of real hardware (lesson 7 shows where it breaks), but it is close enough to predict which algorithm will win as n gets large.

## Counting operations

Here is a function that adds up a list:

```python
def total(xs):
    s = 0              # 1 op
    for x in xs:       # runs n times
        s += x         # 1 op per pass
    return s           # 1 op
```

Counting one operation per commented line gives a simple formula for the work:

```formula
T(n) = n + 2
T(1000) = 1000 + 2 = 1002
where
T(n): the number of basic operations total() performs on a list of n items (a count of steps, not seconds)
n: the input size, here the number of items in the list xs; a whole number with no unit
In words: one operation for each item in the list, plus two more for setting s to 0 and returning it.
```

You could argue the loop itself costs something per pass, making it 2 × n + 2. It doesn't matter: either way, doubling the list doubles the work. That is what we care about.

Now a function that checks whether a list contains a duplicate by comparing every pair:

```python
def has_dup(xs):
    n = len(xs)
    for i in range(n):
        for j in range(i + 1, n):
            if xs[i] == xs[j]:
                return True
    return False
```

In the worst case (no duplicates), how many comparisons? Here n is the number of items in the list, and `i` and `j` are the two positions being compared. When `i = 0`, the inner loop runs n − 1 times; when `i = 1`, n − 2 times; and so on down to 0. Adding these up:

```formula
C(n) = (n − 1) + (n − 2) + … + 1 + 0
C(n) = n × (n − 1) / 2
C(5) = 5 × 4 / 2 = 10
C(1000) = 1000 × 999 / 2 = 499500
where
C(n): the number of comparisons has_dup makes in the worst case (no duplicates), on a list of n items
n: the number of items in the list; a whole number with no unit
…: "and so on": the terms keep falling by 1 until they reach 0
In words: every pair of different positions is compared exactly once, and a list of n items has n × (n − 1) / 2 pairs.
```

Where does the second line come from? Write the sum forwards and then backwards underneath it. Each column adds up to n − 1, and there are n columns, so twice the sum is n × (n − 1). Halve it to get the sum itself. Another way to see it: each of the n items is paired with the n − 1 others, and that counts every pair twice.

So for 5 items that is 10 comparisons, for 1,000 items 499,500, and for 1,000,000 items about 500 billion (1,000,000 × 999,999 / 2 ≈ 5 × 10^11). Doubling n roughly **quadruples** the work, because n appears twice in the product: twice as many items, each compared with twice as many others.

A different approach is to sort the list first and then compare neighbours, since duplicates end up next to each other. Good sorting algorithms take about n × log_2(n) operations ("n log n", where log_2 is the base-2 logarithm, explained in the next section; later modules show how). Another is to put each item in a hash set and stop if it is already there, which is about n operations on average. Same problem, three very different growth rates.

## Growth rates

The function that describes how the operation count grows is the algorithm's **growth rate**. Before comparing them, two pieces of notation need decoding: the logarithm and the power.

A **logarithm** answers "how many times do I multiply 2 by itself to reach n?", or equivalently "how many times can I halve n before I get down to 1?". It is the reverse of raising 2 to a power:

```formula
2^10 = 1024
log_2(1024) = 10
log_2(2^k) = k
where
2^k: 2 raised to the power k: 2 multiplied by itself k times, so 2^3 = 2 × 2 × 2 = 8
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; it grows very slowly (log_2 of a million is about 20)
k: any number used as a power
n: here, any positive number
In words: the base-2 logarithm undoes "2 to the power": since ten 2s multiplied together make 1,024, the base-2 log of 1,024 is 10.
```

Logarithms appear whenever an algorithm repeatedly halves its problem, as binary search does. In this module "log n" means log_2(n) unless another base is stated; later lessons show why the base rarely matters.

Here are the common growth rates side by side:

```formula
f(n) = n × log_2(n)
f(1000) ≈ 1000 × 10 = 10^4
f(n) = n^2 = n × n
f(n) = 2^n
where
f(n): the number of operations an algorithm with this growth rate does on an input of n items
n: the input size, a whole number of items
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n (log_2(1000) ≈ 9.97)
n^2: n squared, n multiplied by itself
2^n: 2 multiplied by itself n times
10^4: ten to the power 4, which is 10,000
≈: approximately equal to (rounded)
In words: each row of the table below is one choice of f; the table shows how many operations each one needs at three input sizes.
```

Values are rounded and logs are base 2:

| f(n) | n = 10 | n = 1,000 | n = 10^6 |
|---|---|---|---|
| log n | 3 | 10 | 20 |
| n | 10 | 1,000 | 10^6 |
| n log n | 33 | 10^4 | 2 x 10^7 |
| n^2 | 100 | 10^6 | 10^12 |
| 2^n | 1,024 | 10^301 | absurd |

Two things jump out.

First, **for small n, nothing matters much.** At n = 10, even 2^n is only about a thousand steps (1,024). This is why a naive algorithm often works fine in testing.

Second, **for large n, the growth rate is everything.** Suppose a machine does about 10^8 simple operations per second (an illustrative assumed rate, not a general hardware benchmark). Turning an operation count into a time is a division:

```formula
t = W / r
t = 10^12 / 10^8 = 10^4 s
t = 10^4 s / 3600 ≈ 2.8 h
where
t: the running time, in seconds (s)
W: the number of operations the algorithm does; here n^2 = 10^12 for n = 10^6 items
r: the machine's speed, assumed to be 10^8 (100 million) simple operations per second
n: the input size, here a million items
s: seconds
h: hours; 1 h = 3,600 s
≈: approximately equal to (rounded)
In words: a trillion operations at a hundred million per second takes ten thousand seconds, nearly three hours.
```

The same division for the other rows gives, at n = 10^6:

| Growth | Operations | Time |
|---|---|---|
| n | 10^6 | 0.01 s |
| n log n | 2 x 10^7 | 0.2 s |
| n^2 | 10^12 | ~2.8 hours |

The quadratic algorithm is not "a bit slower". It is the difference between instant and unusable.

> [!example] The production surprise
> A team writes the pairwise `has_dup` check for a feature that validates uploaded CSV files. In testing, files have 200 rows: 19,900 comparisons, unnoticeable. A customer uploads 2 million rows: about 2 x 10^12 comparisons. The request times out, retries, and takes the worker pool with it. Nothing was "wrong" with the code except its growth rate.

## Faster hardware does not save you

It is tempting to think a faster computer fixes a slow algorithm. Look at what a machine that is **10 times faster** buys you, in terms of the largest input you can handle in the same time. In the table, N stands for the largest input size the old machine could handle; n^3 means n × n × n:

| Growth | Old max n | New max n |
|---|---|---|
| n | N | 10N |
| n^2 | N | ~3.16N |
| n^3 | N | ~2.15N |
| 2^n | N | N + 3.3 |

Where do these numbers come from? Set the work the new machine can do in the same time equal to 10 times the old work, and solve for the new input size:

```formula
N_new^2 = 10 × N^2
N_new = √(10) × N ≈ 3.16 × N
2^{N_new} = 10 × 2^N
N_new = N + log_2(10) ≈ N + 3.3
where
N: the largest input the old machine can handle in the time budget
N_new: the largest input the 10-times-faster machine can handle in the same time
√(10): the square root of 10, the number that multiplied by itself gives 10, about 3.16
2^N: 2 multiplied by itself N times
log_2(10): the base-2 logarithm of 10, the power you raise 2 to in order to get 10, about 3.32
≈: approximately equal to (rounded)
In words: for quadratic work, 10 times the speed buys only √10 ≈ 3.16 times the input; for exponential work, it buys only about 3 more items.
```

For a cubic algorithm the same steps give the cube root of 10, about 2.15. Better algorithms routinely give improvements of thousands or millions of times; hardware gives you a constant factor.

## What "input size" means

n should measure whatever drives the work. Usually it is obvious, but not always:

- For a list or string, n is its length.
- For a graph, the cost often depends on both vertices **V** and edges **E**, so you state both (for example "V + E").
- For arithmetic on big numbers, n is the number of **digits** or bits, not the value. Checking whether a number N is prime by trying every divisor up to N is linear in the *value*, but N has only about log_2(N) bits, so it is exponential in the *size of the input* (worked through below).
- For a matrix, say whether n is the side length or the number of entries. A matrix with n rows and n columns has n × n = n^2 entries, so a 1,000 by 1,000 matrix has a million.

The number-size point is easy to get wrong, so here it is as a formula:

```formula
b = ⌊log_2(N)⌋ + 1
N ≈ 2^b
2^64 ≈ 1.8 × 10^19
where
N: the value of the number being tested, for example 1,000,003
b: the input size: how many bits (binary digits) it takes to write N down
log_2(N): the base-2 logarithm of N, the power you raise 2 to in order to get N
⌊x⌋: floor: round x down to the nearest whole number
2^b: 2 multiplied by itself b times
≈: approximately equal to; a 64-bit number can be as large as 2^64 − 1, about 1.8 × 10^19
In words: adding one bit doubles the largest value you can write, so a loop that runs once per unit of value runs about 2^b times: exponential in the number of bits.
```

When you describe an algorithm's cost, always say what n is.

## Why we ignore the small stuff

Counting precisely (n × (n − 1) / 2 comparisons rather than "about half of n squared") quickly becomes tedious and depends on what you call "one operation". So we make two simplifications. Here they are applied to the duplicate check's count:

```formula
C(n) = n × (n − 1) / 2
C(n) = 0.5 × n^2 − 0.5 × n
C(1000) = 500000 − 500
C(2 × n) ≈ 0.5 × 4 × n^2 = 4 × C(n)
where
C(n): the number of comparisons the pairwise duplicate check makes on n items
n: the number of items in the list
n^2: n squared, n × n
≈: approximately equal to (the small 0.5 × n term is ignored)
In words: the n-squared term is a thousand times bigger than the other term at n = 1,000, and doubling n multiplies it by four whatever the constant in front.
```

1. **Keep only the fastest-growing term.** In 0.5 × n^2 − 0.5 × n, the n^2 term dominates. At n = 1,000 it is 500,000 versus 500.
2. **Drop constant factors.** 0.5 × n^2 and 3 × n^2 grow in the same way: double n, quadruple the work. The constant depends on the machine and how you count; the growth shape does not.

The result is a coarse but robust label: "this algorithm is quadratic". The next lesson makes this precise with Big-O, Big-Omega and Big-Theta.

> [!warning] Constants are not irrelevant in practice
> Dropping constants is a tool for comparing growth, not a claim that constants never matter. An algorithm doing 100 × n operations loses to one doing n^2 (n × n) for every input size n below 100: at n = 50 that is 5,000 operations against 2,500. Lesson 7 covers when constants and hardware effects decide the winner.

## Key takeaways
- An algorithm is a finite, unambiguous, correct procedure. Many algorithms usually solve the same problem.
- Measure cost by counting basic operations as a function of input size n, not by timing alone.
- Nested loops over the same input of n items often give about n^2 (n × n) work; doubling n quadruples it.
- Growth rate dominates for large n. At a million items, the illustrative 10^8-operations-per-second model gives a fraction of a second for n log n and hours for n^2; actual timings require measurement.
- log_2(n) is the number of times you can halve n before reaching 1; it grows very slowly.
- Faster hardware gives a constant factor; better algorithms change the growth rate.
- Always say what n measures. For numbers, it is the number of digits or bits, not the value.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Algorithm)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [MIT 6.006 Introduction to Algorithms (OCW)](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
