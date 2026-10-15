---
id: conc-actor-supervision
title: Links, supervisors and restart budgets
level: advanced
minutes: 4
sourceLesson: conc-actors
summary: Restart strategy and each child’s restart type jointly decide what restarts.
---

Erlang isolation limits the ordinary in-memory damage from one process failing. This unit explains how another process observes that failure and applies an explicit restart policy.

## Let it crash

One error-handling style is to recover locally with checks and exception handlers. Erlang's philosophy, from Joe Armstrong's thesis, is different: write the **happy path**, let a process **crash** on anything unexpected, and have another process **restart it** in a known-good state.

This works because of isolation. Ordinary isolated Erlang terms are not shared writable memory. A process can still have changed external state or called unsafe native code before crashing; restarting does not undo those effects. Two primitives connect processes:

- An **Erlang link** is bidirectional. If one linked process dies abnormally, the linked peer normally terminates on that abnormal exit signal unless it **traps exits**, in which case the signal is ordinarily converted to `{'EXIT', Pid, Reason}` as an ordinary message.
- An **Erlang monitor** is one-way. The watcher receives `{'DOWN', Ref, process, Pid, Reason}` and is not killed.

The direct `exit(Pid, kill)` signal is a special untrappable termination request. Its reason becomes `killed` when propagated through links, which peers may trap; trapping exits is not immunity from every way a process can be killed.

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
n_R: restart attempts counted by the supervisor within its restart-intensity period, including the attempt currently being considered; no restart is performed once that attempt exceeds the budget
MaxR: the maximum number of restarts allowed in that window (Erlang's `intensity` setting); the default is 1 in Erlang and 3 in Elixir
MaxT: the length of the window, in seconds (Erlang's `period` setting); the default is 5 seconds in both
>: is greater than
In words: if the restarts inside the window exceed the allowed maximum, the supervisor stops restarting, kills its remaining children and exits, escalating the failure to its own supervisor.
```

The second line is the worked case with Erlang's defaults: a child that crashes twice within 5 seconds needs a second restart, and 2 is more than the 1 allowed, so the supervisor gives up. With Elixir's defaults the same supervisor would tolerate 3 restarts in 5 seconds and give up on the fourth. Restarts older than the window stop counting, so an occasional crash every few minutes never trips the limit. Supervisors nest into a **supervision tree**, so a fault is retried locally first and only spreads upward if restarting does not fix it.

```elixir
# Start order defines later dependants.
children = [
  {Repo, []},     # started first
  {Cache, []},
  {Worker, []}
]
Supervisor.start_link(children,
  strategy: :rest_for_one)
```

Restarting helps with transient faults: a timeout, a bad message, a race. It does not help with a deterministic bug that crashes on every start; that trips the intensity limit and escalates, which is the right outcome.

## Key takeaways
- Restart strategy and each child’s restart type jointly decide what restarts.
- Repeated failure exceeds an intensity budget and escalates; restart does not undo external effects.

## Further reading
- [Primary source: www.erlang.org](https://www.erlang.org/doc/system/ref_man_processes.html)
- [Primary source: www.erlang.org](https://www.erlang.org/doc/system/sup_princ.html)
- [Primary source: doc.akka.io](https://doc.akka.io/libraries/akka-core/current/general/message-delivery-reliability.html)
