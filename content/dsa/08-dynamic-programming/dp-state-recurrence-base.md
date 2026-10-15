---
id: dp-state-recurrence-base
title: Define states, transitions and base cases
level: basic
minutes: 4
summary: State definitions explain exactly which subproblem a table cell represents.
sourceLesson: dp-method
---

The goal is to describe subproblems precisely enough that cached answers remain valid. A state is a contract: equal states must require equal answers.

Defining the state and recurrence is often the hardest part of a DP problem. A systematic method helps make those decisions explicit.

Here are five questions to answer, in order. Write the answers down in plain English before you write any code.

1. **State**: what does `dp[...]` mean, exactly?
2. **Recurrence**: how is one state computed from smaller ones?
3. **Base cases**: which states can be answered directly?
4. **Order**: in what order must states be evaluated?
5. **Answer and reconstruction**: which state holds the answer, and how do you recover the actual choices, not just the number?

Then add a sixth, quick step: **complexity**: count the states and the work per state.

## Step 1: define the state

The state is the set of parameters that describes a subproblem. It must capture **everything the future depends on**. Extra information can increase cost even when the state remains correct.

A good test: "If I know only these values, can I solve the rest of the problem optimally without knowing how I got here?" If yes, you have a valid state. If the answer also depends on something else (a previous choice, a remaining budget), that something must join the state.

Common state shapes:

| Input | Typical state |
|---|---|
| One sequence | prefix `i` or suffix `i` |
| Two sequences | pair `(i, j)` |
| Sequence, ranges | interval `(i, j)` |
| Items + budget | `(i, capacity)` |
| Tree | node `v` (+ flag) |
| Small set | bitmask |

Write the definition as a full sentence: "`ok[i]` is True if the suffix `s[i:]` can be split into dictionary words." Vague definitions ("`dp[i]` is the answer at i") are the root of most wrong recurrences.

## Step 2: the recurrence

Ask: **what is the first (or last) decision**, and what are the options? Each option leads to a smaller subproblem. Combine the results with whatever the question asks for:

- "minimum/maximum" → `min` / `max` over options
- "how many ways" → **sum** over options (they must be disjoint, or you'll double-count)
- "is it possible" → **or** over options

## Step 3: base cases

The smallest states, where no decision is left: an empty string, a zero weight limit, a single element. Also decide what an **impossible** state returns: `0` for counting, `False` for feasibility, `+∞` (positive infinity, a value worse than any real cost) for minimisation, and `−∞` (negative infinity, worse than any real profit) for maximisation. In Python these are `float('inf')` and `-float('inf')`. A `min` never picks `+∞` when a real option exists, and a `max` never picks `−∞`, so impossible options drop out automatically.

## Apply the state test: decoding digits

Suppose codes from 1 through 26 represent letters A through Z. Define one state per suffix: the number of ways to decode the digits from that position onwards. A suffix starting with zero is impossible. Otherwise a one-digit code is valid; a two-digit code is another disjoint first choice only when its value is between 10 and 26.

```formula
d[n] = 1
d[i] = 0   if s_i = "0"
d[i] = d[i + 1]   if s_i ≠ "0"
  and t_i = 0
d[i] = d[i + 1] + d[i + 2]
  if s_i ≠ "0" and t_i = 1
where
d[i]: the number of valid decodings of the suffix starting at position i
s_i: the digit at zero-based position i in the input
i: a suffix starting position, from zero through n; the last line applies only before n
n: the number of input digits
t_i: one when the two digits starting at i form a code from 10 through 26, otherwise zero; it is zero at the final digit
≠: not equal to
In words: The empty suffix has one completion. Other nonzero starts count the one-digit continuation plus any valid two-digit continuation.
```

For `"106"`, the zero cannot start a code, so the only split is `"10", "6"`. Evaluate suffixes from the end towards the beginning so each continuation is ready. The separate one-digit case avoids reading beyond the table at the final digit.

## Key takeaways
- State definitions explain exactly which subproblem a table cell represents.
- Choose min/max, sum over disjoint alternatives, or logical OR to match the question.
- Impossible states need a sentinel value that cannot beat a feasible answer.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
