---
id: cs2-ride-sharing-geo-candidates
title: Geospatial candidate indexing
level: intermediate
minutes: 4
summary: Compare cell and tree indexes and distinguish graph neighbourhoods from metric radii.
sourceLesson: cs2-ride-sharing
---

## Deep dive 2: geospatial indexing

The query is "the K nearest available drivers within R km of the rider". A lexicographic B-tree on `(lat,lng)` is not a general efficient radius index. Spatial trees, database spatial indexes or cell mappings can support 2D searches.

### Geohash

Geohash interleaves latitude and longitude bits and base-32 encodes them. Shared prefixes mean nearby cells.

| Length | Approx. width × height near equator |
|---|---|
| 5 | 4.9 km × 4.9 km |
| 6 | 1.2 km × 0.6 km |
| 7 | 153 m × 153 m |

- **Pros**: simple, works as a string key in any KV store or DB. Redis `GEOSEARCH` uses a 52-bit geohash in a sorted set.
- **Cons**: the **edge problem**. Two points a metre apart across a cell boundary can share no prefix, so a radius search must cover every cell intersecting the search area and then filter by exact distance. The centre cell plus eight neighbours is sufficient only when the chosen cell size and search radius justify that coverage. Cells are also rectangles that distort with latitude.

### Quadtree

Recursively split a region into four until each leaf holds at most N points (say 100).

- **Pros**: adapts to density. Central London gets tiny cells and the countryside gets huge ones, which can help manage local density. Query work still depends on radius and the number of results.
- **Cons**: moving points can require structural maintenance. A quadtree may be held in memory or persisted; benchmark updates, skew and query cost rather than assuming every implementation is unsuitable for moving drivers.

### S2 (Google)

S2 projects the sphere onto a cube and orders cells along a **Hilbert curve**, which offers useful hierarchical spatial locality rather than a universal performance advantage over geohash's Z-order. Cells have 64-bit ids across 31 levels. A circle can be **covered** by cells at mixed levels. The cell-count limit and required accuracy determine the ranges to scan; a small covering may include substantial extra area.

### H3 (Uber)

H3 tiles the world in **hexagons** across 16 resolutions (0 to 15). Each step down is roughly 7 times smaller in area. Average cell sizes from the H3 docs:

| Resolution | Avg area | Avg edge |
|---|---|---|
| 7 | ~5.2 km² | ~1.4 km |
| 8 | ~0.74 km² | ~530 m |
| 9 | ~0.11 km² | ~200 m |

These are averages: because H3 projects from an icosahedron, hexagon area at one resolution varies by up to about 2x across the globe (excluding the smaller pentagons), so inspect actual local cell areas when density comparisons require precision. A sphere can't be tiled with hexagons alone, so each resolution also has 12 pentagons.

- A regular planar hexagon has six equally spaced neighbours. H3 approximates this geometry on a sphere; actual centre distances vary with projection distortion and pentagon boundaries. A square has edge neighbours and corner neighbours at different distances. This makes "k-ring" searches (all cells within k steps) and smoothing across neighbours clean.
- Uber built H3 specifically for surge pricing and supply/demand analysis.

> [!tip] What to say in the interview
> "I'd index drivers by H3 cell at about resolution 8 in an in-memory sharded store. For a request, I take a k-ring around the rider's cell, gather the available drivers, then rank them by road-network ETA, not straight-line distance." That names a real scheme, handles the edge problem, and shows you know crow-flies distance is misleading (think of a river with no bridge).

## Estimating a graph neighbourhood

Away from pentagons, a planar regular-hexagon approximation counts the centre and successive rings. This estimates query work; it is not an exact coverage guarantee for a metric pickup radius.

A regular planar hexagon model contains one centre cell, six first-ring cells and twelve second-ring cells: nineteen altogether. Real H3 neighborhoods can encounter pentagon distortion; a graph neighborhood is not a guarantee of covering a metric-radius circle.

A cell query still needs enough coverage, freshness checks and distance or ETA filtering. Average area does not prove that every point within a chosen circle is covered.

## Key takeaways
- Geohash needs boundary coverage and exact-distance filtering.
- H3 gives useful graph neighbourhoods with projection distortion and pentagon exceptions.
- Road-network ETA can differ substantially from straight-line distance.

## Further reading
- [H3: hexagonal hierarchical geospatial indexing (docs)](https://h3geo.org/docs/)
- [S2 Geometry library](https://s2geometry.io/)
- [Geohash (Wikipedia)](https://en.wikipedia.org/wiki/Geohash)
- [Quadtree (Wikipedia)](https://en.wikipedia.org/wiki/Quadtree)
- [H3 cell statistics](https://h3geo.org/docs/core-library/restable/)
- [H3 graph traversal](https://h3geo.org/docs/api/traversal/)
- [Redis geospatial representation](https://redis.io/docs/latest/commands/geoadd/)
