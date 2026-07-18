# 妙探闖通關（Sam & Max Hit the Road）繁體中文化 — 工程規格

版本：v0.2（執行版）
狀態：2026-07-18 審閱通過（D1–D6 全數裁示），Phase 0、Phase 1 已完成，Phase 2 已完成（工具鏈＋小樣端到端驗證，詳 §8）
上位文件：`CLAUDE-SAMNMAX.md`（專案指令與硬規則）；本檔將其轉為可執行的工程規格。

## 1. 目的與範圍

把 LucasArts《Sam & Max Hit the Road》中文化為**繁體中文**，遵循「正確性／引擎對齊 ＞ 零 patch ＞ 可玩交付 ＞ 可維護／文件 ＞ 效能／美觀」的優先序。

範圍：

- 做：遊戲內全部文字（對白、verb 列、介面、物品名）繁體中文化；中文字型烘焙；三平台可玩包（本機）；README 與手冊整理（公開 repo）。
- 不做：除 §3 核准的 1 行白名單 patch 外不改 ScummVM 任何其他原始碼、完全不動 scummtr；不翻語音（CD 版英文語音保留，配中文字幕）；不做簡體版；圖形內嵌文字（如標題畫面 logo）的漢化列為選項，見 §13。

## 2. 現況盤點

### 2.1 素材

| 素材 | 位置 | 內容 | 備註 |
|---|---|---|---|
| 遊戲本體 | `samnmax.zip`（工作根目錄） | **CD 語音版**：`samnmax.000/.001` + `monster.sou`（183MB 語音）+ DOS 工具 | 版權物，僅本機使用，不入公開 repo |
| 中文手冊 | `松崗-妙探闖通關-大腳之謎.rar` | 1993 松崗台版手冊掃描 26 頁 JPG | 譯名對照的第一優先來源 |
| MT-32 ROM | `/home/anr2/cht/mt32/` | MT32 + CM32L 全套 | 僅本機包使用，`*.ROM` gitignore |
| 公開 repo | `github.com/wicanr2/sam_and_max_hit_the_road` | 空白 repo（已 clone 至 `workplace/sam_and_max_hit_the_road/`） | patch-only：字型、譯文、工具、文件 |
| 參考專案 | `/home/anr2/cht/indiana-jones-and-last-crusade-cht/` | Indy3 中文化 repo（scummtr 流程、打包、擷圖腳本可借鑑） | 該專案有引擎 patch，本案目標零 patch，路線不同 |

### 2.2 環境

- docker 29.1.3 可用；開發／擷取／打包一律在 docker 內執行。
- 本機無 scummvm（符合 docker-first）；unrar、ffmpeg、python3 已備。
- `CLAUDE-SAMNMAX.md` 提及的 `cht_codec.py`／`build_cht_font.py`（MI2 專案工具）在本機未找到；若無法取得，依 §7 規格重新實作（演算法已完整定義，無外部依賴）。

### 2.3 與上位文件的出入（已確認事實）

- `CLAUDE-SAMNMAX.md` 寫「SCUMM v5（gameid monkey2）」為 MI2 模板殘留。`samnmax` 依多方資料為 **SCUMM v6**；Phase 0 以 `scummvm --list-games` 與偵測結果坐實。
- 素材標註「VGA」但 zip 實為 **CD 語音版**。以 CD 版為工作基礎：SCUMM v6 talkie 支援語音／字幕／兩者並存，中文化後保留英文語音＋中文字幕。

## 3. 技術路線總覽

