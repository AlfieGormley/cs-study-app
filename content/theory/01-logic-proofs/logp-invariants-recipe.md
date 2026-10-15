---
id: logp-invariants-recipe
title: Loop invariants and a running sum
level: intermediate
minutes: 4
sourceLesson: logp-invariants
summary: Initialise the invariant, preserve it across the body and combine it with exit to establish the result.
---


Induction proves facts about recursive definitions. Many algorithms use loops that update variables. How do you prove a `while` loop is correct, for every input, without running it on every input?

The answer is a **loop invariant**: a statement about the program's variables that is true every time execution reaches the top of the loop. If it is true on entry, stays true after each iteration, and combined with the exit condition gives you what you wanted, the loop is correct. That is induction on the number of iterations, packaged for code.

Invariants are also the most practical piece of theory in this module. They are how you write binary search without off-by-one errors, what `assert` statements should check, and what keeps a heap a heap.

## The recipe

To prove a loop correct with invariant I, where B is the loop condition and Q is the goal (the **postcondition**, what should be true when the loop finishes):

1. **Invariant initialisation**: I holds before the first iteration.
2. **Invariant maintenance**: if I holds at the start of an iteration (and the loop condition B is true), it holds at the end.
3. **Loop termination**: when the loop exits, I plus the negated loop condition imply the goal.

In logic symbols, the three obligations are:

```formula
I_0
I ∧ B → I'
I ∧ ¬B → Q
where
I: the loop invariant, a true/false statement about the program's variables
I_0: the invariant evaluated on the starting values, before the first iteration
I': the invariant evaluated on the values after one run of the loop body
B: the loop condition (the test in `while B:`)
Q: the goal, what the loop should achieve
∧: AND: both are true
¬: NOT: ¬B means the loop condition is false, so the loop has exited
→: implies: "if the left side holds, the right side holds"
In words: the invariant starts true (line 1), survives every iteration that runs (line 2), and together with the failed loop test gives the goal (line 3).
```

Steps 1 and 2 are the base case and inductive step. Step 3 is where you cash in.

This proves **partial correctness**: *if* the loop stops, the answer is right. You also need **total correctness**: the loop *does* stop. For that, find a **loop variant** (or **ranking function**): an integer expression that is always is at least 0 and strictly decreases each iteration. A non-negative integer cannot decrease forever. Assuming each loop test and body execution finishes normally, this proves loop termination. More general well-founded orders can also supply ranking functions.


## A first example

Assume a finite list of integers that is not modified concurrently, exact arithmetic and normal execution without resource failures. Include 0 is at most i is at most len(a) in the invariant.

```python
def total(a):
    s, i = 0, 0
    # I: s == sum(a[:i])
    while i < len(a):
        # Include the next unprocessed item.
        s += a[i]
        # Grow the processed prefix by one.
        i += 1
    return s
```

The invariant and how one iteration changes the variables, written as maths:

```formula
s = sum(a[:i])
s' = sum(a[:i]) + a[i] = sum(a[:i + 1])
i' = i + 1
where
s: the running total so far
i: the loop index, how many items have been added
a: the list being summed
a[i]: the item at position i (counting from 0)
a[:i]: the first i items of a (a Python slice)
sum(...): the total of the items listed
s', i': the values of s and i at the end of the iteration
In words: s always holds the sum of the first i items. Adding item number i and moving i on by one keeps that true.
```

- **Init**: s equals 0 and a[:0] is empty, whose sum is 0. ✓
- **Maintain**: if s equals sum(a[:i]) at the start, the second and third lines above show the invariant holds again at the end. ✓
- **Terminate**: on exit i equals len(a) (the length of a), so s equals sum(a). ✓
- **Variant**: len(a) minus i, which is at least 0 and falls by 1 each time.

Notice where the invariant came from: it is the goal s equals sum(a) with the constant len(a) **replaced by the loop variable** i. That is the single most useful trick for finding invariants.


## Key takeaways
- Initialise the invariant, preserve it across the body and combine it with exit to establish the result.
- A decreasing non-negative integer variant proves termination when tests and body executions finish.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Loop invariant — Wikipedia](https://en.wikipedia.org/wiki/Loop_invariant)
