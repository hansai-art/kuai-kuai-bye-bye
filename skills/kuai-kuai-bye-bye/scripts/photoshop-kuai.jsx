#target photoshop
/* Add one hidden, locked original talisman; never save or overwrite the PSD. */
(function () {
    var NAME = "__乖乖拜拜_請勿刪除__";
    if (!app.documents.length) { alert("先開啟要保佑的 Photoshop 文件。"); return; }
    var target = app.activeDocument;
    function find(layers) {
        for (var i = 0; i < layers.length; i++) {
            if ((layers[i].name === NAME || layers[i].name === "__數位乖乖_請勿刪除__")) return true;
            if (layers[i].typename === "LayerSet" && find(layers[i].layers)) return true;
        }
        return false;
    }
    if (find(target.layers)) { alert("乖乖已在原位，請檢查是否隱藏並鎖定。"); return; }
    var file = new File(new File($.fileName).parent.parent.fsName + "/assets/kuai-kuai-bye-bye.png");
    if (!file.exists) file = File.openDialog("選擇 kuai-kuai-bye-bye.png");
    if (!file || !file.exists) return;
    var originalLayer = target.activeLayer;
    var source = null;
    var added = null;
    var previousDialogs = app.displayDialogs;
    try {
        app.displayDialogs = DialogModes.NO;
        source = app.open(file);
        added = source.activeLayer.duplicate(target, ElementPlacement.PLACEATBEGINNING);
        source.close(SaveOptions.DONOTSAVECHANGES);
        source = null;
        app.activeDocument = target;
        added.name = NAME;
        added.visible = false;
        var bottom = target.layers[target.layers.length - 1];
        if (bottom !== added) {
            if (bottom.typename === "ArtLayer" && bottom.isBackgroundLayer) {
                added.move(bottom, ElementPlacement.PLACEBEFORE);
            } else {
                added.move(bottom, ElementPlacement.PLACEAFTER);
            }
        }
        added.allLocked = true;
        target.activeLayer = originalLayer;
        if (added.visible || !added.allLocked) throw new Error("可見性／鎖定狀態驗證失敗。");
        alert("乖乖已安放於底部，已隱藏並鎖定。原文件尚未儲存，請檢視圖層後自行儲存。");
    } catch (err) {
        alert("安放未完成：" + err.message + "。請檢查目前文件，尚未自動儲存。");
    } finally {
        if (source) source.close(SaveOptions.DONOTSAVECHANGES);
        app.displayDialogs = previousDialogs;
        app.activeDocument = target;
    }
}());
