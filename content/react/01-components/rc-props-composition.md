---
id: rc-props-composition
title: Props and reusable composition
level: basic
minutes: 4
summary: Pass read-only inputs and nested children into a reusable card component.
---

A reusable component should describe the same kind of UI with different content. **Props**, short for properties, are the inputs that a parent passes to a child component. A prop can hold a string, number, boolean, object, array, function or JSX value. Props are not limited to HTML attributes.

## Read inputs without changing them

A component receives one props object. Destructuring its parameter gives local names to chosen properties. Props are **read-only**: treat both the props object and values passed through it as immutable inputs. Do not assign a different title or change an array received from a parent while rendering.

Read-only is a programming rule, not a claim that every JavaScript object is deeply frozen. A parent can later render the child with different props. When that happens, the child describes the UI using those new inputs. If the child needs an interaction to request a change, the parent can pass a callback; later lessons develop that pattern.

## Let the caller supply the inside

**children** is the prop containing JSX nested between a component's opening and closing tags. A wrapper can place those children inside its own layout without knowing their detailed content. This is composition: the caller decides the content and the wrapper decides the surrounding structure.

This complete component file renders two cards. `title = 'Untitled'` is a JavaScript default parameter inside destructuring. That default is used when the prop is missing or `undefined`, but not when it is `null` or an empty string.

```jsx
function Card({
  title = 'Untitled',
  children
}) {
  return (
    <section className="card">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export default function App() {
  return (
    <main>
      <Card title="Today">
        <p>Read one lesson.</p>
      </Card>
      <Card>
        <button>Choose a topic</button>
      </Card>
    </main>
  );
}
```

The first card shows `Today` and a paragraph. The second shows `Untitled` and a button. `Card` does not need separate branches for paragraphs and buttons: it simply includes its `children` where the content belongs. The button is presentational here; a later lesson gives it an event handler.

The parent uses an explicit title prop and nested JSX for different jobs. `title` supplies one named value; `children` supplies the flexible content region. Neither changes who owns the data: the parent chooses what it passes, while the child reads it.

> [!analogy] Real-world analogy: A picture frame
> One frame design can surround different pictures and carry different captions.
>
> **How it maps:** The wrapper component supplies the frame, a named prop supplies the caption and `children` supplies the picture placed inside.
>
> **Where it stops:** Children are React values describing content, not objects physically inserted into a frame. The parent can provide new values on another render.

Prefer clear named props over passing a large object that the component does not need. If a card only needs a title, receiving that title directly makes its contract easier to see. Composition helps avoid a single component accumulating a different boolean prop for every possible layout.

## Key takeaways
- Props flow from parent to child as read-only inputs.
- Nested JSX arrives through the `children` prop.
- Defaults apply to missing or `undefined` props, not `null`.
- Compose a reusable wrapper with caller-supplied content.

## Further reading
- [Passing props to a component — React](https://react.dev/learn/passing-props-to-a-component)
