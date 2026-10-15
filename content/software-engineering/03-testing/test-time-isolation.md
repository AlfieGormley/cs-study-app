---
id: test-time-isolation
sourceLesson: test-flaky-coverage-mutation
title: Control test time and repair intermittent failures
level: advanced
minutes: 3
summary: Inject a fixed clock to test exact expiry boundaries.
---

A test can depend on hidden inputs such as the clock, test order or the operating environment. The earlier global-cart example exposed order dependence; this unit controls time and turns intermittent failures into an actionable repair. Assume `from datetime import datetime` in the code below.

## Control the clock

```python
def is_expired(token, now=None):
    now = now or datetime.now()
    return now >= token["expires_at"]
```

A test that creates a token "expiring in 1 second" and checks it is not expired is flaky on a slow CI machine. Passing the clock in makes it exact:

```python
def test_expiry_boundary():
    exp = datetime(2026, 1, 1, 12, 0)
    t = {"expires_at": exp}
    before = datetime(2026, 1, 1,
                      11, 59, 59)
    # Fixed times make the boundary exact.
    assert not is_expired(t, now=before)
    assert is_expired(t, now=exp)
```

Libraries such as `freezegun` or `time-machine` can freeze the clock for code you can't change, but injecting the clock is clearer. Also watch for time-zone assumptions (a test written in London fails in a CI region on UTC-8) and for tests that only fail on 29 February or across a daylight-saving change.

Changing test order and process grouping can reveal shared-state problems. Raising line coverage only asks which statements ran; it does not establish that each test owns its state. The later coverage units explain the measurement in detail.

### What to do with a flaky test

1. **Reproduce**: run it many times in a loop, with random ordering and in parallel, until it fails. Record the seed.
2. **Find the root cause**, using the causes table in the preceding diagnosis unit. Often the bug is in the code (a real race), not the test.
3. **Fix**: inject clocks and randomness, give each test its own data, wait on conditions instead of time, use ephemeral ports (port 0).
4. **If you can't fix it today, quarantine it**: move it out of the blocking suite, with an owner and a deadline, and keep running it to collect data.

> [!warning] Automatic retries
> Retrying failed tests (e.g. `pytest-rerunfailures`) turns red builds green, but it also hides real intermittent bugs, such as a race condition that will hit users. If you retry, track every test that needed a retry and treat that list as a bug backlog, not as a pass.


## Key takeaways
- Inject a fixed clock to test exact expiry boundaries.
- Investigate the root cause before quarantining or retrying a flaky test.
- Wait on conditions, isolate data and record reproduction details.

## Further reading
- [Eradicating Non-Determinism — Martin Fowler](https://martinfowler.com/articles/nonDeterminism.html)
- [Flaky tests — pytest docs](https://docs.pytest.org/en/stable/explanation/flaky.html)
