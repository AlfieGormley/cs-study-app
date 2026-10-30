---
id: test-service-contracts
sourceLesson: test-integration-e2e
title: Verify service contracts and fake compatibility
level: intermediate
minutes: 4
summary: Consumer tests record needed interactions; provider verification checks the real provider against them.
---

Orders calls Users and reads the `email` field. A stub can keep returning that field after Users has renamed it. Contract testing turns the consumer’s expectation into a check against the provider. Assume `import pytest` in the fixture sketch.

## Contract testing

A **contract** is a precise description of the requests a consumer will send and the parts of the responses it relies on. It is tested from both sides:

1. On the consumer side (the **contract consumer**), the consumer's tests run against a mock provider that records the interactions they need. This produces the contract.
2. On the provider side (the **contract provider**), the provider's CI replays every contract against the real provider and checks each response satisfies it.

The idea in miniature:

```python
CONTRACT = {
  "request": {"method": "GET",
              "path": "/users/42"},
  "response": {"status": 200,
               "fields": {"id": int,
                          "email": str}},
}

def test_provider_honours_contract():
    req = CONTRACT["request"]
    exp = CONTRACT["response"]
    # Partial sketch: call the real handler.
    status, body = provider_handle(
        req["method"], req["path"])
    assert status == exp["status"]
    # Ignore fields the consumer never uses.
    for f, typ in exp["fields"].items():
        assert isinstance(body[f], typ)
```

If the provider returns `{"id": 42, "email": "a@x.io", "created": "..."}`, the test passes. The extra `created` field is fine, because the consumer does not use it. If the provider renames `email`, the lookup fails with `KeyError: 'email'` in the *provider's* build, before deploy.

The miniature checker tests required field presence and `isinstance` results, not all response semantics. Python treats `bool` as a subclass of `int`, so a strict integer ID check would also need to exclude booleans. Real contracts need matchers that express the consumer’s actual needs.

### Consumer-driven contracts and Pact

**Pact** is one tool for this. Consumer tests, written against a Pact mock server, generate a pact file. A **Pact Broker** (or PactFlow) stores pacts from every consumer, and providers verify the relevant consumer contracts selected by version and environment in CI. Its `can-i-deploy` check answers "is this version of Users compatible with every consumer version currently in production?"

> [!analogy] Real-world analogy: a kitchen's supplier checklist
> A restaurant tells its supplier exactly what it relies on: "flour in 16 kg sacks, eggs size large". Before each delivery leaves, the supplier checks the load against every restaurant's checklist. The supplier can change anything not on any list, such as the van or the packaging colour.
>
> **How it maps:** Each restaurant is a consumer, its checklist is the contract recorded by the consumer's tests, the supplier is the provider, and checking the load before dispatch is provider verification in CI (with `can-i-deploy` asking "does this load satisfy every customer?"). Freedom to change unlisted things is why contracts list only what consumers use.
>
> **Where it stops:** A checklist is written by hand, so a restaurant can forget an item; a pact is generated from the consumer's tests, so it misses only what those tests do not exercise. Contract checks run automatically on every provider build, and they check the recorded requests and the response details the consumer relies on (often just field types), not the full correctness of the provider's behaviour.

The key property is **consumer-driven**: the contract lists only what consumers actually use. Changes outside the recorded contract can still break consumers if their real dependencies were omitted; contracts need adequate consumer tests. This turns "we can never change this API" into "we can change anything no consumer depends on, and we will know immediately if we break one".

Alternatives include **provider-driven** contracts, where the provider publishes an OpenAPI or protobuf schema and consumers are checked against it. Schemas catch type and shape changes well but say nothing about which fields any consumer actually needs.

### One contract suite for fakes and real implementations

The same idea checks your own fakes. This sketch assumes adapters exposing the same add(email) method and ValueError contract; these are not the earlier raw UserRepo or two-argument InMemoryUsers. Write behavioural tests once and run them against each adapter:

```python
@pytest.fixture(params=[InMemoryUsers,
                        SqliteUsers])
def users(request):
    # Build each adapter in a separate run.
    return request.param()

def test_duplicate_rejected(users):
    users.add("a@x.io")
    # Success means the expected error
    # arose.
    with pytest.raises(ValueError):
        users.add("a@x.io")
```

pytest runs each test twice, once per implementation. If the fake stops enforcing uniqueness, its run fails, so hundreds of fast unit tests built on it can keep trusting it.

## Choosing what to use

| Risk | Best test |
|---|---|
| Wrong SQL or mapping | Narrow integration, real DB |
| HTTP client handling | Client vs stub server |
| API drift between services | Contract test |
| Wiring, config, UI journey | A few E2E tests |

## Key takeaways
- Consumer tests record needed interactions; provider verification checks the real provider against them.
- Passing contracts cover recorded dependencies, so omitted consumer needs can still break.
- Run one behavioural suite against fake and real adapters that expose the same interface.

## Further reading
- [Contract Test — Martin Fowler](https://martinfowler.com/bliki/ContractTest.html)
- [Consumer-Driven Contracts — martinfowler.com](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Pact documentation](https://docs.pact.io/)
- [Contract compatibility and deployment — Pact Broker](https://docs.pact.io/pact_broker/can_i_deploy)
