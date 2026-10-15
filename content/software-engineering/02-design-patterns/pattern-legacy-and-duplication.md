---
id: pattern-legacy-and-duplication
title: Tool fit, legacy branches and duplication
level: advanced
minutes: 3
sourceLesson: pattern-anti-patterns
summary: Familiarity helps only while a tool still fits the actual problem.
---

## Golden hammer

As the saying goes, if all you have is a hammer, everything looks like a nail. A team that knows one tool well applies it to every problem: every data store is Postgres, every integration is Kafka, every problem is solved with microservices, or every design gets an abstract factory.

Familiar tools *are* valuable (operational knowledge counts for a lot), so the question is whether the fit is genuinely good or just familiar. Warning signs: workarounds piling up to make the tool fit, and nobody on the team able to name what the alternative would be.

## Lava flow

Dead or half-finished code from past experiments, which has hardened in place because nobody is sure it's safe to remove. You'll see comments like `# TODO: remove after migration (2019)`, unused feature flags, and classes with no callers that still get "maintained".

```python
def price(order):
    # v1 pricing, DO NOT DELETE
    # (needed by legacy export?)
    # The flag decides which code stays
    # live.
    if settings.LEGACY_PRICING:
        return _old_price(order)
    return _new_price(order)
```

### The way out

Committed code remains recoverable while its history is retained. Use callers, configuration, representative production telemetry and owner knowledge to build evidence that a branch is unused; an observation window with zero hits is not proof that rare or scheduled paths never need it. Give every feature flag an owner and an expiry date.

## Copy-and-paste programming and shotgun surgery

Copying a block and tweaking it is the fastest way to get the second variant working. By the fifth copy, a bug fix has to be found and applied five times, and one copy will be missed.

The related smell is **shotgun surgery**: one conceptual change (say, adding a currency) requires small edits across many files. It means knowledge about one concept is spread out instead of being in one place.

> [!tip] Rule of three
> Duplication twice is often fine; abstracting before then guesses at the wrong shape. On the third occurrence, the common shape is usually clear, so extract it then.

## Key takeaways
- Familiarity helps only while a tool still fits the actual problem.
- Representative telemetry is evidence about branch usage rather than proof of permanent disuse.
- Shotgun surgery spreads one conceptual change across many files.

## Further reading
- [Big Ball of Mud — Brian Foote and Joseph Yoder](https://www.laputan.org/mud/)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
