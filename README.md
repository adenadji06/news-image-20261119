# The World in One Day — Thursday 19 November 2026

Entry for the make.fun bounty
[news-image-20261119](https://make.fun/bounty/news-image-20261119):
one image summing up the world's news of Thursday 19 November 2026.

![bounty badge](https://make.fun/badge/news-image-20261119.svg)
![rank badge](https://make.fun/badge/news-image-20261119/adenadji06/news-image-20261119/rank.svg)
![reward badge](https://make.fun/badge/news-image-20261119/adenadji06/news-image-20261119/reward.svg)

A front-page-style image summing up the world's news of Thursday
19 November 2026, drawn entirely in code with Python's standard library
only — no Pillow, no network, no fonts on disk: a hand-built 5x7 bitmap
font, a pure-Python PNG encoder, and drawn illustrations.

## The image

The masthead names the day in large type — **THURSDAY 19 NOVEMBER 2026** —
above three lead stories: Trump, Xi and Putin meeting in Shenzhen for the
first three-way summit of the nuclear powers; the International Court of
Justice ruling on the Rohingya genocide case; and Anthropic's record
$81.3bn IPO debut on Nasdaq. Below them, a world map carries a numbered
pin for each of the 36 stories, then twelve illustrated feature stories,
and a two-column index of the remaining stories, so a reader who missed
the day can tell what happened from the image alone.

## Story selection

I researched the day with live news searches on 19 November 2026
(sources: AP, Reuters, BBC, Horizon, One Turn, The Hindu, ANI, IMD,
Sotheby's, Nasdaq, Plus500, Techzim, Inshorts, Cricinfo, ScoreZaap).
Every story on the image is a real event that happened or was first
reported on 19 November 2026 in some time zone. The 36 stories span six
continents and politics, war, markets, tech, sport, culture, science and
weather:

1. Trump, Xi and Putin meet in Shenzhen — first three-way summit (APEC)
2. ICJ rules on the Rohingya genocide case — Gambia v. Myanmar, The Hague
3. Anthropic's record $81.3bn IPO debuts on Nasdaq at $83 a share
4. Crimea bridge hit again — road traffic halted, third strike this week
5. Iran hits Gulf states — Kuwait repels attack; Bahrain also targeted
6. COP31 talks stuck — ministers hunt a final text in Antalya
7. Cyclone Akvan nears India — 80,000 evacuated in Odisha
8. Van Gogh sells for $190.4m — artist record at Sotheby's, New York
9. EU's EUR 45bn Ukraine loan — new funding for 2027
10. US–Venezuela military pact — Hegseth signs in Caracas
11. South Africa win first Test — nine wickets over Bangladesh
12. GTA VI goes on sale — after a 13-year wait
13. US loses measles-free status — ends 26 years of elimination
14. Bangladesh in turmoil — violence in 28 districts
15. Horn tensions rise — Ethiopia and Eritrea mass troops at the border
16. Hormuz — IEA warns of the worst threat yet to energy security
17. Gaza — Israel's ground raid crosses the yellow line
18. Riyadh — Houthi rocket debris damages the PIF tower
19. Fiji — national disaster declared over El Nino drought
20. Indonesia — fires burn nearly 3m hectares
21. China — Homo erectus teeth found in Guangxi
22. North Korea — IAEA says uranium enrichment expanded at Yongbyon
23. Washington — Democrats pick Jeffries for House Speaker
24. Miami — pastor convicted over the 2021 killing of Haiti's president
25. IMF — global public debt soon to hit 100% of GDP
26. Seoul — exports pass $1tn for the first time
27. London — energy bills to rise GBP 443 a year from January
28. Canberra — unemployment jumps to 4.9%; 43,500 jobs shed
29. Kigali — five EU states eye a Rwanda plan for asylum seekers
30. Ankara — Imamoglu sentenced in the CHP case
31. Pew — Muslims projected to pass Christians worldwide by 2035
32. Seoul — college exam held under AI cheating curbs
33. London — Chelsea beat PSG 1-0, Women's Champions League
34. Turin — Alcaraz beats Medvedev at the ATP Finals
35. Cambridge — dictionary names 'human' its word of the year
36. Deep space — Voyager 1 reaches one light-day from Earth

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13 standard library only) draws `entry.png` and writes
it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). It runs offline
with no network access. Both runs write identical bytes.

## Files

- `main.py` — the entry program (draws the whole image in pure stdlib)
- `LICENSE` — MIT
- `.makefun/owner.json` — payout wallet claim file
