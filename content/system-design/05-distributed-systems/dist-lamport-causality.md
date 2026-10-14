---
id: dist-lamport-causality
title: Happens-before and Lamport clocks
level: intermediate
minutes: 5
summary: Trace logical counters while avoiding the mistake that a smaller timestamp proves causality.
sourceLesson: dist-time-ordering
---

Wall time cannot reliably answer whether one event influenced another. Logical clocks start from the information that can actually flow between processes.

## Happens-before

Lamport's 1978 paper defined order without clocks. It uses two pieces of notation:

```formula
a → b
a ∥ b
where
a: one event, such as a local step, a message send or a message receive on some process
b: another event, possibly on a different process
→: "happens before": a could have influenced b
∥: "is concurrent with": neither a → b nor b → a holds
In words: a → b means information could have flowed from a to b; a ∥ b means no information could have flowed either way.
```

Event *a* **happens before** *b* (a → b) if:

1. a and b are on the same process and a comes first, or
2. a is sending a message and b is receiving that message, or
3. there's an event c with a → c and c → b (transitivity: chains of happens-before also count).

If neither event happens before the other, the events are **concurrent**. Concurrent doesn't mean simultaneous; it means neither could have influenced the other.

## Lamport clocks

Each process keeps a single whole-number counter, L, starting at 0. Two rules update it:

```formula
L_new = L + 1
L_new = max(L, t) + 1
where
L: this process's current Lamport counter, a whole number with no unit
L_new: the counter's value after the event; it is also that event's timestamp
t: the timestamp carried on an incoming message
max: the larger of its inputs, e.g. max(3, 8) = 8
In words: on a local event or a send, add one (and attach the new value to the message); on a receive, jump past both your own counter and the message's timestamp, then add one.
```

The first rule applies before every local event or send; the second on every receive. Worked example: P1's counter is 7 and P2's is 3. P1 sends a message, so its counter becomes 7 + 1 = 8 and the message carries 8. P2 receives it and sets its counter to the larger of 3 and 8, plus one, which is 9. The send (8) comes before the receive (9), as it must.

```
 P1        P2        P3
 1 a
 2 send--->3 recv
           4 b
           5 send--->6 recv
 3 c                 7 d
```

The guarantee Lamport clocks give:

```formula
a → b ⇒ L(a) < L(b)
where
a: an event
b: another event
→: "happens before": a could have influenced b
⇒: "implies": whenever the left side is true, the right side is true too
L(a): the Lamport timestamp of event a
L(b): the Lamport timestamp of event b
In words: if a happened before b, a's timestamp is smaller. It does not work the other way round: a smaller timestamp doesn't prove a happened first.
```

Break ties with process id to get a **total order** consistent with causality. That's enough for things like a totally ordered mutex queue.

Limitation: the converse fails. In the diagram, L(c) is 3 and L(b) is 4, so c has a smaller timestamp than b, but c and b are concurrent: no message path links them. **A Lamport timestamp can't tell you whether two events are concurrent.**

Read the guarantee the right way round:

- A smaller timestamp means the event *might* have happened before the other, or they might be concurrent.
- Equal timestamps on different processes mean the events are **definitely concurrent**, because causally related events always have different timestamps.
- A larger timestamp means that event did **not** happen before the other. Either the other happened first, or they are concurrent.

### Logical clocks you already use

Many systems contain similar logical epoch counters: Raft's **term**, Paxos's **ballot number**, Kafka's **leader epoch**, ZooKeeper's **zxid**. Each is a number that only goes up and is carried on messages, so a node that sees a higher one knows its own information is out of date. These counters track protocol generations; they do not necessarily assign a distinct Lamport timestamp to every application event. The resource-fencing unit later in this module uses ordered generations for fencing tokens.

## Key takeaways
- Happens-before follows local process order, message delivery and transitive chains; concurrent means neither event could influence the other.
- Lamport counters increment on local events and jump past both local and message counters on receive.
- Causality implies increasing timestamps, but increasing timestamps do not prove causality; equal timestamps on distinct processes imply concurrency.

## Further reading
- [Time, Clocks, and the Ordering of Events (Lamport, 1978)](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
