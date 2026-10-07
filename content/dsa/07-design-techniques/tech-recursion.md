---
id: tech-recursion
title: Thinking recursively
level: basic
minutes: 12
summary: Base cases, the recursive leap of faith, what the call stack really does, tail recursion (and why Python won't optimise it), and how to turn recursion into a loop.
---

A function is **recursive** when its execution can call itself, directly or through other functions. To make a terminating recursive algorithm, use a well-founded progress measure: it must not admit an infinite decreasing chain. A common design has these two properties:

1. There is at least one **base case**: an input small enough to answer directly, with no further calls.
2. Every recursive call makes **progress** towards a base case.

Recursion is the foundation for the rest of this module. Divide and conquer, backtracking and (in a later module) dynamic programming are all recursive ways of thinking, even when the final code uses a loop.

## The shape of a recursive function

Summing the digits of a non-negative integer is a small example. The numerical functions below validate that domain; trees are assumed finite and acyclic.

```python
def digit_sum(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 10:              # base case
        return n
    # recursive case: last digit plus the
    # digit sum of everything before it
    return n % 10 + digit_sum(n // 10)

print(digit_sum(4096))      # 19
```

Each call strips one digit, so the input shrinks and must eventually fall below 10. That is the progress guarantee.

Almost every recursive function follows the same recipe:

- **Identify the smallest inputs** (empty list, 0, a leaf node, a single character) and answer them directly.
- **Assume the function already works** for anything smaller than the current input.
- **Combine** that smaller answer with a little local work to answer the current input.

## The leap of faith

The second step is the one beginners resist. When you write `digit_sum(n // 10)`, you should *not* try to trace every call in your head. Instead, trust that it returns the right digit sum for the shorter number, and only check that your combining step is correct.

This is exactly **proof by induction**:

| Induction | Recursion |
|---|---|
| Base case holds | Base case returns correctly |
| Assume true for k | Trust the smaller call |
| Prove for k + 1 | Combine into the answer |

Thinking this way scales. To count nodes in a binary tree, you say: an empty tree has 0 nodes; otherwise it has 1 plus the count of the left subtree plus the count of the right subtree. The correctness argument need not trace every depth; resource usage still depends on the height.

```python
def count(node):
    if node is None:
        return 0
    return 1 + count(node.left) \
             + count(node.right)
```

> [!tip] Define the function's contract first
> Write one sentence: "`count(node)` returns the number of nodes in the subtree rooted at `node`." The leap of faith is only safe if the contract is precise and every call respects it.

## What the call stack actually does

The leap of faith is how you *design* recursion. To *debug* it, and to understand its cost, you need the machine's view.

Conceptually, a pending call has a **stack frame** holding parameters, local state and where execution resumes. Implementations can inline calls or eliminate tail calls; the examples here use ordinary CPython frames. A returned frame may remain referenced by debugging or traceback objects. Here is `fact(3)` at its deepest point:

```python
def fact(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n <= 1:
        return 1
    return n * fact(n - 1)
```

```
 top   fact(1)  returns 1
       fact(2)  waiting: 2 * ?
       fact(3)  waiting: 3 * ?
 base  <module>
```

Then the stack unwinds: `fact(1)` returns 1, `fact(2)` computes 2 × 1 = 2, `fact(3)` computes 3 × 2 = 6.

Two consequences follow:

- **Space is proportional to depth.** With constant-sized frame state, depth d costs O(d) control-stack space. Retained lists, arbitrary-size integers and other objects must be counted separately. A recursive function over a linked list of length n uses O(n) space; over a balanced tree of n nodes, O(log n).
- **Work after the call happens on the way back up.** Along a single call chain, code before the call runs on descent and code after it runs on return; multiple recursive branches are completed in their program order.

```python
def show(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n == 0:
        return
    print(n, end=" ")    # on the way down
    show(n - 1)
    print(n, end=" ")    # on the way up

show(3)   # 3 2 1 1 2 3
```

### Python's recursion limit

CPython limits active recursion and raises `RecursionError` when the configured allowance is exhausted. The usual default is **1000**; inspect `sys.getrecursionlimit()` rather than assuming how many calls remain. Since CPython 3.11, most Python-to-Python calls no longer consume C stack per call. Raising the limit still increases memory/resource exposure, and calls involving C code can have separate stack limits; the documentation warns that an excessively high setting can crash the process.

In practice: a million-node binary tree with near-minimum height has about 20 levels, well below the usual recursion allowance when entered from a shallow call stack. Recursion over a list, a string, or a tree that might degenerate into a chain is a bug waiting for large input.

## The cost of recursion: recursion trees

When a function makes more than one recursive call, draw the **recursion tree** to estimate its cost. Each non-base invocation of naive Fibonacci makes two recursive calls:

```python
def fib(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

```
            fib(4)
          /        \
      fib(3)       fib(2)
      /    \       /    \
  fib(2) fib(1) fib(1) fib(0)
  /    \
fib(1) fib(0)
```

`fib(4)` makes 9 calls, `fib(5)` 15, `fib(30)` over 2.6 million. The total grows roughly like 1.618ⁿ because the same subproblems are solved again and again. Caching results (memoisation) reduces this to O(n) additions; integer bit costs grow with n, so this is not an O(n) bit-time claim; that idea is the heart of the dynamic programming module.

> [!warning] Hidden O(n) work per call
> `return xs[0] + total(xs[1:])` looks linear, but each slice copies the list. The slices copy (n−1) + (n−2) + ... + 0 = n(n−1)/2 references, giving O(n²) time with constant-cost element addition, and because every frame holds its slice until it returns, O(n²) memory at peak. Pass an index instead of slicing.

## Tail recursion

A call is a **tail call** if it is the very last thing a function does: its result is returned directly, with no work left to do afterwards.

- `return n * fact(n - 1)` is **not** a tail call: the multiplication happens after the call returns.
- `return fact_acc(n - 1, acc * n)` **is** a tail call.

You can often make a function tail-recursive by passing an **accumulator** that carries the partial result down:

```python
def fact_acc(n, acc=1):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    if n <= 1:
        return acc
    return fact_acc(n - 1, acc * n)
```

Why care? Because a tail call needs nothing from the current frame afterwards, so a language can **reuse the frame** instead of pushing a new one. This is **tail-call optimisation (TCO)**, and it turns tail recursion into a loop with O(1) stack space. Scheme requires it by its standard; many functional language implementations rely on it; C compilers such as GCC and Clang often perform it at higher optimisation levels, but the C standard doesn't guarantee it.

### Python does not do TCO

CPython does not eliminate Python-level tail calls. `fact_acc(10000)` still raises `RecursionError` with the usual default allowance, accumulator or not.

Guido van Rossum explained the decision in 2009: eliminating frames would destroy useful **tracebacks**, and he considers recursion a less fundamental tool than iteration in Python. So in Python, rewriting as tail recursion does not by itself eliminate control-stack growth; its value is that it makes the next step, converting to a loop, mechanical.

## Converting recursion to iteration

### Tail recursion becomes a loop

A tail-recursive function maps directly onto a `while` loop: the parameters become variables, and the tail call becomes reassignment.

```python
def fact_iter(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    acc = 1
    while n > 1:     # not yet base case
        n, acc = n - 1, acc * n
    return acc
```

### General recursion needs an explicit stack

When there are several recursive calls or work after the call, replace the call stack with your own list. This pre-order traversal avoids the interpreter recursion limit; its maximum usable input is still constrained by memory and execution time:

```python
def preorder(root):
    out, stack = [], [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        out.append(node.val)
        # push right first so left
        # is popped (visited) first
        stack.append(node.right)
        stack.append(node.left)
    return out
```

A Python list stores pending work in dynamically allocated memory. General simulations can retain a resume point or a visited flag; specialised traversals sometimes need fewer entries. This routine also stores O(n) output. The following table counts control-stack entries, assuming constant-sized entries; it excludes retained data and output.

| Approach | Stack space | Clarity |
|---|---|---|
| Plain recursion | O(depth), capped | High |
| Tail rec. + TCO | O(1) | High |
| Loop replacing self tail calls | O(1) | Medium |
| Explicit stack | O(depth), heap | Lower |

## Common pitfalls

- **Missing or unreachable base case.** `fact(-1)` with base case `n == 0` recurses forever (until `RecursionError`). Reject negative input: changing the base case to `n <= 1` alone terminates but incorrectly returns 1 for negative factorials.
- **Not shrinking the input.** Calling `f(n)` from `f(n)` with a different flag still needs a measure that strictly decreases.
- **Repeated subproblems.** Exponential blow-up, as with naive `fib`.
- **Expensive arguments.** Slicing lists or strings per call adds hidden O(n) work.
- **Shared mutable state.** Appending to one list across calls is fine, but remember every frame sees the same object (this matters a lot in backtracking).

## Key takeaways
- A recursive function needs a base case and guaranteed progress towards it.
- Design with the leap of faith: trust the smaller call, verify the combining step. It's induction.
- With constant-sized frame state, control-stack space is O(depth); retained data is additional. CPython usually starts with recursion limit 1000, but it is configurable.
- Tail calls can reuse the frame (TCO) in some languages, but CPython does not do this for Python function calls.
- Convert tail recursion to a loop by reassigning parameters; convert general recursion with an explicit stack.

## Further reading
- [Recursion (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Recursion_(computer_science))
- [Jeff Erickson, Algorithms, chapter 1: Recursion (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Tail call — Wikipedia](https://en.wikipedia.org/wiki/Tail_call)
- [Guido van Rossum: Tail Recursion Elimination](https://gvanrossum.github.io/neopythonic/tail-recursion-elimination.html)
- [sys.setrecursionlimit — Python docs](https://docs.python.org/3/library/sys.html)
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)
