---
id: tech-recursion-tail-calls
title: Tail calls and accumulators
level: basic
minutes: 2
sourceLesson: tech-recursion
summary: A tail call returns its result without pending work.
---

## Tail recursion

A call is a **tail call** if it is the very last thing a function does: its result is returned directly, with no work left to do afterwards.

- `return n * fact(n - 1)` is **not** a tail call: the multiplication happens after the call returns.
- `return fact_acc(n - 1, acc * n)` **is** a tail call.

You can often make a function tail-recursive by passing an **accumulator** that carries the partial result down:

```python
def fact_acc(n, acc=1):
    # Reject inputs outside the stated
    # domain.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n <= 1:
        return acc
    # Carry the product into the next call.
    return fact_acc(n - 1, acc * n)
```

> [!analogy] Real-world analogy: passing on an enquiry
> At a help desk, one clerk takes your question, adds a note to your file and sends you to the next desk, then forgets about you: the next desk will give you the final answer. Another clerk sends you to the next desk but insists you come back so they can add a fee to whatever that desk tells you.
>
> **How it maps:** the first clerk is making a tail call: nothing is left to do after handing you on, so their desk (the frame) can be reused at once. The note in your file is the accumulator carrying the partial result forward. The second clerk is a non-tail call such as `n * fact(n - 1)`: their desk must stay occupied until the answer comes back.
>
> **Where it stops:** a clerk can always walk away. Whether a program actually frees the frame depends on the language implementation: Scheme guarantees it, C compilers may do it, and CPython never does.

Why care? Because a tail call needs nothing from the current frame afterwards, so a language can **reuse the frame** instead of pushing a new one. This is **tail-call optimisation (TCO)**, and it turns tail recursion into a loop with O(1) stack space. The Scheme programming language requires it by its standard; many functional language implementations rely on it; C compilers such as GCC and Clang often perform it at higher optimisation levels, but the C standard doesn't guarantee it.

### Python does not do TCO

CPython does not eliminate Python-level tail calls. `fact_acc(10000)` still raises `RecursionError` with the usual default allowance, accumulator or not.

Guido van Rossum explained the decision in 2009: eliminating frames would destroy useful **tracebacks**, and he considers recursion a less fundamental tool than iteration in Python. So in Python, rewriting as tail recursion does not by itself eliminate control-stack growth; its value is that it makes the next step, converting to a loop, mechanical.

## Key takeaways
- A tail call returns its result without pending work.
- An accumulator does not remove Python call frames; tail-call elimination is an implementation property.

## Further reading
- [Guido van Rossum: Tail Recursion Elimination](https://gvanrossum.github.io/neopythonic/tail-recursion-elimination.html)
- [Scheme standard](https://standards.scheme.org/r7rs-html5/index.html)
