---
id: cache-proxy-topologies
title: Reduce cache connections with a proxy tier
level: advanced
minutes: 2
summary: Choose a cache topology and calculate the per-node connection count before and after adding proxies.
sourceLesson: cache-distributed
---

A large application fleet can create thousands of connections to every cache node. Proxies hide the fleet topology and concentrate backend connection pools into fewer clients.

## Topology choices

| Option | Good for |
|---|---|
| Single node + replica | Workload fits one node |
| Client-side sharding | Memcached fleets |
| Redis Cluster | Large, self-managing |
| Proxy (mcrouter, Envoy) | Many clients, simple config |

A proxy layer hides the topology from clients and pools connections, which matters when thousands of app instances would otherwise each open connections to every node. Each node holds one pool per client that connects to it:

```formula
C_node = I × P
C_node = 2,000 × 4 = 8,000
C_node = 20 × 4 = 80
where
C_node: the connections one cache node must hold open
I: the number of clients connecting directly to the node: 2,000 app instances without a proxy, or 20 proxies with one
P: the connections each client keeps open to each node (its pool size), here 4
In words: without a proxy every app instance connects to every node; with one, only the proxies do, so the count per node falls a hundredfold here.
```

Facebook's **mcrouter** is a proxy of this kind for Memcached; it also routes invalidations and can replicate writes to pools of servers. Twemproxy (from Twitter) and Envoy's Redis proxy play the same role, and modern Memcached ships its own built-in proxy.

## Key takeaways
- A single node with a replica suits a measured workload that fits one primary; partitioning and proxies address different scaling pressures.
- Per-node connections are direct clients multiplied by each client’s pool size.
- A proxy tier simplifies routing and reduces backend connections but introduces another service to operate.

## Further reading
- [mcrouter — Meta](https://github.com/facebook/mcrouter)
- [Built-in proxy — Memcached](https://docs.memcached.org/features/proxy/)
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
