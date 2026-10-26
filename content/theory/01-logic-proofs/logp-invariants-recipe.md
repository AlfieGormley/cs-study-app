---
id: logp-invariants-recipe
title: Loop invariants and a running sum
level: intermediate
minutes: 4
sourceLesson: logp-invariants
summary: Initialise the invariant, preserve it across the body and combine it with exit to establish the result.
---


Induction proves facts about recursive definitions. Many algorithms use loops that update variables. How do you prove a `while` loop is correct, for every input, without running it on every input?

The answer is a **loop invariant**: a statement about the program's variables that is true every time execution reaches the top of the loop. If it is true on entry, stays true after each iteration, and combined with the exit condition gives you what you wanted, the loop gives the right result if it finishes. Termination needs a separate argument. This is induction on the number of iterations, packaged for code.

Invariants are also the most practical piece of theory in this module. They are how you write binary search without off-by-one errors, what `assert` statements should check, and what keeps a heap a heap.

## The recipe

To prove a loop correct with invariant I, where B is the loop condition and Q is the goal (the **postcondition**, what should be true when the loop finishes):

1. **Invariant initialisation**: I holds before the first iteration.
2. **Invariant maintenance**: if I holds at the start of an iteration (and the loop condition B is true), it holds at the end.
3. **Exit consequence**: if the loop exits, I plus the negated loop condition imply the goal.

These obligations connect an intermediate state to the desired result:

The invariant must hold initially and be restored by each body execution. At exit, combine it with the false loop test to establish the postcondition.

Steps 1 and 2 are the base case and inductive step. Step 3 is where you cash in.

This proves **partial correctness**: *if* the loop stops, the answer is right. **Total correctness** also requires that the loop stops. For that, find a **loop variant** (or **ranking function**): a non-negative integer expression that strictly decreases each iteration. A non-negative integer cannot decrease forever. Assuming each loop test and body execution finishes normally, this proves loop termination. More general well-founded orders can also supply ranking functions.


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

What one iteration preserves:

The running total covers exactly the processed prefix. Adding the next item extends the total by one item; advancing the index extends the prefix by the same item. At the next loop test they agree again.

- **Init**: s equals 0 and a[:0] is empty, whose sum is 0. ✓
- **Maintain**: if s equals sum(a[:i]) at the start, adding the next item and advancing the index restores agreement with the processed prefix. ✓
- **Terminate**: on exit i equals len(a) (the length of a), so s equals sum(a). ✓
- **Variant**: len(a) minus i, which is at least 0 and falls by 1 each time.

Notice where the invariant came from: it is the goal s equals sum(a) with the constant len(a) **replaced by the loop variable** i. That is the single most useful trick for finding invariants.


## Key takeaways
- Initialise the invariant, preserve it across the body and combine it with exit to establish the result.
- A decreasing non-negative integer variant proves termination when tests and body executions finish.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Loop invariant — Wikipedia](https://en.wikipedia.org/wiki/Loop_invariant)
