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

GraphQL moves the fan-out from the client to the server. Each field is backed by a *GraphQL resolver* function. Naïve resolvers make the problem worse, not better:

```
feed resolver:   1 query  -> 20 posts
author resolver: called 20 times
  SELECT * FROM users WHERE id = ?
                 -> 20 queries
Total: 21 queries for these 20 posts
```

Follow how the work grows as the list gets longer:

With naïve per-item resolvers, every extra parent adds more database queries for its nested fields.

So adding comments takes it from 21 to 41 queries. Nest one more level and it multiplies, because each of those children has its own children.

The standard fix is **batching with a DataLoader**. Within one tick of the event loop, the loader collects every `author` id requested, then issues a single query:

```sql
-- Illustrative ids; bind real parameters.
SELECT * FROM users
WHERE id IN (a, b, c, ..., t)
```

When each nested field fits into one supported database batch:

Batching groups compatible loads across parents: one query for the list, one for authors and one for comments in this example.

So the example drops from 41 queries to 3. Parameter limits, batch-size caps and per-parent pagination can require additional work as the parent list grows. DataLoader also caches per request, so the same author appearing on five posts is fetched once.

> [!warning] GraphQL's operational costs
> - **Caching**: if operations use `POST /graphql`, ordinary URL-based CDN caching cannot distinguish request bodies. GraphQL queries may also use GET; mutation operations must not execute through GET. Teams use *persisted queries* (send a hash; allow `GET`) to recover some of this.
> - **Abuse**: a client can write a deeply nested query that fans out to millions of rows. You need query depth limits, complexity scoring and timeouts. GitHub's GraphQL API, for example, charges each query "points" from the connections and backing requests needed.
> - **Errors**: many deployed GraphQL APIs return `200 OK` with an `errors` array. Status handling depends on the transport contract and response media type; inspect GraphQL errors as well as HTTP status.

For a static potential-node budget, count each nesting level by multiplying the number of parents by the requested children per parent, then add the counts across levels. Pagination bounds each branch before any resolver runs; actual database work also depends on resolver implementation.

> [!analogy] Real-world analogy: One shopping list
> **How it maps:** Collecting everyone’s requests before visiting a shop avoids a separate trip for each person. DataLoader similarly groups compatible loads into a batch.
>
> **Where it stops:** A larger list still costs work. Batch size, data ordering, authorisation and per-parent pagination can require more than one backend request.

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
