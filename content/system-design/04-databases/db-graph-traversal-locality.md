---
id: db-graph-traversal-locality
title: Graph traversal and adjacency
level: basic
minutes: 2
summary: Use explicit nodes and edges for multi-hop relationships while recognising traversal and sharding costs.
sourceLesson: db-nosql-families
---

When a query repeatedly follows relationships, represent those relationships directly. The benefit depends on the amount of connected data visited, not just the label "graph database".

## Graph databases

When the relationships *are* the data (social networks, fraud rings, recommendation, access control), a graph database stores **nodes** and **edges** directly, and some engines use direct adjacency structures. Edge traversal cost still depends on caching, representation and network placement; not every graph database uses the same storage design.

```
(:Person {name:'Ana'})-[:FOLLOWS]->(:Person)
```

```cypher
// Neo4j Cypher: friends of friends
// Follow two outgoing friendship edges.
MATCH (me:Person {id: 42})-[:FRIEND]->()
      -[:FRIEND]->(fof)
// Omit direct friends and the starting
// node.
WHERE NOT (me)-[:FRIEND]->(fof)
  AND fof <> me
RETURN fof.name LIMIT 20;
```

The Cypher assumes existing Person nodes and FRIEND relationships. Returned names depend on that graph; LIMIT without ORDER BY does not promise which twenty appear.

- **Examples**: Neo4j, Amazon Neptune, JanusGraph, Dgraph.
- **Cheap**: multi-hop traversals ("within 3 hops"), path finding, pattern matching.
- **Expensive**: bulk aggregation over all nodes, and horizontal sharding (cutting a graph across machines makes traversals cross the network).

A fixed-depth SQL traversal can use self-joins; variable-depth traversal can use a recursive CTE. Intermediate results can grow quickly with branching and depth, but indexes, pruning and the query plan determine the actual cost.

## Why adjacency helps

Neo4j uses index-free adjacency: after locating a starting node, traversal follows its stored relationships. The work is proportional to the neighbours actually visited; a high-degree node or deep expansion can still be expensive. An SQL graph can use indexes and recursive CTEs too, so benchmark the real graph and query rather than expecting a universal speedup.

## Key takeaways
- Graph stores represent relationships directly and can follow adjacency structures efficiently.
- The work still depends on the neighbours visited, caching and placement.
- Splitting a graph across machines can turn traversals into network requests.

## Further reading
- [neo4j.com: graphdb concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/)
- [neo4j.com: match](https://neo4j.com/docs/cypher-manual/current/clauses/match/)
