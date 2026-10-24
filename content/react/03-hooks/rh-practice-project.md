---
id: rh-practice-project
title: Build a searchable task list
level: intermediate
minutes: 5
summary: Combine minimal state, immutable updates, derived search results and stable keys in one small app.
---

Build a task list that filters by text and toggles completion. Keep one source of truth: the task array and search query. The visible rows are derived during rendering, so they do not need their own state or effect. This project has no network connection or external subscription to maintain.

Each task has an immutable, stable identifier independent of its text or filtered position. A checkbox is controlled by `done`. The parent owns the state and passes each row its task plus a callback that requests a toggle.

## A complete small app

This module exports a component for the React-enabled JSX environment used throughout the course. It needs no CSS or external service. The `includes` string method tests whether text contains the query; both are lowercased for a case-insensitive match.

```jsx
import { useState } from 'react';

const initialTasks = [
  { id: 'a', text: 'Read', done: false },
  { id: 'b', text: 'Walk', done: false },
  { id: 'c', text: 'Review', done: true }
];

function TaskRow({ task, onToggle }) {
  return (
    <li>
      <label>
        <input
          type="checkbox"
          checked={task.done}
          onChange={() => onToggle(task.id)}
        />
        {task.text}
      </label>
    </li>
  );
}

export default function TaskApp() {
  const [tasks, setTasks] =
    useState(initialTasks);
  const [query, setQuery] = useState('');
  const search = query.toLowerCase();
  const visible = tasks.filter(task =>
    task.text.toLowerCase().includes(search)
  );

  function toggle(id) {
    setTasks(items => items.map(task =>
      task.id === id
        ? { ...task, done: !task.done }
        : task
    ));
  }

  return (
    <>
      <label>
        Search tasks
        <input
          value={query}
          onChange={event =>
            setQuery(event.target.value)
          }
        />
      </label>
      {visible.length === 0 && (
        <p>No matching tasks.</p>
      )}
      <ul>
        {visible.map(task => (
          <TaskRow
            key={task.id}
            task={task}
            onToggle={toggle}
          />
        ))}
      </ul>
    </>
  );
}
```

The state setter uses an updater function so each toggle works from the current task array. `map` creates a new array and spread creates a new object for the changed task. Unchanged task objects can be reused because this code never mutates them. Filtering creates a display selection without deleting anything from state.

## Check observable behaviour

1. Initially see Read, Walk and Review; only Review is checked.
2. Type `re`: see Read and Review. Type `RE`: see the same two rows.
3. Toggle Read while filtered, then clear the query. Read is still checked and Walk is unchanged.
4. Type `zzz`: see the empty message. Clear it: all tasks return with their saved completion state.
5. Toggle a checkbox twice: its completion returns to its starting value.

These checks test user-visible behaviour rather than a particular number of renders. The stable keys describe sibling identity; state preservation here also relies on storing completion in the parent task objects. A row hidden by filtering is removed from the tree, so any additional local row state would be lost on removal unless stored elsewhere.

No custom Hook or context is necessary for a single parent and its rows. Add them only when they solve an actual sharing or synchronisation need. No memoisation is justified by the size of this example. State is held in memory: reloading or remounting this app starts again from the initial tasks; persistence is a separate feature.

As an extension, design an Add task form. Generate each id once when the task is created, reject blank text, and append immutably. Do not generate keys during rendering. That is a design exercise, not behaviour implemented above.

## Key takeaways

- Own tasks and query once, and calculate the visible list during rendering.
- Use stable ids, controlled inputs and immutable functional updates.
- Test filtering, toggling and empty results; add architecture only when a real need appears.

## Further reading

- [React: Thinking in React](https://react.dev/learn/thinking-in-react)
- [React: Updating Arrays in State](https://react.dev/learn/updating-arrays-in-state)
- [React: Preserving and Resetting State](https://react.dev/learn/preserving-and-resetting-state)
- [MDN: String includes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/includes)
