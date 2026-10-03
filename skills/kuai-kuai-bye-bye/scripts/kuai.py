#!/usr/bin/env python3
"""Reversible talisman rituals using Python's standard library."""
import argparse
import base64
import codecs
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
MARK = "DIGITAL-KUAI-KUAI"
SHRINE = ".kuai-kuai"
HASH = {".py", ".sh", ".bash", ".rb", ".yaml", ".yml", ".toml"}
BLOCK = {".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".c", ".cpp", ".h", ".hpp", ".css", ".go", ".rs", ".java", ".cs", ".swift", ".kt"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_IMAGE = "kuai-kuai-official-green.webp"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def project_path(value):
    root = Path(value).expanduser().resolve(strict=True)
    if not root.is_dir() or (root / SHRINE).is_symlink():
        raise ValueError("使用既有專案資料夾，護身資料夾不能是符號連結。")
    return root

def source_path(root, value):
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("--file 必須是專案內的相對路徑。")
    if set(relative.parts) & {".git", SHRINE, "node_modules", "vendor", "dist", "build"}:
        raise ValueError("不修改版控內部、依賴或建置輸出。")
    path = root / relative
    cursor = path
    while cursor != root:
        if cursor.is_symlink():
            raise ValueError("不修改符號連結或其下的檔案。")
        cursor = cursor.parent
    path = path.resolve(strict=True)
    path.relative_to(root)
    if not path.is_file():
        raise ValueError("指定路徑不是檔案。")
    return path

def image_path(value):
    path = Path(value).expanduser().resolve(strict=True)
    if path.is_symlink() or not path.is_file():
        raise ValueError("護身圖檔必須是實際存在的檔案，不能是符號連結。")
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("護身圖檔只接受 PNG、JPG、JPEG 或 WebP。")
    return path

def load(root):
    path = root / SHRINE / "manifest.json"
    if path.is_symlink():
        raise ValueError("清冊不能是符號連結。")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("project") != MARK or data.get("version") != 1:
        raise ValueError("不是本工具建立的護身清冊。")
    assets = set(data["assets"])
    images = assets - {"talisman.md"}
    if "talisman.md" not in assets or len(images) != 1 or Path(next(iter(images))).suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError("護身資產清單異常。")
    return data

def save(root, data):
    path = root / SHRINE / "manifest.json"
    if path.is_symlink():
        raise ValueError("清冊不能是符號連結。")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def initialize(root, image=None):
    folder = root / SHRINE
    if folder.exists():
        if image:
            raise ValueError("護身資料夾已存在；要改用另一張圖，請先檢查並移除既有儀式後再 init。")
        data = load(root)
        for name, expected in data["assets"].items():
            path = folder / name
            if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != expected:
                raise ValueError("資產已改動或遺失，先處理後再補貨：" + name)
    else:
        selected = image_path(image) if image else (SKILL / "assets" / DEFAULT_IMAGE)
        payload = selected.read_bytes()
        card = "# 乖乖拜拜護身卡\n\n程式乖乖跑，客戶乖乖過稿。\n\n綠色、密封、請勿刪除。效力屬於專案玩笑設定。\n安放狀態見 manifest.json，補貨不會中斷 CI。\n".encode("utf-8")
        folder.mkdir()
        data = {"project": MARK, "version": 1, "assets": {}, "files": {}}
        image_name = DEFAULT_IMAGE if not image else "kuai-kuai-image" + selected.suffix.lower()
        for name, content in {image_name: payload, "talisman.md": card}.items():
            (folder / name).write_bytes(content)
            data["assets"][name] = digest(content)
    data["blessed_on"] = date.today().isoformat()
    data["restock_on"] = (date.today() + timedelta(days=30)).isoformat()
    save(root, data)
    print("乖乖已安放：" + str(folder) + "。補貨日 " + data["restock_on"] + "。")

def comment(extension, nl):
    lines = [MARK + " BEGIN", "乖乖拜拜護身符｜綠色密封，請勿刪除", "程式乖乖跑，客戶乖乖過稿。效力為玩笑設定。", MARK + " END"]
    if extension in HASH:
        result = nl.join("# " + x for x in lines)
    elif extension in BLOCK:
        result = "/*" + nl + nl.join(" * " + x for x in lines) + nl + " */"
    elif extension in {".html", ".htm", ".md"}:
        result = "<!--" + nl + nl.join(lines) + nl + "-->"
    elif extension in {".sql", ".lua"}:
        result = nl.join("-- " + x for x in lines)
    else:
        raise ValueError("此格式不支援註解，改用 .kuai-kuai/talisman.md：" + extension)
    return (result + nl).encode("utf-8")

def bless(root, value):
    path = source_path(root, value)
    data = load(root)
    key = path.relative_to(root).as_posix()
    raw = path.read_bytes()
    raw.decode("utf-8-sig")
    if key in data["files"]:
        if raw.count(base64.b64decode(data["files"][key]["block"])) != 1:
            raise ValueError("既有註解已改動，不重複安放。")
        print("乖乖已在原位：" + key)
        return
    if MARK.encode() in raw:
        raise ValueError("找到未登記的乖乖標記，先確認來源。")
    nl = "\r\n" if b"\r\n" in raw else "\n"
    block = comment(path.suffix.lower(), nl)
    bom = len(codecs.BOM_UTF8) if raw.startswith(codecs.BOM_UTF8) else 0
    offset = bom
    lines = raw[bom:].splitlines(keepends=True)
    if lines and lines[0].startswith(b"#!"):
        if not lines[0].endswith(b"\n"):
            raise ValueError("shebang 末尾缺少換行。")
        offset += len(lines[0])
    if path.suffix.lower() == ".py":
        for index, line in enumerate(lines[:2]):
            coding = re.match(rb"^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)", line)
            if coding:
                if codecs.lookup(coding.group(1).decode("ascii")).name != "utf-8":
                    raise ValueError("Python 使用非 UTF-8 編碼宣告，改用護身卡。")
                if not line.endswith(b"\n"):
                    raise ValueError("編碼宣告末尾缺少換行。")
                offset = max(offset, bom + sum(map(len, lines[:index + 1])))
    if path.suffix.lower() in {".html", ".htm"}:
        match = re.match(rb"\s*<!doctype[^>]*>[^\S\r\n]*(?:\r?\n)?", raw[bom:], flags=re.I)
        if match:
            offset = bom + match.end()
            if not raw[:offset].endswith(b"\n"):
                block = nl.encode() + block
    if path.suffix.lower() == ".md" and lines and lines[0].strip() == b"---":
        closing = next((i for i, line in enumerate(lines[1:], 1) if line.strip() in {b"---", b"..."}), None)
        if closing is None or not lines[closing].endswith(b"\n"):
            raise ValueError("Markdown frontmatter 缺少完整結尾，改用護身卡。")
        offset = bom + sum(map(len, lines[:closing + 1]))
    data["files"][key] = {"block": base64.b64encode(block).decode("ascii")}
    path.write_bytes(raw[:offset] + block + raw[offset:])
    save(root, data)
    print("護身註解已安放：" + key + "。")

def remove_one(root, data, value):
    path = source_path(root, value)
    key = path.relative_to(root).as_posix()
    if key not in data["files"]:
        raise ValueError("此檔案沒有登記的乖乖：" + key)
    block = base64.b64decode(data["files"][key]["block"])
    raw = path.read_bytes()
    if raw.count(block) != 1:
        raise ValueError("註解已改動，保留檔案並停止：" + key)
    path.write_bytes(raw.replace(block, b"", 1))
    del data["files"][key]
    save(root, data)
    print("已拆除護身註解：" + key)

def doctor(root):
    data = load(root)
    problems = []
    for name, expected in data["assets"].items():
        path = root / SHRINE / name
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != expected:
            problems.append("資產遺失／改動：" + name)
    for key, item in data["files"].items():
        if source_path(root, key).read_bytes().count(base64.b64decode(item["block"])) != 1:
            problems.append("註解遺失／改動：" + key)
    if problems:
        print("\n".join(problems))
        return 1
    print("乖乖已到位：資產完整，護身註解 " + str(len(data["files"])) + " 份。")
    if date.today() >= date.fromisoformat(data["restock_on"]):
        print("到了補貨日，請重新 init。此提醒不阻擋工作。")
    print("沒有執行專案測試，也沒有測量當機率或結案率。")
    return 0

def uninstall(root):
    data = load(root)
    folder = root / SHRINE
    owned = set(data["assets"]) | {"manifest.json"}
    if {p.name for p in folder.iterdir()} != owned:
        raise ValueError("護身資料夾有額外檔案，保留資料並停止。")
    for name, expected in data["assets"].items():
        path = folder / name
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError("資產已改動，保留資料並停止：" + name)
    for key, item in data["files"].items():
        if source_path(root, key).read_bytes().count(base64.b64decode(item["block"])) != 1:
            raise ValueError("註解已改動，保留資料並停止：" + key)
    for key in list(data["files"]):
        remove_one(root, data, key)
    for name in owned:
        (folder / name).unlink()
    folder.rmdir()
    print("乖乖已撤下。程式保留，儀式結束。")

def main():
    parser = argparse.ArgumentParser(description="乖乖拜拜護身符：認真安放，效力屬於玩笑。")
    parser.add_argument("command", choices=["init", "bless", "doctor", "remove", "uninstall"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--file")
    parser.add_argument("--image", help="init 時使用已獲授權的 PNG、JPG、JPEG 或 WebP 圖檔")
    args = parser.parse_args()
    if args.command in {"bless", "remove"} and not args.file:
        parser.error("bless／remove 需要 --file")
    try:
        root = project_path(args.project)
        if args.command == "init": initialize(root, args.image)
        elif args.command == "bless": bless(root, args.file)
        elif args.command == "doctor": return doctor(root)
        elif args.command == "remove": remove_one(root, load(root), args.file)
        else: uninstall(root)
        return 0
    except (OSError, ValueError, KeyError, TypeError, LookupError) as exc:
        print("安放未完成：" + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
