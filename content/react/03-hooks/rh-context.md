---
id: rh-context
title: Pass shared values with context
level: intermediate
minutes: 4
summary: Use the nearest provider to supply a value without manually passing it through every layer.
---

Start with props: a child gets a value and callbacks from its parent. If many distant components need the same value, passing it through intermediate components can become repetitive. **Context** lets a component read a value supplied by an ancestor without each intermediate component forwarding a prop.

`createContext(defaultValue)` creates a context object outside components. A **provider** supplies its value to descendants. A **consumer** reads it with `useContext`. The context object identifies the channel; it does not hold a global state variable. Put changing data in state owned by an appropriate parent and provide that value.

## Read the nearest provider

Complete React 19 module example for a React-enabled JSX environment. React 19 supports `<ThemeContext value={...}>` as provider syntax. You may also see `<ThemeContext.Provider value={...}>` in existing code.

```jsx
import {
  createContext, useContext, useState
} from 'react';

const ThemeContext = createContext('light');

function ThemeLabel() {
  const theme = useContext(ThemeContext);
  return <p>Theme: {theme}</p>;
}

export default function ThemeDemo() {
  const [theme, setTheme] =
    useState('dark');
  return (
    <>
      <ThemeLabel />
      <ThemeContext value={theme}>
        <ThemeLabel />
        <ThemeContext value="light">
          <ThemeLabel />
        </ThemeContext>
      </ThemeContext>
      <button onClick={() => setTheme(
        t => t === 'dark' ? 'light' : 'dark'
      )}>
        Switch outer theme
      </button>
    </>
  );
}
```

Read the three labels in order. The first has no provider above it, so reads the default light. The second reads the outer provider's initial dark. The third reads the nearer inner provider's light. After switching the outer theme, the second becomes light; the first and third still read light for their original reasons.

React searches upwards from the component calling `useContext`. A provider returned by that same component is below the call, so it cannot affect that call. The default is a fallback when there is no matching provider, not a value that gets merged into every provider.

> [!analogy] Real-world analogy: A room's noticeboard
> A building has general notices, while an individual room can supply its own local notice.
>
> **How it maps:** A nearer provider overrides the value a consumer would otherwise get from a more distant ancestor.
>
> **Where it stops:** Context follows the React component tree, not physical distance or DOM styling rules.

## Updates still matter

When a provided value changes according to `Object.is`, React updates components reading that context. Wrapping a consumer in `memo` does not block fresh context. A new object used as a provider value has a new identity even if its fields look the same, so careless object creation can cause unnecessary updates.

Context transports a value; it does not decide state ownership or make mutation safe. Keep ordinary immutable state updates. Prefer a small relevant context over placing every unrelated app value in one changing object. For two nearby siblings, lifting state and passing props may be simpler and more explicit.

## Key takeaways

- Try props first; context is useful for values needed across distant descendants.
- Consumers read the nearest matching provider above them, or the default if none exists.
- Context updates reach consumers; context does not replace state ownership or immutability.

## Further reading

- [React: Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context)
- [React: useContext](https://react.dev/reference/react/useContext)
- [React: createContext](https://react.dev/reference/react/createContext)
