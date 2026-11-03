---
id: cs2-video-streaming-egress-budget
title: Video viewing and egress
level: intermediate
minutes: 3
summary: Distinguish peak delivery capacity from daily transferred bytes and regional demand.
sourceLesson: cs2-video-streaming
---

## Budget simultaneous viewing

Delivery capacity follows viewers watching **at the same moment**, their delivered bitrates and where they are. Daily active viewers alone cannot size a peak link: the same audience can watch evenly through the day or arrive together for a release.

An illustrative platform has 200 million daily viewers, averaging one watched hour at 3 Mbps. Spread evenly, that is about 8.3 million simultaneous viewers. If the chosen peak is twice that average, delivery approaches 50 Tbps. These are scenario inputs, not measurements of Netflix or YouTube.

## Peak capacity and daily transfer answer different questions

Peak traffic sizes links and delivery capacity. Total watched time and bitrate determine transferred bytes and the associated bill. Compressing the same viewing into a shorter busy period raises the peak without necessarily changing the day's payload. Holding bitrate and viewing constant while merely adding CDN sites does not reduce the bytes viewers consume.

Better encoding can reduce both peak bandwidth and total payload at the selected quality, but only for compatible devices receiving that encode. Retries, audio, protocol overhead and prefetch beyond what viewers watch add traffic beyond the simple video-payload model.

## Place capacity where demand occurs

Split the estimate by geography and busy hour. A worldwide average can hide one overloaded region. Test edge capacity, cache misses and origin fetches separately: an edge hit saves an upstream fetch but still sends media to the viewer.

Plan for failures and sudden popularity changes. A spare region or origin link is useful only if routing, cached content and authorised access still work when traffic shifts. The illustrative total motivates distributed delivery; it does not prove a particular number of sites or a universal data-centre limit.

## Key takeaways
- Peak egress depends on concurrent viewing rather than daily user count alone.
- Bitrate determines network bits; divide by eight when estimating byte storage.
- A CDN distributes distance and capacity, without a universal single-centre bandwidth cutoff.

## Further reading
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
- [Open Connect technical overview](https://openconnect.netflix.com/Open-Connect-Overview.pdf)
