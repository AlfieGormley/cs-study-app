---
id: test-line-branch-coverage
sourceLesson: test-flaky-coverage-mutation
title: Read line and branch coverage reports
level: advanced
minutes: 4
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

Every line runs, so **line (statement) coverage is 100%**. Line coverage is the share of executable statements that ran at least once:

```formula
C_line = s_run / s × 100 %
C_line = 7 / 7 × 100 % = 100 %
where
C_line: line (statement) coverage, as a percentage
s: the number of executable statements in the measured code, here 7 (the def line plus six body lines)
s_run: how many of those statements ran at least once during the tests, here all 7
%: per cent, parts per hundred
In words: all seven statements of shipping_cost ran, so line coverage is 100 %.
```

Yet we never tested an order under £50, or a non-express order.

**Branch coverage** tracks alternatives between measured source lines; for these two if statements, each has a true and false outcome. It does not necessarily distinguish every short-circuited boolean subexpression. Our test only took the true side of both. If only the seven-statement function is in shipping.py and a separately measured driver invokes it, coverage.py can report the following. Including the test function or driver in the measured file changes the statement total:

```
Stmts Miss Branch BrPart Cover Missing
    7    0      4      2   82% 4->7, 7->9
```

`4->7` means "line 4’s `if` never jumped straight to line 7" (the condition was never false), and similarly for `7->9`. In branch mode, coverage.py puts statements and branch outcomes into one percentage:

```formula
C = (s_run + b_taken) / (s + b) × 100 %
C = (7 + 2) / (7 + 4) × 100 %
C = 9 / 11 × 100 % ≈ 82 %
where
C: the combined coverage percentage coverage.py reports in its Cover column when branch measurement is on
s: the number of executable statements measured, here 7
s_run: how many of those statements ran, here all 7
b: the number of possible branch outcomes, here 4: the true and the false outcome of each of the two if statements
b_taken: how many of those outcomes the tests actually took, here 2 (the true side of each if)
%: per cent, parts per hundred
≈: approximately equal to (9/11 is 81.8 %, shown rounded)
In words: 9 of the 11 statements and branch outcomes were exercised, so the report shows 82 %, even though line coverage alone is 100 %.
```

Counting branch outcomes alone, the test took 2 of 4, which is 50 %. The combined figure sits between the two because it mixes statements (all run) with branch outcomes (half taken).

## Key takeaways
- Coverage records execution rather than the adequacy of assertions.
- Line coverage counts executed statements; branch measurement also tracks alternative transitions.
- coverage.py combines statement and branch opportunities in its branch-mode percentage.

## Further reading
- [Branch coverage measurement — coverage.py](https://coverage.readthedocs.io/en/latest/branch.html)
- [Code Coverage Best Practices — Google Testing Blog](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
