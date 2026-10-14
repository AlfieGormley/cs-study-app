---
id: cx-counting-work
sourceLesson: cx-growth-rates
title: Algorithms and counting work
level: basic
minutes: 4
summary: Count a scan with an explicit model of a basic operation.
---

An **algorithm** is a finite, precise sequence of steps that takes some input and produces an output. "Sort this list", "find the shortest route", "check whether this password matches" all have algorithms behind them.

For this introductory discussion, a deterministic algorithm that correctly solves a total problem should be:

- **Well defined**: every step is unambiguous. "Pick a good pivot" is not a step; "pick the middle element" is.
- **Finite**: it terminates on every valid input.
- **Correct**: it produces the right output for every valid input, not just the ones you tried.

There are usually many correct algorithms for the same problem. This module is about how to compare them, and the main currency is **how the amount of work grows as the input grows**.

## Why not just time it?

The obvious way to compare two programs is to run them and use a stopwatch. That is useful (the later lessons on complexity in practice explain how to do it well), but on its own it tells you little:

- The result depends on the machine, the language, the compiler and what else was running.
- It tells you about the input you tried, not the input you will get next year.
- It does not tell you *why* one is faster, so it does not tell you how to make it faster.

Instead, we **count the basic operations** an algorithm performs as a function of the input size, usually called **n**. A basic operation is anything that takes a fixed amount of time regardless of n: an arithmetic step, a comparison, reading or writing one array element, the overhead of a function call (its body must be counted separately). Arithmetic and comparisons are constant-cost only for bounded-size values in this model.

This simplified machine, where each basic step costs one unit and memory access is uniform, is called the **RAM model**. It is not perfectly true of real hardware (the later lessons on complexity in practice show where it breaks), but it is close enough to predict which algorithm will win as n gets large.

## Counting operations

Here is a function that adds up a list:

```python
# total([2, 3, 5]) returns 10.
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
T_loop(n) = 2n + 2
where
T(n): the number of basic operations total() performs on a list of n items (a count of steps, not seconds)
n: the input size, here the number of items in the list xs; a whole number with no unit
T_loop(n): the operation count when each loop pass also charges one overhead step
In words: one operation for each item in the list, plus two more for setting s to 0 and returning it.
```

You could also count one extra loop-overhead step per pass, as the second cost in the card does. Either way, doubling the list doubles the work. That is what we care about.

## Key takeaways
- A correct algorithm for a total problem uses unambiguous steps and terminates on every valid input.
- Count operations against an explicitly stated input size.
- The running-total example does one addition per item; timings also depend on the environment.

## Further reading
- [Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Algorithm)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
