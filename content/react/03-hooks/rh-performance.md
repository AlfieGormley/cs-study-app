---
id: rh-performance
title: Measure before memoising
level: intermediate
minutes: 4
summary: Understand what memoisation can save while keeping rendering correct without it.
---

A component can render because its own state changes, a parent renders it, or context it reads changes. A render recalculates the description of UI; it does not mean React rewrites every DOM element. First keep rendering pure, put state near the components that need it, and remove unnecessary effects.

If an interaction feels slow, reproduce it with realistic data and inspect it with React Developer Tools' **Profiler** or the browser's performance tools. Compare the same interaction before and after a change. Development checks can add work, so development timing is not a reliable substitute for production measurement. Small examples here teach behaviour, not a measured speedup.

## Three different things to cache

**Memoisation** reuses a previous result when its inputs are unchanged.

| Tool | What it may reuse |
|---|---|
| `memo` | A component's previous render work |
| `useMemo` | A calculated value |
| `useCallback` | A function identity |

`memo` wraps a component and normally compares each prop using `Object.is`. It can skip parent-driven re-rendering with unchanged props, but this is an optimisation, not a guarantee. Its own state and consumed context still update it. A freshly created array, object or callback is a different identity, even when its contents or code look the same.

## Cache a calculation only when worthwhile

Complete component example, assuming `tasks` is an array of objects with `done` booleans. This tiny calculation is illustrative; it has not been shown to need caching.

```jsx
import { useMemo } from 'react';

export default function Summary({ tasks }) {
  const remaining = useMemo(
    () => tasks.filter(t => !t.done),
    [tasks]
  );
  return (
    <p>{remaining.length} remaining</p>
  );
}
```

The calculation must be pure. Replacing a task means copying the changed object and array: if you mutate the existing array, its identity may stay the same and the cached result can become stale. `useMemo` does not make mutation safe. Removing `useMemo` and calculating the filter directly must preserve correctness.

`useCallback` returns a function without calling it. Component-body excerpt, assuming `useCallback` is imported and `setTasks` is the stable `useState` setter:

```jsx
const toggle = useCallback(id => {
  setTasks(items => items.map(item =>
    item.id === id
      ? { ...item, done: !item.done }
      : item
  ));
}, []);
```

The functional update receives current tasks, so this callback does not read a captured `tasks` value. If a callback reads changing props or state, those inputs belong in its dependencies. A stable callback can help when passed to a memoised child; adding one everywhere adds complexity without establishing a benefit.

## Keep caches optional

React may discard cached values or render a memoised component again. Do not put an essential connection or side effect inside `useMemo`, or rely on it to retain application state. An optimisation must preserve behaviour if React recalculates it.

React Compiler can automatically memoise components, values and functions when configured in a supporting build. It is a build tool, not something guaranteed merely by importing React. Check the project's build configuration before adding manual memoisation. Correctness, immutability and useful measurements still come first.

## Key takeaways

- Reproduce and measure slow interactions before adding caches.
- `memo`, `useMemo` and `useCallback` cache different things and do not guarantee correctness or render counts.
- Immutable updates and accurate dependencies matter with or without memoisation.

## Further reading

- [React: memo](https://react.dev/reference/react/memo)
- [React: useMemo](https://react.dev/reference/react/useMemo)
- [React: useCallback](https://react.dev/reference/react/useCallback)
- [React: React Developer Tools](https://react.dev/learn/react-developer-tools)
- [React: Compiler introduction](https://react.dev/learn/react-compiler/introduction)
