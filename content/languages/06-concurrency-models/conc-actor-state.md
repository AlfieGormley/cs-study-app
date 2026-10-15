---
id: conc-actor-state
title: Actor addresses, state and messages
level: advanced
minutes: 4
sourceLesson: conc-actors
summary: Actors interact through messages rather than direct access to another actor’s private state.
---

The preceding channel style organizes communication around explicit channels. The actor model organizes it around actor addresses. In the model, an **actor** encapsulates state and responds to messages addressed to it; practical implementations commonly hold pending messages in a **mailbox**. Actors communicate asynchronously by address. Isolated actor state avoids shared-memory data races. Real actor libraries may allow shared mutable references or external stores, which still need coordination. And because messages are the only interface, the same code can run in one process, across cores, or across machines.

Carl Hewitt, Peter Bishop and Richard Steiger proposed actors in 1973. Erlang, built at Ericsson from 1986 for telephone switches, arrived at almost the same design independently and showed what it was good for: systems that keep running while parts of them fail.

## What an actor can do

When an actor processes a message, it may do only three things:

1. **Send** messages to actors whose addresses it knows.
2. **Create** new actors.
3. Decide how to handle the **next** message (change its state or behaviour).

Common actor implementations serialize message handling; reentrant implementations can interleave requests while retaining serialized execution turns. In a non-reentrant handler implementation, only that actor’s handler accesses its private state, so that state needs no inter-handler lock. Reentrant request handling and deliberately shared references require additional invariant reasoning; other actors can run concurrently.

```
  sender A --msg--+
                  v
  sender B --> [mailbox] --> actor
                  ^         (state,
  sender C --msg--+          one msg
                              at a time)
```

## Erlang processes

An Erlang **process** is an actor. It is a runtime-scheduled lightweight process with its own heap, so garbage collection is per process: collection usually concerns that process rather than every process heap. No universal microsecond pause figure is supplied; shared runtime resources and native code remain relevant. Process termination releases its owned resources, subject to implementation details.

A counter actor:

```erlang
% Loop arguments carry private state.
-module(counter).
-export([start/0, loop/1]).

start() -> spawn(?MODULE, loop, [0]).

loop(N) ->
    receive
        {inc, By} ->
            % Tail-call with the new state.
            loop(N + By);
        {get, From} ->
            % Reply without waiting for
            % handling.
            From ! {count, N},
            loop(N)
    end.
```

`spawn` creates a process and returns its **Erlang pid**. `Pid ! Msg` sends asynchronously: it does not wait for the receiver to process the message. Sending can still suspend due to distribution-buffer backpressure or other runtime conditions. `receive` takes a message matching one of its patterns. State is not a mutable variable: `loop` calls itself with the new value, and the tail call means no stack grows.

```erlang
% One sender preserves ordinary order.
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

This makes request/reply easy: wait for *the* reply, ignoring other traffic. But a new selective receive may scan unmatched messages before its first match, so unmatched traffic can increase receive cost. If 100,000 unmatched ordinary messages precede a matching reply, an unoptimized fresh receive may scan those 100,000 messages first; receive markers, compiler optimizations and priority-message rules can change that cost. The compiler optimises the common case where the pattern contains a freshly created reference (`make_ref()`), skipping messages older than the reference.

## Key takeaways
- Actors interact through messages rather than direct access to another actor’s private state.
- Serial handlers do not make external stores or deliberately shared references safe.
- Ordinary signals preserve sender-to-receiver order; selective receive may skip messages.
- Erlang isolates ordinary mutable process state; binaries and external resources need qualified descriptions.

## Further reading
- [Primary source: www.erlang.org](https://www.erlang.org/doc/system/ref_man_processes.html)
- [Primary source: www.erlang.org](https://www.erlang.org/doc/system/sup_princ.html)
- [Primary source: doc.akka.io](https://doc.akka.io/libraries/akka-core/current/general/message-delivery-reliability.html)
