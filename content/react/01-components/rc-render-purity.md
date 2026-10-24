---
id: rc-render-purity
title: Rendering should calculate, not change
level: intermediate
minutes: 4
summary: Separate rendering from committing and keep component calculations free of external changes.
---

Writing JSX describes a desired result. It does not mean every function call immediately changes the page. Understanding React's **render** and **commit** stages makes it easier to avoid bugs caused by code that does work at the wrong time.

## Calculate first, update the DOM later

A render is React calling components to calculate what their UI should look like. On an initial render React calls the root and the components it returns. On later updates, it calls components as needed to calculate a new result. A parent rendering can cause its children to render too.

A commit is React applying the necessary changes to the browser's DOM. On an update, React compares the new description with the previous result; rendering does not mean replacing every DOM node. The browser then paints what is visible. Do not use the number of component function calls as a count of user actions or committed updates: React may repeat or discard render work.

## Keep render calculations pure

A **pure render** returns the same UI for the same props, state and context inputs, without changing things that existed before it ran. State is a component's remembered data; the next lesson introduces it. Context is another React input mechanism covered later. A render calculation should read those inputs and return its description.

Do not change received props, modify a module-level counter, send a request or write to the DOM during render. Those changes would be **side effects**, observable work beyond producing the returned value. Repeating a render could then repeat the work even without another interaction.

Local mutation can be fine: a fresh array created during this render belongs only to this calculation. This component excerpt creates such an array, fills it and returns elements built from it. It leaves `tasks` and its records untouched.

```jsx
function TaskNames({ tasks }) {
  const names = [];
  // Only this render owns this array.
  for (const task of tasks) {
    names.push(task.title.toUpperCase());
  }
  return <p>{names.join(', ')}</p>;
}
```

Given tasks titled `Read` and `Practise`, it displays `READ, PRACTISE`. Repeating the calculation with the same input gives the same result. The local `names` array starts fresh on every call; it does not accumulate titles across renders.

By contrast, pushing into the `tasks` prop would modify data owned elsewhere. Sorting that same array in place would also modify it, even if the component only meant to change the display order. Later lessons show how to make copies for updates.

> [!analogy] Real-world analogy: A draft shopping list
> You can work out a shopping list on fresh paper without buying anything yet.
>
> **How it maps:** Rendering calculates a description; committing applies the agreed changes to the DOM. Work on a fresh local draft does not alter the shared starting information.
>
> **Where it stops:** React controls scheduling and may repeat calculations. A commit changes browser objects, not a real shopping basket, and is distinct from the browser painting pixels.

## Put actions at the right boundary

An event handler is a natural place for work caused by a user action, such as submitting a request after a button press. Some synchronisation with outside systems belongs in an Effect, taught later. Moving every calculation into an Effect is not the goal: computing a title or filtered list from current inputs belongs in render.

## Key takeaways
- Rendering calculates a description; committing updates the DOM.
- A render can happen without a distinct committed change.
- Treat props as immutable and avoid external changes during render.
- Fresh local arrays can be built during a pure calculation.

## Further reading
- [Render and commit — React](https://react.dev/learn/render-and-commit)
- [Keeping components pure — React](https://react.dev/learn/keeping-components-pure)
