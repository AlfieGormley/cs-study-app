---
id: rel-th-er-cardinality
title: Entities, cardinality and participation
level: advanced
minutes: 4
sourceLesson: rel-th-er-modelling
summary: ER modelling basics: entities, attributes, cardinality versus participation, and mapping each to tables.
---

Normalisation tells you whether a set of tables is well formed. It does not tell you which tables to start with. That comes from **conceptual modelling**: working out, with the people who know the domain, what things exist, how they relate, and which rules always hold.

The standard tool is the **entity–relationship (ER) model**, introduced by Peter Chen in 1976. An ER diagram is small enough to discuss with a product manager and precise enough to turn mechanically into tables. An ER model makes identifiers and relationship rules visible. Mapping it still requires FD and decomposition checks: attributes may depend on non-identifiers, and a diagram alone is not a proof of BCNF.

## The building blocks

- An **entity type** is a kind of thing with its own identity: `Artist`, `Album`, `User`. Each instance is an **entity**.
- An **ER attribute** describes an entity. Its design can distinguish:
  - **Simple ER attributes**, such as `title`, from **composite attributes**, such as an address split into street, city and postcode.
  - **Single-valued attributes**, such as a title, from **multivalued attributes**, such as an artist’s genres.
  - **Stored attributes**, such as `birth_date`, from **derived attributes**, such as current age computed from birth date and today’s date.
- A **key attribute** (entity identifier) distinguishes instances, just as a candidate key does.
- A **relationship type** connects entity types: a `User` *creates* a `Playlist`.

### Relationship cardinality and participation

Each end of a relationship has two constraints:

- **Relationship cardinality** (maximum): can one entity relate to *one* or *many* on the other side? Written 1:1 (one-to-one), 1:N (one-to-many) or M:N (many-to-many), where N and M just stand for "many".
- **Participation** (minimum): must every entity take part (**total**, minimum 1), or may it not (**partial**, minimum 0)?

The colon in 1:N is not division: it separates the maximum at each end. And these labels say nothing about minimums: "1:N" alone does not tell you whether an album may have zero tracks.

Crow's foot notation, the most common in industry tools, draws both at each end of the line:

```
||   exactly one
o|   zero or one
|<   one or many
o<   zero or many
```

A music service:

```
Artist ||----o< Album ||----|< Track
User   ||----o< Playlist
Playlist >o----o< Track
```

Read the first line left to right: an artist has zero or more albums; each album belongs to exactly one artist. Each album has one or more tracks. Playlists and tracks are many-to-many: a playlist holds many tracks, and a track appears on many playlists.

> [!tip] Ask for counterexamples
> To pin down relationship cardinality, ask domain experts concrete questions: "Can an album ever have two artists?" (Yes: collaborations. Then Artist–Album is M:N, not 1:N.) "Can a track exist on no album?" (Singles?) Each answer changes the schema, and changing it after launch is expensive.

## Mapping an ER model to tables

These rules turn a diagram into a schema.

**Strong entity.** Create a table. Its entity identifier becomes the primary key; simple ER attributes become columns; composite attributes are flattened (`street`, `city`, `postcode`).

**One-to-many relationship.** Put its foreign key on the many side. If participation is total, the column is `NOT NULL`.

```sql
CREATE TABLE album (
  album_id  INT PRIMARY KEY,
  artist_id INT NOT NULL
    REFERENCES artist,
  title     TEXT NOT NULL
);
```

**Many-to-many relationship.** Create an associative table (junction table). Its key combines both foreign keys, and any attributes of the relationship itself live here.

**One-to-one relationship.** Use a foreign key with `UNIQUE`, placed on the side with total participation (so it can be `NOT NULL`). If both sides are total and always created together, consider merging them into one table.

**Multivalued attribute.** Create its own table, keyed by owner plus value: artist_genre with artist_id and genre columns. This is 1NF in action.

**Derived attribute.** Usually compute it instead of storing it. Compute it in queries or views, or as a PostgreSQL generated column if it uses an allowed immutable expression over the same row. Age derived from the current date is not immutable.

A foreign key on an album ensures its referenced artist exists; `NOT NULL` ensures that album has an artist. It does not ensure that each artist has an album. Likewise, declaring a track’s album foreign key cannot enforce the diagram’s “at least one track per album” condition. Parent-side minimum participation needs an additional transaction protocol or carefully designed deferred constraint triggers. PostgreSQL nullable `UNIQUE` allows several NULLs by default; for a mandatory one-to-one reference use both `NOT NULL` and `UNIQUE`, or a shared primary key.

## Key takeaways

- Cardinality describes maximum participation; minimum participation is a separate rule.
- Foreign keys, NOT NULL and UNIQUE enforce different parts of a relationship.

## Further reading

- [Chen: The Entity-Relationship Model (1976)](https://openlib.org/home/krichel/courses/lis512/readings/chen76theentity-relationship.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
