---
id: sepr-throughput-forecasts
title: Forecast delivery by resampling throughput
level: intermediate
minutes: 5
summary: Compare average-rate forecasts with a seeded Monte Carlo model and explain the limits of its percentiles.
sourceLesson: sepr-agile-estimation
---

If work items are roughly comparable in size, the history of how many items a team finishes each week can support a forecast without estimating every item separately. The result is a range with likelihoods attached, which is more useful than a single date, as long as you remember it comes from a model.

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

For comparison, the simple average gives a single number: the team finished 30 items in 8 weeks, about 3.75 a week, so 40 items would take roughly 10.7 weeks.

The average says nothing about how likely a miss is; the simulation does. On CPython 3.14.4 (and 3.9.6), this seeded example prints `50%: 11` and `85%: 13`: half the simulated futures finish within 11 weeks, and 85% within 13. The full spread of the 10,000 runs is 7 to 18 weeks. Quoting "13 weeks at 85% confidence" tells a stakeholder much more than "10.7 weeks". (The exact sequence of random choices can differ between Python implementations and versions; record them when reproducing a forecast.)

These percentiles describe the model, not a guarantee about the real team. Resampling assumes:

- this short history is representative of the weeks ahead;
- each week is independent of the last (no holidays, incidents or slow patches that run together);
- the remaining items are comparable in size to the finished ones;
- the backlog stays at 40 items.

Change in scope, staffing or the kind of work invalidates the forecast, so re-run it as weeks complete.

> [!analogy] Real-world analogy: a weather forecast
> A forecaster runs many simulated versions of tomorrow and reports "70% chance of rain" because rain fell in about 70% of them. Nobody reads that as a promise; it tells you whether to take an umbrella.
>
> **How it maps:** Each simulated run of `weeks_to_finish` is one possible future; the 85th percentile is the date that 85% of the simulated futures meet. Like a rain chance, it is a way to make a decision under uncertainty, not a commitment.
>
> **Where it stops:** Weather models are built on physics and decades of observations. This forecast rests on 8 weeks of history and assumes nothing about the team changes, and unlike the weather, the team can change the outcome by cutting scope.

Some teams take this further with **#NoEstimates**: split work into small, similar-sized items and forecast purely from throughput. Whether to estimate at all is debated. Fowler's test is useful: an estimate is worth making when it informs a significant decision, such as choosing between two projects or coordinating with a team that depends on you. Teams that work well without estimates usually do so because no such decision depends on them, and because their items really are small and similar.

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
- [Purpose of Estimation — Martin Fowler](https://martinfowler.com/bliki/PurposeOfEstimation.html)
