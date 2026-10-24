---
id: rs-object-updates
title: Update objects without mutation
level: basic
minutes: 4
summary: Copy changed object paths and preserve previous state snapshots.
---

Objects stored in state are ordinary JavaScript objects, but React code should treat them as **immutable**: never edit an existing state object. Instead, create a replacement and pass it to the setter. A **mutation** changes an existing object in place, potentially affecting every variable that refers to it.

React can skip an update if the next value is the same according to `Object.is`. More fundamentally, mutation damages the old snapshot that earlier handlers or other components might still use. A new outer object is not sufficient if you have already changed one of its shared nested objects.

## Copy the changed path

Object **spread syntax**, written `...previous`, copies an object's own enumerable properties into a new object. Later properties override earlier ones. It is a **shallow copy**: nested objects remain shared references unless you copy them too.

This component-body excerpt assumes `useState` is imported. `renameCity` is an event handler that would be passed to a button's `onClick` prop.

```js
const [profile, setProfile] = useState({
  name: 'Mina',
  address: { city: 'Leeds', postcode: 'A1' }
});
function renameCity() {
  setProfile(previous => ({
    ...previous,
    address: {
      ...previous.address,
      city: 'York'
    }
  }));
}
```

The parentheses after the arrow make the object literal the function's return value. Without them, braces would begin a function body instead.

Trace the update: the callback receives the pending profile; the outer spread preserves `name`; the nested spread preserves `postcode`; the final `city` property overrides Leeds with York. Both the profile and address become new objects. The earlier profile still contains Leeds.

## Copying is selective

You do not need to copy every value in your application. Copy each object along the path from the changed field back to the state root. Unchanged branches may keep their existing references because nothing writes into them.

This deliberately wrong excerpt shows why an outer copy alone cannot repair a mutation. Assume `profile` and `setProfile` exist:

```js
// Intentional counterexample: mutation.
profile.address.city = 'York';
setProfile({ ...profile });
```

The first line already edits the address used by the old profile. The second line changes only the outer object. A new outer reference may trigger rendering, but it does not restore the old data. Avoid the mutation rather than trying to force a render afterwards.

> [!analogy] Real-world analogy: Editing a folder of documents
> To change an address while preserving an old application, make a new address page and a new folder pointing to it. Reuse unchanged pages.
>
> **How it maps:** The folder is the outer object; the address page is a nested object. Copying only the folder still points at the same old page.
>
> **Where it stops:** JavaScript objects are references, not physical paper. A shallow copy intentionally shares unchanged values; it does not recursively duplicate everything.

## Key takeaways
- Replace state objects instead of editing them in place.
- Spread copies one level; copy nested objects on the changed path.
- Put overrides after spreads and preserve fields you did not change.

## Further reading
- [Updating objects in state](https://react.dev/learn/updating-objects-in-state)
- [Spread syntax — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)
