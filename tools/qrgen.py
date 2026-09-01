"""Minimal QR encoder: byte mode, ECC level M, versions 1-10. Emits a compact SVG."""

# ---- GF(256) ----
EXP = [0] * 512
LOG = [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def gmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def rs_generator(n):
    g = [1]
    for i in range(n):
        g2 = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            g2[j] ^= gmul(c, 1)
            g2[j + 1] ^= gmul(c, EXP[i])
        g = g2
    return g


def rs_ecc(data, n):
    g = rs_generator(n)
    res = list(data) + [0] * n
    for i in range(len(data)):
        f = res[i]
        if f:
            for j, c in enumerate(g):
                res[i + j] ^= gmul(c, f)
    return res[len(data):]


# ---- version tables, ECC level M ----
DATA_CW = {1: 16, 2: 28, 3: 44, 4: 64, 5: 86, 6: 108, 7: 124, 8: 154, 9: 182, 10: 216}
TOTAL_CW = {1: 26, 2: 44, 3: 70, 4: 100, 5: 134, 6: 172, 7: 196, 8: 242, 9: 292, 10: 346}
ECC_PER_BLOCK = {1: 10, 2: 16, 3: 26, 4: 18, 5: 24, 6: 16, 7: 18, 8: 22, 9: 22, 10: 26}
# (count, data codewords) groups
GROUPS = {
    1: [(1, 19)], 2: [(1, 34)], 3: [(1, 55)], 4: [(2, 32)], 5: [(2, 43)],
    6: [(4, 27)], 7: [(4, 31)], 8: [(2, 38), (2, 39)],
    9: [(3, 36), (2, 37)], 10: [(4, 43), (1, 44)],
}
ALIGN = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34],
    7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50],
}
VERSION_INFO = {
    7: 0x07C94, 8: 0x085BC, 9: 0x09A99, 10: 0x0A4D3,
}


def pick_version(nbytes):
    for v in range(1, 11):
        count_bits = 8 if v <= 9 else 16
        need = 4 + count_bits + 8 * nbytes
        if need <= DATA_CW[v] * 8:
            return v
    raise ValueError("payload too long for this encoder")


def encode_data(text, version):
    data = text.encode("utf-8")
    count_bits = 8 if version <= 9 else 16
    bits = []

    def put(val, n):
        for i in range(n - 1, -1, -1):
            bits.append((val >> i) & 1)

    put(0b0100, 4)
    put(len(data), count_bits)
    for b in data:
        put(b, 8)

    cap = DATA_CW[version] * 8
    put(0, min(4, cap - len(bits)))            # terminator
    while len(bits) % 8:
        bits.append(0)
    cw = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    i = 0
    while len(cw) < DATA_CW[version]:
        cw.append(pad[i % 2])
        i += 1
    return cw


def interleave(cw, version):
    blocks, ecc_blocks = [], []
    n = ECC_PER_BLOCK[version]
    pos = 0
    for count, dlen in GROUPS[version]:
        for _ in range(count):
            b = cw[pos:pos + dlen]
            pos += dlen
            blocks.append(b)
            ecc_blocks.append(rs_ecc(b, n))
    out = []
    for i in range(max(len(b) for b in blocks)):
        for b in blocks:
            if i < len(b):
                out.append(b[i])
    for i in range(n):
        for e in ecc_blocks:
            out.append(e[i])
    return out


def build_matrix(version, codewords):
    size = version * 4 + 17
    m = [[None] * size for _ in range(size)]

    def finder(r, c):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                rr, cc = r + dr, c + dc
                if 0 <= rr < size and 0 <= cc < size:
                    if not (0 <= dr <= 6 and 0 <= dc <= 6):
                        m[rr][cc] = 0          # separator
                        continue
                    inring = dr in (0, 6) or dc in (0, 6)
                    core = 2 <= dr <= 4 and 2 <= dc <= 4
                    m[rr][cc] = 1 if (inring or core) else 0

    finder(0, 0)
    finder(0, size - 7)
    finder(size - 7, 0)

    for i in range(8, size - 8):
        v = 1 if i % 2 == 0 else 0
        m[6][i] = v
        m[i][6] = v

    centres = ALIGN[version]
    for r in centres:
        for c in centres:
            if (r < 9 and c < 9) or (r < 9 and c > size - 10) or (r > size - 10 and c < 9):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    ring = dr in (-2, 2) or dc in (-2, 2)
                    m[r + dr][c + dc] = 1 if (ring or (dr == 0 and dc == 0)) else 0

    m[size - 8][8] = 1  # dark module

    # reserve format areas
    for i in range(9):
        if m[8][i] is None:
            m[8][i] = 0
        if m[i][8] is None:
            m[i][8] = 0
    for i in range(8):
        if m[8][size - 1 - i] is None:
            m[8][size - 1 - i] = 0
        if m[size - 1 - i][8] is None:
            m[size - 1 - i][8] = 0

    reserved = [[m[r][c] is not None for c in range(size)] for r in range(size)]

    if version >= 7:
        vi = VERSION_INFO[version]
        for i in range(18):
            bit = (vi >> i) & 1
            r, c = i // 3, size - 11 + i % 3
            m[r][c] = bit
            reserved[r][c] = True
            m[c][r] = bit
            reserved[c][r] = True

    # data placement
    bits = []
    for cwv in codewords:
        for i in range(7, -1, -1):
            bits.append((cwv >> i) & 1)
    idx = 0
    col = size - 1
    upward = True
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for r in rows:
            for c in (col, col - 1):
                if not reserved[r][c]:
                    m[r][c] = bits[idx] if idx < len(bits) else 0
                    idx += 1
        upward = not upward
        col -= 2
    return m, reserved, size


