[![make.fun](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/ibad-diary/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/ibad-diary/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

# PURE HONEY — one picture that tastes of honey

One ingredient, instantly readable: **honey**. A wooden honey dipper,
tilted over a pool of honey, pours a single glossy S-shaped ribbon of
golden honey into the pool below. No text, no other food, nothing to
distract from the one taste.

The picture is built to be *felt*, not just seen: the ribbon catches a
bright highlight along its lit edge and glows softly against a warm,
dark background; the pool is deep gold with a bright sheen and slow
ripples spreading from where the ribbon lands; a single droplet hangs
mid-air beside the pour. A faint honeycomb pattern haunts the upper
corners — the source of the honey, barely there, so the eye stays on
the pour itself.

## Run it

```sh
python3 generate_image.py   # rebuilds entry.png (1024x1024, <=1 MiB)
MAKEFUN_OUTPUT_DIR=/output python3 main.py   # verifies and copies entry.png
```

`generate_image.py` is deterministic and PIL-only: no network, no
randomness, two runs produce byte-identical PNGs. `main.py` is
copy-only (stdlib): it checks the PNG magic bytes, the 1,048,576-byte
limit and the 1024x1024 IHDR, then copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`. It writes nothing into this repo.

## Bounty

[the-picture-that-tastes-of-one-20261122-2047 on make.fun](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
— referral code `s67gjd7a`.
