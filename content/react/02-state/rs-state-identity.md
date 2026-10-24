---
id: rs-state-identity
title: Understand when state survives
level: intermediate
minutes: 4
summary: Use position, component type and keys to preserve or reset local state deliberately.
---

React associates state with a component's identity in the rendered tree. Rendering a fresh JSX expression does not necessarily create fresh state. When the same component type stays in the same position with the same key, React normally preserves its state through updates.

A **remount** replaces a component instance with a new one and starts its local state again. Removing a component, changing its type at that place, or changing its key can discard the old state. Consider the resulting tree, not the location of the JSX text in a file.

## A draft for a recipient

These component functions assume `useState` is imported. The parent supplies `recipientId` and `recipientName` as props. This example keeps a local draft while the same recipient remains selected; it does not implement a submit action or contact a recipient.

```jsx
function Draft({ name }) {
  const [text, setText] = useState('');
  return (
    <label>
      Message to {name}
      <input value={text}
        onChange={event =>
          setText(event.target.value)} />
    </label>
  );
}
function Chat({
  recipientId, recipientName
}) {
  return (
    <Draft key={recipientId}
      name={recipientName} />
  );
}
```

Type a draft for recipient 7. Updating only the name of recipient 7 leaves the key and component type unchanged, so the draft survives. Switching to recipient 8 changes the key: React removes the old Draft and creates a fresh one with an empty string. Switching back to 7 creates another fresh Draft; a key does not cache removed state.

Without a key that changes, changing the `name` prop alone would keep the existing draft at this position. That can be useful for cosmetic prop changes and dangerous when the draft belongs to a different person. Decide whether preserving or resetting matches the interaction.

## Stable keys and stable definitions

Keys distinguish siblings within their parent, not components throughout the whole application. A task's stable ID is usually suitable. An array index can attach a row's local state to the wrong task after insertion or reordering. A random key generated on every render forces replacement repeatedly, losing input state rather than fixing identity.

Define component functions at the top level of their module. Defining a child component inside a parent's function creates a different function object on every parent render. React sees a different component type and can reset the child's state unexpectedly. Move the child definition outside and pass needed data as props.

> [!analogy] Real-world analogy: A labelled cubby
> Belongings for a child stay in the same labelled cubby. Reassigning that cubby to a different child means clearing it before use.
>
> **How it maps:** The location and label help model component identity; changing a key requests a fresh state holder in that parent.
>
> **Where it stops:** Keys are local to siblings and do not store discarded state somewhere else. Returning to an old key does not retrieve an archived draft.

## Key takeaways
- State follows identity in the tree, using position, type and key.
- Change a key deliberately when a new entity needs fresh local state.
- Stable IDs and top-level component definitions prevent accidental resets.

## Further reading
- [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)
- [Rendering lists](https://react.dev/learn/rendering-lists)
