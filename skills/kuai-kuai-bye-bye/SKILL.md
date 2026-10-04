---
name: kuai-kuai-bye-bye
description: 替工程師、設計師與動畫師安放乖乖拜拜護身符。當使用者說乖乖拜拜、放乖乖、程式護身符、專案祈福、圖層放乖乖、渲染保平安或認真開玩笑時，建立綠色護身資產、插入純註解，或準備 Photoshop／After Effects 保護圖層。這是台灣科技工作文化的幽默專案。
---

# 乖乖拜拜｜Kuai Kuai Bye Bye

把「拜拜」當成祈福，把「Bye-bye」當成送走 Bug、當機與無止境改稿的願望。這是使用者選定的中英文雙關，不自行換名。

以非常認真的工程態度完成一件非常迷信的事。稱作「安放」「補貨」「保佑」，用台灣繁體中文，少解釋笑點。效力是專案的玩笑設定，不把當機率、結案率、晶片良率或身邊實測寫成經驗證的數據。

## 決定位置

1. 沿用使用者給的專案、檔案或開啟中的文件。沒有路徑時先交付圖檔與可貼的註解，不猜測並修改其他專案。
2. 程式專案讀取必要的專案規則與檔案開頭，預設只新增 `.kuai-kuai/`。只有使用者指定原始碼，才以純註解插入。
3. 設計／動畫讀取 [references/design.md](references/design.md)。具備可操作軟體的連線時直接安放並驗證，否則交付 PNG 與腳本，明確說尚未放入原生專案。
4. 下列 `<skill-dir>` 先解析成此 Skill 的真實目錄。腳本、參考與資產都相對於它。

## 工程師

用 Python 3 標準函式庫腳本，不安裝套件、不新增執行期依賴。若使用首頁示範的程式碼模式，改用 `scripts/code-kuai-kuai.py`，它把 ASCII 圖形放在原始碼裡，只在指定的 build／dev hook 觸發時用 ANSI 綠色輸出，不讀取或嵌入乖乖圖片。

```bash
python3 "<skill-dir>/scripts/kuai.py" init --project "/path/to/project"
python3 "<skill-dir>/scripts/kuai.py" bless --project "/path/to/project" --file "src/main.ts"
python3 "<skill-dir>/scripts/kuai.py" doctor --project "/path/to/project"
```

`init` 安放護身圖檔、清冊與 Markdown 護身卡。內建圖檔是乖乖官方網站公開的綠色奶油椰子包裝；使用者若有另一份已獲授權的圖檔，可用 `init --image "/path/to/official-kuai-kuai.png"` 指定 PNG、JPG、JPEG 或 WebP，腳本會複製圖檔並記錄雜湊。`bless` 只接受明確指定、位於專案內的 UTF-8 檔案，加入純註解並保留 BOM、shebang、Python 編碼宣告與換行格式。JSON 等不能容納註解的格式改用護身卡。重跑不得重複安放。

程式碼模式：`python3 "<skill-dir>/scripts/code-kuai-kuai.py" --event build --on-build`，或用 `--event dev --on-dev` 在開發啟動時輸出。兩個 hook 預設關閉，避免每次執行程式都強制輸出；`--plain` 可關閉 ANSI 顏色，方便測試與重導向。

不要更動程式邏輯、略過失敗測試、吞掉錯誤、刪除 lockfile 或新增自動更新。`doctor` 只檢查資產與註解，不把「乖乖已到位」稱為「程式已穩定」。若修改原始碼，按原專案慣例執行合適的語法／建置檢查。

補貨：重新執行 `init`。30 天是專案設定的儀式週期，到期只提醒，不阻擋開發或 CI。

拆除：`remove --project ... --file ...` 只移除已登記且完整的護身註解，保留後續程式修改。`uninstall --project ...` 移除登記的註解與未修改的護身資產，遇到改動或額外檔案停止並保留。不得因為儀式自行提交、發布或寄訊息。

## 設計師與動畫師

預設圖檔為 `assets/kuai-kuai-official-green.webp`，取自乖乖官方網站的「乖乖玉米脆條－奶油椰子」商品頁。使用者若有自己的授權素材，優先用 `init --image` 或 Adobe 腳本選檔，不要把其他網路圖片冒充官方授權素材。

首頁 Illustrator GIF 只是這套規則的示範動畫，不是安裝 Skill 後自動取得的功能。安裝後提供的是操作規則、圖檔與腳本；沒有 Illustrator 的實際操作連線時，只能交付資產與步驟，不能宣稱已自動修改文件或產生 GIF。

- Photoshop：`scripts/photoshop-kuai.jsx` 先讓使用者選擇已獲授權的 PNG、JPG、JPEG 或 WebP，安放在可用的最底部、隱藏並鎖定。底部是 Background 時放在其上方，不轉換原本背景。
- After Effects：`scripts/after-effects-kuai.jsx` 先讓使用者選擇已獲授權的圖檔，在目前合成底部安放，設成 Guide Layer、關閉可見性並鎖定。保留匯入素材，避免未來重開專案遺失來源。
- Illustrator：把已獲授權的官方綠色圖檔置入文件，保持在畫板上，將 Layers 列拖到最底部，把 Opacity 設為 0%，眼睛保持開啟並鎖定。不要把圖片拖進右側面板。沒有 Illustrator 的實際連線時，只提供圖檔與操作指引，不宣稱已修改原生文件。
- Figma、Blender 等其他軟體：只有具備實際連線與該軟體支援的方法才操作，依 design.md 安放。不要宣稱 JSX 通用所有軟體。

圖層命名 `__乖乖拜拜_請勿刪除__`，既有同名圖層不重複新增。Illustrator 流程以 Opacity 0% 隱藏，不把圖片拖進右側面板，也不以關閉眼睛取代透明度設定。保留原專案，驗證圖層、位置、Opacity、鎖定狀態與輸出排除，不自動儲存覆蓋或開始渲染。

## 回報

首句用簡短儀式回報，例如「乖乖已安放，今天交給綠色處理。」接著說實際位置與驗證結果。沒有執行原生軟體就說「圖檔與腳本已備妥，尚未放入 PSD／AEP」。靜態檢查與 Adobe 實機驗證分開說。

研究背景與公開介紹讀取 [references/research.md](references/research.md)，消息變動時重新查證。不要以全面斷貨當既定事實，也不要暗示勞工應為科技業的迷信繼續生產。官方預設圖來源記在 README，若授權範圍不同，改用使用者提供的圖檔。
