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

Roughly `n + 2` operations. You could argue the loop itself costs something per pass, making it `2n + 2`. It doesn't matter: either way, doubling the list doubles the work. That is what we care about.

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

In the worst case (no duplicates), how many comparisons? When `i = 0`, the inner loop runs `n - 1` times; when `i = 1`, `n - 2` times; and so on down to 0. The total is

```
(n-1) + (n-2) + ... + 1 + 0
  = n(n-1)/2
```

For `n = 5` that is 10 comparisons. For `n = 1,000` it is 499,500. For `n = 1,000,000` it is about 500 billion. Doubling n roughly **quadruples** the work.

A different approach is to sort the list first and then compare neighbours, since duplicates end up next to each other. Good sorting algorithms take about `n log n` operations (later modules show how). Another is to put each item in a hash set and stop if it is already there, which is about `n` operations on average. Same problem, three very different growth rates.

## Growth rates

The function that describes how the operation count grows is the algorithm's **growth rate**. Here are the common ones side by side (logs are base 2, values rounded):

| f(n) | n = 10 | n = 1,000 | n = 10^6 |
|---|---|---|---|
| log n | 3 | 10 | 20 |
| n | 10 | 1,000 | 10^6 |
| n log n | 33 | 10^4 | 2 x 10^7 |
| n^2 | 100 | 10^6 | 10^12 |
| 2^n | 1,024 | 10^301 | absurd |

Two things jump out.

First, **for small n, nothing matters much.** At n = 10, even `2^n` is only about a thousand steps. This is why a naive algorithm often works fine in testing.

Second, **for large n, the growth rate is everything.** Suppose a machine does about 10^8 simple operations per second (an illustrative assumed rate, not a general hardware benchmark). At n = 10^6:

| Growth | Operations | Time |
|---|---|---|
| n | 10^6 | 0.01 s |
| n log n | 2 x 10^7 | 0.2 s |
| n^2 | 10^12 | ~2.8 hours |

The quadratic algorithm is not "a bit slower". It is the difference between instant and unusable.

> [!example] The production surprise
> A team writes the pairwise `has_dup` check for a feature that validates uploaded CSV files. In testing, files have 200 rows: 19,900 comparisons, unnoticeable. A customer uploads 2 million rows: about 2 x 10^12 comparisons. The request times out, retries, and takes the worker pool with it. Nothing was "wrong" with the code except its growth rate.

## Faster hardware does not save you

It is tempting to think a faster computer fixes a slow algorithm. Look at what a machine that is **10 times faster** buys you, in terms of the largest input you can handle in the same time:

| Growth | Old max n | New max n |
|---|---|---|
| n | N | 10N |
| n^2 | N | ~3.16N |
| n^3 | N | ~2.15N |
| 2^n | N | N + 3.3 |

For a quadratic algorithm, 10x the speed gives you only `sqrt(10)`, about 3.16x the input. For an exponential algorithm, it adds about 3 to n (because `2^3.3` is about 10). Better algorithms routinely give improvements of thousands or millions of times; hardware gives you a constant factor.

## What "input size" means

n should measure whatever drives the work. Usually it is obvious, but not always:

- For a list or string, n is its length.
- For a graph, the cost often depends on both vertices **V** and edges **E**, so you state both (for example "V + E").
- For arithmetic on big numbers, n is the number of **digits** or bits, not the value. Checking whether a number N is prime by trying every divisor up to N is linear in the *value*, but N has only about `log2 N` bits, so it is exponential in the *size of the input*.
- For a matrix, say whether n is the side length or the number of entries. An `n x n` matrix has `n^2` entries.

When you describe an algorithm's cost, always say what n is.

## Why we ignore the small stuff

Counting precisely (`n(n-1)/2` versus `0.5n^2`) quickly becomes tedious and depends on what you call "one operation". So we make two simplifications:

1. **Keep only the fastest-growing term.** In `n(n-1)/2 = 0.5n^2 - 0.5n`, the `n^2` term dominates. At n = 1,000 it is 500,000 versus 500.
2. **Drop constant factors.** `0.5n^2` and `3n^2` grow in the same way: double n, quadruple the work. The constant depends on the machine and how you count; the growth shape does not.

The result is a coarse but robust label: "this algorithm is quadratic". The next lesson makes this precise with Big-O, Big-Omega and Big-Theta.

> [!warning] Constants are not irrelevant in practice
> Dropping constants is a tool for comparing growth, not a claim that constants never matter. An algorithm doing `100n` operations loses to one doing `n^2` for every n below 100. Lesson 7 covers when constants and hardware effects decide the winner.

## Key takeaways
- An algorithm is a finite, unambiguous, correct procedure. Many algorithms usually solve the same problem.
- Measure cost by counting basic operations as a function of input size n, not by timing alone.
- Nested loops over the same input often give about n^2 work; doubling n quadruples it.
- Growth rate dominates for large n. At n = 10^6, the illustrative 10^8-operations/s model gives a fraction of a second for n log n and hours for n^2; actual timings require measurement.
- Faster hardware gives a constant factor; better algorithms change the growth rate.
- Always say what n measures. For numbers, it is the number of digits or bits, not the value.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Algorithm)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [MIT 6.006 Introduction to Algorithms (OCW)](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
