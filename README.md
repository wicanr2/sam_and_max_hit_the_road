# 妙探闖通關——大腳之謎（Sam & Max Hit the Road）繁體中文化

1993 年 LucasArts 經典《Sam & Max Hit the Road》（松崗台版譯名《妙探闖通關——大腳之謎》）的繁體中文化 patch。本 repo 只含中文化資料與工具（patch-only），**不含遊戲本體**；遊戲請自備 CD 版（`SAMNMAX.000/.001`＋`MONSTER.SOU`）。

## 現況

工作進行中：全文本 6,016 行已翻譯完成，校對與實機驗證階段。完成後會在此提供打包好的成品與安裝說明。

## 內容物

| 目錄 | 內容 |
|---|---|
| `patches/` | ScummVM 1 行白名單 patch（`charset.cpp` 的 ZH_CHN 白名單加入 `GID_SAMNMAX`，基準 v2.8.0） |
| `tools/` | 中文化工具鏈：碼表蒐集、編解碼、字型烘焙、回填修補、譯文校驗（繁體中文註解） |
| `font/` | `cht_table.json`——自訂碼空間碼表（GB2312 佈局、繁體字形） |
| `translation/` | 繁體中文譯文（scummtr 匯出格式，TAG 對位） |
| `docs/` | 工程規格、譯名表、翻譯指南、松崗手冊要點、防拷答案對照表 |

## 技術原理（簡述）

1. **引擎**：原版 ScummVM 的中文渲染白名單不含 samnmax，唯一更動是白名單加一行（`patches/`）；其餘沿用 ScummVM 內建 CJK 路徑，遊戲夾放 `chinese_gb16x12.fnt` 即自動切中文。
2. **碼空間**：自訂雙位元組編碼，位元組落在 GB2312 合法區間並避開 scummtr 會 remap 的 27 個高位元組，引擎與 scummtr 都不用改。
3. **字型**：依碼表從文泉驛微米黑烘 12×12 點陣，寫成 `chinese_gb16x12.fnt`。
4. **文字**：scummtr 匯出 → 翻譯 → 編碼 → scummtr 回填（round-trip 已驗證 byte 級可逆）。

細節見 `docs/engineering-spec.md`。

## 致謝與資料來源

- 松崗電腦《妙探闖通關》台版手冊（譯名第一優先來源）
- 青衫（邱冀）攻略站的本作資料
- [scummtr](https://github.com/dwatteau/scummtr)（dwatteau, MIT）、[ScummVM](https://www.scummvm.org/)

LucasArts 與 Sam & Max 相關權利屬原權利人；本專案為非營利愛好者中文化，僅散布 patch。
