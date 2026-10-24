---
id: rc-events-state
title: Events and a component’s memory
level: basic
minutes: 5
summary: Pass a function as an event handler and use state to remember interaction results.
---

A rendered button needs a way to respond when someone uses it. An **event handler** is a function React calls in response to an interaction. A component can then update **state**, its remembered data, so that its next render describes the changed screen.

## Pass a function for React to call

The built-in button's `onClick` prop receives a function. Pass the function itself, such as `onClick={handleClick}`. Writing `onClick={handleClick()}` calls it while rendering and passes its return value instead. If that call updates state during render, it can cause repeated rendering rather than waiting for a click.

An arrow callback is also useful when a handler needs an argument: the arrow function can call another function when the event happens. The key question is whether JSX is receiving a function to run later or the result of running it now.

## Remember a value with useState

**useState** is a React **Hook**, a function that gives a component a React feature. Call it at the top level of the component, before any conditional return; do not call it inside a loop, condition or handler. Later lessons explain the Hook rules in more detail.

`useState(0)` supplies an initial value. It returns an array with two entries: the current state value and a setter function. Array destructuring gives them local names. Calling the setter requests an update; it does not change the current render's variable in place.

This complete component file has two independent counter instances. The named import obtains `useState` from React. An arrow updater receives the pending previous value and returns the next value; later lessons explain update queues.

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    // Calculate from the previous value.
    setCount(previous => previous + 1);
  }

  return (
    <button onClick={handleClick}>
      Completed: {count}
    </button>
  );
}

export default function App() {
  return (
    <>
      <Counter />
      <Counter />
    </>
  );
}
```

Both buttons initially display `Completed: 0`. Click the first twice and the second still displays zero while the first displays two. React keeps state for each component instance. Two uses of the same function do not automatically share memory.

For one click, React calls the handler, the setter requests the update, React renders using the new state, then commits any necessary DOM change. The component function can run again without resetting state to the initial value. The initial value starts that instance's state; it is not an instruction to overwrite it every render.

## Why a normal variable is insufficient

A local variable inside a component starts fresh when the function runs again. Changing it also does not request a React render. State solves both needs: React retains the value between renders and its setter tells React there is an update to process. State lasts while React preserves that component instance in the UI; a later lesson explains removal and resetting.

> [!analogy] Real-world analogy: Separate scorecards
> Two players using identical scorecard designs still keep separate scores.
>
> **How it maps:** The component function is the shared design; each rendered instance has its own state value and setter.
>
> **Where it stops:** React manages that memory according to component identity in the UI. It is not permanent storage and does not survive every removal or page reload.

## Key takeaways
- Pass event handlers as functions; do not invoke them during render.
- `useState` returns the current value and a setter that requests an update.
- A normal local variable neither persists nor schedules a React update.
- Separate component instances have independent state.

## Further reading
- [Responding to events — React](https://react.dev/learn/responding-to-events)
- [State: a component’s memory — React](https://react.dev/learn/state-a-components-memory)
