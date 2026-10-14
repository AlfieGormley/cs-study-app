---
id: cs2-video-streaming-storage-budget
title: Video storage capacity
level: intermediate
minutes: 4
summary: Estimate original and rendition storage from explicitly dated upload inputs.
sourceLesson: cs2-video-streaming
---

## Back-of-the-envelope

Assume a YouTube-scale platform.

**Uploads.** In 2019 YouTube said that more than 500 hours of video were uploaded every minute. Use that dated figure as an illustrative planning input, not a measurement of current upload volume.

First, turn the per-minute upload rate into hours of video per day, because storage is planned per day. A day has 1,440 minutes.

```formula
H_day = H_min × 1,440 min/day
H_day = 500 h/min × 1,440 min/day
H_day = 720,000 h/day
where
H_day: hours of new video uploaded per day, in hours per day (h/day)
H_min: hours of new video uploaded per minute, in hours per minute (h/min); here 500
h: hours of video playing time
min: minutes
day: one day of 24 hours (1,440 minutes)
In words: 500 hours arriving every minute, for all 1,440 minutes of a day, is 720,000 hours of new video a day.
```

Next, work out how many bytes one hour of source video takes. A video's bitrate is given in bits per second, but storage is counted in bytes, and one byte is 8 bits, so you divide by 8 at the end. Assume an average source of about 10 megabits per second (Mbps), typical of a 1080p upload.

```formula
S_hour = rt / 8
S_hour = 10,000,000 b/s × 3,600 s / 8
S_hour = 4,500,000,000 B ≈ 4.5 GB
where
S_hour: the size of one hour of source video, in bytes (B)
r: the source bitrate, in bits per second (b/s); here 10 Mbps = 10,000,000 b/s
t: the length of the video, in seconds (s); one hour is 3,600 s
8: the number of bits in one byte
b/s: bits per second; a bit is a single 0 or 1
s: seconds
B: bytes; one byte is 8 bits
GB: gigabytes; 1 GB = 1,000,000,000 bytes
≈: approximately equal to
In words: a 10 megabit-per-second video uses 4.5 gigabytes for every hour of footage.
```

Multiply the two to get the daily volume of original uploads:

```formula
S_rate = S_hour / (1 h)
S_day = H_day × S_rate
S_day = 720,000 h/day × 4.5 GB/h
S_day = 3,240,000 GB/day ≈ 3.2 PB/day
where
S_day: bytes of original uploads stored per day, in gigabytes per day (GB/day)
H_day: hours uploaded per day; here 720,000 h/day
S_hour: size of one hour of source, 4.5 gigabytes (GB)
S_rate: bytes per source hour, here 4.5 gigabytes per hour (GB/h)
h: hours
GB: gigabytes; 1 GB = 1,000,000,000 bytes
PB: petabytes; 1 PB = 1,000,000 GB = 10^15 bytes
day: one day
≈: approximately equal to
In words: 720,000 hours a day at 4.5 GB an hour is about 3.2 petabytes of originals every day.
```

For a hypothetical storage model, assume additional renditions bring total new storage to **6–8 PB/day**. This multiplier depends on the actual ladders/codecs and is not a measured YouTube ratio. Over a year that is:

```formula
S_year = S_day × 365 days
S_year = 6 PB/day × 365 day
S_year = 2,190 PB ≈ 2.2 EB
S_year = 8 PB/day × 365 day
S_year = 2,920 PB ≈ 2.9 EB
where
S_year: new storage needed per year, in petabytes (PB) or exabytes (EB)
S_day: total new storage per day including renditions, in petabytes per day (PB/day); here 6 to 8
PB: petabytes; 1 PB = 10^15 bytes
EB: exabytes; 1 EB = 1,000 PB = 10^18 bytes
days: days in the year (365)
day: one day
≈: approximately equal to
In words: adding 6 to 8 petabytes a day for a year comes to about 2 to 3 exabytes, before any replication copies.
```

So the platform grows by **about 2–3 EB** a year, before replication. These are deliberately rough: real sources range from 5 Mbps phone clips to 50+ Mbps 4K. Clip duration does not itself reduce the assumed bytes per hour; source bitrate and format determine that.

## Key takeaways
- Convert incoming video hours into source bytes using the assumed bitrate.
- Model renditions and replication separately rather than treating a multiplier as measured.
- A dated upload figure is a planning example rather than current platform telemetry.

## Further reading
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Netflix Open Connect overview](https://openconnect.netflix.com/en/)
- [YouTube 2019 official historical statements](https://youtube.googleblog.com/2019/?hl=ms)
