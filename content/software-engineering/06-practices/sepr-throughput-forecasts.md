---
id: sepr-throughput-forecasts
title: Forecast delivery by resampling throughput
level: intermediate
minutes: 4
summary: Compare average-rate forecasts with a seeded Monte Carlo model and explain the limits of its percentiles.
sourceLesson: sepr-agile-estimation
---

If work items are sufficiently comparable, completed-item history can support a forecast without estimating every item separately. This model is an example, not a guaranteed probability for a real team.

## Forecasting from data: Monte Carlo

If the team tracks how many items it finishes each week, it can forecast without estimating individual items. Simulate the future by sampling from past throughput:

```python
import random
# Fix this run's random sampling sequence.
random.seed(42)

# items finished in each past week
history = [3, 5, 2, 6, 4, 4, 1, 5]

def weeks_to_finish(backlog):
    done, weeks = 0, 0
    while done < backlog:
        # Sample one week of completed work.
        done += random.choice(history)
        weeks += 1
    return weeks

runs = sorted(weeks_to_finish(40)
              for _ in range(10_000))
# Indexed sorted runs approximate quantiles.
print("50%:", runs[5_000])
print("85%:", runs[8_500])
```

For comparison, the simple average gives a single-number answer:

```formula
λ = (3 + 5 + 2 + 6 + 4 + 4 + 1 + 5) / 8
λ = 30 items / (8 wk)
λ = 3.75 items per wk
T ≈ B / λ
T ≈ 40 items / (3.75 items per wk)
T ≈ 10.7 wk
where
λ: flow-rate lambda, the average throughput over the 8 recorded weeks, in items finished per week
8: the number of past weeks in the history
T: the naive forecast time to finish the backlog, in weeks
wk: weeks, the unit of time used here
items: count of completed or remaining work items
B: the remaining backlog, here 40 items
≈: approximately equal to
In words: the team finished 30 items in 8 weeks, about 3.75 a week, so 40 items would take roughly 10.7 weeks at that average pace.
```

The average says nothing about how likely a miss is; the simulation does. On CPython 3.14.4, this seeded example prints `50%: 11` and `85%: 13`. The sequence can depend on the Python implementation and version; record those when reproducing it. These are model outputs, not guaranteed real-world probabilities. Resampling assumes this short history represents future throughput, weeks can be sampled independently, remaining items are comparable and the backlog stays fixed. Changes in scope, staffing or dependence can invalidate the forecast.

Some teams take this further with **#NoEstimates**: split work into small, similar-sized items and forecast purely from throughput.

## Pitfalls
- **Cargo-cult Scrum.** All the ceremonies, none of the feedback. Ignoring feedback that requires adaptation undermines the Review; it need not change the backlog on every occasion.
- **Velocity as a performance target.** Goodhart's law warns that using points as a productivity target can encourage inflation. Velocity is a planning tool for the team.
- **Treating points as fixed hours.** A rule such as “one point always means eight hours” hides uncertainty and team-local sizing. Empirical team-level forecasts should retain those assumptions and variation.
- **Ignoring the retrospective.** A retro that picks no action, or never checks last time's action, is a wasted hour.
- **Single-number estimates treated as promises.** Give ranges with a confidence level, and re-forecast as you learn.

## Key takeaways
- Sampling historical throughput creates a distribution of modelled completion times.
- Percentiles describe the simulation under its assumptions, rather than guaranteed real-world probabilities.
- Re-forecast when scope, staffing, item comparability or dependence changes.

## Further reading
- [random — Python docs](https://docs.python.org/3/library/random.html)
- [The Kanban Guide — flow metrics and forecasts](https://kanbanguides.org/the-kanban-guide/2025.5/)
