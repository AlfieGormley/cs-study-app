---
id: conc-distributed-actors
title: OTP calls, distribution and virtual actors
level: advanced
minutes: 3
sourceLesson: conc-actors
summary: Request/reply waits can bound one caller’s work without bounding all senders.
---

Supervision controls child failure, while request/reply and distribution add different protocol obligations. Keep delivery, processing order and application effects separate when comparing actor frameworks.

### OTP behaviours

OTP behaviors package common receive-loop protocols. OTP's **gen_server** wraps the loop and offers two kinds of request:

- `gen_server:cast` sends asynchronously; no reply.
- `gen_server:call` sends and waits for the reply, with a default timeout of 5 seconds. A timeout raises an exit exception; if unhandled, the caller terminates. A supervisor responds only if that process is supervised and restart policy applies.

`call` also gives natural **backpressure**: a sequential caller waits for completion or failure before its next call. This bounds outstanding work per caller, not the total mailbox if callers are unbounded.

## Distribution and location transparency

An Erlang pid can refer to a process on another node. `Pid ! Msg` is the same syntax either way, and links and monitors work across nodes (a lost connection triggers `'DOWN'` with reason `noconnection`). That is **location transparency**.

It is transparent in syntax, not in physics. Across a network, messages can be lost, and you cannot tell a slow node from a dead one. Erlang's guarantees reflect this: delivery is not guaranteed, only ordering per sender-receiver pair while the connection lasts. Robust Erlang code assumes any request may go unanswered and uses timeouts and monitors.

## Akka and Orleans

**Akka** brought actors to Scala and Java. In Akka Typed, an actor is a `Behavior[T]` that accepts only messages of type `T`, so the type system restricts message types, but does not prove every value is handled or delivered. For ordinary direct messages, its documented core guarantees are:

- **At-most-once** delivery: a message is delivered once or not at all. No automatic retries.
- **Ordering per sender-receiver pair**.

For request/reply, the **ask** pattern sends a message containing a temporary reply-to address and returns a `Future` that fails after a timeout. Akka has supervision too, with a different default: in Akka Typed a failing actor is **stopped**, and you opt in to restarts by wrapping its behaviour in `Behaviors.supervise(...)`. In 2022 Akka moved to the Business Source Licence; the Apache-licensed fork is **Apache Pekko**.

**Microsoft Orleans** (.NET, used for Halo's online services) introduced **virtual actors**, called *Orleans grains*. An Orleans grain is addressed by an ID and always exists logically: the runtime activates it on some server when the first message arrives and deactivates it when idle. Applications normally obtain grain references by ID and let the runtime manage activation; developers still design persistence and failure recovery, and by default each processes one request at a time. Orleans popularised the pattern for stateful cloud services; Akka's *cluster sharding* and Dapr's actors offer similar ideas.

## Key takeaways
- Request/reply waits can bound one caller’s work without bounding all senders.
- Remote actor addresses hide location in syntax, not latency, loss or failure.

## Further reading
- [Primary source: www.erlang.org](https://www.erlang.org/doc/system/ref_man_processes.html)
- [Primary source: www.erlang.org](https://www.erlang.org/doc/system/sup_princ.html)
- [Primary source: doc.akka.io](https://doc.akka.io/libraries/akka-core/current/general/message-delivery-reliability.html)
