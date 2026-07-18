# 換裝防拷（room 71）答案表

> 來源：`workplace/analysis/descumm.txt` room 71 的 Script# 203（`LSCR @file 0x00bb5a7f`）與
> Script# 202（`LSCR @file 0x00bb5722`）；物品名稱取自 `game-cd/samnmax.001` room 71 的 OBCD/OBNA。
> **10/10 頁全部解出，Sam、Max 各 10 組，無缺漏。**

## 一、防拷機制（反組譯摘要）

- 開機後 room 1 ENCD：若 `bitvar223 == 0` 就 `loadRoom(71)` 進入換裝防拷；答對後設 `bitvar223 = 1`，之後開機不再問。
- room 71 Script# 203（初始化）：
  - `var152 = getRandomNumberRange(1,10)`：指定**手冊頁碼 1–10**。
  - `var153 = getRandomNumber(1)`：指定角色，**1 = Max（兔子）、0 = Sam（狗）**。
  - `array304[0] = "BZLBUOJXKFZRIWOHTIA\SAWNE]MCSPCNQDXJD[UGYKFVPEVQG^RCYMHYTGTL"`：答案字串，共 60 字元。
  - 另隨機為兩個娃娃穿上「初始服裝」（干擾用），初始範圍見下表。
- room 71 Script# 204：顯示提示文字「dress up SAM (the dog) / MAX (the rabbit) as he is on page N of your manual, then hit the big red button.」
- room 71 Script# 202（按紅色大按鈕 = 物件 771 時判定）：
  ```
  localvar6 = ((var152 - 1) * 6) + (var153 * 3)   // 每頁 6 字元：前 3 個 Sam、後 3 個 Max
  答案物件 = (字元 - 65) + 基址                    // 基址：Sam = 715、Max = 745
  ```
  檢查該角色物件全區間（Sam 715–744、Max 745–770）：3 個答案物件必須是穿上狀態（state ≠ 0），
  其餘物件必須全部脫下（state ≠ 1）。
- 答錯第一次：「that's not right, but we'll give you one more chance」；答錯第二次：「bye-bye!」並 `systemOps.shutDown()` 強制結束遊戲。
- 答對：「Have fun!」→ `bitvar223 = 1` → 載入 room 1 正式開始。

### 答案字串解碼