1. **最小 1 行引擎 patch**（2026-07-18 使用者核准，見 §13 D6）：R1 查證確認 samnmax 不在 ScummVM 的 ZH_CHN 白名單（`engines/scumm/charset.cpp` `loadCJKFont()`，master 與 2.8 分支相同），零 patch 路線不成立。唯一更動：白名單加入 `_game.id == GID_SAMNMAX`（patch 檔：`patches/scummvm-samnmax-zh-chn-whitelist.patch`，基準版本 v2.8.0）。其餘完全沿用 monkey2 零 patch 配方——中文顯示走 CJK 字型偵測路徑（遊戲夾放中文字型檔即自動啟用），渲染器與 v5 相同。scummtr 不動。不送 upstream。
2. **碼空間**：自訂雙位元組編碼，所有位元組落在 `0xA1–0xFD`（GB2312 合法區間），索引公式 `idx=(lead-0xA1)*94+(trail-0xA1)`。字形為**繁體中文**——碼位借用 GB2312 的「佈局」，填入的字形由自烘字型決定，引擎只檢查位元組範圍、不關心語意字集。ASCII 字元走 latin-1 原樣通過。
3. **抽字／回填**：scummtr 匯出文本 → 翻譯 → 編碼轉換 → scummtr 回填。
4. **驗證**：descumm 反組譯與 headless 實機截圖為唯一 oracle；引擎行為不憑記憶斷言。

## 4. 關鍵未知項與風險登錄

上位文件的規則多蒸餾自 MI2（SCUMM v5）實戰。本作為 SCUMM v6，下列各項**一律先驗證再引用**，不得照搬：

| # | 未知項／風險 | 影響 | 驗證方式 | 驗證階段 |
|---|---|---|---|---|
| R1 | ~~`samnmax` 是否在 ScummVM 中文版（ZH_CHN）白名單~~ **已判定（2026-07-18）**：不在白名單（`charset.cpp` `loadCJKFont()`，master／2.8 相同）→ 採 1 行 patch 方案，使用者核准，見 §3、§13 D6 | 零 patch 不成立，改自編引擎 | 源碼查證＋patch 自編＋冒煙測試 | Phase 1（已結案） |
| R2 | ~~v6 的中文字型檔名與格式是否同 v5 配方~~ **已判定（2026-07-18）**：相同。`chinese_gb16x12.fnt`、無 header、12×12、1bpp MSB-first、每 glyph 24 bytes、`numChar=8178`、總長 196,272 bytes、索引 `(lead-0xA1)*94+(trail-0xA1)`（`charset.cpp:123-166, 303-305`） | 無（與 MI2 配方一致） | 源碼查證 | Phase 1（已結案） |
| R3 | ~~scummtr 是否支援 `samnmax`（SCUMM v6）匯出／回填~~ **已判定通過（2026-07-18）**：scummtr 0.6.0（commit `a50c6f4`）支援。無 padding 模式 round-trip：`.001` byte-identical；`.000` 僅 offset 696–699 四 bytes 差異——原版 DSCR entry #8 與 #9 共用 SCRP 區塊，scummtr 去重寫 `0xFFFFFFFF`；descumm 全量反組譯（854 區塊）證實全遊戲無任何 reference script 8，無害；回填後把該四 bytes 修補回原值 `46 0F 69 69` 即完全 byte-identical（已驗證） | 無（回填流程納入 4-byte 修補） | round-trip diff＋descumm 854 區塊比對 | Phase 1（已結案） |
| R4 | ~~CD 版防拷~~ **已判定（2026-07-18），假設反轉：本作有強制防拷**。room 1 ENCD 檢查 `bitvar223`，必進 room 71「娃娃換裝」手冊防拷（版本字串 `CD1.11, 3-24-94`）；答錯兩次直接 `shutDown()`。ScummVM 內建 copy_protection 跳過邏輯**不含 samnmax**（只涵蓋 Monkey2/Loom/Zak/Indy3/Indy4/Maniac/DOTT）→ 玩家必須答題。防拷提示文字在匯出文本中可正常翻譯；答案表 `array304` 是 LSCR#0203 腳本內 XOR 資料。**Phase 2 實機補充（2026-07-19）**：預設開機流程下 boot script（room 1 SCRP，`dup[1]` 各分支）一律先把 `bitvar223` 設為 1，ENCD 判定永不成立——多次完整開場實測皆直接進辦公室、未出現防拷畫面；且 ScummVM 另有 `kEnhUIUX` 增強（`scumm.cpp:1501`，預設開啟）在 `_bootParam == 0` 時改寫為 -1 同樣繞過。換裝畫面可用 `--boot-param=1506` 進入（doll 畫面正常），但該路徑 `bitvar223==1` 不啟動 LSCR#0203/0204 提示文字（原版未改資料同現象，非翻譯問題）。玩家實際是否會遇到防拷，Phase 4 需以還原測試（如模擬器或修改 bitvar）再確認 | 玩家體驗風險：中文玩家需答案對照表（頁碼是英文手冊頁碼，松崗手冊頁碼可能不同） | descumm room 71 LSCR#0202-0204 反組譯＋實機 | Phase 1（已結案）；**後續工作：Phase 3 從 array304 或攻略整理 10 頁答案對照表，入 README／手冊要點** |
| R5 | v6 對白渲染的行寬／換行行為與 v5 不同 | 中文對白超框、截斷 | 試譯一批對白後多場景截圖 | Phase 2、4 |
| R6 | 撞碼（字元級亂碼：某行前半亂後半正常） | 交付品質致命傷 | 碼空間硬規則（全位元組 `0xA1–0xFD`）＋全量回填後逐場景截圖掃 | Phase 2、4 |
| R7 | verb 列／介面字串在資源中的位置與 v5 不同 | 介面漏譯 | 匯出文本全量檢視，對照實機截圖 | Phase 2 |
| R8 | 語音版字幕時序（talkie 字幕逐行對應語音） | 字幕過長時顯示時間不足 | 實機觀察開場對白；必要時拆行或精簡譯文 | Phase 4 |
| R9 | 翻譯量 | **已統計（2026-07-18）**：匯出 6,016 行（LSCR 2,078／SCRP 1,904／OBNA 836／VERB 713／ENCD 479／EXCD 4），payload 約 17 萬字元；配音台詞開頭固定 8 bytes 語音 offset/長度控制碼（`\255\010…`），必須原樣保留 | 批次 fan-out 翻譯＋第二輪校對 | Phase 3 |

