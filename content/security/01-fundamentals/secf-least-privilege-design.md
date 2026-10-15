---
id: secf-least-privilege-design
title: Design for least privilege
level: intermediate
minutes: 3
sourceLesson: secf-principles
summary: Grant only the authority the component needs.
---

Specific vulnerabilities change every year. The principles that prevent them have barely changed since 1975, when Jerome Saltzer and Michael Schroeder published *The Protection of Information in Computer Systems*. Their list of eight design principles is still the backbone of how security engineers review a design.

This lesson covers those principles plus defence in depth, with the question each one asks of your system.

## Least privilege

> Every program and every user should operate using the least set of privileges necessary to complete the job.

The intuition: you can't prevent every compromise, so limit what a compromise can do. This is often described as limiting the **blast radius**.

```
Web app has broad database authority
  SQLi may read/alter/drop accessible data;
  extra role powers depend on the DB

Web app credentials: SELECT/INSERT on
  orders, SELECT on products
  SQLi may read orders/products,
  insert orders (still serious)
```

In practice least privilege means:

- **Service accounts scoped to one job.** The thumbnail worker gets read access to one bucket, not `s3:*`.
- **No standing admin rights.** Engineers request elevated access for a time-limited window (just-in-time access), which is logged.
- **Avoid unnecessary elevated execution.** Use an unprivileged service with a narrowly scoped binding mechanism where supported. If start-up needs elevation, drop the unneeded identities, groups and Linux capabilities afterwards. Non-root containers still need appropriately restricted Linux capabilities and access controls.
- **Short-lived credentials** rather than long-lived keys, so a leaked token expires.

The hard part isn't the principle; it is keeping permissions tight over time. Permissions accrete: someone adds a wildcard to fix an outage and nobody removes it. Tools such as AWS IAM Access Analyzer compare granted permissions with those actually used.

> [!example] Capital One, 2019
> Capital One reported unauthorised access affecting approximately 100 million individuals in the US and six million in Canada. The company identified a configuration vulnerability. The exact exploit chain and the counterfactual claim that a narrower role would have made the incident minor are not established by the disclosure used here, so those details are omitted.

## Key takeaways
- Grant only the authority the component needs.
- Review standing permissions and use scoped, short-lived credentials.
- Least privilege limits damage rather than proving a component safe.

## Further reading
- [Saltzer and Schroeder: protection principles](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
