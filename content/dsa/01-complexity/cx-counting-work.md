---
id: cx-counting-work
sourceLesson: cx-growth-rates
title: Algorithms and counting work
level: basic
minutes: 2
summary: Count a scan with an explicit model of a basic operation.
---

An algorithm is a precise procedure for carrying out a task. Before comparing speed, establish what inputs are valid and what answer is required. For the terminating problems in this module, a correct solution must finish and return the right answer on every valid input. Passing a few tests is evidence, not a proof of that guarantee.

## Count the work that repeats

Timings tell you how one implementation behaves on one machine. Counting operations explains how its workload changes when the input grows. Here n is the number of list items.

```python
# total([2, 3, 5]) returns 10.
def total(xs):
    s = 0
    for x in xs:
        s += x
    return s
```

This scan adds each item once. Doubling a long list roughly doubles the additions. Initialising and returning the total add fixed overhead; they do not change that linear growth.

A **cost model** states what counts as one step. A simple RAM model treats a bounded-size comparison, arithmetic operation or memory access as constant cost. Counting loop overhead changes the coefficient, but this scan remains linear. A function call also includes the work its body performs.

Python integers can grow to many digits, and comparing long strings may inspect many characters. Treating those operations as constant cost is an explicit simplification, not a property of every Python value. Real memory access and allocation also have costs the simple model omits.

> [!analogy] Real-world analogy: Checking a guest list
> Checking each printed name once takes more work when the list grows.
>
> **How it maps:** One check per name corresponds to one addition per input item; picking up the list is fixed setup work.
>
> **Where it stops:** Human checks vary in duration. The algorithm model counts specified operations and must state which have constant cost.

## Key takeaways
- Correctness and termination come before efficiency.
- Define input size and the operation being counted.
- One pass with constant work per item has linear growth.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
