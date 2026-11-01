---
id: git-delivery-deployment
title: Delivery, deployment and releasing behaviour
level: advanced
minutes: 3
sourceLesson: git-cd-release
summary: Continuous delivery keeps production release possible on demand; deployment automates the final gate.
---

CI tells you a change is probably good. **Continuous delivery** (CD) takes it the rest of the way: every change that passes the pipeline produces something you *could* put in front of users, safely and on demand.

This lesson covers how changes reach production, how to limit the damage when a bad one gets through, and how to communicate change to the people who depend on you: version numbers, tags and release notes.

## Delivery versus deployment

The two terms are easy to mix up:

- **Continuous delivery**: the software is kept in a state where it **can be released to production at any time**. The decision to release may still be a human pressing a button.
- **Continuous deployment**: every change that passes the pipeline **goes to production automatically**, with no human gate.

Continuous deployment requires continuous delivery, but not the reverse. A mobile app team can practise continuous delivery perfectly while app store review stops them deploying continuously.

## Deploy is not release

**Deploying** puts new code on production machines. **Releasing** exposes a behaviour to users. Feature flags let you separate them:

- Deploy on Tuesday with the feature flag off: the gated behaviour remains hidden, provided initialisation, schema and other deployment changes remain compatible.
- Release on Thursday by turning the flag on for 1% of users, then everyone.
- Turn the flag off to return to the old path without redeploying, if that path is still compatible. Propagation takes time and disabling the flag does not undo data changes or completed side effects.

A **dark launch** goes further: the new code path runs in production on real traffic (for example computing new recommendations) but its result is discarded or only logged, so you can check performance and correctness before anyone sees it.

> [!analogy] Real-world analogy: building the set behind the curtain
> A theatre crew can build and test a new set on stage while the curtain is down, then raise the curtain when the director says so. If the scene goes badly, they can lower the curtain without dismantling the set.
>
> **How it maps:** Building the set is deploying: the code is on production machines. Raising the curtain is releasing: a feature flag exposes the behaviour to users. Lowering the curtain is turning the flag off, returning users to the old path without a redeploy.
>
> **Where it stops:** Hidden code can still have effects: it is loaded, may initialise and may share a database with visible code. And lowering a flag does not undo what users already did, such as data written or payments taken while it was on.

## The deployment pipeline

```
 commit --> CI: build + unit tests
               |
               v  artefact app:sha-abc123
            acceptance tests
               |
               v
            staging (same artefact)
               |
               v  gate: auto or approval
            production: progressive rollout
               |
               v
            monitor -> continue / roll back
```

Each stage increases confidence and cost. The same artefact moves through every stage; only configuration differs per environment.

## Key takeaways

- Continuous delivery keeps production release possible on demand; deployment automates the final gate.
- Deployment installs code while a flag can release its behaviour later.
- Flags do not undo side effects, and the old path must remain compatible.

## Further reading

- [Continuous Delivery — Martin Fowler](https://martinfowler.com/bliki/ContinuousDelivery.html)
