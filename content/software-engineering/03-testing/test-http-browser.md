---
id: test-http-browser
sourceLesson: test-integration-e2e
title: Check HTTP boundaries and critical browser journeys
level: intermediate
minutes: 4
summary: A stub server exercises a different boundary from an in-process HTTP interceptor.
---

Database integration tests check one kind of seam. HTTP clients need checks at their own boundaries, while a few browser journeys check how the deployed parts fit together. The browser example needs a configured staging application and Playwright’s `page` fixture.

## Testing HTTP clients and other services

A narrow integration test can run the real client against a local **stub server**, such as WireMock. Python libraries `responses` and `respx` instead intercept client-library calls in-process; they are not local HTTP servers and exercise a different boundary.

Keeping the client code real can check URL construction, headers, query encoding, JSON parsing, timeout and retry behaviour, and how you handle a 503 or a malformed body.

An in-process interceptor does not exercise real sockets, TLS or actual network timeouts; injected exceptions only check handling. Neither approach alone establishes whether canned responses match what the real service sends. That is the job of contract tests, below.

## End-to-end tests

An E2E test drives the whole running system from the outside. For a web app, that usually means a real browser controlled by a tool such as **Playwright** or Selenium:

```python
from playwright.sync_api import expect

def test_checkout(page):
    page.goto("https://staging.shop/")
    # Roles describe UI purpose, not
    # styling.
    page.get_by_role(
        "button", name="Add to basket"
    ).click()
    # Roles describe UI purpose, not
    # styling.
    page.get_by_role(
        "link", name="Checkout").click()
    # Retry the condition until timeout.
    expect(page.get_by_text(
        "Order confirmed")).to_be_visible()
```

E2E tests provide evidence that selected journeys work through the tested wiring and configuration; they do not prove correctness for all users, inputs or environments. They often cost more to run and diagnose, and have more opportunities for environmental flakiness. Use them deliberately:

- **Cover a few critical journeys**: sign up, log in, buy, pay. Not every edge case; push those down the pyramid.
- **Wait for conditions, never for time.** Playwright's `expect` retries until the element appears or a timeout passes. `time.sleep(2)` is slow when the page is fast and flaky when it is slow.
- **Own your test data.** Each test creates the user and products it needs, with unique names, rather than relying on shared records that another test may change.
- **Use stable selectors**: roles, labels or dedicated test ids, not CSS paths that change with every redesign.
- **Wrap pages in page objects** (`CheckoutPage.pay_with(card)`) so a UI change means editing one class, not forty tests.

> [!note] Shared staging environments
> A single staging environment shared by many teams is a common source of E2E pain: someone else's half-deployed service breaks your tests. Ephemeral per-branch environments help, as does moving most cross-service checks to contract tests.

## The microservice problem

Picture two services. **Orders** (the *consumer*) calls **Users** (the *provider*) at `GET /users/42` and reads `email`.

```
 Orders  --GET /users/42-->  Users
         <-- {id, email} --
```

Each team tests well in isolation. Orders' tests stub the Users API with `{"id": 42, "email": "a@x.io"}`. Users' tests check their own endpoint. Then the Users team renames `email` to `primary_email`. Every test in both repositories passes. Production breaks.

The stub encoded Orders' *belief* about Users, and nothing checked that belief. You could catch it with broad E2E tests that run both services, but those require the journey’s real dependencies together and can cost more to run and diagnose. **Contract tests** check the seam directly instead.

## Key takeaways
- A stub server exercises a different boundary from an in-process HTTP interceptor.
- Keep browser checks focused on critical journeys, own their data and wait for conditions.
- Shared staging and unchecked stubs create cross-team failure modes.

## Further reading
- [Integration Test — Martin Fowler](https://martinfowler.com/bliki/IntegrationTest.html)
- [Larger Testing — Software Engineering at Google, ch. 14](https://abseil.io/resources/swe-book/html/ch14.html)
- [Playwright for Python](https://playwright.dev/python/docs/intro)
