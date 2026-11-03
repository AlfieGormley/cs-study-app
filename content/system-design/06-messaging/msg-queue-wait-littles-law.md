---
id: msg-queue-wait-littles-law
title: Convert average queue depth into waiting time
level: basic
minutes: 2
summary: Use Little's Law with a stable queue and a consistent system boundary.
sourceLesson: msg-sync-vs-async
---

Queue depth is a count, but users experience a delay. Little's Law connects the two. Decide what you count before using it: messages still waiting correspond to queue wait, while waiting plus in-flight messages correspond to total time in that system.

## Little's Law: a useful sanity check

Little's Law says that, in a stable system (one where, over time, items leave as fast as they arrive), the average number of items in it equals the arrival rate times the average time each item spends in it. Rearranged, it tells you the average wait from two numbers a dashboard already shows:

```formula essential
L = λ × W
W = L / λ
where
L: the average number of items in the system; for a queue, the average queue depth, in messages
λ: lambda, the average arrival rate, in messages per second
W: the average time an item spends in the system, in seconds (s)
s: seconds
In words: average depth equals arrival rate times average wait, so depth divided by arrival rate gives the average wait.
```

So a queue that receives 400 messages per second and holds a steady 12,000 makes each message wait about 30 seconds on average. This turns "queue depth" (which dashboards show) into "delay" (which users feel).

The same depth can mean very different delays. 12,000 messages waiting in a queue that receives 4,000 a second is only about a 3-second wait; in one that receives 40 a second it is about 5 minutes. Depth alone does not tell you whether users are waiting: you need the rate as well.

Little's Law holds for long-run averages in a stable system, whatever the number of consumers or the order they serve messages in. While a queue is growing during a burst, the momentary numbers need not match it.

> [!analogy] Real-world analogy: people inside a café
> If about two customers walk into a café each minute and there are usually about ten people inside, each customer must be staying about five minutes on average. You can work that out from the door counter and a head count, without timing anyone.
>
> **How it maps:** The head count is the queue depth (L), customers per minute is the arrival rate (λ) and the average stay is the wait (W). Choosing whether to count only people waiting for coffee, or also people sitting down, is choosing the system boundary.
>
> **Where it stops:** The estimate only works when the café is in a steady state; at opening time, when it is filling up, a head count and the door rate do not give the stay. And it gives the *average* stay, not how long the unluckiest customer waited.

## Key takeaways

- In a stable system, average depth divided by average arrival rate gives average time spent inside the measured boundary.
- Waiting-only depth measures time before processing; including active work measures the whole residence time.
- Use long-run averages; a snapshot taken during burst growth need not obey the steady-state estimate.

## Further reading

- [Little's law (Wikipedia)](https://en.wikipedia.org/wiki/Little%27s_law)
- [Avoiding insurmountable queue backlogs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
