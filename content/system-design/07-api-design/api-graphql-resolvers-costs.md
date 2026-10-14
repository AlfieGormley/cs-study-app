---
id: api-graphql-resolvers-costs
title: GraphQL resolvers, batching and query costs
level: intermediate
minutes: 4
summary: Use DataLoader batching while controlling nested-query work and HTTP caching.
sourceLesson: api-rest-graphql-grpc
---

One client request can still trigger many database queries. Follow the work inside the resolver tree, as well as the shape of the HTTP response.

## GraphQL: the client asks for exactly what it needs

GraphQL, open-sourced by Facebook in 2015, exposes a GraphQL schema. Clients send a query that mirrors the shape of the data they want, usually as `POST /graphql`.

```
query {
  feed(first: 20) {
    id
    title
    author { name avatarUrl }
    comments(first: 3) { text }
  }
}
```

One HTTP request selects the requested fields. Successful data follows that selection; errors and nullability can alter what is returned. The GraphQL schema supports introspection, so tools like GraphiQL give autocomplete and type-checking for free.

## The N+1 problem

GraphQL moves the fan-out from the client to the server. Each field is backed by a *resolver* function. Naïve resolvers make the problem worse, not better:

```
feed resolver:   1 query  -> 20 posts
author resolver: called 20 times
  SELECT * FROM users WHERE id = ?
                 -> 20 queries
Total: 21 queries for these 20 posts
```

The general count, for a list of N parents where each nested field gets its own resolver call per parent:

```formula
Q_naive = 1 + L × N
Q_naive = 1 + 1 × 20 = 21
Q_naive = 1 + 2 × 20 = 41
where
Q_naive: the number of database queries one GraphQL request makes with naïve resolvers
N: the number of parent items the list query returns, here 20 posts
L: the number of nested fields resolved separately for each parent: 1 for author only, 2 for author and comments
In words: one query fetches the list, then every nested field adds one query per item, so the total grows in step with the list length.
```

So adding comments takes it from 21 to 41 queries. Nest one more level and it multiplies, because each of those children has its own children.

The standard fix is **batching with a DataLoader**. Within one tick of the event loop, the loader collects every `author` id requested, then issues a single query:

```sql
-- Illustrative ids; bind real parameters.
SELECT * FROM users
WHERE id IN (a, b, c, ..., t)
```

With one database batch per nested field, the count no longer depends on N:

```formula
Q_batched = 1 + L
Q_batched = 1 + 2 = 3
where
Q_batched: the number of database queries with batching
L: the number of nested fields batched, here 2 (author and comments)
In words: one query for the list plus one batched query per nested field, however many posts the list returns.
```

So the example drops from 41 queries to 3. Parameter limits, batch-size caps and per-parent pagination can require additional work as N grows. DataLoader also caches per request, so the same author appearing on five posts is fetched once.

> [!warning] GraphQL's operational costs
> - **Caching**: if operations use `POST /graphql`, ordinary URL-based CDN caching cannot distinguish request bodies. GraphQL queries may also use GET; mutation operations must not execute through GET. Teams use *persisted queries* (send a hash; allow `GET`) to recover some of this.
> - **Abuse**: a client can write a deeply nested query that fans out to millions of rows. You need query depth limits, complexity scoring and timeouts. GitHub's GraphQL API, for example, charges each query "points" from the connections and backing requests needed.
> - **Errors**: responses are often `200 OK` with an `errors` array, which breaks status-code-based monitoring.

For a static potential-node budget, count each nesting level by multiplying the number of parents by the requested children per parent, then add the counts across levels. Pagination bounds each branch before any resolver runs; actual database work also depends on resolver implementation.

## Key takeaways
- GraphQL gives clients a typed response shape and moves fan-out to resolvers.
- Request-scoped DataLoader batches supported loads and caches repeated identities.
- Persisted read queries over GET can support ordinary URL caching; mutations must not execute through GET.
- Budget depth, potential node count and execution time; inspect GraphQL errors as well as HTTP status.

## Further reading
- [GraphQL: Introduction to GraphQL](https://graphql.org/learn/)
- [GraphQL: Performance (N+1 and DataLoader)](https://graphql.org/learn/performance/)
- [DataLoader on GitHub](https://github.com/graphql/dataloader)
- [GitHub: GraphQL query limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api)
