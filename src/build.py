#!/usr/bin/env python3
"""
Build the NUS talk deck.

Takes the source deck in src/, injects real scannable QR codes in place of
`<!--QR_*-->` tokens, and writes two outputs:

  dist/NUS_Act1.html   standalone file — open in a browser and present from it
  dist/act1-body.html  same content minus <!doctype>/<html>/<head>/<body>,
                       which is the form the Claude Artifact tool publishes

Usage:  python3 src/build.py
"""

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

FG = "#1F1915"   # --ink
BG = "#FDFAF4"   # --card


def build():
    src_path = os.path.join(ROOT, "src", "act1.html")
    with open(src_path, encoding="utf-8") as f:
        src = f.read()

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
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        + head + '</head>\n<body>\n<div id="viewport">' + rest + '\n</body>\n</html>\n'
    )
    standalone_path = os.path.join(dist, "NUS_Act1.html")
    with open(standalone_path, "w", encoding="utf-8") as f:
        f.write(standalone)

    print("  wrote %s (%d bytes)" % (os.path.relpath(body_path, ROOT), len(src)))
    print("  wrote %s (%d bytes)" % (os.path.relpath(standalone_path, ROOT), len(standalone)))


if __name__ == "__main__":
    print("building deck...")
    build()
    print("done.")
