---
id: tech-recursion-contracts
title: Recursive contracts and progress
level: basic
minutes: 4
sourceLesson: tech-recursion
summary: State a domain, a base case and a measure that cannot decrease forever.
---

A function is **recursive** when its execution can call itself, directly or through other functions. To make a terminating recursive algorithm, use a well-founded progress measure: it can never decrease forever (no infinite decreasing chain). A common design has these two properties:

1. There is at least one **base case**: an input small enough to answer directly, with no further calls.
2. Every recursive call makes **progress** towards a base case.

Recursion is the foundation for the rest of this module. Divide and conquer, backtracking and (in a later module) dynamic programming are all recursive ways of thinking, even when the final code uses a loop.

## The shape of a recursive function

Summing the digits of a non-negative integer is a small example. The numerical functions below validate that domain; trees are assumed finite and acyclic.

```python
def digit_sum(n):
    # Reject inputs outside the stated
    # domain.
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
    # An empty subtree contributes no nodes.
    if node is None:
        return 0
    # Combine the two smaller subtree
    # answers.
    return 1 + count(node.left) \
             + count(node.right)
```

> [!tip] Define the function's contract first
> Write one sentence: "`count(node)` returns the number of nodes in the subtree rooted at `node`." The leap of faith is only safe if the contract is precise and every call respects it.

## Common pitfalls

- **Missing base case, or one that is never reached.** `fact(-1)` with base case `n == 0` recurses forever (until `RecursionError`). Reject negative input: changing the base case to `n <= 1` alone terminates but incorrectly returns 1 for negative factorials.
- **Not shrinking the input.** Calling `f(n)` from `f(n)` with a different flag still needs a measure that strictly decreases.
- **Repeated subproblems.** Exponential blow-up, as with naive `fib`.
- **Expensive arguments.** For a copied slice of length n, slicing lists or strings per call adds hidden O(n) work.
- **Shared mutable state.** Appending to one list across calls is fine, but remember every frame sees the same object (this matters a lot in backtracking).

## Key takeaways
- State a domain, a base case and a measure that cannot decrease forever.
- Trust smaller calls only after establishing their contract and progress.

## Further reading
- [Recursive algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
- [Recursion](https://en.wikipedia.org/wiki/Recursion_(computer_science))
