---
id: rel-th-weak-and-junction
title: Weak entities and relationship keys
level: advanced
minutes: 2
sourceLesson: rel-th-er-modelling
summary: Weak entities and relationship keys, with explicit examples and the conditions that make the reasoning valid.
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
