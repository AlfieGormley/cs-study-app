---
id: rel-low-volume-slo-review
title: Low-volume SLOs and operational review
level: advanced
minutes: 2
summary: Adapt objectives and alerts when small event counts make one failure dominate.
sourceLesson: rel-slos-error-budgets
---

Multiwindow alert maths assumes enough steady traffic for ratios to be informative. Quiet admin services violate that intuition: one event can dominate a whole hour. This unit closes the SLO sequence by adapting the policy and review process to the service.

### Low-traffic services

With 10 requests in an hour, one failure gives a 10% hourly error rate and can trigger the fast page rule; longer windows depend on their own event counts. The workbook's options:

- **Generate representative synthetic traffic** to detect persistent failures; keep real-user outcomes visible so synthetic successes do not hide user-specific problems.
- **Aggregate small services** that share failure modes into one combined SLO.
- **Change the product** so a single failure matters less (client-side retries, for example).
- **Lower the SLO or lengthen the windows**, accepting slower detection where a brief failure has little real impact.

## Putting it to work

1. Pick 2–4 critical user journeys.
2. Define a ratio SLI for each, measured near the user.
3. Set SLOs from historical data and user expectations.
4. Agree an error-budget policy with product leadership *before* it's needed.
5. Implement multi-window burn-rate alerts; delete cause-based pages that no longer add value.
6. Review SLOs quarterly.

## Key takeaways

- A single failure in a quiet service can create a large measured error ratio.
- Use representative synthetic checks, meaningful aggregation or a revised objective/window while keeping real users visible.
- Agree objectives, policy and alerts as one process, then review them against user needs.

## Further reading

- [Alerting on SLOs (Google SRE workbook)](https://sre.google/workbook/alerting-on-slos/)
- [Implementing SLOs (Google SRE workbook)](https://sre.google/workbook/implementing-slos/)
- [Error budget policy (Google SRE workbook)](https://sre.google/workbook/error-budget-policy/)
