---
id: sea-layer-feature-boundaries
sourceLesson: sea-layered
title: Feature packages and enforced layer rules
level: basic
minutes: 3
summary: Keep a feature’s layers together and check the intended dependency direction with Import Linter.
---

A feature often changes presentation, application, domain and storage together. Package layout can keep these related edits close while an automated rule protects their dependencies.

### Changes cut across every layer

Most feature work is *vertical*: "add a gift message to orders" touches the view, the service, the domain and the table. If the code is packaged by layer, one feature means edits in four distant folders.

```
 by layer            by feature
 views/              orders/
   orders.py           views.py
   users.py            services.py
 services/             model.py
   orders.py           repo.py
   users.py          users/
 repos/                views.py
   orders.py           ...
   users.py
```

**Package by feature** (sometimes called vertical slices) keeps the layers *inside* each feature folder. You still get the dependency rule, but related code sits together, which is high cohesion. The modularity units return to module boundaries and public interfaces.

> [!tip] Rule of thumb
> Layers are about dependency direction, not folder names. You can have one file with clearly separated functions that respect the rule, or ten folders that violate it. Check the imports, not the tree.

## Enforcing the rule

Conventions decay unless something checks them. In Python, `import-linter` can fail the build when a lower layer imports a higher one:

```ini
[importlinter]
root_package = shop

[importlinter:contract:layers]
name = Layered architecture
type = layers
layers =
    shop.presentation
    shop.application
    shop.data
    shop.domain
```

The `layers` contract lists layers top to bottom and forbids any import from a lower layer to a higher one. Higher layers importing lower ones is allowed, whether or not they skip a level. Notice that `domain` is listed *last* here, below `data`, so the repository may import `Order` but `Order` may never import SQL code. Many Python teams end up with this order, which is already the hexagonal idea in disguise.

## Key takeaways
- Package by feature keeps related vertical changes near each other.
- Layering is about actual dependencies rather than directory names.
- Import Linter lists layers from highest to lowest; its default layers contract permits downward skips.
- Putting domain below data in the contract permits repositories to import domain objects.

## Further reading
- [Import Linter: contract types](https://import-linter.readthedocs.io/en/stable/contract_types/)
- [Presentation Domain Data Layering — Martin Fowler](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
