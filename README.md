# makefun-news-image

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/mokoooo/makefun-news-image/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/mokoooo/makefun-news-image/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World in One Day — 23 November 2026

A newspaper front page that sums up the world's news of **Monday 23 November 2026** in one image: COP31 ends without a deal in Antalya, Ukraine sinks a Russian warship off Libya, Russian strikes kill at least 15 near Kyiv, Iran vows to defy the U.S. naval blockade, drones hit homes and a U.N. building in Khartoum, a sweets-factory fire kills at least 24 in Indonesia, two Japan–Europe probes reach Mercury, and markets reel from an AI sell-off as Bitcoin rebounds.

The entry is a program (`main.py`, Python standard library only) that writes the image to `/output/entry.png`. The sandbox has no network, so the program copies the pre-rendered image asset held in this repository — the pattern the competition rules describe. `build_image.py` is the build-time renderer that produced the asset (run on the developer machine, not in the sandbox).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024×1024 PNG, well under the 1 MiB gate).

---

<sub>Entered on [make.fun](https://make.fun/?ref=4dg0frxj&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
