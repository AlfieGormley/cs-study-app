---
id: test-path-coverage-limits
sourceLesson: test-flaky-coverage-mutation
title: Find the gaps left by full branch coverage
level: advanced
minutes: 3
summary: Full branch coverage can miss combinations of decisions and their path-specific faults.
---

The preceding shipping example starts with a cost of 5, makes the base free for totals of at least 50, and adds 10 for express shipping. A single test exercised both true outcomes; now consider what remains untested even after both outcomes of each decision have run.

Even full branch coverage doesn't cover every **execution path**, a complete route from the function's entry to its exit. Two independent `if`s give four paths (under or over £50, times express or not). Each extra independent `if` doubles the number of paths but adds only two branch outcomes:

```formula
N_paths = 2^k
N_paths = 2^2 = 4
N_br = 2 × k = 2 × 2 = 4
where
k: the number of independent if statements in a row, each without an else-if chain and with no loops; here 2
N_paths: the number of distinct routes through the code, one for each combination of true and false outcomes
N_br: the number of branch outcomes, a true and a false for each if
^: raise to a power: 2^k means k twos multiplied together
In words: with two ifs there are four paths and four branch outcomes, but with ten ifs there would be 1,024 paths and only 20 branch outcomes.
```

Two tests, `(60, True)` and `(10, False)`, take all four branch outcomes but only two of the four paths. If `cost += 10` becomes `cost = 10`, those tests still pass: the first starts express pricing from zero and the second skips it. Only a paid-base express case such as `(10, True)` distinguishes 15 from the incorrect 10. The formula assumes every combination of outcomes is possible; when conditions depend on each other, some paths are infeasible and the real count is lower. Loops can produce unbounded paths. Full path coverage is often infeasible, though finite small regions can be exhaustively exercised.

## What coverage tells you, and what it doesn't

Coverage is excellent at one thing: showing code **no test executes**. If the error-handling branch for a failed payment has 0% coverage, you know it is untested.

It cannot tell you that covered code is well tested. Coverage counts execution, not checking. A test that calls every function and asserts nothing has high coverage and catches almost nothing.

> [!note] Goodhart's law
> "When a measure becomes a target, it ceases to be a good measure." Mandate 90% coverage and you get tests written to raise the number: assertion-free calls, tests of trivial getters, tests coupled to implementation. Google's published guidance offers 60% as "acceptable", 75% "commendable" and 90% "exemplary", but explicitly avoids organisation-wide mandates.

Practical uses that work well:

- Look at **uncovered lines in the diff** during code review, and ask whether they matter.
- Watch for **coverage dropping** on a change, which often means new code arrived without tests.
- Use branch coverage, not just line coverage.


## Key takeaways
- Full branch coverage can miss combinations of decisions and their path-specific faults.
- Path counts grow quickly only when the model’s decision combinations are feasible.
- Use uncovered code to guide review instead of treating a percentage as proof.

## Further reading
- [Branch coverage measurement — coverage.py](https://coverage.readthedocs.io/en/latest/branch.html)
- [Code Coverage Best Practices — Google Testing Blog](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
- [Test Coverage — Martin Fowler](https://martinfowler.com/bliki/TestCoverage.html)
