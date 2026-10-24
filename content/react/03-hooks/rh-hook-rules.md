---
id: rh-hook-rules
title: Where Hooks belong
level: basic
minutes: 3
summary: Keep ordinary Hook calls in a stable order inside components and custom Hooks.
---

You have already used `useState`. It is a **Hook**: a React function that connects a component to a capability such as state. A **custom Hook** is your own function that calls Hooks to reuse logic. Its name starts with `use` followed by a capital letter, such as `useCounter`.

These rules apply to the ordinary Hooks in this course, including `useState`, `useRef` and `useEffect`. React has other APIs with different rules; you do not need those APIs here.

## Keep the calls predictable

Make each **top-level Hook call** directly in a function component or custom Hook body, before any conditional return. Do not call them inside conditions, loops, event handlers, nested callbacks or ordinary utility functions. React must be rendering the component when these Hooks are called.

React associates a component's Hook state with the order of its calls. If a conditional Hook disappears on a later render, subsequent calls no longer line up. Giving the variables different names does not solve that problem.

> [!analogy] Real-world analogy: Labelled seats
> Imagine handing out numbered seats in the same order at each rehearsal.
>
> **How it maps:** A component's successive Hook calls need a consistent ordering, like the same people receiving the same numbered seats.
>
> **Where it stops:** React tracks calls within component instances; it does not inspect variable names or literally allocate theatre seats.

## Put the condition after the Hook

This complete component example assumes the React-enabled JSX environment from the first module. The import makes `useState` available; the environment transforms JSX before the browser executes it.

```jsx
import { useState } from 'react';

export default function Counter({
  hidden
}) {
  const [count, setCount] = useState(0);
  if (hidden) return null;

  return (
    <button
      onClick={() => setCount(c => c + 1)}
    >
      Count: {count}
    </button>
  );
}
```

When `hidden` changes from false to true, the component still calls its Hook and then returns nothing. When it becomes false again at the same tree position, its count is preserved. Moving the Hook below the conditional return would break the ordering rule.

An event handler may call `setCount`, because a setter is an ordinary function React returns to you. Calling `useState` inside that handler would be a new Hook call outside rendering. Distinguish creating the state during render from requesting an update later.

If each row needs local state, make a `Row` component and render rows with stable keys. Put its Hooks at the top of `Row`, rather than calling a Hook inside the parent's `map` callback. A React Hooks linter can catch many ordering and dependency mistakes before you run the app.

## Key takeaways

- Call ordinary Hooks at the top level of components or custom Hooks, before conditional returns.
- Hook order belongs to each component instance; variable names do not identify its state.
- Handlers may call setters; ordinary Hook calls belong in rendering.

## Further reading

- [React: Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks)
- [React: State is tied to a position in the tree](https://react.dev/learn/preserving-and-resetting-state)
