---
id: msg-event-notification-state-contracts
title: Event notification and state-carrying contracts
level: advanced
minutes: 2
summary: Choose between callbacks and local state copies, then design a versioned event contract.
sourceLesson: msg-event-driven-architecture
---

Event notification, event-carried state transfer, event sourcing and CQRS describe different designs. First focus on events published between services: should a subscriber call back for details or already have the state it needs?

## Four patterns under one name

### 1. Event notification

A service emits a small event saying something happened, with little data:

```json
{ "type": "CustomerAddressChanged",
  "customerId": "c-42", "at": "..." }
```

Interested services that need details **call back** to the source (`GET /customers/c-42`).

- Low coupling on the publisher: it does not know who listens.
- But consumers depend on the source being available at callback time, and a popular event can trigger a thundering herd of callbacks.
- It is hard to see the overall flow: behaviour is spread across many listeners.

### 2. Event-carried state transfer

The event carries the **state** consumers need:

```json
{ "type": "CustomerAddressChanged",
  "customerId": "c-42",
  "address": { "line1": "...",
               "postcode": "SW1A 1AA" } }
```

Consumers keep their own local copy of the data they care about.

- Consumers can work when the source is down, with lower latency (local reads).
- But data is duplicated and **eventually consistent**, and every event schema is now a public contract.



## Designing good events

- **Name them in the past tense** for facts (`OrderPlaced`), and keep commands (`ShipOrder`) separate.
- **Include an event ID, type, schema version, timestamp and aggregate ID.** CloudEvents standardises an envelope with required `id`, `source`, `specversion` and `type`, plus optional `time`, `subject` and `dataschema`. `specversion` versions the envelope, not your business payload; define aggregate identity and payload version deliberately.
- **Evolve schemas compatibly**: add optional fields, never repurpose or remove required ones. Schema compatibility depends on the encoding and reader behavior. Configure the required backward/forward/transitive checks in the registry and CI; backward-only checks do not protect every old reader or replay.
- **Key events by aggregate ID** so per-entity ordering holds in a partitioned log.
- Decide deliberately between **thin events** (notification) and **fat events** (state transfer). Fat events reduce coupling at runtime but increase coupling at the schema level.

## Key takeaways

- Thin notifications keep payloads small but can cause callback availability coupling and thundering herds.
- State-carrying events let consumers read locally while duplicating data and exposing a schema contract.
- Give events stable identity, payload version and aggregate identity; CloudEvents envelope versions are separate.
- Choose compatibility checks for old readers and replay, then keep aggregate key mapping stable.

## Further reading

- [What do you mean by "Event-Driven"? (Martin Fowler)](https://martinfowler.com/articles/201701-event-driven.html)
