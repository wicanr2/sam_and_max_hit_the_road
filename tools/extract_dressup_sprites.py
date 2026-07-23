#!/usr/bin/env python3
# 抽取 Sam & Max（SCUMM v6）room 71 換裝娃娃 sprite。
# 忠實移植 ScummVM gfx.cpp 的 SMAP 解碼（drawStripBasicV / MajMinCodec），非猜測。
# 用法: python3 extract_dressup_sprites.py <SAMNMAX.001> <out_dir>
import sys, struct, json, os
from PIL import Image

XOR = 0x69

def load(path):
    return bytes(b ^ XOR for b in open(path, "rb").read())

def be32(d, o): return struct.unpack(">I", d[o:o+4])[0]
def le16(d, o): return struct.unpack("<H", d[o:o+2])[0]
def le32(d, o): return struct.unpack("<I", d[o:o+4])[0]
def tag(d, o): return d[o:o+4].decode("latin1", "replace")

def children(d, off, end):
    out = []; o = off
    while o < end - 8:
        t = tag(d, o); sz = be32(d, o+4)
        if sz < 8 or o+sz > end or not all(32 <= c < 127 for c in d[o:o+4]):
            break
        out.append((t, o, sz)); o += sz
    return out

def find_all(d, off, end, want, acc):
    for t, o, sz in children(d, off, end):
        if t == want:
            acc.append((o, sz))
        if t in ("LECF", "LFLF", "ROOM", "RMIM", "OBIM", "PALS", "WRAP"):
            find_all(d, o+8, o+sz, want, acc)
    return acc

# ---- SMAP 解碼 ----
class MajMin:
    """移植自 ScummVM MajMinCodec（gfx.cpp:5010）"""
    def __init__(self, shift, d, p):
        self.repeat = False; self.nb = 16; self.shift = shift
        self.color = d[p]; self.bits = d[p+1] | (d[p+2] << 8)
        self.ptr = p+3; self.d = d; self.cnt = 0
    def readBits(self, n):
        if self.nb <= 8:
            self.bits |= self.d[self.ptr] << self.nb; self.ptr += 1; self.nb += 8
        v = self.bits & ((1 << n) - 1)
        self.nb -= n; self.bits >>= n
        return v
    def decodeLine(self, count):
        out = []
        for _ in range(count):
            out.append(self.color)
            if not self.repeat:
                if self.readBits(1):
                    if self.readBits(1):
                        diff = self.readBits(3) - 4
                        if diff:
                            self.color = (self.color + diff) & 0xFF
                        else:
                            self.repeat = True
                            self.cnt = self.readBits(8) - 1
                    else:
                        self.color = self.readBits(self.shift)
            else:
                self.cnt -= 1
                if self.cnt == 0:
                    self.repeat = False
        return out

def decode_basicV(d, p, w, h, shr, mask):
    """drawStripBasicV（gfx.cpp:4154）：8 寬、逐欄由上而下。回傳 [h][w] index。"""
    buf = [[0]*w for _ in range(h)]
    color = d[p]; bits = d[p+1]; ptr = p+2; cl = 8
    inc = -1
    for x in range(8):
        for row in range(h):
            buf[row][x] = color
            # READ_BIT logic
            if cl <= 8:
                bits |= d[ptr] << cl; ptr += 1; cl += 8
            b0 = bits & 1; bits >>= 1; cl -= 1
            if not b0:
                pass
            else:
                b1 = bits & 1; bits >>= 1; cl -= 1
                if not b1:
                    if cl <= 8:
                        bits |= d[ptr] << cl; ptr += 1; cl += 8
                    color = bits & mask; bits >>= shr; cl -= shr; inc = -1
                else:
                    b2 = bits & 1; bits >>= 1; cl -= 1
                    if not b2:
                        color = (color + inc) & 0xFF
                    else:
                        inc = -inc; color = (color + inc) & 0xFF
    return buf

def decode_complex(d, p, w, h, shr):
    """drawStripComplex（gfx.cpp:4101）：逐列 8 px。回傳 [h][w] index。"""
    buf = [[0]*w for _ in range(h)]
    mm = MajMin(shr, d, p)
    for row in range(h):
        line = mm.decodeLine(8)
        for i in range(8):
            buf[row][i] = line[i]
    return buf

def decode_strip(d, p, h):
    code = d[p]; shr = code % 10; mask = 0xFF >> (8 - shr) if shr else 0
    src = p + 1
    if 34 <= code <= 38 or 14 <= code <= 18:      # ZIGZAG_V / VT
        return decode_basicV(d, src, 8, h, shr, mask)
    if 84 <= code <= 88 or 124 <= code <= 128 or 64 <= code <= 68 or 104 <= code <= 108:
        return decode_complex(d, src, 8, h, shr)   # MAJMIN / RMAJMIN (H/HT)
    if code == 1:                                  # RAW256
        buf = [[0]*8 for _ in range(h)]
        for row in range(h):
            for i in range(8):
                buf[row][i] = d[src]; src += 1
        return buf
    raise ValueError(f"unhandled strip code {code} at {p}")

