---
id: rh-effect-dependencies
title: Dependencies must match the effect
level: intermediate
minutes: 4
summary: Identify the values an effect reads and avoid stale subscriptions or unnecessary effects.
---

An effect's **dependency array** lists the reactive values its setup reads: props, state, and variables or functions declared in the component body. React compares each listed value with its previous value using `Object.is`. For objects and functions this compares identity, not a deep inspection of their contents.

Dependencies describe the code. They are not a menu of when you would like an effect to run. Use a React Hooks linter and fix a missing dependency by changing the code or including the value; suppressing the warning can leave behaviour tied to an old render.

## Reconnect to the selected room

Component example: `connectRoom` is a stable imported helper defined outside components supplied by the teaching environment. It takes a room name, opens an external connection and returns an object with `disconnect()`. Its internal network implementation is outside this example.

```jsx
import { useEffect } from 'react';
import { connectRoom } from './chat.js';

export default function Room({ room }) {
  useEffect(() => {
    const connection = connectRoom(room);
    return () => connection.disconnect();
  }, [room]);

  return <p>Room: {room}</p>;
}
```

Mount with `room` set to `music`: setup connects to music. Change it to `books`: React first runs cleanup for music, then setup connects to books. Re-render with books again: that dependency has not changed, so this update does not require re-synchronisation. Removing the component disconnects books.

If you replace `[room]` with `[]`, the connection remains with music after the prop changes. This is a **stale closure**: the original setup and its functions retain the values from the render that created them. The visible JSX may say books while the external connection still uses music.

## Three dependency choices

| Argument | Behaviour |
|---|---|
| `[room]` | Re-synchronise when room changes |
| `[]` | No reactive inputs to compare |
| Omitted | Re-run after this component commits |

All three run setup when the effect first starts; cleanup and development checks still apply. An empty array does not mean that an effect can never start again after a component is removed and mounted afresh.

An object created inside rendering is a fresh object each time. If an effect only needs `room`, build its connection options inside setup and depend on `room`, instead of depending on an unnecessary fresh options object. This reduces unnecessary reconnecting without hiding a real input.

## Remove the effect when possible

To show tasks matching a search query, call `tasks.filter(...)` during rendering. Both tasks and query are already available inputs; a second state variable and an effect introduce another value to keep consistent. For sending a message after a click, use the click handler. First decide whether there is an external synchronisation to maintain; only then design its dependencies.

## Key takeaways

- Include the reactive inputs actually read by an effect.
- Missing dependencies can leave external behaviour using an old render's values.
- Reduce dependencies by simplifying the code, and derive render data directly when possible.

## Further reading

- [React: Removing Effect Dependencies](https://react.dev/learn/removing-effect-dependencies)
- [React: Lifecycle of Reactive Effects](https://react.dev/learn/lifecycle-of-reactive-effects)
- [React: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [MDN: Object.is](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is)
