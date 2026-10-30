---
id: sep-yagni-change-cost
title: Defer speculative features while keeping change safe
level: intermediate
minutes: 4
summary: YAGNI defers speculative capabilities rather than tests and refactoring.
sourceLesson: sep-dry-kiss-yagni
---

Building a feature before anyone needs it feels like saving time later. This lesson weighs what that actually costs, which decisions *do* deserve forethought, and how the design slogans pull against each other.

## YAGNI: build what you need now

YAGNI ("you aren't gonna need it") comes from Extreme Programming. Fowler traces it to Kent Beck replying to Chet Hendrickson's list of capabilities a system would soon need. The rule: **don't build a capability until you actually need it**.

```python
# Requirement: export orders as CSV.

# YAGNI violation
class ExporterFactory:
    def create(self, fmt: str,
               plugin_dir=None):
        ...  # CSV, XML, Parquet, plugins

# Enough
def orders_to_csv(orders, file):
    writer = csv.writer(file)
    for o in orders:
        writer.writerow([o.id, o.total])
```

Martin Fowler breaks down what a presumptive feature costs. Even when the guess turns out right, you still pay the cost of delay and the cost of carry:

- **Cost of build**: the analysis, coding and testing time spent now, wasted entirely if the feature is never needed.
- **Cost of delay**: the features you didn't ship because you were building this one.
- **Cost of carry**: every reader, test and change must work around the extra code.
- **Cost of repair**: even a feature that is needed was often built the wrong way, because you only learn what it should do later; reworking it is technical debt. A feature that is never needed must also be ripped out.

> [!analogy] Real-world analogy: building the nursery early
> A couple build a nursery extension "because we'll probably have children". Even if they do, they paid the builders years early, put off a holiday to afford it, and heated and cleaned an empty room in the meantime. If their plans change and they need a home office instead, the room has to be rebuilt.
>
> **How it maps:** Paying the builders is the cost of build; the postponed holiday is the cost of delay; heating and cleaning the unused room is the cost of carry; rebuilding it is the cost of repair.
>
> **Where it stops:** Some things are far cheaper to plan up front, such as foundations strong enough for a second storey. In software these are the costly-to-change decisions in the table below: public APIs, shared formats and security models.

### What YAGNI does not mean

- **It doesn't mean skip quality.** Fowler is explicit: YAGNI applies to *features*, not to refactoring, tests or clean structure that make the code easier to change. Those are what make deferring features safe.
- **It doesn't apply equally to things that are expensive to change later.** A public API, a wire format, a database schema shared by many services, or security: these deserve forethought because changing them later means migrations, versioning and coordinating other teams.

| Cheap to change: YAGNI | Costly to change: plan |
|---|---|
| Internal function | Public API or SDK |
| Private class layout | Event and file formats |
| One service's code | Shared database schema |
| UI wording | Auth and security model |

## When the principles collide

They regularly pull against each other:

- **DRY versus KISS.** Removing duplication between two 5-line functions by adding a generic, configurable helper can make the code *less* simple. Prefer the version a newcomer understands faster.
- **DRY versus decoupling.** Two microservices sharing a "common" library for their domain models can couple their evolution. Compatible, versioned releases can be adopted independently; a breaking shared-model change may instead force coordination. Duplicating a small DTO across a service boundary is often the right call.
- **YAGNI versus OCP.** OCP invites extension points; YAGNI says wait until there's a second case. The rule of three can guide that choice.
- **KISS versus performance.** The simplest code is sometimes too slow. Optimise where measurement says it matters, and keep the complexity contained there.

## Key takeaways
- YAGNI defers speculative capabilities rather than tests and refactoring.
- A correctly guessed feature can still cost delay and ongoing maintenance.
- Public contracts and shared formats deserve forethought because later change requires coordination.

## Further reading
- [Martin Fowler: Yagni](https://martinfowler.com/bliki/Yagni.html)
- [Martin Fowler: Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)
