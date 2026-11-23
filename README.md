[![news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Tiiashtf/makefun-news-image-20261123/rank.svg)](https://make.fun/c/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Tiiashtf/makefun-news-image-20261123/reward.svg)](https://make.fun/c/news-image-20261123)

# COP31 Collapses — The World in One Image, 23 November 2026

A newspaper front page summing up the world news of **Monday 23 November
2026**, drawn entirely in code: a 5x7 bitmap font, vector pictograms and a
front-page layout, rendered by a pure-stdlib Python program to a single
1024x1024 PNG.

## The image

- **Main story — COP31 COLLAPSES.** After two weeks of talks in Antalya,
  Turkiye, the UN climate summit ends with no deal: the EU and allied
  nations reject the "Antalya Pact" because its final text makes no mention
  of fossil fuels. The longest COP in history, and the first summit failure
  since Copenhagen 2009.
- **GULF WAR WIDENS.** Iran hits U.S. bases in Bahrain; tankers are struck
  in the Strait of Hormuz as the Gulf conflict escalates.
- **DEMOCRATS WIN 258 SEATS.** The biggest U.S. House majority since 1992,
  258 to 173, after the North Carolina call.
- **FACTORY FIRE IN INDONESIA.** Dozens of workers missing after a blaze at
  a candy plant; at least three dead.
- **NEPAL PM MEETS MODI.** Balendra Shah in Delhi for talks on trade and ties.
- **In brief:** the U.N. keeps talking on lethal AI weapons; South Korea's
  education minister quits over an AI exam-cheating scandal; Anthropic makes
  a record Nasdaq debut; "Sunrise on the Reaping" tops the box office with
  $120M; a Russian ship is still burning off Finland; 14 missing after a
  drone hit near Kyiv.

Every story was verified against reporting published on 23 November 2026.

## How it runs

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is Python 3.13, standard library only, no network. It draws the
page and writes `/output/entry.png` (1024x1024 PNG, under 1 MiB). It runs
twice and writes the same bytes both times; it clears only the contents of
the output directory, never the directory itself.

## Entry

Built for the make.fun competition
[news-image-20261123](https://make.fun/c/news-image-20261123) — "Sum up
23 November's world news in one image".
