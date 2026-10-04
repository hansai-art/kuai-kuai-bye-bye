# 乖乖拜拜｜Kuai Kuai Bye Bye 💚

### 拜一包乖乖，跟 Bug 說 Bye-bye。

## 先看兩種安放方式

### 設計師｜Illustrator

把圖留在畫板上，將它的 Layers 列拖到最底部，再以 `Opacity 0%` 隱藏；眼睛保持開啟，最後鎖定。

![Illustrator：把官方綠色乖乖留在畫板上，拖曳 Layers 列到底部，再將 Opacity 設為 0%](https://raw.githubusercontent.com/hansai-art/kuai-kuai-bye-bye/main/docs/demo-illustrator-kuai-kuai.gif)

[GIF 無法播放？開啟 Illustrator 靜態 PNG 備援 →](https://raw.githubusercontent.com/hansai-art/kuai-kuai-bye-bye/main/docs/demo-illustrator-kuai-kuai.png)

### 工程師｜直接用程式碼

不插入圖片，直接把帶有明暗層次的 ASCII 乖乖寫進原始碼，在 build hook 輸出。

![程式碼：把 ASCII 乖乖寫進原始碼，在 build hook 輸出](https://raw.githubusercontent.com/hansai-art/kuai-kuai-bye-bye/main/docs/demo-code-kuai-kuai.gif)

[GIF 無法播放？開啟程式碼靜態 PNG 備援 →](https://raw.githubusercontent.com/hansai-art/kuai-kuai-bye-bye/main/docs/demo-code-kuai-kuai.png)

「拜拜」是祈福，「Bye-bye」是送走。

把台灣工程師放在機器旁邊的那包綠色信仰，放進程式碼、設計圖層與動畫合成。保佑程式乖乖跑、客戶乖乖過稿，跟 Bug、當機和第十八版修改說拜拜。

乖乖可能缺貨，Deadline 不會。

所以我們做了「乖乖拜拜」。工程師把它放進註解，設計師把它壓在圖層最底下，動畫師讓它陪著每一個合成。今天沒當機，就算它有幫忙。今天還是當機，請保留 log。

**這是一個開玩笑的專案，但安放、檢查、補貨與拆除都是認真寫的。**

## 它到底是什麼？

這是一個 AI Skill，加上官方綠色包裝圖檔與小型腳本。把 Skill 交給支援本機技能與執行工具的 AI，它就知道怎麼在你的專案裡安放乖乖。只有對話、沒有檔案或桌面軟體操作權限時，它可以提供圖檔與腳本，不能隔空修改 PSD。

| 身分 | 乖乖放哪裡 | 真的做了什麼 |
| --- | --- | --- |
| 工程師 | `.kuai-kuai/` 與指定的原始碼 | 可選擇新增護身卡、官方圖檔、清冊、純註解，或用程式碼直接畫出像素版乖乖 |
| 設計師 | Illustrator Layers 最底部 | 拖入官方圖檔，Opacity 設為 0%，鎖定，保留 Background |
| 動畫師 | After Effects 合成最底部 | 匯入 PNG，設 Guide Layer、關閉可見性、鎖定 |

結案率提升、當機率下降、客戶突然只改一版，屬於本專案的信仰設定。程式沒有修復軟體或提高成交率的功能，也沒有蒐集這些成效數據。

## 最快的用法

把 `skills/kuai-kuai-bye-bye/` 整個資料夾交給你的 AI。請它先讀 `SKILL.md`，再說：

> 幫我的專案放一包數位乖乖。專案是 /path/to/project，請在 src/main.ts 放護身註解，檢查完告訴我它在哪裡。

或說：

> 我要保佑這個 Photoshop 專案。請準備數位乖乖圖檔與安放腳本，放在最下面、隱藏並鎖定。

## 安裝成 Skill

整個 `skills/kuai-kuai-bye-bye/` 是可安裝單位，不能只複製 SKILL.md，否則會缺圖檔與腳本。不要把整個 GitHub 專案當成單一 Skill。

| 使用環境 | 安裝方式 |
| --- | --- |
| Claude Code | 放到專案的 `.claude/skills/kuai-kuai-bye-bye/` |
| 本機 Codex | 放到 `.agents/skills/kuai-kuai-bye-bye/` |
| 其他 AI Agent | 依該工具的技能安裝方法，保留完整資料夾 |
| 只有雲端對話 | 上傳／提供完整 Skill 與資產，操作能力依可用工具而定 |

安裝路徑來源：[Codex 官方文件](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 官方文件](https://code.claude.com/docs/en/skills)。

這些是 Agent Skill 的資料夾安裝方式，PNG 是設計素材，JSX 是 Adobe 指令碼，兩者不是 Skill 安裝檔。桌面軟體仍需要實際執行腳本或具備可用的操作連線。

## 工程師：直接執行

需要 Python 3，不需要 npm 套件、API Key 或網路連線。下列指令在本專案根目錄執行，把路徑換成自己的專案。

```bash
# 安放一包：新增專用資料夾，不改原始碼
python3 skills/kuai-kuai-bye-bye/scripts/kuai.py init --project /path/to/project

# 若有自己已取得授權的圖檔，指定它（可省略，預設使用專案附的官方公開商品圖）
python3 skills/kuai-kuai-bye-bye/scripts/kuai.py init --project /path/to/project --image /path/to/official-kuai-kuai.webp

# 明確指定要保佑的檔案
python3 skills/kuai-kuai-bye-bye/scripts/kuai.py bless --project /path/to/project --file src/main.ts

# 檢查乖乖在不在、圖檔有沒有改動
python3 skills/kuai-kuai-bye-bye/scripts/kuai.py doctor --project /path/to/project

# 不放圖片，直接在 build 時從原始碼輸出綠色乖乖
python3 skills/kuai-kuai-bye-bye/scripts/code-kuai-kuai.py \
  --event build --on-build

# 拆除單一檔案的護身註解
python3 skills/kuai-kuai-bye-bye/scripts/kuai.py remove --project /path/to/project --file src/main.ts

# 撤下整包，只刪本工具登記且未改動的資產
python3 skills/kuai-kuai-bye-bye/scripts/kuai.py uninstall --project /path/to/project
```

註解長這樣：

```js
/*
 * DIGITAL-KUAI-KUAI BEGIN
 * 乖乖拜拜護身符｜綠色密封，請勿刪除
 * 程式乖乖跑，客戶乖乖過稿。效力為玩笑設定。
 * DIGITAL-KUAI-KUAI END
 */
```

支援 Python、JavaScript／TypeScript／JSX／TSX、C／C++、CSS、Go、Rust、Java、C#、Swift、Kotlin、Shell、Ruby、YAML、TOML、HTML、Markdown、SQL 與 Lua 的註解形式。這表示腳本會選相應的註解語法，並非已在所有編譯器與框架逐一實機測試。JSON 沒有註解位置，改用旁邊的護身卡。

重跑不多放一包。30 天補貨一次，重新 `init` 更新儀式日期。到期只提醒，絕不讓 CI 因為乖乖過期失敗。`doctor` 檢查的是護身資產，不是你的程式測試。

拆除只拿掉完整的標記註解，後來修改的程式碼保留。註解本身已改動、護身資料夾有其他檔案或資產被改過，就停止並保留資料。

## 工程師：直接用程式碼輸出乖乖

首頁第二張 GIF 直接參考 [vite-plugin-kuaikuai](https://github.com/unickhow/vite-plugin-kuaikuai) 的做法：不是把 PNG 塞進程式碼，也不是先產生一個圖片檔，而是把包含包裝、五官、手腳與明暗網點的乖乖圖形寫成多行 `█▓▒░` 字元常數，在 `build` 或 `dev` 事件發生時用 ANSI 綠色輸出。這樣最簡單，沒有圖片資產，也不需要繪圖套件。

```python
ASCII_ART = r"""
                               ███████████
                           ████████████████████
                        ████████████████████████████████████▓
                      ██████████████████████████████▓▒░░░▓▓▓██
                         ...（完整字元圖見 scripts/code-kuai-kuai.py）
        ▓▓▓▓██▓▓▓▓▓    ▓▓                       ▓▓▓▓▓█▓▓▓▓▓
""".strip()

def bless(event, on_build=False, on_dev=False):
    if event == "build" and not on_build:
        return ""
    print("\033[32m" + ASCII_ART + "\033[0m")
```

`code-kuai-kuai.py` 預設只在明確指定事件時輸出。`--event build --on-build` 對應建置完成，`--event dev --on-dev` 對應開發伺服器啟動，兩個 hook 預設關閉，不會偷偷污染一般終端輸出。

## 設計師：Illustrator

首頁第一張 GIF 就是這個流程：把已授權的官方綠色乖乖置入 Illustrator，讓乖乖保持在畫板上，將它的 Layers 列拖到最底部，再把 Opacity 設為 0%，最後鎖定。這裡不關閉眼睛，也不把圖片拖出畫板放進右側面板；隱藏效果由 Opacity 0% 完成。手動操作時請使用 `assets/kuai-kuai-official-green.webp`，或用你自己的授權圖檔；不要把護身圖層納入輸出。

1. 置入官方綠色圖檔，讓圖片留在原本的畫板位置。
2. 在 Layers 面板拖曳乖乖圖層列到最底部，眼睛保持開啟。
3. 在控制列或 Appearance 面板將 Opacity 設為 `0%`。
4. 鎖定圖層，不要把圖片本身拖進右側面板。

## 設計師：Photoshop

1. 開啟 PSD。
2. 選「檔案 → 指令碼 → 瀏覽」，執行 `skills/kuai-kuai-bye-bye/scripts/photoshop-kuai.jsx`。
3. 檢查 `__乖乖拜拜_請勿刪除__` 圖層，確認位於可用的最底部、眼睛關閉、已鎖定。
4. 檢視後另存工作副本。腳本不自動儲存。

有 Background 的文件，乖乖放在它上方，不轉換原本背景。沒有腳本也可以直接置入 `assets/kuai-kuai-official-green.webp`，移到最底下、隱藏、鎖定；若使用自己的授權素材，直接置入自己的圖檔。

**只放最下面還不夠，透明背景會讓它出現在成品。隱藏這一步要做。**

## 動畫師：After Effects

1. 開啟目標合成。
2. 選「File → Scripts → Run Script File」，執行 `skills/kuai-kuai-bye-bye/scripts/after-effects-kuai.jsx`。
3. 檢查乖乖在最底部、Guide Layer 已開、Video switch 已關、圖層已鎖。
4. 保留圖檔素材來源。移動資料夾時重新連結，或使用 Collect Files 打包。

Render Settings 的 Guide Layers 使用 All Off。腳本不開始渲染、不修改既有 Render Queue，也不自動存檔。

Illustrator、Figma、Blender 的手動安放建議在 [設計工作流程](skills/kuai-kuai-bye-bye/references/design.md)，第一版沒有這三個軟體的自動腳本。

## 供奉規範 v1.0

- 只能綠色。讓 CI 保持綠色，至少在精神上。
- 保持密封。PNG 裡的封口不要剪掉。
- 乖乖可以隱藏，不能假裝測試通過。
- 「請勿刪除」是儀式名稱。真的要拆，有拆除指令。
- Bug 出現時先保留證據，祈福與除錯可以同時進行。
- 客戶還是可以改稿。乖乖無法取得客戶的管理員權限。

## 已有人做過嗎？

有，數位乖乖不是第一次出現。

- [vite-plugin-kuaikuai](https://github.com/unickhow/vite-plugin-kuaikuai)：Vite 外掛，在 build／dev 時輸出乖乖訊息，onBuild／onDev 預設關閉。
- [kuaikuai](https://github.com/nephoooooo/kuaikuai)：npm CLI，範例是 `kuaikuai && <your-app>`，啟動前祈福。
- [KKTerm](https://github.com/ryantsai/KKTerm)：以乖乖文化命名的終端與連線工具，並非安放護身符的同類產品。

這版的重點是讓 AI 執行安放儀式，並把程式碼、設計圖層與動畫合成放在同一套工作流程。上述專案只有研究參考，沒有把它們的程式或圖片搬進來。完整查證在 [研究紀錄](skills/kuai-kuai-bye-bye/references/research.md)。

## 罷工與缺貨消息

截至 2026-10-02，乖乖中壢舊廠的賣地與遷廠爭議引發罷工，工會於當天清晨 5 點開始行動。這讓「乖乖拜拜」多了一層告別的聯想：實體供應讓人擔心，就先在專案裡安放一包數位的。

新聞談的是中壢廠、遷廠與員工保障，沒有確認乖乖整家公司永久停業，也沒有確認全台已斷貨。[聯合報最新報導，2026-10-02 12:20](https://udn.com/news/story/7240/9790433)

這個專案開的是科技工作者相信乖乖的玩笑。做出實體乖乖的人，也應該被好好對待。

## 驗證與限制

執行 `python3 -m unittest discover -s tests -v`，檢查安放與拆除是否保留 BOM、CRLF、shebang、Python 編碼宣告、Markdown frontmatter、HTML doctype 與後續原始碼改動，也檢查重跑、JSON 拒絕、symlink 拒絕、修改過的資產保留，以及程式碼 hook 是否只在指定事件開啟時輸出。

Adobe JSX 已做 JavaScript 語法檢查，尚未在 Photoshop／After Effects 桌面軟體實機驗證。第一版請先在專案副本測試，檢查輸出沒有乖乖，再儲存自己的工作檔。

## 授權與素材

MIT 授權適用於本專案提供的程式與文件。官方乖乖包裝圖檔不是本專案創作，也不因放入此倉庫而改變原有著作權、商標權或授權條件；使用者應依自己的授權範圍使用。商品圖來源：[乖乖官方網站](https://www.kuai.com.tw/web/product/product_in.jsp?lang=tw&pd_id=PD1703181127376)。

作者：Hans 林思翰
