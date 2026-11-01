---
id: sepr-debugging-search
title: Minimise inputs and bisect history
level: intermediate
minutes: 5
summary: Shrink reproductions and use deterministic good/bad tests to localise regressions.
sourceLesson: sepr-debugging
---

With a reliable reproduction in hand, shrink the problem. A smaller input and a narrower slice of history each cut down the number of plausible causes.

## Step 2: minimise it
A bug that appears with a 3 MB input file and 40 config flags is hard to reason about. Shrink it: remove half the input and keep the smaller version if it still fails. If neither half fails alone, the failure needs pieces of both, so try removing smaller chunks instead. Stop when no remaining piece can be removed without the failure disappearing.

This is **delta debugging**, formalised by Andreas Zeller, and tools automate it. Property-based testing libraries like Hypothesis do the same thing automatically, "shrinking" a failing random input toward simpler cases that still fail; shrinking does not guarantee the globally smallest case.

A minimal reproduction often makes the cause obvious. It also makes a perfect regression test.

## Step 3: localise it by binary search
When you do not know where the bug is, halve the search space with each experiment. In an ideal binary search, 20 yes/no tests distinguish about a million candidates. That only works when each test cleanly says "the cause is in this half"; interacting settings or a failure that comes and goes do not split so neatly.

You can binary-search almost anything:

- **Code path**: log or assert at the midpoint of the pipeline. Is the value already wrong there?
- **Data**: does it fail on the first half of the records or the second?
- **Configuration**: revert half the changed settings.
- **History**: which commit introduced it?

### git bisect

If something used to work, `git bisect` finds the commit that broke it by binary search over history.

A typical session looks like this. Bisect checks out commits for you, so start from a clean working tree and finish with `git bisect reset`:

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

How many tests does bisect need? Each test halves the range of suspect commits, so the count grows with the number of halvings, not the number of commits: about 10 tests for 1,000 commits, and only about one more each time the history doubles.

```formula reference
2^T ≥ N
where
T: the number of commits you must test (build and check)
N: the number of candidate commits between the known good and known bad revisions
2^T: 2 multiplied by itself T times: how many candidates T halvings can tell apart
≥: greater than or equal to
In words: you need just enough tests that repeatedly halving the suspects gets down to one; 10 tests cover 1,024 commits and 20 cover over a million.
```

That count assumes one good-to-bad transition and a test that answers reliably at every commit. Bisect trusts every answer: a flaky test that fails once on a good commit sends the search into the wrong half, and bisect then confidently names an innocent commit. A bug that was fixed and reintroduced, or two separate regressions, break the model too. If the named commit makes no sense, review the marks with `git bisect log` and make the test deterministic before trusting the answer.

> [!analogy] Real-world analogy: finding the moment on CCTV
> Your bike vanished some time in a 12-hour recording. Rather than watching from the start, you jump to the middle: is the bike still there? If yes, it went in the second half; if no, the first. Each jump halves the footage, so about ten jumps pin down the minute.
>
> **How it maps:** The recording is the commit history, a jump is checking out a midpoint commit, and "is the bike there?" is your test marking it good or bad. Bisect is the person doing the jumping.
>
> **Where it stops:** Looking at a frame is instant and always truthful. Testing a commit may need a full build, some commits cannot be tested at all, and a flaky test is like footage that sometimes shows a bike that is not there.

Better still, automate it with a script whose exit code tells git the answer:

```
git bisect run pytest tests/test_tax.py
```

Exit code 0 means good, 1 to 127 (except 125) means bad, **125** means "cannot test this commit, skip it" (for example, when it does not build), and anything else aborts the run. Beware: pytest also exits non-zero when it is interrupted, hits an internal error or collects no tests, and bisect would read those as "bad". A small wrapper script that returns 125 for untestable commits and 1 only for the real test failure keeps the answers honest.

## Key takeaways
- Shrinking finds a smaller failure, not necessarily the globally smallest input.
- Bisect trusts every answer: a flaky test or several regressions can make it name the wrong commit.
- In git bisect run, distinguish target failures from untestable revisions and tooling errors.

## Further reading
- [Git bisect documentation](https://git-scm.com/docs/git-bisect)
- [pytest exit codes](https://docs.pytest.org/en/stable/reference/exit-codes.html)
- [Reducing Failure-Inducing Inputs — Andreas Zeller](https://www.debuggingbook.org/html/DeltaDebugger.html)
