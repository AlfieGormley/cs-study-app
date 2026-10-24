---
id: rs-queued-updates
title: Queue state updates deliberately
level: basic
minutes: 4
summary: Choose replacement or functional updates and trace their order.
---

Sometimes one event needs several changes to the same state. React processes queued updates to calculate the next value. **Batching** groups updates so React can display the resulting state together after the event handler finishes. Do not expect the screen to update between two setter calls in that handler.

## A value requests a replacement

Here is a handler excerpt inside a component whose `count` state is initially 0. Both lines evaluate their argument using the same snapshot.

```js
setCount(count + 1);
setCount(count + 1);
```

Both requests mean “replace with 1”, so the next displayed count is 1, not 2. The second line does not read the result of the first request.

## A function transforms the pending value

An **updater function** receives the pending value from React's update queue. This handler excerpt uses arrow functions: `n => n + 1` means “take a value named n and return one more”.

```js
setCount(n => n + 1);
setCount(n => n + 1);
```

Starting at 0, the first updater returns 1. React passes that pending result to the second updater, which returns 2. This expresses two increments without depending on the handler's older snapshot. Prefer this form when the next state depends on the previous state.

Replacement and functional updates can be mixed. Starting at 0, trace this excerpt from top to bottom:

```js
setCount(5);
setCount(n => n + 1);
setCount(2);
```

The replacement chooses 5. The updater transforms that to 6. The final replacement chooses 2, so the next count is 2. This is an ordered queue, not a rule that all increments must win.

## Keep updaters pure

A **pure updater** calculates and returns the next state without modifying old state or doing external work. Do not send requests, change another state variable, or write to external arrays inside an updater. Put event-specific external work in the handler instead. In development Strict Mode, React may call updater functions twice to expose accidental impurities; one result is ignored. Correct logic must not depend on the number of updater calls.

React does not batch separate intentional clicks into one event. For this lesson, trace each handler in order, then consider the next interaction with the newly displayed state. Batching is useful behaviour, not a timer you should attempt to exploit for correctness.

> [!analogy] Real-world analogy: Editing instructions in order
> A clerk receives “use 5”, “add one”, then “use 2” before updating a display.
>
> **How it maps:** Replacement updates choose a pending value; updater functions transform the current pending value in queue order.
>
> **Where it stops:** The clerk is only a model of this queue. React can perform additional internal work, and pure updater functions must tolerate repeated development checks.

## Key takeaways
- Repeating a snapshot-based replacement does not accumulate increments.
- Functional updates receive the pending value and compose in order.
- Updaters must only calculate state; keep external work outside them.

## Further reading
- [Queueing state updates](https://react.dev/learn/queueing-a-series-of-state-updates)
- [useState caveats](https://react.dev/reference/react/useState)
