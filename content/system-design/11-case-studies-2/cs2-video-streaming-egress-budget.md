---
id: cs2-video-streaming-egress-budget
title: Video viewing and egress
level: intermediate
minutes: 3
summary: Convert daily watch hours into concurrency, peak throughput and daily payload.
sourceLesson: cs2-video-streaming
---

**Viewing.** Say 200 M (200 million) daily viewers each watching 1 hour at an average 3 Mbps.

The network has to be sized for how many people are watching *at the same moment*, not per day. If viewing were spread evenly over the day, the average number watching at once is total viewing hours divided by the hours in a day:

```formula
C_avg = (D × T_watch) / (24 h)
C_avg = 200 M × 1 h / 24 h ≈ 8.3 M
C_peak ≈ 2 × C_avg ≈ 17 M
where
C_avg: average number of viewers watching at the same moment
C_peak: number watching at once at the busiest time of day; assumed about twice the average
D: daily viewers, people who watch at least once a day; here 200 M
T_watch: viewing time per viewer per day, in hours (h); here 1 h
24 h: the hours in one day
h: hours
M: million (1,000,000)
≈: approximately equal to
In words: 200 million people each watching an hour a day means about 8.3 million watching at any moment on average, and roughly 17 million at the evening peak.
```

The "2x" peak factor is an assumption: real daily curves depend on time zones and audience. Egress (data sent out of your network to viewers) at peak is the number watching times the bitrate each one receives:

```formula
E_peak = C_peak × r
E_peak = 17 M × 3 Mbps ≈ 51 Tbps ≈ 50 Tbps
where
E_peak: peak egress, in terabits per second (Tbps)
C_peak: viewers watching at once at peak; here about 17 M
r: average bitrate each viewer streams, in megabits per second (Mbps); here 3
M: million
Mbps: megabits per second; 1 Mbps = 1,000,000 bits per second
Tbps: terabits per second; 1 Tbps = 1,000,000 Mbps
≈: approximately equal to
In words: 17 million streams at 3 megabits per second each add up to about 50 terabits per second leaving the platform.
```

Daily egress, in bytes, is every viewer's watch time in seconds times the bitrate, divided by 8 to turn bits into bytes:

```formula
E_day = D × t × r / 8
E_day = 200 M × 3,600 s × 3 Mbps / 8
E_day = 2.7 × 10^17 B ≈ 270 PB
where
E_day: data sent to viewers per day, in bytes (B)
D: daily viewers; here 200 M
t: viewing time per viewer per day, in seconds (s); 1 hour is 3,600 s
r: average bitrate, in megabits per second (Mbps); here 3
8: bits per byte
M: million
Mbps: megabits per second; 1 Mbps = 1,000,000 bits per second
s: seconds
B: bytes
PB: petabytes; 1 PB = 10^15 bytes
≈: approximately equal to
In words: 200 million hours of viewing at 3 megabits per second is about 270 petabytes of video delivered every day.
```

Serving 50 Tbps to a global audience makes geographic distribution, network capacity and egress cost central design concerns. A CDN also reduces network distance; 50 Tbps is not a universal single-data-centre limit.

## Key takeaways
- Peak egress depends on concurrent viewing rather than daily user count alone.
- Bitrate determines network bits; divide by eight when estimating byte storage.
- A CDN distributes distance and capacity, without a universal single-centre bandwidth cutoff.

## Further reading
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [Content delivery network (Wikipedia)](https://en.wikipedia.org/wiki/Content_delivery_network)
