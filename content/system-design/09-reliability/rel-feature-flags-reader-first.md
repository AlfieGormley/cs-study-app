---
id: rel-feature-flags-reader-first
title: Feature flags and reader-first rollback
level: advanced
minutes: 3
summary: Separate code deployment from feature exposure while keeping persisted data rollback-compatible.
sourceLesson: rel-safe-deployments
---

Canaries stage binary releases; flags stage behaviour already deployed. Both can require rollback. This unit joins those decisions to the formats written by a new path, because switching routing or a flag cannot reverse an incompatible stored effect.

## Feature flags: separating deploy from release

A **feature flag** (feature toggle) wraps new behaviour in a runtime condition:

This Python function-body fragment assumes an existing flag client, user context and two checkout functions. It shows routing behaviour, not a complete flag service.

```python
# The same user gets a stable cohort policy.
if flags.enabled("new_checkout",
                 user=ctx.user):
    # Effects still need rollback
    # compatibility.
    return new_checkout(cart)
# Disabled users follow the established
# path.
return old_checkout(cart)
```

This splits two things that used to be one:

- **Deploy**: ship the code to production (dark, off).
- **Release**: turn the behaviour on, for staff first, then a small user cohort, then wider populations.

Benefits: potentially fast behavior rollback by flipping a flag (subject to propagation and already-started effects), trunk-based development with unfinished features merged behind flags, and A/B experiments.

Pete Hodgson's article on martinfowler.com classifies flags by longevity and dynamism: **release toggles** (short-lived), **experiment toggles**, **ops toggles** (kill switches for expensive features under load) and **permission toggles**.

> [!warning] Flags are debt and config is code
> Every independent on/off flag doubles the number of possible configurations (see the formula below), although not every combination is reachable or a distinct execution path. Remove release flags once rolled out. And remember a flag change is a production change: stage it, audit it and monitor it like a deploy. Several major outages have come from a config or flag pushed globally at once.

The number of possible configurations grows exponentially with the number of flags:

```formula
C = 2^n
C = 2^10 = 1,024
where
C: the number of possible on/off combinations
n: the number of independent binary (on/off) flags, here 10
^: "to the power of"
In words: each extra flag doubles the combinations, so 10 flags allow 1,024 configurations, far more than anyone tests.
```

## Rollback safety

Rolling back only works if the old version can run against whatever the new version did. AWS's guidance is that **every change must be backwards and forwards compatible** with the version on either side of it.

The classic trap: v2 writes data in a new format. You roll back to v1, which can't read it, and now the rollback is causing the outage. AWS's solution is a **two-phase deployment**:

1. Deploy a version that can *read* the new format but still *writes* the old one. Let it reach 100%.
2. Deploy a version that *writes* the new format.

Now rolling back from step 2 to step 1 is safe, because step 1 can read both.

## Key takeaways

- A flag separates deployment from release and can provide a fast kill switch under stated propagation and state assumptions.
- Flags multiply configurations and require staged, audited changes and removal.
- Deploy compatible readers everywhere before enabling new writers; a flag cannot make old readers understand new data.

## Further reading

- [Automating safe, hands-off deployments (AWS Builders' Library)](https://aws.amazon.com/builders-library/automating-safe-hands-off-deployments/)
- [Ensuring rollback safety during deployments (AWS Builders' Library)](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)
- [Feature toggles (Pete Hodgson, martinfowler.com)](https://martinfowler.com/articles/feature-toggles.html)
