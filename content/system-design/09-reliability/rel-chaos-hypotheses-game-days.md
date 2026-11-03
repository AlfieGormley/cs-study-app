---
id: rel-chaos-hypotheses-game-days
title: Chaos hypotheses and game days
level: intermediate
minutes: 3
summary: Test a recovery hypothesis with measurable steady state and a limited blast radius.
sourceLesson: rel-disaster-recovery
---

A written recovery plan is a hypothesis. This unit describes how teams test it. The example is an experiment specification, not a runnable fault injector; it requires a controlled environment, a monitoring system and an authorised operator.

## Chaos engineering

You only know your DR and redundancy work if you've seen them work. **Chaos engineering** is the discipline of running controlled experiments on a system to build confidence that it withstands turbulent conditions.

Netflix described **Chaos Monkey** in 2011: it randomly terminated production instances during business hours to test resilience to instance loss. The same account described whole-zone experiments with Chaos Gorilla; a 2015 account described regional-outage simulations with Chaos Kong.

The principles (from principlesofchaos.org):

1. Define **steady state** as a measurable output (e.g. successful plays per second), not internal metrics.
2. **Hypothesise** that steady state will continue in both control and experiment groups.
3. Introduce real-world events: kill instances, add latency, sever a dependency, fill a disk.
4. Try to **disprove** the hypothesis by looking for a difference in steady state.
5. Run in production where possible, **minimise blast radius**, and automate experiments to run continuously.

The illustrative experiment compares user-visible checkout success and stops before a small experiment becomes a large outage:

```
Experiment: checkout survives recs loss
Target: at least 99.5% checkout success
Inject: recs errors for 5% of users
Abort: checkout success below 99%
Result: pass/fail, fix and re-run
```

The injected recommendations failure rate is 100% for the selected 5% user cohort. These are illustrative thresholds chosen for the exercise, not recommended production defaults.

### Game days

A **game day** is a scheduled exercise where a team simulates a disaster (e.g. "us-east-1 is gone") and executes the DR runbook for real. It tests people and process as well as systems: do on-call engineers know the steps, do they have the right access, is the runbook current? Google runs company-wide DiRT (Disaster Recovery Testing) exercises for this purpose.

## Key takeaways

- Define a user-visible steady state and compare control with experiment.
- Inject a realistic fault with a limited scope and explicit abort condition.
- Game days test runbooks, people and permissions alongside systems.

## Further reading

- [Principles of chaos engineering](https://principlesofchaos.org/)
- [The Netflix Simian Army (Netflix, 2011)](https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116)
- [Chaos engineering upgraded (Netflix, 2015)](https://netflixtechblog.com/chaos-engineering-upgraded-878d341f15fa)
- [Chaos engineering (Wikipedia)](https://en.wikipedia.org/wiki/Chaos_engineering)