def decode_smap(d, smap_off, w, h):
    """smap_off 指向 'SMAP' tag。回傳 [h][w] index buffer。"""
    ns = w // 8
    full = [[0]*w for _ in range(h)]
    for s in range(ns):
        off = le32(d, smap_off + 8 + s*4)
        strip = decode_strip(d, smap_off + off, h)
        for row in range(h):
            for x in range(8):
                full[row][s*8 + x] = strip[row][x]
    return full

def parse_imhd(d, o):
    b = o + 8
    return dict(objid=le16(d, b), numimg=le16(d, b+2), numzp=le16(d, b+4),
                x=le16(d, b+8), y=le16(d, b+10), w=le16(d, b+12), h=le16(d, b+14))

def zone_of(oid):
    """依 room 71 物件編號分區（見 docs/copy-protection-answers.md）。"""
    if 715 <= oid <= 724 or 745 <= oid <= 752: return "body"
    if 725 <= oid <= 735 or 753 <= oid <= 762: return "acc"
    if 736 <= oid <= 744 or 763 <= oid <= 770: return "head"
    return None

def doll_of(oid):
    if 715 <= oid <= 744: return "sam"
    if 745 <= oid <= 770: return "max"
    return None

def find_room_with(d, obj):
    def rec(off, end):
        for t, o, sz in children(d, off, end):
            if t in ("LECF", "LFLF"):
                r = rec(o+8, o+sz)
                if r: return r
            if t == "ROOM":
                for ct, co, csz in children(d, o+8, o+sz):
                    if ct == "OBIM" and tag(d, co+8) == "IMHD" and le16(d, co+8+8) == obj:
                        return o, sz
        return None
    return rec(0, len(d))

def decode_obim(d, o, sz):
    hd = parse_imhd(d, o+8)
    w, h = hd["w"], hd["h"]
    if w == 0 or h == 0: return None
    im = next((c for c in children(d, o+8, o+sz) if c[0].startswith("IM") and c[0] != "IMHD"), None)
    if not im: return None
    smap = next((c for c in children(d, im[1]+8, im[1]+im[2]) if c[0] == "SMAP"), None)
    if not smap: return None
    return hd, decode_smap(d, smap[1], w, h)

def to_rgba(idx, palette, trans):
    h = len(idx); w = len(idx[0])
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); px = img.load()
    for row in range(h):
        for x in range(w):
            c = idx[row][x]
            px[x, row] = (0, 0, 0, 0) if c == trans else (*palette[c], 255)
    return img

def main():
    src = sys.argv[1]; outdir = sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    d = load(src)
    TRANS = 5

    ro, rsz = find_room_with(d, 715)
    # room 級調色盤（room 71 內唯一彩色 APAL）
    apals = find_all(d, 0, len(d), "APAL", [])
    inr = [a for a in apals if ro < a[0] < ro+rsz]
    pal = list(d[inr[0][0]+8: inr[0][0]+8+768])
    palette = [(pal[i*3], pal[i*3+1], pal[i*3+2]) for i in range(256)]

    # room 背景（含兩個裸娃娃 + 橘色爆炸框）→ stage_bg.png
    rmw = rmh = None
    for t, o, sz in children(d, ro+8, ro+rsz):
        if t == "RMHD": rmw, rmh = le16(d, o+8), le16(d, o+10)
        if t == "RMIM":
            im00 = next(c for c in children(d, o+8, o+sz) if c[0] == "IM00")
            smap = next(c for c in children(d, im00[1]+8, im00[1]+im00[2]) if c[0] == "SMAP")
            idx = decode_smap(d, smap[1], rmw, rmh)
            bg = Image.new("RGB", (rmw, rmh)); bpx = bg.load()
            for row in range(rmh):
                for x in range(rmw):
                    bpx[x, row] = palette[idx[row][x]]
            bg.save(os.path.join(outdir, "stage_bg.png"))
    print(f"stage_bg {rmw}x{rmh}")

    # 換裝物件 715-771（含紅色大按鈕 771）
    obims = {le16(d, o+8+8): (o, sz) for o, sz in find_all(d, 0, len(d), "OBIM", [])
             if tag(d, o+8) == "IMHD"}
    manifest = {"stage": {"w": rmw, "h": rmh, "bg": "stage_bg.png"}, "trans_index": TRANS,
                "objects": []}
    for oid in range(715, 772):
        if oid not in obims: continue
        o, sz = obims[oid]
        res = decode_obim(d, o, sz)
        if not res: continue
        hd, idx = res
        img = to_rgba(idx, palette, TRANS)
        fn = f"obj_{oid}.png"
        img.save(os.path.join(outdir, fn))
        manifest["objects"].append(dict(id=oid, x=hd["x"], y=hd["y"], w=hd["w"], h=hd["h"],
                                        doll=doll_of(oid), zone=zone_of(oid), file=fn))
        print(f"  #{oid}: {hd['w']}x{hd['h']} @({hd['x']},{hd['y']}) {doll_of(oid)}/{zone_of(oid)}")
    json.dump(manifest, open(os.path.join(outdir, "manifest.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"done: {len(manifest['objects'])} sprites + bg -> {outdir}")

if __name__ == "__main__":
    main()
