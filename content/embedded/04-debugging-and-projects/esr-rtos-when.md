---
id: esr-rtos-when
title: Decide when an RTOS helps
level: intermediate
minutes: 4
summary: Compare a cooperative loop with scheduled tasks without treating priority as a deadline proof.
---

A small cooperative loop can remain easy to inspect when every operation is bounded. As communication, sampling and reporting become independent activities, an **RTOS**, or real-time operating system, can help organise their scheduling and waiting. Adding an RTOS does not make an unbounded driver call or an overloaded processor meet a deadline.

## Work can wait without consuming the processor

An RTOS task has execution state and a task stack. In a single-core system, only one task executes on that core at an instant. A task can be ready to run, running, or blocked while waiting for a supported event or time condition. Other states and exact scheduling rules depend on the kernel and configuration.

With preemption enabled in a priority-based FreeRTOS configuration, a higher-priority ready task can preempt a lower-priority one. A blocked high-priority task is not ready; lower-priority ready work can run. Equal-priority time sharing and other details depend on configuration.

Consider a deliberately simplified single-core trace with preemption enabled. The sensor task has higher priority than the logger:

| Event | Sensor task | What can run |
|---|---|---|
| Waiting on a supported event | Blocked | Ready logger |
| Event makes sensor ready | Ready | Sensor can preempt logger |
| Sensor finishes bounded work and waits | Blocked | Logger can resume |

> [!analogy] Real-world analogy: a shared workshop bench
> Several workers need one bench. Someone waiting for a delivery can step aside; an urgent ready job can be given the next use of the bench.
>
> **How it maps:** The bench is one CPU core, tasks are the workers, and a blocking wait removes work from the ready set until its event occurs. Priority helps choose among ready work.
>
> **Where it stops:** The kernel follows exact scheduling rules rather than social judgement. Shared resources, interrupt work and execution time can still delay an urgent task beyond its deadline.

## Add ownership before adding tasks

Assign one owner to a peripheral or protect its use with the appropriate mechanism. A queue can carry commands or results between tasks, but its finite capacity needs a rule for handling a full buffer. Kernel scheduling does not make every SDK driver safe for simultaneous calls.

Each task also needs a stack budget, and scheduling adds its own configuration and debugging work. Measure the actual workload, check blocking behaviour and bound competing work. If the small indicator application already meets its requirements with a measured loop, keeping that loop is a valid choice. Introduce tasks when they simplify explicit waiting, ownership and coordination enough to justify their costs.

## Key takeaways
- A blocked task is not ready work competing for the CPU.
- Priority does not establish a worst-case deadline guarantee.
- Tasks still need bounded work, shared-device ownership and stack capacity.

## Further reading
- [FreeRTOS task states and task API contracts](https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/main/include/task.h)
- [FreeRTOS scheduling implementation](https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/main/tasks.c)
- [FreeRTOS queues and wait timeouts](https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/main/include/queue.h)
