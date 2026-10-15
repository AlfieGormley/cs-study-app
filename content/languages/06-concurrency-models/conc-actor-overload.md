---
id: conc-actor-overload
title: Mailbox overload and actor deadlocks
level: advanced
minutes: 3
sourceLesson: conc-actors
summary: Asynchronous sends require a deliberate overload policy.
---

Private actor state removes some shared-memory hazards, but message protocols still need capacity and progress guarantees. The calculations below model an overloaded mailbox, not a benchmark.

## Where actors hurt

- **Unbounded mailboxes.** Local sends do not wait for message processing, so a fast producer can flood a slow actor until memory runs out. The fix is designed in: use synchronous calls, bounded mailboxes (an option in Akka), or explicit flow control (Akka Streams).
- **Deadlock still exists.** If actor A `call`s B while B `call`s A, both wait for a reply that never comes. With default gen_server call timeouts and unhandled failures, a timeout or peer exit can terminate a participant; exact timing and exit reasons depend on the race.
- **Ordering is local.** If A tells B and C, and B then tells C, C can receive B's message before A's.
- **A hot actor is a bottleneck.** A single actor is sequential, so a hot actor (one counter for the whole system) is a bottleneck.

How fast an unbounded mailbox fills is simple arithmetic: it grows by the difference between the rate messages arrive and the rate the actor handles them.

```formula
Q = (λ − μ)t
Q = (50,000/s − 30,000/s) × 60 s
Q = 20,000/s × 60 s = 1,200,000
where
Q: modelled messages waiting after t seconds, starting empty, with constant arrival rate above service rate, no drops and no other traffic
λ: lambda, the arrival rate: messages sent to the actor per second (/s)
μ: mu, the service rate: messages the actor finishes handling per second (/s)
t: how long the overload lasts, in seconds (s)
s: seconds
In words: while messages arrive faster than the actor can handle them, the backlog grows by the difference every second, and it never shrinks until arrivals slow below the handling rate.
```

For example, a logger receiving 50,000 events a second but writing only 30,000 a second is 1.2 million messages behind after one minute, and every one of those messages occupies memory. The formula only applies while messages arrive faster than they are handled; once arrivals fall below the handling rate, the backlog shrinks by the difference each second instead.

## Actors vs CSP

| | CSP (Go) | Actors (Erlang) |
|---|---|---|
| Named thing | Channel | Process (Erlang pid) |
| Send | Sync by default | Async |
| Buffer | Fixed size | Unbounded mailbox |
| Failure | Unrecovered panic terminates program | Links, supervisors |
| Distribution | Go channels are local; protocols can bridge | Erlang node messaging built in |

Neither is strictly better. CSP's synchronous channels make backpressure and some deadlocks easier to see. Actors' asynchronous, named mailboxes make distribution and failure handling natural. You can build either from the other: a Go goroutine reading one channel is an actor, and an Erlang process that only forwards messages is a channel.

## Key takeaways
- Asynchronous sends require a deliberate overload policy.
- Synchronous actor calls can form wait cycles; default timeouts do not prove a protocol safe.

## Further reading
- [Actor model — Wikipedia](https://en.wikipedia.org/wiki/Actor_model)
- [A Universal Modular ACTOR Formalism for Artificial Intelligence — Hewitt, Bishop and Steiger (1973)](https://www.ijcai.org/Proceedings/73/Papers/027B.pdf)
- [Concurrent Programming — Erlang system documentation](https://www.erlang.org/doc/system/conc_prog.html)
- [Supervisor Behaviour — Erlang system documentation](https://www.erlang.org/doc/system/sup_princ.html)
- [Making reliable distributed systems in the presence of software errors — Joe Armstrong (2003)](https://erlang.org/download/armstrong_thesis_2003.pdf)
- [Message Delivery Reliability — Akka documentation](https://doc.akka.io/libraries/akka-core/current/general/message-delivery-reliability.html)
- [Microsoft Orleans overview — Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/orleans/overview)
- [Primary verification source 1](https://www.erlang.org/doc/system/ref_man_processes.html)
- [Primary verification source 2](https://www.erlang.org/doc/system/eff_guide_processes.html)
- [Primary verification source 3](https://www.erlang.org/doc/apps/stdlib/gen_server.html)
- [Primary verification source 4](https://www.erlang.org/docs/25/man/supervisor.html)
- [Primary verification source 5](https://elixir.hexdocs.pm/Supervisor.html)
- [Primary verification source 7](https://doc.akka.io/libraries/akka-core/current/typed/fault-tolerance.html)
- [Primary verification source 8](https://learn.microsoft.com/en-us/dotnet/orleans/grains/request-scheduling)
- [Primary verification source 9](https://pekko.apache.org/)
- [Primary verification source 10](https://akka.io/blog/why-we-are-changing-the-license-for-akka)
