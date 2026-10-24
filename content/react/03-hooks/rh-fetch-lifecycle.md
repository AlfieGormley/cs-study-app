---
id: rh-fetch-lifecycle
title: Fetching without stale results
level: intermediate
minutes: 5
summary: Model loading, error, empty and success states, and ignore results from obsolete requests.
---

Network responses can arrive in a different order from requests. Request list A, then list B: if B finishes first and A finishes later, blindly storing both results makes A overwrite B. This **race condition** depends on timing, so a quick test on a fast connection may miss it.

This lesson uses a deliberately small **client-only** fetch example to teach effect lifecycle. Production applications may use a framework's data facilities or a data library for caching, request sharing and other needs. This example does not provide those facilities.

## Represent the request's outcome

The Fetch API's `fetch(url)` returns a **Promise**, an object representing a result that may arrive later. In an `async` function, `await` waits for that result without blocking the browser's whole JavaScript execution. `try...catch` handles failures: a thrown error in its try block transfers control to its catch block, including a rejected Promise encountered by `await`. The `Error` constructor creates the error object used with `throw` in this example. An HTTP error such as 404 does not itself reject fetch: check `response.ok`. `response.json()` asynchronously parses the response body as JSON.

Assume a same-origin teaching endpoint whose URL arrives as a string prop. It returns an array of objects with stable unique `id` and string `text` fields. The data contract is assumed; a real application should validate untrusted data. Complete component example, with JSX transformed by the environment:

```jsx
import { useEffect, useState } from 'react';

export default function Results({ url }) {
  const [view, setView] = useState({
    url: null, status: 'loading', items: []
  });

  useEffect(() => {
    let ignore = false;
    setView({
      url, status: 'loading', items: []
    });

    async function load() {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Request failed');
        }
        const items = await response.json();
        if (!ignore) {
          setView({
            url, status: 'success', items
          });
        }
      } catch {
        if (!ignore) {
          setView({
            url, status: 'error', items: []
          });
        }
      }
    }

    load();
    return () => { ignore = true; };
  }, [url]);

  if (view.url !== url ||
      view.status === 'loading') {
    return <p role="status">Loading…</p>;
  }
  if (view.status === 'error') {
    return (
      <p role="alert">Could not load.</p>
    );
  }
  if (view.items.length === 0) {
    return <p>No tasks found.</p>;
  }
  return (
    <ul>
      {view.items.map(item => (
        <li key={item.id}>{item.text}</li>
      ))}
    </ul>
  );
}
```

The inner async function handles the asynchronous work. The effect itself returns an ordinary cleanup function, not a Promise. A single status distinguishes loading, error and success; an empty successful array gets its own message. The stored URL prevents displaying a previous URL's data during a render before the new effect has started.

## Trace overlapping requests

Each setup gets its own local `ignore` variable. Changing from A to B runs A's cleanup, setting A's flag to true, and starts B with a separate false flag. If B succeeds first, its data is stored. If A later succeeds or fails, its flag prevents either branch from changing state. Unmounting similarly marks the active request obsolete.

> [!analogy] Real-world analogy: An old takeaway order
> You replace an order and disregard a later message about the cancelled choice.
>
> **How it maps:** Cleanup marks an earlier request obsolete so its late reply cannot replace the current result.
>
> **Where it stops:** The flag does not cancel network traffic or undo server work. It only prevents applying an obsolete result.

Ignoring and cancelling are different: `AbortController` can cancel a supported fetch, but this example only ignores obsolete outcomes. Test response order explicitly, including stale errors, loading, an empty array, a current error and removal before completion.

## Key takeaways

- Fetch needs an explicit HTTP success check and separate loading, error and empty handling.
- Cleanup marks obsolete work so late responses cannot replace the active result.
- This teaching pattern is not a complete production data layer.

## Further reading

- [React: Fetching data with Effects](https://react.dev/reference/react/useEffect#fetching-data-with-effects)
- [MDN: Using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [MDN: async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
