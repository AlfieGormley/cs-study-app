---
id: logp-induction-bases-recursion
title: Choosing a base and proving recursive code
level: intermediate
minutes: 3
sourceLesson: logp-induction
summary: A valid step proves nothing without a true base case in its range.
---

## Choosing the first true case

### Example: the base case matters

Claim: 2 to the power n is greater than n squared for all integers n at least 5 (2 to the power n is n copies of 2 multiplied together, n squared is n times n).

**Base case**, n equals 5: 2 to the power five equals 32 and 5 squared equals 25, and 32 is greater than 25. ✓

**Step**: assume 2 to the power n is greater than n squared for some integer n at least 5. Doubling both sides gives the first line below; the rest shows that 2n squared is at least (n plus 1) squared:

```formula
2^{n+1} = 2 × 2^n > 2n^2
2n^2 ≥ (n + 1)^2 = n^2 + 2n + 1
  iff n^2 ≥ 2n + 1
n^2 ≥ 3n = 2n + n > 2n + 1
  for n ≥ 3
where
n: an integer with 2^n > n^2 assumed (the inductive hypothesis)
2^n: n copies of 2 multiplied together
n^2: n multiplied by itself
>, ≥: is greater than, is greater than or equal to
In words: doubling 2^n keeps it above 2n², and 2n² is at least (n + 1)² whenever n ≥ 3, so 2^{n+1} > (n + 1)².
```

So 2 to the power (n plus one) is greater than (n plus 1) squared. ∎

The inductive step works for every integer n at least 3, yet the claim is **false** at n equals 3 (2 cubed equals 8 is less than 3 squared equals 9) and at n equals 4 (2 to the power four equals 16 equals 4 squared equals 16). Without a correct base case, a valid step proves nothing. The dominoes are lined up, but the first one you push must actually fall.


## Recursion is induction

Here is a recursive function and its correctness proof side by side.

```python
def total(xs):
    # An empty list ends the recursion.
    if not xs:
        return 0
    # Add the head to the smaller tail sum.
    return xs[0] + total(xs[1:])
```

In an ideal execution model, total(xs) returns the exact sum of any finite integer list. Induct on the length n of the list. Actual Python has a recursion limit and finite resources; this slicing implementation also copies Θ(n squared) list elements overall (a number of copies that grows like n squared). Floating-point addition does not obey all exact-arithmetic rearrangements.

- **Base, n equals 0**: the empty list returns 0, its sum. ✓
- **Step**: assume `total` is correct on all lists of length n. A list of length n plus 1 returns `xs[0] + total(xs[1:])`. The tail has length n, so by the IH that call returns the tail's sum. Adding `xs[0]` gives the whole sum. ✓

That is exactly the "leap of faith" you make when writing recursion: trust the recursive invocation on a smaller input. Induction is what makes the leap legitimate. It also tells you what can go wrong: a missing base case, or a recursive invocation that is not on a smaller input, breaks the proof and usually the program.


## Key takeaways
- A valid step proves nothing without a true base case in its range.
- Recursive correctness needs correct smaller calls, a reachable base and an execution model that permits the calls.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Strong induction — Wikipedia](https://en.wikipedia.org/wiki/Strong_induction)
