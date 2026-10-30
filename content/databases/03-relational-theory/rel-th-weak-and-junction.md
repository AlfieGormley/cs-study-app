---
id: rel-th-weak-and-junction
title: Weak entities and relationship keys
level: advanced
minutes: 2
sourceLesson: rel-th-er-modelling
summary: Weak entities, relationship attributes and choosing a junction-table key that matches the real rule.
---

## Weak entities

A **weak entity** cannot be identified on its own, only relative to an **owner entity**. Track 3 means nothing without saying which album. Its key is the owner's key plus a **partial key**:

```sql
CREATE TABLE track (
  album_id INT REFERENCES album
    ON DELETE CASCADE,
  track_no INT,
  title    TEXT NOT NULL,
  PRIMARY KEY (album_id, track_no)
);
```

> [!analogy] Real-world analogy: flat numbers
> "Flat 3" is not an address on its own: every block on the street may have a flat 3. Only "Flat 3, 12 Mill Lane" identifies a home, and if the block is demolished, its flats go with it.
>
> **How it maps:** The block is the owner entity (album), the flat number is the partial key (track number), and the full address is the composite primary key (album id plus track number). Demolishing the block is `ON DELETE CASCADE`.
>
> **Where it stops:** When a council renumbers flats, residents simply start using the new number. Changing part of a primary key in a database must update every row that references it, which is one reason many teams add a surrogate id.

`ON DELETE CASCADE` reflects existence dependency: if the album goes, its tracks go. Many teams give tracks a surrogate `track_id` anyway, for shorter foreign keys and URLs. That is fine, as long as `UNIQUE (album_id, track_no)` still enforces the real rule.

## Relationship attributes and duplicate entries

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

## Key takeaways

- A weak entity needs its owner key plus its partial key.
- Relationship attributes belong on the junction, and its key must reflect whether duplicates are allowed.

## Further reading

- [Chen: The Entity-Relationship Model (1976)](https://openlib.org/home/krichel/courses/lis512/readings/chen76theentity-relationship.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
