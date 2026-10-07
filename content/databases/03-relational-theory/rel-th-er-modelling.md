---
id: rel-th-er-modelling
title: ER modelling
level: advanced
minutes: 15
summary: Entities, relationships, cardinality and participation, the rules for mapping an ER model to tables, weak entities, ternary relationships, inheritance mappings and the polymorphic-association trap.
---

Normalisation tells you whether a set of tables is well formed. It does not tell you which tables to start with. That comes from **conceptual modelling**: working out, with the people who know the domain, what things exist, how they relate, and which rules always hold.

The standard tool is the **entity–relationship (ER) model**, introduced by Peter Chen in 1976. An ER diagram is small enough to discuss with a product manager and precise enough to turn mechanically into tables. A good ER model, mapped with the rules below, usually lands in BCNF without further work, because the functional dependencies come straight from each entity's identifier.

## The building blocks

- An **entity type** is a kind of thing with its own identity: `Artist`, `Album`, `User`. Each instance is an **entity**.
- An **attribute** describes an entity. Attributes can be:
  - **simple** (`title`) or **composite** (`address` = street, city, postcode);
  - **single-valued** or **multivalued** (an artist's set of genres);
  - **stored** or **derived** (`age` from `birth_date`).
- A **key attribute** (identifier) distinguishes instances, just as a candidate key does.
- A **relationship type** connects entity types: a `User` *creates* a `Playlist`.

### Cardinality and participation

Each end of a relationship has two constraints:

- **Cardinality** (maximum): can one entity relate to *one* or *many* on the other side?
- **Participation** (minimum): must every entity take part (**total**, minimum 1), or may it not (**partial**, minimum 0)?

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
> To pin down cardinality, ask domain experts concrete questions: "Can an album ever have two artists?" (Yes: collaborations. Then Artist–Album is M:N, not 1:N.) "Can a track exist on no album?" (Singles?) Each answer changes the schema, and changing it after launch is expensive.

## Mapping an ER model to tables

These rules turn a diagram into a schema.

**1. Strong entity → table.** Its identifier becomes the primary key; simple attributes become columns; composite attributes are flattened (`street`, `city`, `postcode`).

**2. 1:N relationship → foreign key on the "many" side.** If participation is total, the column is `NOT NULL`.

```sql
CREATE TABLE album (
  album_id  INT PRIMARY KEY,
  artist_id INT NOT NULL
    REFERENCES artist,
  title     TEXT NOT NULL
);
```

**3. M:N relationship → associative (junction) table.** Its key combines both foreign keys, and any attributes of the relationship itself live here.

**4. 1:1 relationship → foreign key with `UNIQUE`**, placed on the side with total participation (so it can be `NOT NULL`). If both sides are total and always created together, consider merging them into one table.

**5. Multivalued attribute → its own table**, keyed by owner plus value: `artist_genre(artist_id, genre)`. This is 1NF in action.

**6. Derived attribute → usually not stored.** Compute it in queries or views, or as a PostgreSQL generated column if it uses an allowed immutable expression over the same row. Age derived from the current date is not immutable.

### Weak entities

A **weak entity** cannot be identified on its own, only relative to an **owner**. Track 3 means nothing without saying which album. Its key is the owner's key plus a **partial key**:

```sql
CREATE TABLE track (
  album_id INT REFERENCES album
    ON DELETE CASCADE,
  track_no INT,
  title    TEXT NOT NULL,
  PRIMARY KEY (album_id, track_no)
);
```

`ON DELETE CASCADE` reflects existence dependency: if the album goes, its tracks go. Many teams give tracks a surrogate `track_id` anyway, for shorter foreign keys and URLs. That is fine, as long as `UNIQUE (album_id, track_no)` still enforces the real rule.

### Relationship attributes and the duplicate trap

When a user adds a track to a playlist, *when* they added it and *where* it sits are facts about the relationship, not about either entity. They belong on the junction table. The following PostgreSQL example assumes the surrogate-key alternative above: track has a single-column primary key track_id, plus NOT NULL album_id/track_no and UNIQUE(album_id, track_no). It is not directly compatible with the preceding composite-key-only track definition:

```sql
CREATE TABLE playlist_entry (
  playlist_id INT REFERENCES playlist
    ON DELETE CASCADE,
  position    INT,
  track_id    INT NOT NULL
    REFERENCES track,
  added_at    TIMESTAMPTZ NOT NULL
    DEFAULT now(),
  PRIMARY KEY (playlist_id, position)
);
```

Notice the key. The textbook junction key `(playlist_id, track_id)` would forbid the same song appearing twice on one playlist, which real playlists allow. The key must reflect the rule you actually want, so here it is position within playlist.

## Ternary relationships

Some facts involve three entities at once: *supplier S supplies part P to project J*. It is tempting to replace this with three binary relationships, but that loses information.

```
Supplies(S, P, J):
S1 P1 J2
S1 P2 J1
S2 P1 J1
```

Project into SP, PJ and SJ and join them back, and you get an extra row, `S1 P1 J1`. Each pair in it is true (S1 supplies P1 to someone; P1 goes to J1; S1 supplies J1), but S1 never supplied P1 to J1. A genuine three-way fact needs a three-way table with all three foreign keys. (In the language of the normal forms lesson, this is a join dependency, the territory of 5NF.)

## Inheritance: specialisation and generalisation

Sometimes entities share most attributes but differ in some: a `Payment` is either a `CardPayment` (card token, last four digits) or a `BankTransfer` (sort code, reference). The ER model calls this specialisation. Subtypes can be **disjoint** (at most one subtype; exactly one only when also total) or **overlapping**, and specialisation can be **total** (every payment is some subtype) or **partial**.

For portable relational schemas, choose one of three mappings. PostgreSQL also has native table inheritance, with different semantics and limitations; the mappings here do not rely on it. They are named in Martin Fowler's *Patterns of Enterprise Application Architecture*:

| Mapping | Tables | Main cost |
|---|---|---|
| Single table | one, with type column | many NULLs |
| Class table | parent + one per subtype | joins |
| Concrete table | one per subtype | no shared key |

**Single-table inheritance** puts every column in one table with a `kind` discriminator. It is fast and simple, but subtype columns must be nullable, so declare kind NOT NULL and use CHECK constraints to keep them coherent:

```sql
CHECK (
  (kind = 'card'
   AND card_last4 IS NOT NULL
   AND sort_code IS NULL)
  OR
  (kind = 'bank'
   AND sort_code IS NOT NULL
   AND card_last4 IS NULL))
```

**Class-table inheritance** has `payment(payment_id, amount, ...)` plus `card_payment(payment_id PRIMARY KEY REFERENCES payment, ...)`. No NULL columns and clean constraints, at the cost of a join to load a whole payment.

**Concrete-table inheritance** has a full table per subtype. Queries over "all payments" need `UNION ALL`, and nothing enforces unique ids across the tables.

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

The related **entity–attribute–value** (EAV) pattern, a table of `(entity_id, attribute_name, value)` rows, gives up types, constraints and simple queries in exchange for schema flexibility. If attributes are truly open-ended, a `jsonb` column is usually the better compromise in Postgres.

## Keys: surrogate or natural?

A **natural key** comes from the domain (ISBN, ISO country code). A **surrogate key** is generated (`GENERATED ALWAYS AS IDENTITY`, UUID). Natural keys can change (emails, names) or turn out not to be unique; surrogates are stable and compact. The common practice is a surrogate primary key **plus** `UNIQUE` constraints on the natural keys, so the real-world rules are still enforced.

## Key takeaways
- An ER model captures entities, attributes, relationships, cardinality (max) and participation (min) before you write any DDL; get the cardinalities from concrete domain questions.
- Mapping rules: entity → table; 1:N → foreign key on the many side; M:N → junction table holding the relationship's attributes; multivalued attribute → its own table; weak entity → owner key + partial key.
- Choose junction-table keys from the actual rule (duplicates allowed or not), not by habit.
- A true ternary fact cannot be split into three binary relationships without inventing tuples.
- Map inheritance as single-table, class-table or concrete-table, and avoid polymorphic associations and EAV, which defeat foreign keys.

## Further reading
- [Entity–relationship model — Wikipedia](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model)
- [Associative entity — Wikipedia](https://en.wikipedia.org/wiki/Associative_entity)
- [Weak entity — Wikipedia](https://en.wikipedia.org/wiki/Weak_entity)
- [Class Table Inheritance — Martin Fowler](https://martinfowler.com/eaaCatalog/classTableInheritance.html)
- [Single Table Inheritance — Martin Fowler](https://martinfowler.com/eaaCatalog/singleTableInheritance.html)
- [Entity–attribute–value model — Wikipedia](https://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model)
