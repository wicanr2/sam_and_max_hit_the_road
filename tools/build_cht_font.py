#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_cht_font.py — 依 cht_table.json 烘焙 chinese_gb16x12.fnt

用法：
    python3 build_cht_font.py -t cht_table.json [-f 字型.ttc] -o chinese_gb16x12.fnt
    python3 build_cht_font.py -t cht_table.json --dump 中   # 印出單字 ASCII 點陣預覽

設計要點：
- 用 PIL 從 wqy-microhei.ttc 以 12px 渲染每個字元，轉成 12×12 1bpp 點陣
- 點陣格式（對齊 ScummVM charset.cpp ZH_CHN 預期）：無 header、
  每 glyph 12 列 × 2 bytes = 24 bytes、MSB-first（bit x → 0x80 >> x）、
  每列第 2 個 byte 的低 4 bit 無效（補零）
- 依碼表 idx 寫進 idx * 24 位置；未用碼位保持 0
- 輸出固定 196,272 bytes（8178 glyphs × 24 bytes）
- 渲染以灰階繪製再以閾值二值化；--y-offset 可微調垂直位置
"""
import argparse
import json
import sys

from PIL import Image, ImageDraw, ImageFont

from cht_common import FONT_FILE_SIZE, NUM_GLYPHS

DEFAULT_TTC = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
GLYPH_SIZE = 12          # 預設 12×12；--size 16 走 hi-res（main 依 --size 覆寫）
BYTES_PER_GLYPH = 24     # = GLYPH_SIZE * ceil(GLYPH_SIZE/8)；main 依 --size 重算
THRESHOLD = 128          # 二值化閾值


def render_glyph_bitmap(font, ch, y_offset=0, x_offset=0):
    """渲染單字，回傳 12×12 的 0/1 二維列表"""
    img = Image.new('L', (GLYPH_SIZE, GLYPH_SIZE), 0)
    draw = ImageDraw.Draw(img)
    draw.text((x_offset, y_offset), ch, font=font, fill=255)
    px = img.load()
    return [[1 if px[x, y] >= THRESHOLD else 0 for x in range(GLYPH_SIZE)]
            for y in range(GLYPH_SIZE)]


def bitmap_to_bytes(bits):
    """12×12 0/1 點陣 → 24 bytes（MSB-first，每列 2 bytes）"""
    out = bytearray()
    row_bytes = (GLYPH_SIZE + 7) // 8   # 12→2, 16→2
    for row in bits:
        for byte_i in range(row_bytes):
            b = 0
            for bit in range(8):
                x = byte_i * 8 + bit
                if x < GLYPH_SIZE and row[x]:
                    b |= 0x80 >> bit
            out.append(b)
    return bytes(out)


def dump_ascii(bits):
    """把 12×12 點陣印成 ASCII art（預覽用）"""
    return '\n'.join(''.join('#' if v else '.' for v in row) for row in bits)


def main():
    ap = argparse.ArgumentParser(description='依 cht_table.json 烘焙 chinese_gb16x12.fnt')
    ap.add_argument('-t', '--table', required=True, help='cht_table.json 路徑')
    ap.add_argument('-f', '--font', default=DEFAULT_TTC, help='TTF/TTC 字型路徑')
    ap.add_argument('-o', '--output', help='輸出字型檔路徑')
    ap.add_argument('--y-offset', type=int, default=-1, help='繪字垂直位移（px，wqy-microhei 12px 以 -1 對位最佳）')
    ap.add_argument('--x-offset', type=int, default=0, help='繪字水平位移（px）')
    ap.add_argument('--dump', metavar='字元', help='只渲染單字並印出 ASCII 點陣預覽')
    ap.add_argument('--size', type=int, default=12, help='點陣邊長：12（原）或 16（hi-res）')
    args = ap.parse_args()

    global GLYPH_SIZE, BYTES_PER_GLYPH
    GLYPH_SIZE = args.size
    BYTES_PER_GLYPH = GLYPH_SIZE * ((GLYPH_SIZE + 7) // 8)   # 12→24, 16→32

    font = ImageFont.truetype(args.font, GLYPH_SIZE)

    if args.dump:
        bits = render_glyph_bitmap(font, args.dump, args.y_offset, args.x_offset)
        print(dump_ascii(bits))
        return 0

    if not args.output:
        ap.error('非 --dump 模式必須指定 -o 輸出檔')

    with open(args.table, 'r', encoding='utf-8') as f:
        table = json.load(f)

    buf = bytearray(NUM_GLYPHS * BYTES_PER_GLYPH)
    count = 0
    for ch, ent in table['chars'].items():
        idx = ent['idx']
        if not (0 <= idx < NUM_GLYPHS):
            raise SystemExit('錯誤：字元 %r 的 idx=%d 超出範圍 0–%d'
                             % (ch, idx, NUM_GLYPHS - 1))
        bits = render_glyph_bitmap(font, ch, args.y_offset, args.x_offset)
        buf[idx * BYTES_PER_GLYPH:(idx + 1) * BYTES_PER_GLYPH] = bitmap_to_bytes(bits)
        count += 1

    with open(args.output, 'wb') as f:
        f.write(buf)
    print('字型烘焙完成：%d 字 → %s（%d bytes）' % (count, args.output, len(buf)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
