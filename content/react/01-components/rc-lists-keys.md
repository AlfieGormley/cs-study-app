---
id: rc-lists-keys
title: Lists and stable keys
level: intermediate
minutes: 5
summary: Transform arrays into elements and choose keys that keep each item associated with its identity.
---

A task list should come from task data rather than repeated handwritten tags. JavaScript array methods choose which records to show and transform them into JSX. React also needs a reliable way to match items between renders when a list changes.

## Filter records, then map them

Array **filter** returns a new array containing items whose callback returned a truthy value. Array **map** returns a new array containing each callback's result. Neither method inherently changes the source array, although a callback can still incorrectly mutate the objects it receives.

This component excerpt receives a `tasks` array. Each record has a stable string `id`, a `title` and a boolean `done`. The arrow callback with parentheses implicitly returns its JSX.

```jsx
function OpenTasks({ tasks }) {
  const open = tasks.filter(
    task => !task.done
  );

  return (
    <ul>
      {open.map(task => (
        <li key={task.id}>
          {task.title}
        </li>
      ))}
    </ul>
  );
}
```

Suppose the records are `a: Read` (open), `b: Rest` (done) and `c: Practise` (open). Filtering keeps records `a` and `c`. Mapping returns two list elements, displaying `Read` and `Practise`. The original array still contains all three records.

## Give each sibling a stable React key

A **React key** is an identity hint for an element in a collection of siblings. It helps React match a record's previous UI to its next UI when items are inserted, removed or reordered. Put the key on the element returned directly from `map`; a key buried inside a child component is too far down.

Keys must be unique among siblings and stable for the same item across renders. They need not be globally unique across separate lists. Use an identifier from the data. Create an identifier when creating a new record, rather than generating a random key during rendering. Random keys change on each render and can cause React to recreate items, losing user input or component state.

The array **index** is an item's current position, not its identity. Imagine rows A and B each have a text input. Someone edits A's input, then inserts C before A. With index keys, the first position still has key zero but now represents C; input or component state can become associated with the wrong record. Stable record ids let React follow A as it moves. Index keys can be acceptable for a truly fixed list, but become risky when insertion, deletion or reordering is possible.

> [!analogy] Real-world analogy: A cloakroom ticket
> A ticket follows one person's coat even if staff rearrange the pegs.
>
> **How it maps:** A stable key identifies the same list item when its position among siblings changes; a peg position alone is like an array index.
>
> **Where it stops:** Keys only identify items within a particular sibling list. They do not globally locate components or preserve state after an item is removed.

`key` is special React information, not a normal prop delivered to the child. If a `TaskRow` needs its record id, pass it separately, for example as an `id` prop as well as the key. Reusing the same data value for those two purposes is fine.

## Key takeaways
- `filter` selects records; `map` transforms them into elements.
- Put a stable key on the element returned directly by `map`.
- Use data identity rather than changing positions or random values.
- Pass an id separately if the child needs it; it cannot read `key` as an ordinary prop.

## Further reading
- [Rendering lists — React](https://react.dev/learn/rendering-lists)
- [Array map — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map)
