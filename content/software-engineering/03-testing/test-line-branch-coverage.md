---
id: test-line-branch-coverage
sourceLesson: test-flaky-coverage-mutation
title: Read line and branch coverage reports
level: advanced
minutes: 3
summary: Coverage records execution rather than the adequacy of assertions.
---

Once failures are trustworthy, ask which code the suite actually exercises. Coverage helps locate missing execution, but a high percentage cannot establish that assertions detect wrong results.

## Code coverage

**Code coverage** measures which parts of the code ran while the tests ran. In Python the standard tool is **coverage.py** (`pytest --cov` via pytest-cov).

### Line versus branch coverage

```python
def shipping_cost(total, express):
    cost = 5
    # At 50 or above, base shipping is free.
    if total >= 50:
        cost = 0
    # Express adds to the chosen base cost.
    if express:
        cost += 10
    return cost

def test_free_express():
    # Both conditions take the true branch.
    assert shipping_cost(60, True) == 10
```

Every line runs, so **line (statement) coverage is 100%**: all seven executable statements (the `def` line plus six body lines) ran at least once. Yet we never tested an order under £50, or a non-express order.

**Branch coverage** tracks alternatives between measured source lines; for these two if statements, each has a true and false outcome. It does not necessarily distinguish every short-circuited boolean subexpression. Our test only took the true side of both. If only the seven-statement function is in shipping.py and a separately measured driver invokes it, coverage.py can report the following. Including the test function or driver in the measured file changes the statement total:

```
Stmts Miss Branch BrPart Cover Missing
    7    0      4      2   82% 4->7, 7->9
```

`4->7` means "line 4’s `if` never jumped straight to line 7" (the condition was never false), and similarly for `7->9`. Those two missing jumps are the useful part of the report: they name the cases no test reached, an order under £50 and a non-express order.

The 82 % needs care. In branch mode, coverage.py counts each executable statement and each possible branch outcome as one opportunity and reports the share exercised: here 7 statements plus 2 of the 4 branch outcomes, 9 of 11. So the figure is neither line coverage (100 %) nor branch-outcome coverage (2 of 4, 50 %), but a blend of the two. Whatever the number, it says only what ran: a test with no assertions at all would produce the same report.

## Key takeaways
- Coverage records execution rather than the adequacy of assertions.
- Line coverage counts executed statements; branch measurement also tracks alternative transitions.
- coverage.py combines statement and branch opportunities in its branch-mode percentage.

## Further reading
- [Branch coverage measurement — coverage.py](https://coverage.readthedocs.io/en/latest/branch.html)
- [Code Coverage Best Practices — Google Testing Blog](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
