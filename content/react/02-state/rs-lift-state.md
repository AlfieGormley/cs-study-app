---
id: rs-lift-state
title: Give shared state one owner
level: basic
minutes: 4
summary: Coordinate sibling controls through a common parent and callback props.
---

Two components may need to display and update the same information. Giving each a separate `useState` variable creates two independent copies, not shared state. If they must agree, choose a single owner and pass the value down through props.

**Lifting state up** moves state to the closest common parent of the components that need it. The parent owns the value; children receive it plus a **callback prop** to request changes. Data travels down, and events travel up through function calls. A child does not edit its props or reach into a sibling.

## Two editors, one value

The following component functions assume `useState` is imported. `Editor` has no local state for this value. Its `label` prop supplies a visible name and its `onChange` prop accepts the next string, not the browser event.

```jsx
function Editor({
  label, value, onChange
}) {
  return (
    <label>
      {label}
      <input value={value}
        onChange={event =>
          onChange(event.target.value)} />
    </label>
  );
}
function SharedEditors() {
  const [text, setText] = useState('');
  return (
    <>
      <Editor label="First" value={text}
        onChange={setText} />
      <Editor label="Second" value={text}
        onChange={setText} />
      <p>{text}</p>
    </>
  );
}
```

Type “Hello” into First. Its handler calls `setText('Hello')` through the prop. The parent receives the update and renders again. Both editors now receive “Hello”, and the paragraph displays it too. Editing Second follows exactly the same route. No extra synchronisation step is necessary because only one string is stored.

## Controlled is a design relationship

An application component is often described as a **controlled component** when its important behaviour is determined by props. Here the parent controls the editors' text. A component can still have unrelated local state, such as whether a help message is open. Controlled and uncontrolled are useful design descriptions, not strict categories imposed on every custom component.

Lift only as high as necessary. If no other component needs a temporary draft, keeping it local makes the relationship easier to understand. Moving every variable to the top of the application makes distant components responsible for details they do not use.

Do not automatically initialise a child's state from a prop and expect it to follow later changes. `useState(initialValue)` uses that initial value when the component first mounts; subsequent prop updates do not overwrite the stored state. Keep the value controlled, or deliberately design an independent draft and its reset behaviour.

> [!analogy] Real-world analogy: Two displays, one thermostat
> Two wall displays show one thermostat setting. Each sends adjustment requests to the same controller.
>
> **How it maps:** The parent is the owner of the setting; props show the current value and callback props request updates from either child.
>
> **Where it stops:** React does not require physical messages or a central owner for all data. Independent settings can stay in independent components.

## Key takeaways
- Shared values need one owner at the nearest useful common parent.
- Pass current data down and change-request callbacks to children.
- Keep independent data local; do not mirror props into state by default.

## Further reading
- [Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Choosing state structure](https://react.dev/learn/choosing-the-state-structure)