## 5. 目錄結構

```
sam_and_max_hit_to_road/          # session 工作根目錄（本機）
├── samnmax.zip                   # 原版遊戲（版權物，本機）
├── 松崗-妙探闖通關-大腳之謎.rar    # 手冊掃描（本機）
└── workplace/
    ├── docker/                   # Dockerfile 與進容器腳本
    ├── game-cd/                  # 解出的原版遊戲（gitignored）
    ├── game-cht/                 # 中文化遊戲夾（gitignored）
    ├── manual/                   # 手冊掃描解出（本機；公開化方式見 §13）
    ├── dist-all/                 # 打包產物（gitignored，每平台留最新一份）
    └── sam_and_max_hit_the_road/ # 公開 repo（patch-only）
        ├── docs/                 # 本規格、譯名表、手冊要點、技術筆記
        ├── patches/              # scummvm-samnmax-zh-chn-whitelist.patch（1 行白名單）
        ├── tools/                # cht_codec.py、build_cht_font.py、翻譯／回填／驗證腳本
        ├── translation/          # scummtr 匯出原文與繁中譯文（TAG 對位）
        ├── font/                 # cht_table.json 與烘焙設定（不附 GPL 字型本體，附取得方式）
        └── README.md
```

## 6. 工具鏈與 docker 環境

docker image（`workplace/docker/Dockerfile`，以 `CLAUDE-SAMNMAX.md` 的版本為基礎）：

