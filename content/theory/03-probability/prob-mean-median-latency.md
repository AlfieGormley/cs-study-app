---
id: prob-mean-median-latency
title: Compare mean and median latency
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: A mean reflects totals and outliers; a median describes the centre.
---

A latency average should answer a specific question. The **arithmetic mean** reflects totals; the **median** describes the middle observation. Neither alone describes the slow tail.

## One timeout changes the story

Suppose 99 requests take 10 milliseconds and one takes 5,000 milliseconds. The mean is 59.9 milliseconds, while the median is 10 milliseconds. Most requests are still fast, but the timeout contributes strongly to total elapsed latency across the requests.

The mean is the total of the observations divided by their count. The median sorts them and takes the middle value, conventionally averaging the two middle values for an even-sized numeric sample. Weighting each distinct latency equally would ignore how often each occurred.

## Choose the summary for the decision

For total resource work, mean resource use per request is useful: multiplied by request count it gives the total. Wall-clock latency includes waiting and is not automatically CPU service time, so mean latency alone does not determine machine capacity.

The median is robust to a small number of extreme observations. That makes it useful for typical experience, but also means a median dashboard can hide painful timeouts. Conversely, a higher mean does not imply most requests became slower.

Use appropriate tail percentiles or threshold exceedance rates alongside the centre. Record time windows and populations consistently so a change in traffic mix does not masquerade as a change in each request's behaviour.

## Key takeaways
- A few extreme values can move the mean while leaving the median unchanged.
- Means, medians and tail measures answer different questions.
- Distinguish elapsed latency from resource service time.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
