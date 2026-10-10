---
id: conc-actors
title: Actors, Erlang and Akka
level: advanced
minutes: 14
summary: The actor model of isolated processes with mailboxes, how Erlang builds fault-tolerant systems from it with links, supervisors and "let it crash", and how Akka and Orleans bring it to the JVM and .NET.
---

The channel style in lesson 4 organizes communication around explicit channels. The actor model organizes it around actor addresses. Every concurrent entity is an **actor** with private state and a **mailbox**; the only way to affect it is to send it a message, asynchronously, by name. Isolated actor state avoids shared-memory data races. Real actor libraries may allow shared mutable references or external stores, which still need coordination. And because messages are the only interface, the same code can run in one process, across cores, or across machines.

Carl Hewitt, Peter Bishop and Richard Steiger proposed actors in 1973. Erlang, built at Ericsson from 1986 for telephone switches, arrived at almost the same design independently and showed what it was good for: systems that keep running while parts of them fail.

## What an actor can do

When an actor processes a message, it may do only three things:

1. **Send** messages to actors whose addresses it knows.
2. **Create** new actors.
3. Decide how to handle the **next** message (change its state or behaviour).

Common actor implementations serialize message handling; reentrant implementations can interleave requests while retaining serialized execution turns. Inside an actor the code is sequential, with no locks, because no one else can touch its state. Concurrency exists only *between* actors.

```
  sender A --msg--+
                  v
  sender B --> [mailbox] --> actor
                  ^         (state,
  sender C --msg--+          one msg
                              at a time)
```

## Erlang processes

An Erlang **process** is an actor. It is a green thread (lesson 3) with its own heap, so garbage collection is per process: collection usually concerns that process rather than every process heap. No universal microsecond pause figure is supplied; shared runtime resources and native code remain relevant. Process termination releases its owned resources, subject to implementation details.

A counter actor:

```erlang
-module(counter).
-export([start/0, loop/1]).

start() -> spawn(?MODULE, loop, [0]).

loop(N) ->
    receive
        {inc, By} ->
            loop(N + By);
        {get, From} ->
            From ! {count, N},
            loop(N)
    end.
```

`spawn` creates a process and returns its **pid**. `Pid ! Msg` sends asynchronously: it does not wait for the receiver to process the message. Sending can still suspend due to distribution-buffer backpressure or other runtime conditions. `receive` takes a message matching one of its patterns. State is not a mutable variable: `loop` calls itself with the new value, and the tail call means no stack grows.

```erlang
C = counter:start(),
C ! {inc, 2},
C ! {inc, 3},
C ! {get, self()},
receive {count, X} -> X end.
% X = 5
```

Why is `X` always 5? Erlang guarantees that messages from **one sender to one receiver** arrive in the order they were sent. All three messages come from the same shell process, so `get` is handled after both `inc`s. Messages from *different* senders have no ordering relative to each other.

Ordinary message terms are copied between processes, with placement depending on message-queue configuration. That costs something for large terms, but it is what makes per-process GC and isolation work. Same-node reference-counted binaries and literals can be shared instead of copied. Binary representation depends on the runtime; remote messages are serialized rather than sharing local pointers.

### Selective receive

`receive` does not just take the oldest message. It scans from the start of the message queue and takes the first matching message. Ordinary messages retain per-sender arrival order; OTP 28 priority-message support can place priority messages ahead of ordinary ones. Messages that match nothing stay where they are.

```
mailbox: [{log,a}, {log,b}, {reply,7}]

receive {reply, V} -> V end
=> V = 7
mailbox: [{log,a}, {log,b}]
```

This makes request/reply easy: wait for *the* reply, ignoring other traffic. But a new selective receive may scan unmatched messages before its first match, so a process whose mailbox fills with messages it never matches gets slower and slower: a mailbox of 100,000 stale messages means a 100,000-item scan per receive. The compiler optimises the common case where the pattern contains a freshly created reference (`make_ref()`), skipping messages older than the reference.

## Let it crash

One error-handling style is to recover locally with checks and exception handlers. Erlang's philosophy, from Joe Armstrong's thesis, is different: write the **happy path**, let a process **crash** on anything unexpected, and have another process **restart it** in a known-good state.

This works because of isolation. Ordinary isolated Erlang terms are not shared writable memory. A process can still have changed external state or called unsafe native code before crashing; restarting does not undo those effects. Two primitives connect processes:

- An **Erlang link** is bidirectional. If one linked process dies abnormally, an exit signal kills the other too, unless it **traps exits**, in which case it receives `{'EXIT', Pid, Reason}` as an ordinary message.
- An **Erlang monitor** is one-way. The watcher receives `{'DOWN', Ref, process, Pid, Reason}` and is not killed.

### Supervisors

A **supervisor** is a process that traps exits from its children and uses restart strategy together with each child's restart type (permanent, transient or temporary). For a restart-eligible child:

| Strategy | When one child dies |
|---|---|
| `one_for_one` | Restart only that child |
| `one_for_all` | Restart all children |
| `rest_for_one` | Restart it and those started after it |

Use `one_for_one` for independent workers, `one_for_all` when children only make sense together, and `rest_for_one` when later children depend on earlier ones (a connection pool started before the workers that use it).

A supervisor also has a **restart intensity**: a limit on how often it will restart children before deciding that restarting is not working. It is set by two numbers, a maximum restart count and a time window, and the supervisor gives up as soon as this condition holds:

```formula
n_R > MaxR
n_R = 2 > MaxR = 1
where
n_R: the number of restarts the supervisor has made during the last MaxT seconds, a sliding window that ends now
MaxR: the maximum number of restarts allowed in that window (Erlang's `intensity` setting); the default is 1 in Erlang and 3 in Elixir
MaxT: the length of the window, in seconds (Erlang's `period` setting); the default is 5 seconds in both
>: is greater than
In words: if the restarts inside the window exceed the allowed maximum, the supervisor stops restarting, kills its remaining children and exits, escalating the failure to its own supervisor.
```

