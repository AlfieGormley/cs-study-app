---
id: rs-state-shape
title: Store the minimum useful state
level: intermediate
minutes: 4
summary: Derive display values and represent statuses that cannot be active together directly.
---

State should store information that must be remembered between renders. If a value can be calculated from current props and state, usually calculate it during render instead. **Derived state** such as a filtered list or full name does not need a separate setter merely because it appears on screen.

Every duplicated value creates another update that you might forget. A search box with `query`, `tasks` and a separately stored `visibleTasks` can become inconsistent when tasks change but the filtered copy does not.

## Derive a filtered result

This component-body excerpt assumes `useState` is imported and `tasks` is an array prop containing objects with string `title` fields. The query starts empty. `toLowerCase` returns lower-case text. The string method `String.prototype.includes`, used as `title.includes(needle)` below, tests whether the title string contains the search text. The callback has a block body, so its result needs an explicit `return`.

```js
const [query, setQuery] = useState('');
const needle = query.toLowerCase();
const visibleTasks = tasks.filter(task => {
  const title = task.title.toLowerCase();
  return title.includes(needle);
});
const visibleCount = visibleTasks.length;
```

With “Read React” and “Buy tea”, the query “READ” produces just “Read React”, and the count is 1. If the parent later removes that task, the next render recalculates an empty result. There is no second stored list to repair. The original task array is unchanged.

The calculation belongs in render because it only reads inputs and produces a result. It does not contact a server, change the DOM directly, or request state updates. For a small list, start with this simple calculation; performance tools and optional caching belong later.

## Avoid impossible combinations

A submit workflow can be idle, submitting, successful or failed. Four booleans allow contradictory combinations, such as successful and failed simultaneously. One status string restricts the current mode to one chosen value. This component-body excerpt defines the initial status:

```js
const [status, setStatus] = useState(
  'idle'
);
const isBusy = status === 'submitting';
```

Use `setStatus('submitting')` when starting an operation and an appropriate terminal status when it finishes. This does not start or finish a submission by itself; it supplies a representation that is easier to reason about. An error message can still be stored separately if the application needs to remember its content.

When selecting one task, prefer storing its ID over a duplicate task object. Find the current object from the task array during render. If the ID is absent after deletion, handle that case explicitly, for example by showing no selection. This avoids a selected copy silently keeping an old title while the main list has a new one.

> [!analogy] Real-world analogy: One bill, calculated totals
> A receipt stores its line items and calculates the total from them. Keeping a second editable total invites disagreement after an item changes.
>
> **How it maps:** Tasks and query are the inputs; the filtered result and count are calculations from those inputs.
>
> **Where it stops:** Some values really are independent records, such as a historical price agreed earlier. Only derive values whose meaning is determined by current inputs.

## Key takeaways
- Derive display values from current inputs during render.
- Represent modes that cannot be active together with one status value.
- Store an identity rather than a duplicate object when selecting existing data.

## Further reading
- [Choosing state structure](https://react.dev/learn/choosing-the-state-structure)
- [Reacting to input with state](https://react.dev/learn/reacting-to-input-with-state)
