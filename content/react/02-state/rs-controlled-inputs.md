---
id: rs-controlled-inputs
title: Control inputs with state
level: basic
minutes: 4
summary: Connect labelled text and checkbox inputs to state and handle submission.
---

A **controlled input** displays a value supplied by React state. User edits call an event handler, which immediately updates that state. React then renders the accepted value. For text, connect `value` to a string and read `event.target.value`. For a checkbox, connect `checked` to a boolean and read `event.target.checked`.

An **uncontrolled input** instead keeps its current value in the browser; `defaultValue` or `defaultChecked` supplies only its initial value. Both approaches have uses. This lesson uses controlled inputs so the application can calculate what to display from state.

## A small complete component

This component function assumes `useState` is imported and JSX is transformed. The parent supplies an `onSave` callback; it receives a plain object. Wrapping each input in a visible `label` associates the control with its name.

```jsx
function TaskForm({ onSave }) {
  const [title, setTitle] = useState('');
  const [done, setDone] = useState(false);
  function handleSubmit(event) {
    event.preventDefault();
    onSave({ title, done });
  }
  return (
    <form onSubmit={handleSubmit}>
      <label>
        Task
        <input value={title}
          onChange={event =>
            setTitle(event.target.value)} />
      </label>
      <label>
        <input type="checkbox"
          checked={done}
          onChange={event =>
            setDone(event.target.checked)}
        />
        Complete
      </label>
      <button type="submit">
        Save
      </button>
    </form>
  );
}
```

Typing “Read” updates `title` through the text change handler. Clicking Complete updates `done` through the checkbox handler. Submitting then passes `{ title: 'Read', done: true }` to `onSave`. This example saves through a callback; it does not make a network request or guarantee persistence after a reload.

## Submission and input pitfalls

The form's `onSubmit` handles submission, including keyboard submission where supported by the browser. `preventDefault` stops the form's normal navigation; it does not automatically stop event propagation. A submit button is explicit here. Give any other button inside the form `type="button"` if it should perform a local action without submitting.

A controlled text input needs a string throughout its lifetime. Initialise it to an empty string instead of `undefined` or `null`; otherwise it can switch between uncontrolled and controlled behaviour. Its change handler must synchronously update the state used by `value`. Passing a fixed `value` without such an update makes the field effectively read-only. A checkbox uses `checked`, not its `value` string, for the selected state.

For a separate label, JSX uses `htmlFor` to match an input's unique `id`. A placeholder is not a replacement for a visible label. The association helps users understand and activate the control.

## Key takeaways
- Control text with value/string and checkboxes with checked/boolean.
- Update the controlling state immediately in onChange.
- Use visible labels and handle form submission deliberately.

## Further reading
- [Input reference](https://react.dev/reference/react-dom/components/input)
- [preventDefault — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault)
