---
id: para-desired-state
title: Declarative UI and desired state
level: basic
minutes: 3
sourceLesson: para-imperative-declarative
summary: Kubernetes reconciles continuously; Terraform normally acts during explicit runs.
---

A declarative description can specify a screen or infrastructure as well as a query result. The key question is when and how the system brings the observed state into line with that description.

## Declarative UI and desired state

Two of the most influential modern systems are declarative at heart.

**React** describes a user interface as a function of state. Instead of "find the button, change its text, hide the spinner" (the jQuery style), you write what the UI should look like *for a given state*:

```javascript
// Render the branch for current items.
function Cart({ items }) {
  return items.length === 0
    ? <p>Your cart is empty</p>
    : <p>{items.length} items</p>;
}
```

React compares the new description with the previous one and computes DOM updates needed by its reconciliation model. Components normally describe output rather than mutate React-managed DOM directly, although refs provide imperative escape hatches.

**Kubernetes** continuously reconciles declared desired state, such as three Pod replicas, against observed state. When replicas disappear its controllers attempt to restore them, subject to capacity and scheduling constraints. **Terraform** also declares desired infrastructure, but normally refreshes and reconciles during explicit plan/apply runs; it is not a continuously running self-healing controller. Imperative scripts can also run repeatedly and inspect state if programmed to do so.

> [!tip] Declarative surface, imperative engine
> Declarative systems are almost always built on imperative code. The SQL planner, React's reconciler and Kubernetes controllers are imperative programs. The paradigm describes the layer you work with, not what happens all the way down.

A useful goal of desired-state operations is **idempotence** under stable inputs and provider behavior: applying the same declaration twice gives the same result as applying it once. Written as a formula, an operation is idempotent when:

```formula
f(f(s)) = f(s)
where
f: an operation applied to a system, such as "ensure 3 replicas exist"
s: the state of the system before the operation, such as how many replicas are running
f(s): the state after applying the operation once
f(f(s)): the state after applying it a second time, straight after the first
In words: an operation is idempotent when doing it again changes nothing more than doing it once did.
```

Running "ensure 3 replicas" ten times still leaves 3 replicas: from 0 running, the first run gives 3 and every later run finds 3 and does nothing. Running "start 3 containers" ten times leaves 30, because each run adds 3 more (0, then 3, then 6, ...), so applying it twice does not give the same state as applying it once. The idea only holds while nothing else changes the system between runs.

## Key takeaways
- Kubernetes reconciles continuously; Terraform normally acts during explicit runs.
- Idempotence is a property of the operation under stable assumptions.

## Further reading
- [React: describing the UI](https://react.dev/learn/describing-the-ui)
- [Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Terraform state](https://developer.hashicorp.com/terraform/language/state)
