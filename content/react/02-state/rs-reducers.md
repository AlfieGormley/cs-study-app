---
id: rs-reducers
title: Describe state transitions with reducers
level: intermediate
minutes: 4
summary: Move related update rules into a pure reducer and trace dispatched actions.
---

Several handlers may update the same related state. A **reducer** gathers those update rules in one pure function. It receives the current state and a **reducer action**, then returns the next state. An action describes what happened; by convention it is an object with a `type` string plus any data needed for that event.

`useReducer` is an alternative to `useState`, not a global store. Each mounted component instance has its own reducer state, preserved across its renders. It is useful when several events must follow consistent rules, while a simple text field may remain clearer with `useState`.

## A pure reducer

This complete JavaScript function needs no React import. The object spread preserves other fields while replacing `count`. The **switch statement** selects a branch from `action.type`; the **throw statement** reports an unexpected action instead of silently losing the state.

```js
function counterReducer(state, action) {
  switch (action.type) {
    case 'added':
      return {
        ...state,
        count: state.count + action.amount
      };
    case 'reset':
      return { ...state, count: 0 };
    default:
      throw Error('Unknown action');
  }
}
```

The reducer must not mutate its inputs, send network requests or produce random identifiers. It calculates the next value from the given state and action. If an event needs an ID or the current time, create that event information in the handler and put it in the action. Then repeated reducer evaluation produces the same result.

## Connect an event to the reducer

This component function assumes `useReducer` is imported from React and the reducer above is in scope. Call `useReducer` at the top level of the component. **Dispatch** is the function React returns for requesting a transition.

```jsx
function Counter() {
  const [state, dispatch] = useReducer(
    counterReducer, { count: 0 }
  );
  return (
    <>
      <p>{state.count}</p>
      <button onClick={() => dispatch({
        type: 'added', amount: 2
      })}>Add two</button>
      <button onClick={() => dispatch({
        type: 'reset'
      })}>Reset</button>
    </>
  );
}
```

Clicking Add two dispatches `{ type: 'added', amount: 2 }`. React passes that action and current state to the reducer. Starting at 0, two separate Add two clicks produce 2, then 4. Reset produces 0. The component displays each resulting state; the handler does not assign to `state.count` directly.

Dispatch requests a future update, so code after `dispatch` still reads its render's existing snapshot. In development Strict Mode, React may call a reducer twice to expose impurities and ignore one result. Keep reducers pure and test state transitions rather than assuming an exact call count.

> [!analogy] Real-world analogy: A scorekeeper with event cards
> A scorekeeper follows written rules for “add two” and “reset” cards. The same score and card always produce the same next score.
>
> **How it maps:** The current score is state, a card is an action, and the rulebook is the reducer. Dispatch submits an event for React to process.
>
> **Where it stops:** The reducer itself must only calculate. It does not physically update a display, send messages or create event information.

## Key takeaways
- Reducers centralise related update rules as pure transitions.
- Actions describe events; dispatch asks React to apply one.
- Return new state, preserve required fields and keep external work in handlers.

## Further reading
- [Extracting state logic into a reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer)
- [useReducer reference](https://react.dev/reference/react/useReducer)
