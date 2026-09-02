#!/usr/bin/env python3
"""
Build the NUS talk deck.

Takes the source deck in src/, injects real scannable QR codes in place of
`<!--QR_*-->` tokens, and writes two outputs:

  index.html            standalone file served by GitHub Pages
  dist/NUS_Act1.html    same standalone file for local presenting
  dist/act1-body.html   same content minus <!doctype>/<html>/<head>/<body>,
                        which is the form the Claude Artifact tool publishes

Usage:  python3 src/build.py
"""

import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import qrgen  # noqa: E402

# ---------------------------------------------------------------------------
# QR targets. Add a token here and the matching <!--QR_NAME--> in the source.
# Keep URLs as short as you can: fewer characters means fewer modules, which
# means the code scans from further back in the lecture hall.
#   66 chars -> version 5, 37 modules   (current)
#  103 chars -> version 7, 45 modules   (the /videos/ URL — avoid)
# ---------------------------------------------------------------------------
QR_TARGETS = {
    "QR_LENNY": "https://www.lennysnewsletter.com/p/building-a-meaningful-career-jason",
    # "QR_SLIDO": "https://app.sli.do/event/XXXXXXXX",   # <- add when available
}

# Vendored assets are embedded so the built deck stays fully self-contained and
# works without venue wifi. The source URLs and provenance live in
# docs/content-sources.md.
EMBED_ASSETS = {
    "../assets/logos/ubs.svg": "assets/logos/ubs.svg",
    "../assets/logos/groupon.svg": "assets/logos/groupon.svg",
    "../assets/logos/glu-mobile.svg": "assets/logos/glu-mobile.svg",
    "../assets/logos/ea.svg": "assets/logos/ea.svg",
    "../assets/logos/deloitte.svg": "assets/logos/deloitte.svg",
    "../assets/logos/delivery-hero.svg": "assets/logos/delivery-hero.svg",
    "../assets/QR Code for NUS FoS Career Talk.png": "assets/QR Code for NUS FoS Career Talk.png",
}

FG = "#1F1915"   # --ink
BG = "#FDFAF4"   # --card


def build():
    src_path = os.path.join(ROOT, "src", "act1.html")
    with open(src_path, encoding="utf-8") as f:
        src = f.read()

    for source_ref, filename in EMBED_ASSETS.items():
        if source_ref not in src:
            print("  ! asset reference %s is not used in the source — skipped" % source_ref)
            continue
        asset_path = os.path.join(ROOT, filename)
        with open(asset_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        mime = "image/png" if filename.lower().endswith(".png") else "image/svg+xml"
        src = src.replace(source_ref, "data:%s;base64," % mime + encoded)
        print("  embedded %s" % os.path.relpath(asset_path, ROOT))

    for token, url in QR_TARGETS.items():
        marker = "<!--%s-->" % token
        if marker not in src:
            print("  ! token %s has no marker in the source — skipped" % token)
            continue
        matrix, size, version, mask = qrgen.make(url)
        svg = qrgen.to_svg(matrix, size, fg=FG, bg=BG)
        src = src.replace(marker, svg)
        print("  %s -> v%d, %d modules, mask %d (%s)" % (token, version, size, mask, url))

    remaining = [t for t in ("QR_SLIDO",) if ("<!--%s-->" % t) in src]
    if remaining:
        print("  ! still unfilled: %s (placeholder box will show instead)" % ", ".join(remaining))

    dist = os.path.join(ROOT, "dist")
    os.makedirs(dist, exist_ok=True)

    body_path = os.path.join(dist, "act1-body.html")
    with open(body_path, "w", encoding="utf-8") as f:
        f.write(src)

    head, rest = src.split('<div id="viewport">', 1)
    standalone = (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        + head + '</head>\n<body>\n<div id="viewport">' + rest + '\n</body>\n</html>\n'
    )
    standalone_path = os.path.join(dist, "NUS_Act1.html")
    with open(standalone_path, "w", encoding="utf-8") as f:
        f.write(standalone)

    pages_path = os.path.join(ROOT, "index.html")
    with open(pages_path, "w", encoding="utf-8") as f:
        f.write(standalone)

    print("  wrote %s (%d bytes)" % (os.path.relpath(body_path, ROOT), len(src)))
    print("  wrote %s (%d bytes)" % (os.path.relpath(standalone_path, ROOT), len(standalone)))
    print("  wrote %s (%d bytes)" % (os.path.relpath(pages_path, ROOT), len(standalone)))


if __name__ == "__main__":
    print("building deck...")
    build()
    print("done.")
