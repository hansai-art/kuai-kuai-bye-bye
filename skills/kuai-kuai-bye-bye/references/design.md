# 設計與動畫安放規則

## Photoshop

開啟 PSD，選「檔案 → 指令碼 → 瀏覽」，執行 scripts/photoshop-kuai.jsx。腳本會讀取同一個 Skill 的 assets/kuai-kuai-bye-bye.png。保留整個資料夾結構，或依選檔視窗指定 PNG。

驗收：找到 `__乖乖拜拜_請勿刪除__`，確認是像素圖層、位於底部、眼睛關閉、已鎖定。若有 Background，它保持原狀，乖乖位於其正上方。既有同名圖層不重複新增。原 PSD 不自動儲存，檢視後另存工作副本。

手動方式：置入 PNG → 改圖層名稱 → 移至底部 → 關閉眼睛 → 鎖定。即使畫面是全透明，也不能露出乖乖。展示儀式時可暫時打開眼睛，交付前關閉。

## After Effects

開啟目標合成，選「File → Scripts → Run Script File」，執行 scripts/after-effects-kuai.jsx。

驗收：名稱正確、圖層在最底部、Guide Layer 為 true、Video switch 關閉、Locked 為 true。Guide Layer 是另一層保護，Render Settings 的 Guide Layers 仍應選 All Off。腳本關閉可見性避免不同輸出設定誤帶入圖像，不修改既有 Render Queue。

PNG 是外部素材，移動資料夾後要重連素材。先複製到專案的固定 assets 目錄，再執行腳本，必要時改由選檔指定該 PNG。使用 Collect Files 打包時保留此來源。腳本不自動儲存、不啟動渲染，一次 Undo 可撤回新增操作。

## 其他軟體

| 軟體 | 安放方式 | 輸出保護 |
| --- | --- | --- |
| Illustrator | 專用底層置入 PNG | 隱藏、鎖定，保留原圖層 |
| Figma | Frame 外或專用群組置入 PNG | 關閉可見性，鎖定，不納入匯出選取 |
| Blender | 專用 Collection 放 Image Empty | 關閉 viewport／render，保留貼圖路徑 |
| 其他 | 用該軟體原生支援的方法新增一層 | 隱藏、排除輸出、鎖定或可用的保護方式 |

這些是安放建議，第一版沒有附對應的自動腳本。沒有 API／外掛連線時交付資產與操作方式，不宣稱已改好原生文件。

## 實機驗證界線

JSX 需在 Adobe 桌面軟體內執行，Node 的語法解析不能證明 Adobe 物件模型操作成功。發布時分別標示「語法檢查」「Adobe 實機測試」。遇到錯誤保留目前文件，回報軟體版本與實際錯誤，不嘗試覆蓋儲存。

Adobe 官方：[Guide Layers 與渲染](https://helpx.adobe.com/il_en/after-effects/desktop/render-and-export/basics-of-rendering-and-exporting/basics-rendering-exporting.html)、[Photoshop Layer API](https://developer.adobe.com/photoshop/uxp/2022/ps-reference/classes/layer)。後者是 UXP API，與本專案 ExtendScript JSX 不是同一個執行環境。
