---
id: test-path-coverage-limits
sourceLesson: test-flaky-coverage-mutation
title: Find the gaps left by full branch coverage
level: advanced
minutes: 3
summary: Full branch coverage can miss combinations of decisions and their path-specific faults.
---

The preceding shipping example starts with a cost of 5, makes the base free for totals of at least 50, and adds 10 for express shipping. A single test exercised both true outcomes; now consider what remains untested even after both outcomes of each decision have run.

Even full branch coverage doesn't cover every **execution path**, a complete route from the function's entry to its exit. Two independent `if`s give four paths (under or over £50, times express or not) but only four branch outcomes. Each extra independent `if` doubles the number of paths while adding just two branch outcomes: ten such `if`s in a row give 1,024 possible paths but only 20 branch outcomes. That doubling assumes every combination of outcomes is possible; when conditions depend on each other, some paths are infeasible and the real count is lower. Loops can produce unbounded paths. Full path coverage is often infeasible, though finite small regions can be exhaustively exercised.

Two tests, `(60, True)` and `(10, False)`, take all four branch outcomes but only two of the four paths. If `cost += 10` becomes `cost = 10`, those tests still pass: the first starts express pricing from zero and the second skips it. Only a paid-base express case such as `(10, True)` distinguishes 15 from the incorrect 10.

> [!analogy] Real-world analogy: every junction versus every route
> A delivery driver may have taken both the left and the right turn at every junction in town without ever driving one particular combination of turns, such as left at the first junction then right at the second.
>
> **How it maps:** Junctions are decisions (`if` statements), each turn taken is a branch outcome, and a whole trip from depot to doorstep is an execution path. Branch coverage asks "has every turn been taken at least once?"; path coverage asks "has every whole route been driven?". The `cost = 10` bug lives on one route: under £50, then express.
>
> **Where it stops:** Some combinations of turns are impossible on a real map and in code alike, but loops in code can repeat a junction any number of times, giving unbounded routes. And taking a route is not the same as checking the delivery arrived: coverage of any kind records what ran, not whether the result was asserted.

## What coverage tells you, and what it doesn't

Coverage is excellent at one thing: showing code **no test executes**. If the branch that handles a failed payment has 0% coverage, you know it is untested.

It cannot tell you that covered code is well tested. Coverage counts execution, not checking. A test that calls every function and asserts nothing has high coverage and catches almost nothing.

> [!note] Goodhart's law
> Named after the economist Charles Goodhart, and usually quoted in the wording used by the anthropologist Marilyn Strathern in a 1997 paper: "When a measure becomes a target, it ceases to be a good measure." Mandate 90% coverage and you get tests written to raise the number: assertion-free calls, tests of trivial getters, tests coupled to implementation. Google's published guidance offers 60% as "acceptable", 75% "commendable" and 90% "exemplary", but explicitly avoids organisation-wide mandates.

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