- 字元直接印在反組譯裡（SCUMM v6 資料檔字串以 XOR 0xFF 編碼，descumm 已解碼；`\` 在反組譯中顯示為 `\\` 跳脫）。
- 字元 − 65 得位移：`A`–`Z` = 0–25，`[` = 26、`\` = 27、`]` = 28、`^` = 29（剛好蓋滿 Sam 區間 30 個物件）。
- 60 字元 = 10 頁 × 6（Sam 3 件＋Max 3 件），依序切分：

```
頁1  BZL BUO    頁5  E]M CSP    頁9  G^R CYM
頁2  JXK FZR    頁6  CNQ DXJ    頁10 HYT GTL
頁3  IWO HTI    頁7  D[U GYK
頁4  A\S AWN    頁8  FVP EVQ
```

### 物件區間（Sam 715–744／Max 745–770，各三欄）

| 欄位 | Sam 物件 | Max 物件 | 內容 |
|---|---|---|---|
| 身體（服裝） | 715–724 | 745–752 | 整套服裝圖（*-image） |
| 手持/配件 | 725–735 | 753–762 | 拿在手上或戴在身上的配件 |
| 頭部 | 736–744 | 763–770 | 帽子、髮型、面具等 |

> 註：Script# 203 的「初始服裝」隨機範圍（Sam 715–722／725–735／736–744，Max 745–752／753–762／763–770）
> 不含 723、724（sam-surfer-image、sam-tatooed-image）；這兩件只會出現在答案表裡（頁 3、頁 2）。

## 二、玩家用答案表（10/10 完整）

中文部件名為本專案依英文物件名翻譯（手冊只有插圖、無部件文字，故中文名非官方譯名）；
「松崗手冊頁」欄見第三節對照。

| 頁碼 | 角色 | 身體 | 頭部 | 手持/配件 |
|---|---|---|---|---|
| 1 | Sam（山姆） | 圍裙裝 apron（#716） | 牛仔帽 cowboy-hat（#740） | 鋸子 saw（#726） |
| 1 | Max（麥斯） | 金屬盔甲裝 metal（#746） | 新娘頭紗 veil（#765） | 鬥牛披風 bull-cape（#759） |
| 2 | Sam | 刺青裝 tatooed（#724） | 探險帽 indy-hat（#738） | 熱狗 weenie（#725） |
| 2 | Max | 披薩裝 dominos（#750） | 泡泡糖頭 bubblegumhead（#770） | 鬧鐘 alarm-clock（#762） |
| 3 | Sam | 衝浪裝 surfer（#723） | 外科口罩 surgical-mask（#737） | 烙鐵 brand（#729） |
| 3 | Max | 潛水裝 scuba（#752） | 龐克頭 punk-hair（#764） | 瑞士刀 swiss-knife（#753） |
| 4 | Sam | 圍裙裝 apron（#715） | 睡帽 nightcap（#742） | 牙膏 toothpaste（#733） |
| 4 | Max | 童軍裝 scout（#745） | 貝雷帽 beret（#767） | 鬥牛劍 bull-sword（#758） |
| 5 | Sam | 盲人裝 blind-guy（#719） | 衝浪金髮 surf-hair（#743） | 骷髏頭 skull（#727） |
| 5 | Max | 新娘禮服 bridal（#747） | 童軍帽 scout-hat（#763） | 披薩切片 pizza-slice（#760） |
| 6 | Sam | 綠衣裝 greens（#717） | 大鬍子 beard（#728）※配件欄 | 手杖 cane（#731） |
| 6 | Max | 吸血鬼裝 vampire（#748） | 披薩帽 pizza-cap（#768） | 吉他 guitar（#754） |
| 7 | Sam | 掘墓人裝 graverobber（#718） | 高禮帽 top-hat（#741） | 劍 sword（#735） |
| 7 | Max | 睡衣 pajamas（#751） | 南瓜頭 pumpkinhead（#769） | 雞 chicken（#755） |
| 8 | Sam | 牛仔裝 cowboy（#720） | 廚師帽 chef-hat（#736） | 手杖 cane（#730） |
| 8 | Max | 鬥牛士裝 bullfighter（#749） | 尖牙 fangs（#766） | 泰迪熊 teddy-bear（#761） |
| 9 | Sam | 燕尾服 tuxedo（#721） | 主教冠 mider（#744，應為 mitre 拼字） | 牙刷 toothbrush（#732） |
| 9 | Max | 新娘禮服 bridal（#747） | 南瓜頭 pumpkinhead（#769） | 蝙蝠 vampire-bat（#757） |
| 10 | Sam | 睡衣 pajamas（#722） | 太陽眼鏡 sunglasses（#739） | 獎牌 medal（#734） |
| 10 | Max | 睡衣 pajamas（#751） | 龐克頭 punk-hair（#764） | 花束 bouquet（#756） |

※ 頁 6 Sam 的「大鬍子」（#728）在程式上屬於配件欄（725–735 區間），判定只看三個物件是否穿上，不限欄位。

## 三、英文手冊頁碼 ↔ 松崗手冊頁 ↔ 掃描檔對照

結論：**頁碼 1:1 相同**，不需換算。松崗手冊正文第 1–10 頁每頁頁尾的換裝素描插圖，
就是英文原版手冊同頁的防拷插圖（松崗版為英文版逐頁翻譯，版式與頁碼一致）。

| 頁碼 | 松崗手冊 | 掃描檔 | 插圖位置 |
|---|---|---|---|
| 1 | 第 1 頁 | doc047187_007 | 右頁頁尾 |
| 2 | 第 2 頁 | doc047187_008 | 左頁頁尾 |
| 3 | 第 3 頁 | doc047187_008 | 右頁頁尾 |
| 4 | 第 4 頁 | doc047187_009 | 左頁頁尾 |
| 5 | 第 5 頁 | doc047187_009 | 右頁頁尾 |
| 6 | 第 6 頁 | doc047187_010 | 左頁頁尾 |
| 7 | 第 7 頁 | doc047187_010 | 右頁頁尾 |
| 8 | 第 8 頁 | doc047187_011 | 左頁頁尾 |
| 9 | 第 9 頁 | doc047187_011 | 右頁頁尾 |
| 10 | 第 10 頁 | doc047187_012 | 左頁頁尾 |

### 插圖比對驗證（掃描 vs 答案表）

- **頁 1**（放大掃描 _007 確認）：Sam 戴牛仔帽、穿長圍裙、手持鋸子 ✓；Max 穿金屬盔甲、罩頭紗、持鬥牛披風 ✓。
- **頁 5**：Max 新娘禮服（bridal）✓ 與插圖一致。
- **頁 7**：Sam 高禮帽＋長大衣（graverobber＋top-hat）✓ 與插圖一致。
- **頁 10**：Sam 條紋睡衣（pajamas）✓、Max 爆炸頭（punk-hair）✓ 與插圖一致。
- 其餘各頁插圖與答案表無矛盾；部分手持小物在掃描中線條過細，無法 100% 目視確認者，
  以上表答案（來自腳本本身）為準。

## 四、給中文化 patch 的技術附註

- 判定物件狀態的程式在 room 71 Script# 202；提示文字在 Script# 204（兩條 `printLine.msg`，
  分別對應 Max／Sam）。中文化需翻譯的字串：
  - `"dress up MAX (the rabbit)\nas he is on page N of your manual,\nthen hit the big red button."`
  - `"dress up SAM (the dog)\nas he is on page N of your manual,\nthen hit the big red button."`
  - `"hit a key to activate SAM AND MAX'S\nreally tough copy protection"`（Script# 203）
  - `"that's not right,\nbut we'll give you one more chance^"`、`"bye-bye!"`、`"Have fun!"`（Script# 202）
- 台版手冊的防拷說明在手冊第 2 頁「遊戲保護」（掃描 doc047187_008 左頁），譯文可與其用語對齊
  （衣櫃、箭頭圖形、紅色的大按鈕、「您可以有第二次機會」）。
- 同名不同物件：#715/#716 皆為 `sam-apron-image`（頁 4 用 #715、頁 1 用 #716），
  #730/#731 皆為 `sam-cane-image`（頁 8 用 #730、頁 6 用 #731）；應為兩種圍裙/手杖圖，判定按物件編號。
- 拼字存疑（照錄）：`sam-mider`（應為 mitre 主教冠）、`max-pizza-scice`（應為 slice）、`sam-tatooed-image`（應為 tattooed）。
- 手冊頁 12「山姆和麥斯的化妝家家酒」（Snuckey's 貨架小遊戲）使用同一批娃娃物件（685–712 為衣櫃圖示側），
  但屬遊戲內小遊戲，不影響本答案表。
