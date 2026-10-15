---
id: sepr-debugging-search
title: Minimise inputs and bisect history
level: intermediate
minutes: 5
summary: Shrink reproductions and use deterministic good/bad tests to localise regressions.
sourceLesson: sepr-debugging
---

Start from the reliable reproduction and recorded evidence established in the preceding unit. Smaller inputs and a narrower history reduce the number of plausible causes.

## Step 2: minimise it
A bug that appears with a 3 MB input file and 40 config flags is hard to reason about. Shrink it: remove half the input; if it still fails, keep the smaller version; if not, try the other half. If neither half fails, test smaller removals from the original failing input; an interaction may require pieces from both halves. Continue until no individual remaining piece can be removed while preserving the failure.

This is **delta debugging**, formalised by Andreas Zeller, and tools automate it. Property-based testing libraries like Hypothesis do the same thing automatically, "shrinking" a failing random input toward simpler cases that still fail; shrinking does not guarantee the globally smallest case.

A minimal reproduction often makes the cause obvious. It also makes a perfect regression test.

## Step 3: localise it by binary search
When you do not know where the bug is, halve the search space with each experiment. In an ideal binary search, 20 yes/no tests distinguish roughly a million candidates (20 halvings cover 1,048,576). Arbitrary code, configuration interactions and non-monotonic failures need not provide such a partitioning oracle.

You can binary-search almost anything:

- **Code path**: log or assert at the midpoint of the pipeline. Is the value already wrong there?
- **Data**: does it fail on the first half of the records or the second?
- **Configuration**: revert half the changed settings.
- **History**: which commit introduced it?

### git bisect

If something used to work, `git bisect` finds the commit that broke it by binary search over history.

The commands below are a workflow template. They depend on the repository’s revisions and tests and temporarily change the checkout; they are not a standalone reproducible output example.

```
git bisect start
git bisect bad HEAD
git bisect good v2.3.0
# git checks out a midpoint commit;
# test it, then mark it:
git bisect good    # or: git bisect bad
# ...repeat until git names the commit
git bisect reset
```

How many tests does bisect need? Each test halves the range of suspect commits, so the question is how many halvings it takes to get from all the candidates down to one:

```formula
2^T ≥ N
T ≈ log_2(N)
2^10 = 1,024 ≥ 1,000
T = ⌈log_2(1,000)⌉ = ⌈9.97⌉ = 10
where
T: the number of commits you must test (build and check)
N: the number of candidate commits between the known good and known bad revisions; here 1,000
2^T: T copies of 2 multiplied together: the number of candidates that T halvings can tell apart
log_2: the logarithm to base 2: log_2(N) is the power you must raise 2 to in order to get N, which is the number of halvings that shrink N to 1
≥: greater than or equal to
≈: approximately equal to
⌈ ⌉: ceiling: round up to the next whole number, because you cannot run part of a test
In words: each test halves the suspects, and 10 halvings are enough for 1,024 commits, so about 10 tests find the culprit among 1,000.
```

This assumes a linear history with one deterministic good-to-bad transition and no skipped commits. Merges, flaky tests, reversions and untestable commits complicate this bound. Doubling the history to 2,000 commits adds only about one more test.

Better still, automate it with a script whose exit code tells git the answer:

```
git bisect run pytest tests/test_tax.py
```

Exit code 0 means good, 1 to 127 (except 125) means bad, and **125** means "cannot test this commit, skip it" (for example, when it does not build). With pytest, exit codes for interruption, internal errors, usage errors or no collected tests must not be interpreted as evidence of the target regression. Use a wrapper that maps an untestable revision to 125 or aborts the run, and returns 1 only for the relevant test failure.

## Key takeaways
- Shrinking finds a smaller failure, not necessarily the globally smallest input.
- Binary-search bounds require a reliable partition; interactions and flaky failures can break the model.
- In git bisect run, distinguish target failures from untestable revisions and tooling errors.

## Further reading
- [Git bisect documentation](https://git-scm.com/docs/git-bisect)
- [pytest exit codes](https://docs.pytest.org/en/stable/reference/exit-codes.html)
- [Reducing Failure-Inducing Inputs — Andreas Zeller](https://www.debuggingbook.org/html/DeltaDebugger.html)
