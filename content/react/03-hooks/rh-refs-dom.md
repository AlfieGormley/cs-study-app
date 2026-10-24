---
id: rh-refs-dom
title: Refs and focusing an input
level: basic
minutes: 3
summary: Use a ref for a value that survives rendering without driving the displayed output.
---

State describes information used to render the screen. A **ref**, created with `useRef`, holds a mutable value that survives re-renders without scheduling a render when changed. React returns the same ref object on later renders of that component instance. Its `current` property starts with the argument passed to `useRef`.

Store a timer identifier or a DOM element in a ref. Store a displayed count, input value or selected task in state. If changing a value should change JSX, a ref alone is the wrong tool.

## Ask the DOM to focus

The **DOM** is the browser's tree of objects describing the page. A DOM element's `focus()` method moves keyboard focus to it. React supports attaching a ref to an element so a handler can perform this small browser operation.

Complete component example for a React-enabled JSX environment:

```jsx
import { useRef } from 'react';

export default function SearchFocus() {
  const inputRef = useRef(null);

  function focusSearch() {
    inputRef.current?.focus();
  }

  return (
    <>
      <label>
        Search tasks
        <input ref={inputRef} />
      </label>
      <button onClick={focusSearch}>
        Focus search
      </button>
    </>
  );
}
```

The `?.` operator is **optional chaining**. It skips the method call if `current` is null or undefined. Initially the ref contains `null`. When React commits the input to the DOM, it sets `current` to the actual element. Clicking the button reads the ref in the handler and focuses that input. When React removes the element, it clears this object ref to `null`.

The label gives the input an accessible name; focus does not replace the need for a label. Here focusing responds directly to a click, so no effect is necessary.

## An escape hatch with boundaries

Refs give controlled access outside React's normal data flow. Do not read or write `current` to calculate the displayed output during rendering. Keep those accesses in event handlers or effects. A ref mutation does not notify React; an unrelated future render might reveal a changed value, which makes display behaviour unreliable.

> [!analogy] Real-world analogy: A bookmark
> A bookmark remembers a place without rewriting the book's contents.
>
> **How it maps:** A ref remembers a value between renders, while changing it does not request a new screen.
>
> **Where it stops:** A ref can hold any JavaScript value, and a DOM ref is managed by React during commit rather than by a reader.

Use a DOM ref for focus or scrolling. Avoid manually removing React's children or changing text that React manages; React's next update assumes control of that structure. React should describe the content, while the ref handles the narrow browser operation.

## Key takeaways

- Ref changes persist but do not request a render; state changes are for displayed data.
- Read DOM refs in handlers or effects after the element exists.
- Focus is a useful escape hatch; keep React in charge of rendered content.

## Further reading

- [React: useRef](https://react.dev/reference/react/useRef)
- [React: Manipulating the DOM with refs](https://react.dev/learn/manipulating-the-dom-with-refs)
- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: HTMLElement focus](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus)
