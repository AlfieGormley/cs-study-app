---
id: prob-mean-median-latency
title: Compare mean and median latency
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: A mean reflects totals and outliers; a median describes the centre.
---

Probability goes from a model to predictions. **Statistics** goes the other way: from data back to conclusions about the world. Engineers do this constantly, often without noticing. Is the new build slower? Did the checkout redesign raise conversion? Is the 99th-percentile (p99) latency within the SLO (service level objective)?

This lesson covers the handful of statistical ideas that come up most in engineering, and the traps that catch experienced teams.

## Mean versus median

The **arithmetic mean** is the sum divided by the count. The **median** is the middle sorted value, conventionally the average of the two middle values for an even-sized numeric sample. For a finite symmetric sample the mean and this median agree; for skewed data they can be wildly different.

In symbols, the mean of a sample of values is:

```formula
x̄ = (x_1 + x_2 + … + x_n) / n
where
x̄: "x-bar", the sample mean
x_1, x_2, x_n: the first, second and last values in the sample
n: the number of values
…: and so on, every value in between
In words: add every value and divide by how many there are.
```

> [!example] One slow request
> 99 requests take 10 ms (milliseconds) and one takes 5,000 ms (a timeout).

```formula
x̄ = (99 × 10 ms + 5,000 ms) / 100
x̄ = 5,990 ms / 100 = 59.9 ms
M = 10 ms
where
x̄: the mean latency, in milliseconds (ms)
M: the median latency, the middle value when sorted (both middle values are 10 ms)
ms: milliseconds, thousandths of a second
In words: one timeout drags the mean to about 60 ms even though 99 of the 100 requests took 10 ms; the median stays at 10 ms.
```

The mean describes no actual request. The median ignores the timeout entirely.

Neither is "right"; they answer different questions.

- The **arithmetic mean** matters for totals: total resource use is the request count times mean resource use per request. Wall-clock latency includes waiting and is not automatically CPU service time; capacity also depends on concurrency, utilisation and variability.
- The **median** describes the typical experience and is robust to outliers.
- Neither tells you about the slow tail that users complain about.

## Key takeaways
- A mean reflects totals and outliers; a median describes the centre.
- Wall-clock latency is not automatically CPU service time.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
