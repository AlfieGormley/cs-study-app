---
id: rel-th-reference-design
title: References, evolving models and keys
level: advanced
minutes: 2
sourceLesson: rel-th-er-modelling
summary: Polymorphic references, EAV, surrogate versus natural keys and changing a relationship after launch.
---

## The polymorphic-association trap

Frameworks such as Rails make this easy:

```
comment(id, body,
        commentable_type,  -- 'Photo'
        commentable_id)    -- 42
```

One column points at different tables depending on another column. A single ordinary foreign key cannot choose its referenced table from the type value. Without other integrity checks, orphaned references can accumulate, and queries must account for the type. Two relational alternatives:

1. **Exclusive arc**: one nullable foreign key per target, and a check that exactly one is set.

```sql
photo_id INT REFERENCES photo,
video_id INT REFERENCES video,
CHECK (num_nonnulls(photo_id,
                    video_id) = 1)
```

2. **A common supertype**: make `Photo` and `Video` subtypes of a `Commentable` entity (class-table inheritance) and reference its key.

The related **entity–attribute–value** (EAV) pattern, a table of `(entity_id, attribute_name, value)` rows, makes per-attribute types and constraints harder to express, and complicates ordinary queries in exchange for schema flexibility. For truly open-ended attributes, consider PostgreSQL `jsonb` together with validation and indexes. It is a trade-off, not a general proof that JSON is always better than a carefully constrained typed EAV design.

## Keys: surrogate or natural?

A **natural key** comes from the domain (ISBN, ISO country code). A **surrogate primary key** is generated (`GENERATED ALWAYS AS IDENTITY`, UUID). Natural keys can change (emails, names) or turn out not to be unique; a generated integer surrogate can give compact references when the application keeps it stable. UUID surrogates are larger, and a surrogate is not inherently immutable. The common practice is a surrogate primary key **plus** `UNIQUE` constraints on the natural keys, so the real-world rules are still enforced.

## Changing a relationship after launch

If albums may have several artists with roles, replace the single album foreign key with an album/artist junction holding `role`. Preserve uniqueness of the pair when each artist has one role per album; choose a different key if several roles per artist are permitted. Backfill existing artist references as the primary role. An online schema migration needs coordinated writers, backfill, validation and a read switch before removing the old column. The junction does not alone enforce “every album has at least one artist”; keep that minimum participation rule explicit.

## Key takeaways

- An ordinary foreign key names one target table; polymorphic target columns need another integrity strategy.
- A surrogate does not replace business uniqueness, and relationship changes need coordinated migrations.

## Further reading

- [Chen: The Entity-Relationship Model (1976)](https://openlib.org/home/krichel/courses/lis512/readings/chen76theentity-relationship.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
