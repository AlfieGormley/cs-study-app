---
id: api-versioning-compatibility
title: Versioning and safe deprecation
level: intermediate
minutes: 3
summary: Distinguish additive changes from breaking ones and retire APIs with explicit migration signals.
sourceLesson: api-designing-good-apis
---

## Versioning

Sooner or later you'll need a breaking change. Common strategies:

| Strategy | Example |
|---|---|
| URL path | `/v2/orders` |
| Header | `Accept: ...;version=2` |
| Date-based | `Stripe-Version: 2024-06-20` |
| None (evolve only) | GraphQL style |

**URL versioning** makes versions visible in logs and straightforward to route at a gateway. Its weakness is that `v2` tends to be a big-bang rewrite, and you end up running `v1` for years.

**Stripe's versioning architecture**, described in its engineering article, uses small **version change modules** to adapt current representations for older API versions. This is a useful compatibility pattern, rather than a guarantee that every business operation has one identical code path. Consult the current Stripe versioning policy for account defaults and upgrade requirements. The diagram below is illustrative, not a list of actual releases.

```
latest response
   | transform 2026-03 -> 2025-09
   | transform 2025-09 -> 2024-06
   v
response in client's pinned version
```

## Backwards compatibility

Most changes shouldn't need a new version at all. The key is knowing which changes are safe.

| Change | Safe? |
|---|---|
| Add optional request field | Yes |
| Add response field | Yes, if tolerant |
| Add new endpoint | Yes |
| Add new enum value | Risky |
| Remove or rename field | No |
| Make optional field required | No |
| Change a field's type | No |
| Change default behaviour | No |

Adding response fields is only safe if clients follow the **robustness principle**: be tolerant of unknown fields. Strict deserialisers that reject unknown properties turn every additive change into an outage. Say so in your docs.

New **enum values** are a classic trap. If a client has a `switch` over `status` with no default case, a new `"partially_refunded"` value can crash it. Document that enums may grow and clients must handle unknown values.

> [!warning] Hyrum's Law
> "With a sufficient number of users of an API, all observable behaviours of your system will be depended on by somebody." Response ordering, timing, error message wording: someone relies on it. Be deliberate about what you expose and document what is *not* guaranteed.

## Deprecating safely

1. Announce in docs and changelog with a date.
1. Return `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers on affected endpoints, so clients' tooling can warn developers automatically.
1. Monitor usage per client; contact heavy users directly.
1. Consider communicated, risk-assessed brownouts only where deliberate temporary failures are acceptable; critical integrations may need other migration signals.
1. Remove only when traffic is near zero.

## Key takeaways
- Optional additions work only when clients follow the documented tolerance contract.
- New enum values and default changes can break clients without removing a field.
- Version changes can be isolated into compatibility transformations rather than separate deployments.
- Announce retirement, signal it in headers, monitor client usage and assess any brownout risk.

## Further reading
- [Stripe blog: APIs as infrastructure, future-proofing with versioning](https://stripe.com/blog/api-versioning)
- [Google Cloud API design guide](https://cloud.google.com/apis/design)
- [RFC 9745: Deprecation header](https://www.rfc-editor.org/rfc/rfc9745)
- [RFC 8594: Sunset header](https://www.rfc-editor.org/rfc/rfc8594)
