#target aftereffects
/* Add a user-selected disabled guide layer; preserve footage and never auto-save/render. */
(function () {
    var NAME = "__乖乖拜拜_請勿刪除__";
    if (!app.project || !(app.project.activeItem instanceof CompItem)) {
        alert("先開啟要保佑的 After Effects 合成。"); return;
    }
    var comp = app.project.activeItem;
    for (var i = 1; i <= comp.numLayers; i++) {
        if ((comp.layer(i).name === NAME || comp.layer(i).name === "__數位乖乖_請勿刪除__")) {
            alert("乖乖已在原位，請檢查 Guide Layer、可見性與鎖定。"); return;
        }
    }
    var file = File.openDialog("選擇已獲授權的乖乖圖檔（PNG、JPG、JPEG 或 WebP）", "*.png;*.jpg;*.jpeg;*.webp");
    if (!file || !file.exists) return;
    app.beginUndoGroup("安放數位乖乖");
    try {
        var footage = null;
        for (var n = 1; n <= app.project.numItems; n++) {
            var item = app.project.item(n);
            if (item instanceof FootageItem && item.file && item.file.fsName === file.fsName) {
                footage = item; break;
            }
        }
        if (!footage) footage = app.project.importFile(new ImportOptions(file));
        var layer = comp.layers.add(footage);
        layer.name = NAME;
        layer.guideLayer = true;
        layer.enabled = false;
        layer.moveToEnd();
        layer.locked = true;
        if (layer.enabled || !layer.guideLayer || !layer.locked || layer.index !== comp.numLayers) {
            throw new Error("保護圖層狀態驗證失敗。");
        }
        alert("乖乖已安放於合成最底部，Guide Layer 已開、可見性已關、圖層已鎖。尚未儲存或渲染。請保留 PNG 來源。");
    } catch (err) {
        alert("安放未完成：" + err.message + "。可用 Undo 撤回這次安放。");
    } finally {
        app.endUndoGroup();
    }
}());
