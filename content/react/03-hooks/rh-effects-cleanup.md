---
id: rh-effects-cleanup
title: Effects start and stop synchronisation
level: intermediate
minutes: 4
summary: Connect to external systems after commit and undo the connection with cleanup.
---

An **effect**, declared with `useEffect`, synchronises a component with something outside React: a browser event subscription, a connection or a non-React widget. Rendering calculates JSX; an effect performs external work after React commits a render. Effects run in the browser, not during server rendering.

Do not use an effect merely because state changed. Calculating a filtered list belongs in rendering. A purchase triggered by a particular click belongs in that event handler. An event subscription that must exist while a component is present is a good effect.

## Pair setup with cleanup

This complete component reports the last key pressed while it is mounted. `window.addEventListener` registers a browser callback. `removeEventListener` unregisters that same function.

```jsx
import { useEffect, useState } from 'react';

export default function LastKey() {
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

  return <p>Last key: {key}</p>;
}
```

The **setup** function registers the callback. The returned function is **cleanup**: React calls it when stopping this synchronisation. Return the function rather than calling it immediately. Removing a different function with similar code would not remove the original listener.

The empty dependency array means the effect reads no changing props or state. `setKey` has a stable identity, so it can be omitted here. The callback gets the key from the browser event instead of closing over `key`.

Trace the behaviour: mount the component, press A, and its state shows A. Remove the component, then press B. Cleanup has removed its listener, so that removed component no longer responds. A new mount creates its own subscription.

## Reconnecting and Strict Mode

For an effect with changing dependencies, React stops the previous setup before starting the new one: cleanup uses the old render's values, then setup uses the new values. Final removal also runs cleanup. Cleanup is therefore more than an unmount notification.

> [!analogy] Real-world analogy: A library loan
> Borrow a book when you need it, return it before replacing it, and return the last book when you leave.
>
> **How it maps:** Setup acquires an external resource; cleanup releases that particular resource before replacement or removal.
>
> **Where it stops:** Some effects require no cleanup, and React schedules these steps around commits rather than human visits.

When Strict Mode is enabled at the root during development, React runs an extra setup-and-cleanup cycle for effects before the ongoing setup. This helps expose missing cleanup. It is a development check, not a production promise about how many times a component renders. Correct code leaves only the intended active subscription and cleans it up when removed. Do not hide the check with a ref that prevents a later setup.

## Key takeaways

- Effects synchronise external systems; calculations and direct event responses usually belong elsewhere.
- Cleanup undoes the matching setup before replacement and on removal.
- Development Strict Mode helps find effects that do not clean up correctly.

## Further reading

- [React: Synchronising with Effects](https://react.dev/learn/synchronizing-with-effects)
- [React: useEffect](https://react.dev/reference/react/useEffect)
- [React: StrictMode](https://react.dev/reference/react/StrictMode)
- [MDN: removeEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/removeEventListener)
