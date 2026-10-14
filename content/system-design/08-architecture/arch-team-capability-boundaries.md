---
id: arch-team-capability-boundaries
title: Drawing boundaries around capabilities
level: basic
minutes: 4
summary: Use team communication, feature changes and data ownership to decide whether a service should exist.
sourceLesson: arch-monolith-vs-microservices
---

Services offer independent ownership only when their boundaries fit how the business and teams work. Use the costs from the previous unit to evaluate a proposed extraction.

## Conway's law

> "Any organisation that designs a system will produce a design whose structure is a copy of the organisation's communication structure." Melvin Conway, 1968

Eric Raymond's well-known paraphrase: if four groups work on a compiler, you get a four-pass compiler. If your payments and checkout teams barely talk, the interface between their services will be awkward and slow to change.

This works in both directions:

- **Descriptive**: communication patterns constrain and influence architecture; this is an organizational observation, not a deterministic prediction from team count.
- **Prescriptive** (the "inverse Conway manoeuvre"): design the team structure you want the architecture to have. If you want an independent search service, create a team that owns search end to end.

The deepest reason to adopt microservices is organisational: they let you give a team **full ownership** of a capability, including its data and on-call. With 8 engineers, that benefit is small. With 400, it can be decisive.

## When to split

Martin Fowler's "Monolith First" advice is widely followed: start with a well-structured monolith, learn where the real boundaries are, then extract services when you have a concrete reason. Good reasons include:

1. **Team contention.** Many teams are blocked on each other's deploys or merge conflicts in one codebase.
2. **Different scaling profiles.** One component (video transcoding, search indexing) needs very different hardware or scale.
3. **Different reliability or security needs.** Card handling might need PCI isolation; a flaky experimental feature shouldn't share a process with checkout.
4. **Different change rates.** A pricing engine that changes daily next to a ledger that changes yearly.

Bad reasons: "Netflix does it", "it's modern", or a CV-driven rewrite.

### Finding the boundaries

Business capabilities (orders, billing, inventory) can guide boundaries. A DDD bounded context is the scope in which a domain model and its language are consistent; it is not simply a synonym for a capability or necessarily one service. Avoid mechanically splitting every technical layer into a service. A "database service" or "validation service" that every request passes through couples everything to it.

A good boundary has **high cohesion inside, low coupling outside**: most changes touch one service, and services exchange a small number of well-defined messages.

Three practical tests for a proposed service:

- **Can it be deployed alone?** If releasing it usually means releasing a neighbour too, the boundary is wrong.
- **Does it own its data?** No other service writes its tables, and nobody else reads them directly.
- **Does a typical feature stay inside it?** Look at the last 20 features and count how many services each would have touched.

Size matters less than these. "Micro" is about independence, not line count. A service per table often fragments a capability and increases coordination. Evaluate the actual change and data-access boundaries rather than using table count as a rule.

When one service needs another's data, it either calls the owner's API at request time (simple, but couples availability and adds latency) or keeps a **local copy** fed by the owner's events (fast and independent, but eventually consistent). Joins that used to be one SQL query become one of those two choices.

### Making a local copy dependable

For frequently read customer names and loyalty tiers that rarely change, Orders can keep a read model fed by customer events when the page accepts delayed visibility. It needs a bootstrap snapshot, deletion handling, monitored lag and a repair path. Duplicate delivery must be idempotent, and versions or defined ordering must prevent older complete snapshots from replacing newer ones. A credit limit instead needs the authoritative owner to atomically validate and reserve credit: a fresh read followed by a separate write can still race.

## Key takeaways
- Conway's law is an organisational observation, not an exact service-count prediction.
- Extract a capability for a concrete deployment, scaling, security or ownership need.
- Strong boundaries keep most feature changes local and expose data through an owner's interface or events.
- A local read copy trades request-time independence for delayed visibility; it is unsuitable for independently enforcing a credit limit.

## Further reading
- [Martin Fowler: Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [Martin Fowler: Conway's Law](https://martinfowler.com/bliki/ConwaysLaw.html)
