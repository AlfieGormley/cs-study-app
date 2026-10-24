---
id: rh-custom-hooks
title: Reuse logic with custom Hooks
level: intermediate
minutes: 4
summary: Extract useful behaviour into named Hooks while keeping each call's state independent.
---

A **custom Hook** is a function that uses React Hooks to provide a reusable behaviour. Name it for what it does, beginning with `use` followed by a capital letter. Give it clear inputs and return values. Calling it is part of rendering the caller; it must follow the same top-level ordering rules as built-in Hooks.

Do not turn every utility into a Hook. A plain function that only filters an array needs no special Hook name. Extract a Hook when it packages stateful or external synchronisation logic with a useful purpose.

## Share the recipe, not the state

Complete module example for a React-enabled JSX environment. A returned object's shorthand `{ count, increment }` means properties named `count` and `increment` containing those local values.

```jsx
import { useState } from 'react';

export function useCounter(step) {
  const [count, setCount] = useState(0);
  function increment() {
    setCount(c => c + step);
  }
  return { count, increment };
}

function Counter({ step }) {
  const { count, increment } =
    useCounter(step);
  return (
    <button onClick={increment}>
      {count}
    </button>
  );
}

export default function Pair() {
  return (
    <>
      <Counter step={1} />
      <Counter step={2} />
    </>
  );
}
```

Click the first button twice: its value becomes 2 while the second stays 0. Click the second once: it becomes 2 without changing the first. Each call uses its own state, even though both execute the same Hook function. To share one count, move one Hook call to a common parent and pass its value and handlers down.

> [!analogy] Real-world analogy: One recipe, two kitchens
> Two cooks can follow the same recipe while keeping separate ingredients and meals.
>
> **How it maps:** A custom Hook shares the instructions for behaviour; each call has its own state and effects.
>
> **Where it stops:** A Hook may deliberately connect to a shared external source, so independent local state does not imply the outside world is separate.

## Keep synchronisation inside the Hook

A Hook that installs a browser listener must also remove it. The following complete Hook definition extracts the previous lesson's keyboard behaviour. A component calls `useLastKey()` at its top level and renders the returned string.

```jsx
import { useEffect, useState } from 'react';

export function useLastKey() {
  const [key, setKey] = useState('None');
  useEffect(() => {
    function onKey(event) {
      setKey(event.key);
    }
    window.addEventListener(
      'keydown', onKey
    );
    return () => {
      window.removeEventListener(
        'keydown', onKey
      );
    };
  }, []);
  return key;
}
```

Two components using this Hook both respond to the same keyboard because they observe the same browser, not because they share a state variable. Removing one component removes its subscription while the other continues working. Extraction should preserve the original behaviour, dependencies and cleanup.

The `step` input in `useCounter` is read from each current render. If a parent changes it, future clicks use the new step without resetting the count. Initial state is only initial state; passing different inputs to a Hook does not automatically mean resetting every value inside it.

## Key takeaways

- Custom Hooks share stateful logic; separate calls have independent state.
- Clear inputs and outputs make a Hook easier to read and test.
- Keep effect cleanup and accurate dependencies with the behaviour being extracted.

## Further reading

- [React: Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [React: Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks)
- [MDN: Object initialiser shorthand](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Object_initializer)