def mask_fn(k, r, c):
    if k == 0: return (r + c) % 2 == 0
    if k == 1: return r % 2 == 0
    if k == 2: return c % 3 == 0
    if k == 3: return (r + c) % 3 == 0
    if k == 4: return (r // 2 + c // 3) % 2 == 0
    if k == 5: return (r * c) % 2 + (r * c) % 3 == 0
    if k == 6: return ((r * c) % 2 + (r * c) % 3) % 2 == 0
    return ((r + c) % 2 + (r * c) % 3) % 2 == 0


def format_bits(mask):
    data = (0b00 << 3) | mask          # ECC level M = 00
    v = data << 10
    g = 0b10100110111
    for i in range(4, -1, -1):
        if v & (1 << (i + 10)):
            v ^= g << i
    return ((data << 10) | v) ^ 0b101010000010010


def apply_format(m, size, mask):
    f = format_bits(mask)
    for i in range(15):
        bit = (f >> i) & 1
        # copy 1: column 8 going down, then row 8 going left
        if i < 6:
            m[i][8] = bit
        elif i == 6:
            m[7][8] = bit
        elif i == 7:
            m[8][8] = bit
        elif i == 8:
            m[8][7] = bit
        else:
            m[8][14 - i] = bit
        # copy 2: row 8 from the right edge, then column 8 up from the bottom
        if i < 8:
            m[8][size - 1 - i] = bit
        else:
            m[size - 15 + i][8] = bit
    m[size - 8][8] = 1  # dark module, always last


def penalty(m, size):
    score = 0
    for line in list(m) + [list(col) for col in zip(*m)]:
        run, prev = 0, None
        for v in line:
            if v == prev:
                run += 1
            else:
                if run >= 5:
                    score += 3 + (run - 5)
                run, prev = 1, v
        if run >= 5:
            score += 3 + (run - 5)
    for r in range(size - 1):
        for c in range(size - 1):
            s = m[r][c] + m[r][c + 1] + m[r + 1][c] + m[r + 1][c + 1]
            if s in (0, 4):
                score += 3
    pat = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    for line in list(m) + [list(col) for col in zip(*m)]:
        for i in range(size - 10):
            if line[i:i + 11] == pat or line[i:i + 11] == pat[::-1]:
                score += 40
    dark = sum(sum(r) for r in m)
    score += 10 * (abs(dark * 100 // (size * size) - 50) // 5)
    return score


def make(text):
    v = pick_version(len(text.encode()))
    cw = interleave(encode_data(text, v), v)
    base, reserved, size = build_matrix(v, cw)
    best, best_score = None, None
    for k in range(8):
        m = [row[:] for row in base]
        for r in range(size):
            for c in range(size):
                if not reserved[r][c] and mask_fn(k, r, c):
                    m[r][c] ^= 1
        apply_format(m, size, k)
        s = penalty(m, size)
        if best_score is None or s < best_score:
            best, best_score, bk = [row[:] for row in m], s, k
    return best, size, v, bk


def to_svg(m, size, fg="#1F1915", bg="#FDFAF4", quiet=2):
    n = size + quiet * 2
    d = []
    for y, row in enumerate(m):
        c = 0
        while c < size:
            if row[c]:
                c0 = c
                while c < size and row[c]:
                    c += 1
                d.append("M%d %dh%dv1h-%dz" % (c0 + quiet, y + quiet, c - c0, c - c0))
            else:
                c += 1
    return ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
            'shape-rendering="crispEdges" role="img">'
            '<rect width="%d" height="%d" fill="%s"/><path d="%s" fill="%s"/></svg>'
            % (n, n, n, n, bg, "".join(d), fg))


if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    m, size, v, k = make(url)
    svg = to_svg(m, size)
    sys.stderr.write("version=%d size=%d mask=%d svgbytes=%d\n" % (v, size, k, len(svg)))
    sys.stdout.write(svg)
