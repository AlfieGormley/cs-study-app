---
id: rs-state-snapshots
title: State is a render snapshot
level: basic
minutes: 4
summary: Predict what a handler reads before and after requesting a state update.
---

A state setter requests a future render; it does not rewrite the state variable in the function already running. Each render receives a **state snapshot**. The JSX and event handlers created by that render use that snapshot.

This distinction answers a common beginner question: “Why did I read the old number immediately after setting it?” You read the number that belongs to the current render. React will call the component again with the next value and create new handlers for that render.

## Trace a single click

The following component function assumes `useState` is imported from React and JSX is transformed by a React-enabled build. Its `report` prop is a function supplied by the parent; it records the value passed to it. It is a teaching example inside an event handler, not logging during render.

```jsx
function Counter({ report }) {
  const [count, setCount] = useState(0);
  function handleClick() {
    setCount(count + 1);
    report(count);
  }
  return (
    <button onClick={handleClick}>
      {count}
    </button>
  );
}
```

Initially the button displays 0. The first click requests 1, then reports 0. After React processes the update, the button displays 1. A second click uses the new handler: it requests 2 and reports 1. Calling the setter is not an instruction to change the existing `count` binding halfway through the handler.

A normal local variable also does not remember values between component calls. React state supplies that memory. Directly assigning to a local variable will not tell React to display a new result.

## Delayed work keeps its captured values

A JavaScript **closure** lets a function retain access to the variables from where it was created. A delayed callback created by a handler therefore keeps that render's state values. It does not automatically switch to values from a later render.

For example, suppose a Send handler schedules a message using the currently selected recipient. Changing the selection before the callback runs does not change the already captured recipient. Decide whether the operation should use the value at the time of the click or a later value; do not assume those are interchangeable. We will use functional updates next when an update needs the latest pending state.

> [!analogy] Real-world analogy: A printed order slip
> A waiter prints the order as it stood when you pressed Send. Later edits make a new order slip.
>
> **How it maps:** The printed slip is a render snapshot; its handler reads those recorded values even after requesting another render.
>
> **Where it stops:** React state is held by React, and JavaScript closures capture bindings. There is no literal copy of every object: mutating shared objects can corrupt older snapshots.

## Key takeaways
- A handler reads the state snapshot of the render that created it.
- Setters request another render; they do not change the current state binding.
- Delayed callbacks retain their captured values unless you deliberately design another mechanism.

## Further reading
- [State as a snapshot](https://react.dev/learn/state-as-a-snapshot)
- [useState reference](https://react.dev/reference/react/useState)
- [Closures — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
