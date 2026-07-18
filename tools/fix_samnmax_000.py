#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
fix_samnmax_000.py — 修補 scummtr 回填後 SAMNMAX.000 的 DSCR 去重標記

用法：
    python3 fix_samnmax_000.py /path/to/SAMNMAX.000

背景：
- 原版 samnmax.000 的 DSCR 目錄中，room 1 有兩筆相鄰 entry 指向同一個
  SCRP 區塊（LucasArts 自己做的去重）
- scummtr 回填時把前一筆的 offset 改寫成 0xFFFFFFFF（去重標記），
  與原版語意不符；雖已查證全遊戲無腳本引用該 entry，仍還原為
  「與後一筆相同位址」以對齊原版行為
- 本工具掃描 DSCR offsets（檔案以 0x69 XOR），把每個 0xFFFFFFFF
  修補為後一筆 entry 的 offset；找不到則回報
注意：必須在 scummtr -if 之後執行；對未回填的原檔不造成任何改動。
"""
import struct
import sys

XOR_KEY = 0x69


def find_dscr(data):
    """回傳 (offsets 陣列起始位址, entry 數)；DSCR 格式：
    'DSCR' + size(4BE) + count(2LE) + rooms[count] + offsets[count×4LE]"""
    if data[0:4] != b'DSCR':
        # 找 DSCR tag（.000 開頭通常先是 RNAM/MAXS/DROO）
        off = 0
        while off + 8 <= len(data):
            tag = data[off:off + 4]
            size = struct.unpack('>I', data[off + 4:off + 8])[0]
            if tag == b'DSCR':
                break
            off += size
        else:
            raise SystemExit('錯誤：找不到 DSCR 區塊')
    else:
        off = 0
    count = struct.unpack('<H', data[off + 8:off + 10])[0]
    return off + 10 + count, count


def main():
    if len(sys.argv) != 2:
        raise SystemExit('用法：python3 fix_samnmax_000.py SAMNMAX.000')
    path = sys.argv[1]
    dec = bytearray(b ^ XOR_KEY for b in open(path, 'rb').read())

    base, count = find_dscr(dec)
    fixed = 0
    for i in range(count - 1):
        pos = base + i * 4
        if dec[pos:pos + 4] == b'\xff\xff\xff\xff':
            dec[pos:pos + 4] = dec[pos + 4:pos + 8]
            fixed += 1
            print('修補 entry #%d：offset 設為 0x%x（與 entry #%d 相同）'
                  % (i, struct.unpack('<I', dec[pos:pos + 4])[0], i + 1))
    if fixed == 0:
        print('無 0xFFFFFFFF 去重標記，未改動（原檔或已修補）')
        return 0

    with open(path, 'wb') as f:
        f.write(bytes(b ^ XOR_KEY for b in dec))
    print('完成：%d 處修補 → %s' % (fixed, path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
