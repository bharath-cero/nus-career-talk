# NUS Career Accelerator talk — Bharath Krishnamachari

A 45-minute talk to ~160 MSc and PhD students at the NUS Faculty of Science.
Self-contained HTML deck, presented from a browser.

The full 18-slide talk is built, including audience interaction, the career
trail, the food-delivery and data craft sections, closing advice, and Q&A.

**Public deck:** <https://bharath-cero.github.io/nus-career-talk/>

---

## Run it

```bash
python3 src/build.py          # no dependencies, stdlib only
open dist/NUS_Act1.html       # or just double-click it
```

The build also writes `index.html`, which is the GitHub Pages entry point. The
built deck is one file with no external assets except Google Fonts. The
editable source page loads its vendored logos from `assets/logos/`; the build
embeds those same files as data URIs. It degrades to system fonts if the venue
wifi is down.

## Presenting

| key | does |
| --- | --- |
| `→` `space` | **next beat** — advances one reveal, then moves to the next slide |
| `←` | back one beat |
| `↓` `↑` | skip a whole slide |
| `O` | grid of all slides, click to jump; header shows the running time budget |
| `N` | speaker notes |
| `T` | start/pause timer |
| `F` | fullscreen |
| click | right 75% = next, left 25% = back |

Beats matter: slides with staged content gate `→` through their reveals before
advancing. Slides intended to remain static have no reveal steps.

## Layout

```
src/act1.html      the deck — content, styles and engine in one file
src/build.py       injects QR codes, emits both dist/ variants
index.html         generated standalone deck served by GitHub Pages
tools/qrgen.py     QR encoder (byte mode, ECC M, versions 1–10)
assets/logos/      vendored official brand marks, embedded by the build
dist/              build output, committed so the deck is presentable from a clone
docs/              where the content came from, and the design tokens
```

## How the deck is structured

Slides live in a `S.push({...})` array near the top of the `<script>`. Each entry:

```js
S.push({
  act:   "Act I",              // eyebrow, top left
  wp:    "The trail",          // eyebrow, after the bullet
  title: "The trail",          // grid label + notes header
  min:   4,                    // minutes; the grid header sums these
  html:  '...',                // slide markup
  notes: "..."                 // speaker notes, N to toggle
});
```

Reveals are opt-in per element: add `data-step="1"`, `data-step="2"` and so on.
The engine counts the highest `data-step` on the current slide and gates `→`
through them before advancing. Elements without `data-step` are always visible.

## The QR codes are real

There was no QR library available and no package network, so `tools/qrgen.py` is
a from-scratch encoder. It was verified by rendering its output to a canvas and
decoding it with the browser's `BarcodeDetector` — versions 1, 2, 4, 5 and 7 all
round-trip correctly, including the multi-block Reed–Solomon cases and the
version-information bits that only appear from v7 up.

**If you change the QR encoder, re-run that check.** Two bugs got through
structural review and were only caught by decoding: dark modules written into the
finder separator ring, and both copies of the format-information bits placed
transposed. A QR code that looks plausible is not a QR code that scans.

## Conventions

- No build step beyond `build.py`, no npm, no framework. It has to still work
  from a USB stick in a lecture theatre.
- Inline everything. No external images — the Artifact CSP blocks non-font hosts.
- Every slide must fit the 1280×720 stage at **every** beat. Check it; two slides
  silently overflowed during development. See HANDOFF.md for the check script.
- Colours come from the token block at the top of `act1.html`. Don't hardcode hex
  in slide markup except for brand wordmarks.
