---
id: rc-components
title: Components describe the screen
level: basic
minutes: 4
summary: Read a function component and trace how nested components form a user interface.
---

React is a JavaScript library for building a **user interface**: the things a person sees and interacts with. A **component** describes one part of that interface. It might be a heading, a task row or an entire screen. Starting with small named parts makes a larger screen easier to read and reuse.

This course assumes basic JavaScript variables, functions, arrays and objects. It explains the extra syntax as it appears. Examples belong in a React-enabled project or playground whose build tool transforms JSX into JavaScript; pasting JSX directly into an ordinary browser script will not work. Project installation is outside this course.

## A function that describes UI

A function component returns a description of what should appear. **JSX** is the HTML-like syntax inside the JavaScript below. HTML is the browser's document markup language; JSX is JavaScript syntax that a tool transforms. They look similar but are not interchangeable.

This complete component file can be used as the root component in that prepared environment. `export default` makes `StudyPage` available for another file to import. The environment mounts that root component into the page.

```jsx
function Welcome() {
  return <h2>Ready to study?</h2>;
}

export default function StudyPage() {
  return (
    <main>
      <h1>My study app</h1>
      <Welcome />
      <Welcome />
    </main>
  );
}
```

`StudyPage` returns one `main` element containing a heading and two uses of `Welcome`. Each use describes an `h2` with the same text. The browser therefore displays the main heading followed by two smaller headings. Writing a function definition alone does not put it on the screen: some rendered component must use it.

`<Welcome />` tells React to use the JavaScript component named `Welcome`. `<main>` and `<h1>` refer to built-in browser elements. Names used as custom JSX tags must begin with a capital letter. Writing `<welcome />` would describe a lowercase element rather than call the `Welcome` component.

The parentheses after `return` group several lines into one returned expression. Keep the opening parenthesis on the same line as `return`; JavaScript can otherwise end the return statement before the markup.

## Compose a screen from parts

**Composition** means combining smaller components to make a larger one. A component can contain ordinary elements and other components. Keep component definitions at the top level of a file, rather than defining one inside another component's function. This gives the component a stable definition; later lessons explain why component identity matters for state.

> [!analogy] Real-world analogy: A reusable recipe
> A recipe for a sandwich can be used twice when preparing two lunches.
>
> **How it maps:** The component function is the reusable description; each JSX use asks React for another instance of that part of the interface.
>
> **Where it stops:** A component returns a UI description, not a physical object. React decides when to run it and how to update the browser.

Choose a component when a part has a clear responsibility or is reused. You do not need to make every single tag a separate component. A useful boundary lets you understand its purpose from its name and inputs.

## Key takeaways
- A function component describes a piece of UI by returning JSX.
- Capitalised JSX names refer to components; lowercase names are treated as browser element names.
- Nesting and reusing components is composition.
- Use a React-enabled environment that transforms JSX before the browser runs it.

## Further reading
- [Your first component — React](https://react.dev/learn/your-first-component)
- [Importing and exporting components — React](https://react.dev/learn/importing-and-exporting-components)
