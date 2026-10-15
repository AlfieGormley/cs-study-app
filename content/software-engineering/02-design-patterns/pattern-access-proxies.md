---
id: pattern-access-proxies
title: Access proxies and hidden work
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: A proxy controls access to a real object, including lazy creation.
---

## Proxy pattern

### The problem

You want a stand-in that controls access to a real object: create it lazily, check permissions, call it over the network, or cache its results.

### The structure

```
 Client ---> Subject interface
               ^           ^
               |           |
          RealSubject <-- Proxy
                          +request():
                           check/load,
                           then forward
```

Structurally identical to decorator. The difference is intent: a proxy *manages* the real object (often creating it), while a decorator *adds* features to one it's given.

### In Python

A lazy (virtual) proxy:

```python
class BigReport:
    def __init__(self):
        print("expensive load")
        self.rows = list(range(3))

    def total(self):
        return sum(self.rows)

class LazyReport:
    def __init__(self):
        self._real = None

    def total(self):
        # Construct only on first access.
        if self._real is None:
            self._real = BigReport()
        # Later calls reuse the loaded
        # object.
        return self._real.total()

r = LazyReport()      # nothing loaded yet
print(r.total())      # expensive load, 3
print(r.total())      # 3 (no reload)
```

### When not to use it

- When the "transparent" stand-in hides behaviour that callers need to know about. A **remote proxy** makes a network call look like a local method call, but networks fail, time out and can have much higher and more variable latency than a local call; the ratio depends on the work and environment. Treating it as local falls for two classic fallacies of distributed computing: "the network is reliable" and "latency is zero".
- Lazy proxies can cause the **N+1 query problem**: looping over 100 lazily loaded ORM objects triggers 100 separate queries.

The name comes from counting the database round trips. One query fetches the list of N objects; then touching a lazily loaded related object on each of them runs one more query per object:

```formula
Q = 1 + N
Q = 1 + 100 = 101
where
Q: the total number of database queries the loop sends (a plain count, no unit)
N: the number of objects in the list, each with one lazily loaded related object that the loop touches; here 100
In words: one query for the list, plus one hidden query for every item in it, so the query count grows in step with the list.
```

For a remote database, each sequential query can add a network round trip. In a deliberately simplified example at 1 millisecond per query, 101 queries contribute about 0.1 seconds, while one or two contribute roughly one or two milliseconds. This counts only the assumed per-query time; local databases, query execution, transfer sizes, parallelism and connection behaviour change real timings. The count assumes nothing is cached or prefetched; ORMs offer eager loading (in Django, `select_related` and `prefetch_related`) precisely to collapse the N extra queries.

### In real libraries

- **`xmlrpc.client.ServerProxy`**: method calls become XML-RPC requests to a server.
- **`weakref.proxy`**: forwards to an object without keeping it alive.
- **Django's `SimpleLazyObject`**: `request.user` defers authentication lookup until needed; whether that lookup queries a database depends on the session and authentication backend.
- **ORM lazy loading** in SQLAlchemy and Hibernate: related objects are proxies or loaders that query on first access.

## Key takeaways
- A proxy controls access to a real object, including lazy creation.
- Local-looking calls can conceal network failure, latency and database queries.
- Eager loading can replace one query per related object with a join or batched fetch.

## Further reading
- [QuerySet API — Django documentation](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Advanced usage — Requests documentation](https://requests.readthedocs.io/en/latest/user/advanced/)
