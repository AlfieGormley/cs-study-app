---
id: net-reverse-proxy-buffering
title: "Proxy buffering and trusted client addresses"
level: intermediate
minutes: 3
summary: "Distinguish proxy direction, decouple slow clients and validate forwarded address chains."
sourceLesson: net-proxies-gateways-mesh
---
Reverse proxies, API gateways and service meshes are often built from the same software (Envoy, NGINX, HAProxy) and share many features. The difference is mostly **where they sit** and **whose problems they solve**:

- A **reverse proxy** fronts a set of servers.
- An **API gateway** fronts a set of *APIs* for external clients.
- A **service mesh** handles traffic *between* your services.

```
         Internet
            |
     [CDN / edge proxy]
            |
      [API gateway]      <- north-south
            |
   +--------+--------+
   |                 |
[svc A]+sidecar  [svc B]+sidecar
   |     <---- mesh ---->  |
   |   (east-west, mTLS)   |
```

"North-south" traffic enters and leaves your system; "east-west" traffic flows between services inside it.

## Forward vs reverse proxy

A **forward proxy** acts for *clients*: a corporate proxy that all employees' browsers go through. The server sees the proxy, not the user.

A **reverse proxy** acts for *servers*: clients think they're talking to `example.com`, but they're talking to a proxy that forwards to hidden backends.

## Reverse proxies

A reverse proxy (NGINX, HAProxy, Envoy, Caddy, Traefik) typically handles:

| Job | Why at the proxy |
|---|---|
| TLS termination | One place for certs |
| Load balancing | Hide backend topology |
| Compression | Offload CPU from apps |
| Static files, caching | Fast, no app involved |
| Buffering | Protect slow apps |
| Request limits | Size, timeouts, rate |

**Buffering** deserves a mention. A slow mobile client might take 10 s to upload a request or download a response. If an app server process (say a Python worker) talked to it directly, that worker would be stuck for 10 s. With request/response buffering enabled and enough buffer or temporary-file capacity, NGINX can decouple a synchronous worker from a slow client. The worker remains busy for response generation and transfer to the proxy, not necessarily only milliseconds. Streaming, buffer limits and disabled buffering change this behavior. This is why NGINX in front of Gunicorn or Puma is standard practice.

The proxy also adds headers so the app knows the real client: `X-Forwarded-For` (client IP), `X-Forwarded-Proto` (was it HTTPS?) and the standardised `Forwarded` header (RFC 7239). Each proxy *appends* the address it received the connection from, so after a CDN and a load balancer the header reads `client, CDN`, and the app sees the load balancer as the connection's source address.

> [!warning] Trusting forwarded headers
> Clients can send their own `X-Forwarded-For`. First verify that the direct peer is a trusted proxy, then parse the forwarded chain from the right, skipping only explicitly trusted proxy hops. The first untrusted address is the client boundary; it may itself be an external proxy, not the original person’s device. Ensure attackers cannot bypass the trusted entry path. Otherwise attackers can spoof their IP to bypass rate limits or IP allow-lists.

### Streaming changes the buffering choice

For Server-Sent Events, buffering small updates can delay their arrival and produce bursts. NGINX can disable response buffering for the streaming route with `proxy_buffering off;` or, when permitted by its configuration, the response header `X-Accel-Buffering: no`. These are illustrative directive and header fragments, not a complete server configuration. Check read timeouts and send stream keep-alives as appropriate; changing buffering does not make synchronous application workers asynchronous.

## Key takeaways

- A forward proxy represents clients; a reverse proxy represents backend servers.
- Buffering can free synchronous workers, but streaming routes need different buffering decisions.
- Verify the direct trusted peer and walk forwarded addresses from the right; client-supplied headers can be forged.

## Further reading

- [Proxy buffering (NGINX)](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering)
- [X-Forwarded-For (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Forwarded-For)
- [Forwarded HTTP extension (RFC 7239)](https://www.rfc-editor.org/rfc/rfc7239)