- `ubuntu:24.04` + `scummvm xvfb x11-utils xdotool imagemagick ffmpeg python3 python3-pil fonts-wqy-microhei fonts-noto-cjk zstd zip unzip curl file git`，另加 scummvm 自編依賴（`libsdl2-dev zlib1g-dev libpng-dev libjpeg-dev libfreetype6-dev libvorbis-dev libflac-dev libmp3lame-dev libmad0-dev libfaad-dev libtheora-dev libmpeg2-4-dev liba52-dev libfluidsynth-dev libcurl4-openssl-dev`）
- **scummtr**（dwatteau，MIT）：自編，鎖定 commit `a50c6f4`（v0.6.0pre2-116）。
- **descumm**（scummvm-tools）：自編，鎖定 commit `6a2f2a00`；單檔 200KB 上限，大量反組譯用 `/work/analysis/disasm_all.py` 區塊 walker 驅動（854 區塊全量反組譯已產出 `/work/analysis/descumm.txt`）。
- scummtr 操作細節：Linux 下遊戲檔名須全大寫（`SAMNMAX.000/.001/MONSTER.SOU`）；匯出用 `scummtr -g samnmax -p <dir> -cwh -A aov -of <txt>`，回填換 `-if`；回填後修補 `.000` offset 696–699 為 `46 0F 69 69` 達 byte-identical。
- **scummvm v2.8.0 自編**：套用 §3 的 1 行 patch，`--disable-all-engines --enable-engine=scumm --enable-mt32emu`，產出 `scummvm-cht`；apt 原版（2.8.0）保留作為對照組。

工具實作（放公開 repo `tools/`）：

- `cht_codec.py`：字串 ↔ 自訂碼空間編碼／解碼。ASCII 原樣；CJK 依 `cht_table.json` 查碼位。
- `build_cht_font.py`：依 `cht_table.json` 從 `wqy-microhei.ttc`（GPL，docker 內 `fonts-wqy-microhei` 提供）算 12×12 bitmap，依 `idx=(lead-0xA1)*94+(trail-0xA1)` 寫入字型檔對應位置。
- `collect_charset.py`：從譯文蒐集用到的 CJK 字元，去重排序（頻率優先、同頻按 Unicode），產生穩定的 `cht_table.json`。字集上限 94×94=8836，對本作綽綽有餘。
- 翻譯／回填／截圖驗證腳本：Phase 內逐步建立，先求可重跑再求自動化。

## 7. 碼空間與字型設計（硬規則）

