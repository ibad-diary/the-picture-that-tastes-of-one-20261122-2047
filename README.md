[![make.fun](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/ibad-diary/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/ibad-diary/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

# PURE HONEY — The picture that tastes of one ingredient

One ingredient, unmistakable at a glance: **golden honey**. A wooden honey
dipper pours a single glossy S-shaped ribbon of honey into a still pool of
honey, on a dark warm background with a faint honeycomb. No other food, no
text, nothing to distract from the one taste the picture is built on — you
can almost feel the slow pour.

## Run it

```sh
python3 generate_image.py   # rebuilds entry.png (1024x1024, <=1 MiB)
MAKEFUN_OUTPUT_DIR=/output python3 main.py   # verifies and copies entry.png
```

`generate_image.py` draws the picture with Pillow only — no network, no
randomness, two runs are byte-identical. `main.py` is copy-only (stdlib):
it checks the PNG magic bytes, the 1,048,576-byte limit and the 1024x1024
IHDR, then copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`. It writes
nothing into this repo.

## Bounty

[the-picture-that-tastes-of-one-20261122-2047 on make.fun](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
