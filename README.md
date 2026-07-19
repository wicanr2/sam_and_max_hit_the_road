# 妙探闖通關——大腳之謎（Sam & Max Hit the Road）繁體中文化

1993 年 LucasArts 的公路冒險喜劇《Sam & Max Hit the Road》——一隻穿西裝的狗偵探山姆、一隻沒有下限的兔子麥斯，開著偷來的警車橫越美國找一頭失蹤的雪怪大腳。當年松崗電腦以《妙探闖通關——大腳之謎》之名代理台版（遊戲編號 917302，建議售價 NT$560）。這個 repo 讓它重新用**繁體中文**開口說話。

本專案為 **patch-only**：只含中文化資料與工具，**不含遊戲本體**。你需要自備 CD 版的 `SAMNMAX.000` / `SAMNMAX.001`（＋語音 `MONSTER.SOU`），套上本 patch 後用 ScummVM 遊玩。

> 🎮 **線上懷舊：防拷紙娃娃**  
> 當年開機得翻手冊、把山姆或麥斯打扮成插圖的樣子才能進遊戲。手冊掉了?
> 我們把 10 頁防拷答案全用反組譯還原，做成一頁互動網頁（原創手繪 SVG）：  
> **https://wicanr2.github.io/sam_and_max_hit_the_road/**  
> （需在 repo Settings → Pages 指定由 `docs/` 發佈後生效。）

---

## 現況

- ✅ 全文本 **6,016 行**翻譯完成，二輪校對（約 440 處修正）。
- ✅ CJK 撞碼修復（114 行 latin-1 高位字元編入碼表）。
- ✅ 自訂 12×12 **embedded-bitmap** 字型（清晰版），真機驗證中文正常、無雪花。
- ✅ 本機完整版打包（Linux）：ScummVM + 中文資料 + MT-32 音色，可玩。
- ✅ 防拷換裝答案 10/10 反組譯還原 → 線上懷舊網頁。

---

## 內容物

| 目錄 | 內容 |
|---|---|
| `patches/` | ScummVM 1 行白名單 patch（`charset.cpp` 的 ZH_CHN 白名單加入 `GID_SAMNMAX`，基準 v2.8.0） |
| `tools/` | 中文化工具鏈：碼表蒐集、編解碼、字型烘焙（PIL 版＋embedded-bitmap 版）、回填修補、譯文校驗（繁體中文註解） |
| `font/` | `cht_table.json`（自訂碼空間碼表）＋ `chinese_gb12emb.fnt`（出貨字型） |
| `translation/` | 繁體中文譯文（scummtr 匯出格式，TAG 對位） |
| `docs/` | 工程規格、譯名表、松崗手冊整理（`manual.md`）、防拷答案表、線上防拷網頁（`index.html`） |

---

## 技術原理

這是一個「不改引擎行為、只借引擎既有中文路徑」的中文化。四個關鍵決策：

### 1. 引擎：只加一行白名單
原版 ScummVM 的 CJK 渲染白名單不含 samnmax。唯一的引擎更動，是在 `charset.cpp` 的 ZH_CHN 白名單加一行 `GID_SAMNMAX`（見 `patches/`）；其餘完全沿用 ScummVM 內建的中文（ZH_CHN）渲染路徑。遊戲目錄放進 `chinese_gb16x12.fnt` 就自動切中文。

### 2. 碼空間：寄生在 GB2312 合法區間
用自訂雙位元組編碼，讓每個位元組落在 GB2312 合法範圍（0xA1–0xFD），並**避開 scummtr 會 remap 的 27 個高位元組**。這樣引擎與 scummtr 工具都不必改，就能塞進 2000+ 個繁體字。

一個踩過的坑：SCUMM 的 CJK 模式下，任何 `byte ≥ 0x80` 都被當成雙位元組的前導位元組。譯文裡的人名間隔號「·」、`Flambé` 的 é 等**單位元組拉丁字元**正好落在這個範圍，會觸發撞碼連鎖錯位——修法是把這些字元也收進碼表當合法字處理（commit `5f61414`）。

### 3. 字型：16×16 是死路，關鍵在烘字法不在尺寸
一開始覺得 12×12 繁體字「彆扭」，想學 PC98/FM-Towns 版走 16×16 高解析。**第一性坐實這是死路**：ScummVM 的 16×16 中文需要 `_textSurfaceMultiplier=2` 的底圖放大管線，而那條管線只綁在 FM-Towns / Mac 版；DOS 版的 samnmax（SCUMM v6）沒有 → 底圖 pitch 錯位，畫面變「雪花」。

真正讓字「彆扭」的不是尺寸，是烘字法。原本用 PIL 對向量字二值化，12px 下筆劃細如噪點。改用 **WenQuanYi Zen Hei Sharp 的 embedded bitmap**（設計師手繪點陣）重烘，字就清晰了（`tools/build_cht_font_embedded.py`）。

### 4. 文字：scummtr round-trip
`scummtr` 匯出 → 翻譯 → 編碼 → `scummtr` 回填，全程 byte 級可逆（已驗證）。

細節見 [`docs/engineering-spec.md`](docs/engineering-spec.md)。

---

## 遊玩方式

1. 準備一份 Sam & Max Hit the Road CD 版遊戲檔（`SAMNMAX.000/.001` + `MONSTER.SOU`）。
2. 套用 `patches/` 的 ScummVM 白名單 patch 並自行編譯 ScummVM v2.8.0，或使用已內建 patch 的 build。
3. 把中文資料檔與 `font/chinese_gb12emb.fnt`（更名為引擎預期的 `chinese_gb16x12.fnt`）放進遊戲目錄。
4. 在 ScummVM 加入遊戲、語言設為中文、開字幕即可。

> 本機完整版打包（含字型、MT-32 音色 launcher）不放進 repo（含遊戲語音與 ROM 等版權物，僅供個人本機使用）。

---

## 譯名對照（部分，全表見 `docs/glossary.md`）

| 原文 | 松崗譯名 |
|---|---|
| Sam & Max Hit the Road | 妙探闖通關——大腳之謎 |
| Sam | 山姆（狗偵探） |
| Max | 麥斯（兔子） |
| Bigfoot | 大腳 |

譯名以松崗台版手冊為第一優先來源，手冊整理見 [`docs/manual.md`](docs/manual.md)。

---

## 致謝與資料來源

- 松崗電腦（Unalis Corporation）《妙探闖通關——大腳之謎》台版手冊（譯名第一優先來源）
- 骨灰集散地掃描計畫的手冊掃描（2016-08-21，25 張）
- 青衫（邱冀）攻略站的本作資料
- [scummtr](https://github.com/dwatteau/scummtr)（dwatteau, MIT）、[ScummVM](https://www.scummvm.org/)
- [WenQuanYi Zen Hei](http://wenq.org/)（字型，GPL/Apache 授權）

LucasArts、Steve Purcell 與 Sam & Max 相關權利屬原權利人；本專案為非營利愛好者中文化，僅散布 patch 與工具。