- 所有雙位元組字元的 lead 與 trail 都必須落在 `0xA1–0xFD`。
- **禁用 GBK**：其 trail 可為 `0x40–0x7E`／`0xFE`，會撞 SCUMM／scummtr 的特殊位元組（`@`=0x40 padding、`\`=0x5C escape、`0xFE/0xFF` 控制碼），造成字元級亂碼與回填錯誤。
- **scummtr `-c` 會 remap 27 個高位元組**（Phase 2 實測，scummtr text.cpp win1252→final charset 表：`0xA9`、`0xC4/C6/C7/C9`、`0xD6/DC`、`0xDF`、`0xE0-E2/E4/E6-EC/EE/EF`、`0xF2/F4/F6/F9/FB/FC`）——碼空間 lead/trail 必須全面避開，上限 63 lead × 66 trail = **4,158 碼位**（本作字集遠小於此）。已內建於 `tools/cht_common.py` 的 `FORBIDDEN_BYTES`，產碼表自動跳過。
- 啟動語系：放字型檔即自動偵測 ZH_CHN，玩家零設定；若手動指定只能用 `--language=cn`——`zh` 會解析成 ZH_ANY、不進 CJK 路徑，中文渲染成白條（Phase 2 實測）。
- 引擎 GUI 字串（F5 選單的 Music/Voice/Sfx/Display Text/Text Speed）不在 scummtr 匯出範圍，第一版維持英文；Phase 4 再評估是否走 ScummVM 自帶翻譯系統。
- 字型檔規格已坐實（R2）：`chinese_gb16x12.fnt`、無 header、12×12、1bpp MSB-first、`numChar=8178`、總長 196,272 bytes。放遊戲夾後 patched ScummVM 偵測到即自動切中文渲染，玩家零設定。
- 繁體字形填 GB2312 碼位是刻意設計：引擎與 scummtr 只看位元組範圍，字形由自烘字型決定。

## 8. 階段計畫與驗收標準

每階段完成後回報驗收結果；標「gate」者未過不得進下一階段。

### Phase 0 — 環境

- 建 docker image；解 `samnmax.zip` 至 `game-cd/`；解手冊掃描至 `manual/`。
- `scummvm --list-games` 記錄 `samnmax` 的 gameid 與 SCUMM 版本；`scummvm --auto-detect` 確認偵測。
- 驗收：headless（Xvfb）能啟動英文原版並截到開場畫面。

### Phase 1 — 可行性驗證（GO/NO-GO gate）

- 讀 scummvm 源碼確認 R1（白名單）、R2（字型檔名／格式）；clone 源碼僅供閱讀，不編不 patch。
- 編 scummtr、descumm；`scummtr -g samnmax -w -H` 匯出全文本。
- round-trip：原封不動回填 → 與原檔 diff=0。
- descumm 開場 script 確認 R4（防拷）。
- 統計文本量（行數／字元數／CJK 字集預估）供 Phase 3 規劃。
- 驗收：R1 已判定（不在白名單，改走 §3 的 1 行 patch，使用者核准）；R3 須通過且 round-trip diff=0；patched 引擎放字型檔後能進遊戲（對照組：原版引擎同條件報 `Could not load any font`）。**R3 不通過 → 停，回報使用者評估。**

### Phase 2 — 端到端中文顯示（小樣驗證 gate）

- 實作 `cht_codec.py`、`collect_charset.py`、`build_cht_font.py`。
- 只試譯一小批：開場對白數十句＋物件名（OBNA）＋常用介面字串。注意：本作無 verb bar（LucasArts 首款游標圖示介面），「verb 列」驗收改為**句子列／物品欄的物件名（OBNA）**。
- 烘字型放 `game-cht/` → 回填（含 4-byte DSCR 修補）→ patched 引擎 headless 截圖。
- 驗收：截圖中物件名與對白全中文、逐字正確、**無撞碼**、無超框截斷（R5、R6、R7）。不通過先回碼空間／字型檢查。

### Phase 3 — 全量翻譯

- 先建譯名表 `docs/glossary.md`：人物／地名／物品／專有名詞，來源優先序：松崗手冊 ＞ 當年雜誌／攻略（含 `chiuinan.github.io` 的本作資料）＞ 現代通行譯名。手冊掃描需逐頁讀取整理。
- 批次 fan-out 翻譯（subagent 前景有界執行）；文風規範見 §9。
- 第二輪校對：統一譯名、檢查控制碼保留、長度與語氣。
- 驗收：譯文全量涵蓋匯出文本；譯名表落實率 100%；控制碼（`\`、`%s` 類、換行）逐條核對無缺漏。

### Phase 4 — 全量回填與實機驗證

- 全量編碼回填 → headless 多場景截圖（開場、數個房間、對白樹、物品欄、存讀檔介面）。
- 語音＋字幕並存實測（R8）。
- 驗收：各場景無撞碼、無超框；字幕與語音節奏可接受；存讀檔正常。

### Phase 5 — 打包

- `dist-all/` 三平台：因 §3 的 1 行 patch，三平台一律**自編 binary**（Windows 交叉編譯單 exe；macOS 交叉或本機編 `.app`，從 Linux 交叉編譯 macOS 是已知麻煩點，必要時降為「先出 Windows＋Linux」；Linux AppImage）。Indy3 專案的自編／打包腳本可借鑑。
- launcher 的 ROM-aware 分支：有 ROM（本機版）→ 附 ROM 進遊戲夾＋`--music-driver=mt32 --extrapath=<遊戲夾>`；無 ROM（公開版）→ 不設 mt32 預設，保 AdLib。兩者缺一不可，不許「設 mt32 卻無 ROM」的阻擋框體驗。
- leak-scan：確認各包與公開 repo 無遊戲本體、無 `*.ROM`、無手冊原圖（視 §13 決策）。
- 驗收：打包後的包 headless 跑開場，log 無 `cannot be used`，截圖中文正常。

### Phase 6 — 文件與推廣

- README.md：故事鉤子＋松崗代理史＋譯名對照＋技術深潛＋遊玩方式；頁首嵌實機 GIF（靜音）。
- 手冊與攻略整理進 repo（形式依 §13 決策）。
- （選）宣傳片：x11grab 錄真實遊玩片段＋ffmpeg 標題卡／字幕；配樂錄**原版真實音訊**（`SDL_AUDIODRIVER=disk`；MT-32 錄音須送鍵推進到開場動畫後才有樂，前段靜音為音色上傳期，屬正常）。
- （選）dev-setup 接續包。
- `git push` 與 Release 前一律先回報確認。

## 9. 翻譯規範

- **譯名**：以松崗官方手冊為準建立對照表；查不到官方譯名的，用當年資料或現代通行譯名，並在譯名表註明來源。不憑印象自創。
- **文風**：保留原作插科打諢，適度台式瘋趣；不硬塞當代流行語破壞 1993 年代感。Sam 的冷面吐槽與 Max 的暴走無厘頭是語氣基準。
- **技術約束**：scummtr 的 TAG／位置對位，不靠行號；控制碼與格式符原樣保留；對白長度以不超框為上限（Phase 2 先建立長度經驗值）。
- **OBNA 政策（2026-07-19 實證拍板）**：v6 無引擎句子行、無 verbOps、無 `getObjectName` opcode；場景 56 點懸停像素比對零命中——**物件名不會顯示給玩家**，純內部識別用。故連字符內部名（`twine-museum-sign`、`sam-apron-image` 類）**不譯**；已譯的可讀名稱保留無妨。Phase 4 實機若發現畫面出現英文名，再回來修訂。

## 10. 驗證方法學

- oracle 只有兩個：descumm 反組譯結果、實機截圖。引擎行為斷言必附其一。
- headless 流程：`Xvfb` + `scummvm --path --auto-detect --boot-param=<room> -e adlib` + `import -window root` 截圖；長指令一律 `timeout` 包。
- 背景／長任務：前景有界執行，不做 sentinel 輪詢；機械性批次任務派 subagent 並盯到結束。

## 11. 打包與發佈政策

- 公開 repo 只含：引擎 patch 檔、碼表、譯文、工具、文件、README——**patch-only**。遊戲本體、ROM、含版權配樂影片一律不入。
- 本機完整版（含遊戲＋ROM）只留 `dist-all/`。
- 每次打包後跑 leak-scan 再交付。

## 12. 與上位文件硬規則的關係

`CLAUDE-SAMNMAX.md` 的硬規則清單全文適用，本規格不重複；唯一例外是「零 source patch」一條——因 R1 查證結果，經使用者於 2026-07-18 核准改為「最小 1 行白名單 patch」（§3、§13 D6），其餘硬規則不變。執行中若規格與上位文件衝突，以上位文件為準並修訂本規格。

## 13. 決策點與開放問題

D1–D5 已於 2026-07-18 由使用者全數核准建議預設；D6 同日裁示。

| # | 問題 | 決議 | 影響階段 |
|---|---|---|---|
| D1 | 手冊掃描原圖是否入公開 repo？手冊為松崗版權物 | **已定**：只放整理後的要點索引與譯名對照文字，原圖留本機 | Phase 6 |
| D2 | 圖形內嵌文字（標題 logo、開場圖卡）是否漢化？需動圖形資源，成本高且超出字串層 | **已定**：第一版不做，字串中文化完成後再評估 | Phase 4 後 |
| D3 | 宣傳片是否製作 | **已定**：字串驗收通過後再做，列為必做前的最後一項 | Phase 6 |
| D4 | 手冊掃描若需 OCR／人工抄寫以建立譯名表，範圍？ | **已定**：只抄與譯名／設定相關頁面，不全文數位化 | Phase 3 |
| D5 | `cht_codec.py`／`build_cht_font.py` 無法從 MI2 專案取得時，依 §6–7 重寫 | **已定**：接受重寫 | Phase 2 |
| D6 | samnmax 不在 ZH_CHN 白名單，零 patch 路線不成立，怎麼走？ | **已定**：只做本地 1 行 patch（白名單加 `GID_SAMNMAX`），自編 scummvm 走到底，不送 upstream | Phase 1 起全程 |
