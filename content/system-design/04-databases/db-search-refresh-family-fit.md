---
id: db-search-refresh-family-fit
title: Search refresh and specialist stores
level: basic
minutes: 2
summary: Explain near-real-time search visibility and compare the core strengths of the NoSQL families.
sourceLesson: db-nosql-families
---

Search is a derived access path with its own visibility rules. A successful index write and a successful search for that write are different events.

## Search engines

Elasticsearch and OpenSearch (both built on Apache Lucene) maintain **inverted indexes**: a map from each term to the documents containing it. They're excellent at full-text relevance ranking, fuzzy matching and faceted filters, and are usually fed *from* a primary database rather than being the system of record.

They're also **near-real-time**: a newly indexed document becomes searchable only after the next *index refresh*, every second by default for actively searched Elastic Stack indexes; serverless deployments and OpenSearch settings may differ. Check the configured interval. Fetching a document by id is real-time. Search architecture is covered in the architecture module.

## Summary table

| Family | Best at | Weak at |
|---|---|---|
| Key-value | Lookup by key | Queries on values |
| Document | Whole aggregates | Many-to-many |
| Wide-column | Writes at scale | Ad-hoc queries |
| Graph | Multi-hop links | Bulk analytics |
| Time-series | Time-range stats | Updates, joins |
| Search | Text relevance | Source of truth |

> [!tip] The lines are blurring
> Postgres has `jsonb`, full-text search and extensions for time series (TimescaleDB) and graphs (Apache AGE). MongoDB has multi-document ACID transactions. DynamoDB has transactions too. Pick based on the *core* access pattern, not the feature checklist.

## Key takeaways
- Inverted indexes map terms to matching documents.
- An indexed write becomes searchable after refresh; fetching by id uses a different visibility path.
- Compare the core access pattern and trade-offs rather than a product feature checklist.

## Further reading
- [Elasticsearch: Near real-time search](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search)
- [www.elastic.co: operation get](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-get)