The second line is the worked case with Erlang's defaults: a child that crashes twice within 5 seconds needs a second restart, and 2 is more than the 1 allowed, so the supervisor gives up. With Elixir's defaults the same supervisor would tolerate 3 restarts in 5 seconds and give up on the fourth. Restarts older than the window stop counting, so an occasional crash every few minutes never trips the limit. Supervisors nest into a **supervision tree**, so a fault is retried locally first and only spreads upward if restarting does not fix it.

```elixir
children = [
  {Repo, []},     # started first
  {Cache, []},
  {Worker, []}
]
Supervisor.start_link(children,
  strategy: :rest_for_one)
```

Restarting helps with transient faults: a timeout, a bad message, a race. It does not help with a deterministic bug that crashes on every start; that trips the intensity limit and escalates, which is the right outcome.

### OTP behaviours

OTP behaviors package common receive-loop protocols. OTP's **gen_server** wraps the loop and offers two kinds of request:

- `gen_server:cast` sends asynchronously; no reply.
- `gen_server:call` sends and waits for the reply, with a default timeout of 5 seconds. A timeout raises an exit exception; if unhandled, the caller terminates. A supervisor responds only if that process is supervised and restart policy applies.

`call` also gives natural **backpressure**: a sequential caller waits for completion or failure before its next call. This bounds outstanding work per caller, not the total mailbox if callers are unbounded.

## Distribution and location transparency

A pid can refer to a process on another node. `Pid ! Msg` is the same syntax either way, and links and monitors work across nodes (a lost connection triggers `'DOWN'` with reason `noconnection`). That is **location transparency**.

It is transparent in syntax, not in physics. Across a network, messages can be lost, and you cannot tell a slow node from a dead one. Erlang's guarantees reflect this: delivery is not guaranteed, only ordering per sender-receiver pair while the connection lasts. Robust Erlang code assumes any request may go unanswered and uses timeouts and monitors.

## Akka and Orleans

**Akka** brought actors to Scala and Java. In Akka Typed, an actor is a `Behavior[T]` that accepts only messages of type `T`, so the type system restricts message types, but does not prove every value is handled or delivered. Its documented guarantees are the same two as Erlang's:

- **At-most-once** delivery: a message is delivered once or not at all. No automatic retries.
- **Ordering per sender-receiver pair**.

For request/reply, the **ask** pattern sends a message containing a temporary reply-to address and returns a `Future` that fails after a timeout. Akka has supervision too, with a different default: in Akka Typed a failing actor is **stopped**, and you opt in to restarts by wrapping its behaviour in `Behaviors.supervise(...)`. In 2022 Akka moved to the Business Source Licence; the Apache-licensed fork is **Apache Pekko**.

**Microsoft Orleans** (.NET, used for Halo's online services) introduced **virtual actors**, called *Orleans grains*. An Orleans grain is addressed by an ID and always exists logically: the runtime activates it on some server when the first message arrives and deactivates it when idle. Applications normally obtain grain references by ID and let the runtime manage activation; developers still design persistence and failure recovery, and by default each processes one request at a time. Orleans popularised the pattern for stateful cloud services; Akka's *cluster sharding* and Dapr's actors offer similar ideas.

## Where actors hurt

- **Unbounded mailboxes.** Local sends do not wait for message processing, so a fast producer can flood a slow actor until memory runs out. The fix is designed in: use synchronous calls, bounded mailboxes (an option in Akka), or explicit flow control (Akka Streams).
- **Deadlock still exists.** If actor A `call`s B while B `call`s A, both wait for a reply that never comes. With default gen_server call timeouts and unhandled failures, a timeout or peer exit can terminate a participant; exact timing and exit reasons depend on the race.
- **Ordering is local.** If A tells B and C, and B then tells C, C can receive B's message before A's.
- **A hot actor is a bottleneck.** A single actor is sequential, so a hot actor (one counter for the whole system) is a bottleneck.

How fast an unbounded mailbox fills is simple arithmetic: it grows by the difference between the rate messages arrive and the rate the actor handles them.

```formula
Q = (λ − μ) × t
Q = (50,000/s − 30,000/s) × 60 s
Q = 20,000/s × 60 s = 1,200,000
where
Q: the number of messages waiting in the mailbox after t seconds, starting from empty
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
| Named thing | Channel | Process (pid) |
| Send | Sync by default | Async |
| Buffer | Fixed size | Unbounded mailbox |
| Failure | Unrecovered panic terminates program | Links, supervisors |
| Distribution | Local only | Built in |

Neither is strictly better. CSP's synchronous channels make backpressure and some deadlocks easier to see. Actors' asynchronous, named mailboxes make distribution and failure handling natural. You can build either from the other: a Go goroutine reading one channel is an actor, and an Erlang process that only forwards messages is a channel.

## Key takeaways
- An actor has private state and a mailbox, handles one message at a time, and can only send, create and change its behaviour.
- Erlang processes have separate heaps and per-process GC; messages are copied, and ordering is guaranteed only per sender-receiver pair.
- Selective receive scans the mailbox for the first match. Unmatched messages can increase selective-receive cost; catch-all receives and compiler reference optimizations can avoid long scans.
- "Let it crash": links, monitors and supervisors (`one_for_one`, `one_for_all`, `rest_for_one`) with a restart intensity that escalates repeated failure.
- Akka promises at-most-once delivery and per-pair ordering; Orleans' virtual actors are activated on demand.
- Actors still need backpressure and can still deadlock via synchronous calls.

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
