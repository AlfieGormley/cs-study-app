---
id: sched-cpu-burst-prediction
title: Predict bursts and understand SJF’s limits
level: basic
minutes: 2
sourceLesson: sched-cpu-basics
summary: Exponential averaging blends the measured burst with the previous prediction.
---

## The catch: you don't know the future

The OS can't know how long a burst will be. It can **predict** from history. Threads tend to behave like they did recently, so a common textbook method is an **exponential average**: after each burst, blend the burst that just happened with the previous prediction.

```formula
τ_{n+1} = αt_n + (1 − α)τ_n
τ_1 = 10 ms
τ_2 = 0.5 × 6 ms + 0.5 × 10 ms = 8 ms
τ_3 = 0.5 × 4 ms + 0.5 × 8 ms = 6 ms
where
τ_{n+1}: tau, the predicted length of the next CPU burst, in milliseconds (ms)
t_n: the measured length of the burst that just finished, in ms; here t_1 = 6 ms and then t_2 = 4 ms
τ_n: the previous prediction, the one made for the burst that just finished, in ms
α: alpha, the weight given to the latest burst, between 0 and 1; 0.5 here. Near 1, the prediction follows the last burst closely; near 0, it barely changes
τ_1: the initial guess before any burst has been measured, 10 ms here
τ_2, τ_3: the second and third predictions, in ms
ms: milliseconds, thousandths of a second
In words: the next prediction is part the latest real burst and part the old prediction; with α = 0.5 it is exactly halfway between the two.
```

It is called exponential because each update multiplies older contributions by the complement of the latest-burst weight. With the weight set to one half, the burst before last counts a quarter, the one before that an eighth, and so on. For a fixed weight strictly between zero and one, old contributions approach zero without reaching it in exact arithmetic. At a weight of one, only the latest burst counts; at zero, the prediction never updates. The method works only as well as the past predicts the future; a thread that suddenly changes behaviour is mispredicted for a few bursts.

SJF also risks **starvation**: if short jobs keep arriving, a long job may never run. The next lesson covers how real schedulers avoid that.

## Key takeaways
- Exponential averaging blends the measured burst with the previous prediction.
- The newest burst’s weight controls how quickly the estimate adapts.
- Known-burst SJF results depend on the arrival and cost model; repeated short arrivals can starve a long job.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
