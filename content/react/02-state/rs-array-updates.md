---
id: rs-array-updates
title: Update arrays and their items
level: basic
minutes: 4
summary: Use spread, filter and map to change lists without editing old state.
---

A task list is often an array of objects. There are two separate things to protect: the array and the objects stored inside it. Creating a new array does not automatically create new item objects.

Use stable item IDs to describe which task changed. An ID identifies the task even if the array is filtered or reordered. The array index only describes its current position.

## Add, remove and replace

Array spread, written `[...previous]`, places the previous elements into a new array. `filter` returns an array containing the elements that pass its test. `map` returns an array containing one callback result per original element. These operations can preserve the original array when your callbacks do not mutate its items.

This component-body excerpt assumes `useState` is imported. Its functions handle task changes within the component. A UI event handler would call `addTask` with a newly created task whose ID is unique in the list. The ternary operator chooses the expression after `?` when its condition is true, otherwise the expression after `:`.

```js
const [tasks, setTasks] = useState([]);
function addTask(task) {
  setTasks(previous => [...previous, task]);
}
function removeTask(id) {
  setTasks(previous => previous.filter(
    task => task.id !== id
  ));
}
function finishTask(id) {
  setTasks(previous => previous.map(task =>
    task.id === id
      ? { ...task, done: true }
      : task
  ));
}
```

Suppose the list contains task 7, “Read”, and task 8, “Practise”, both unfinished. Finishing 7 makes a new array and a new object for task 7. Task 8 keeps its existing object because it did not change. Removing 7 then keeps only task 8. The previous arrays and the original object for task 7 remain unchanged.

## The shallow-copy trap

This intentionally wrong excerpt assumes `tasks` is non-empty and `setTasks` exists:

```js
// Intentional counterexample: mutation.
const next = [...tasks];
next[0].done = true;
setTasks(next);
```

The array is new, but its first element still refers to the old task object. The assignment mutates that shared object. Copy the changed item with object spread instead, as `finishTask` does.

Methods such as `push`, `splice`, `sort` and `reverse` mutate the array on which they are called. If you need sorting, first copy the array, then sort that copy. Sorting a fresh array is safe provided the comparison function itself does not mutate shared items. For small study projects, a clear immutable update is usually the most valuable first goal.

> [!analogy] Real-world analogy: A guest list of contact cards
> A new guest list can refer to the same contact cards. Editing a shared card still changes what the old list sees.
>
> **How it maps:** The list is an array and each contact card is an item object. Updating one item requires a new array plus a replacement for that card.
>
> **Where it stops:** Arrays contain references rather than actual cards. Reusing unchanged item objects is intentional and safe when they remain read-only.

## Key takeaways
- Add with spread, remove with filter and replace with map.
- Copy changed item objects as well as the containing array.
- Treat mutating array methods carefully; operate on a fresh copy.

## Further reading
- [Updating arrays in state](https://react.dev/learn/updating-arrays-in-state)
- [Updating objects in state](https://react.dev/learn/updating-objects-in-state)
