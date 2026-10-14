---
id: cs2-video-streaming-codec-economics
title: Codec choices and encoding economics
level: intermediate
minutes: 3
summary: Compare extra encode cost with compatible watched-byte savings under explicit inputs.
sourceLesson: cs2-video-streaming
---

## Spending compute where views are

Assume a skewed popularity distribution for this design; measure the actual catalogue before allocating expensive encode work. A sensible policy:

- On upload, encode a fast H.264 ladder so the video is watchable within minutes.
- When a video crosses a view threshold, re-encode it in VP9/AV1. Potential bitrate savings and encoding cost depend on content, encoder settings and quality metrics; benchmark a representative corpus before choosing a migration threshold. Re-encode only when expected egress savings exceed compute, storage and operational costs for supported playback devices.

## An illustrative encoding break-even

Convert the delivered bytes saved per watched minute into an egress saving, then compare the extra encode cost. Suppose the alternative codec saves forty per cent of a hypothetical 2.5 Mbps stream and costs an extra $0.40 to encode. At a hypothetical $0.01 per GB:

```formula
S = (2.5 Mbps × 60 s) / 8
S = 0.01875 GB
v = 0.4 × 0.01875 GB/min × $0.01/GB
v = $0.000075/min
T = $0.40 / v ≈ 5,333 min
where
S: delivered bytes in one watched minute
v: egress dollars saved per watched minute
min: minutes
T: watched minutes needed to recover the added encode cost
Mbps: million bits per second
s: seconds
GB: a billion bytes
$: US dollars
8: bits per byte
≈: approximately equal after rounding
In words: About 5,333 compatible watched minutes recover forty cents under this restricted encode/egress model.
```

Only compatible views save these bytes; added storage, licence costs and operational work can change the result. These inputs are hypothetical rather than a measured AV1 saving.


## Choose the population being priced

The watch-minute denominator matters. A video may be popular while most of its viewers use clients that cannot receive the proposed codec. Count only compatible delivered minutes when applying the saving. If the product keeps both encodes, the new rendition adds storage rather than replacing all existing files.

A useful decision record separates measured inputs from business choices: the observed quality comparison and encoder runtime, the device mix, the expected future watch minutes, the actual egress price, and the extra storage or operational cost. The calculation above deliberately prices only its stated encode and egress terms. It is a scenario threshold to recompute when any input changes, rather than a universal rule that popular content should always be re-encoded.

## Key takeaways
- Measure codec savings on a representative corpus at the chosen quality target.
- Count views that can actually receive the codec, rather than all views.
- Compare total additional costs with repeatable egress savings before re-encoding.

## Further reading
- [Netflix Open Connect](https://openconnect.netflix.com/en/)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
