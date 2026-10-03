import ast
import codecs
import importlib.util
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/kuai-kuai-bye-bye/scripts/kuai.py"
spec = importlib.util.spec_from_file_location("kuai", SCRIPT)
kuai = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kuai)

class RitualTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        with redirect_stdout(StringIO()):
            kuai.initialize(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_python_ast_shebang_encoding_crlf_and_roundtrip(self):
        raw = b'#!/usr/bin/env python3\r\n# coding: utf-8\r\n"""module doc"""\r\nfrom __future__ import annotations\r\nx = 3\r\n'
        p = self.root / "main.py"
        p.write_bytes(raw)
        kuai.bless(self.root, "main.py")
        blessed = p.read_bytes()
        self.assertTrue(blessed.startswith(b'#!/usr/bin/env python3\r\n# coding: utf-8\r\n'))
        self.assertEqual(ast.dump(ast.parse(raw)), ast.dump(ast.parse(blessed)))
        self.assertNotIn(b'\n', blessed.replace(b'\r\n', b''))
        kuai.bless(self.root, "main.py")
        self.assertEqual(p.read_bytes(), blessed)
        kuai.remove_one(self.root, kuai.load(self.root), "main.py")
        self.assertEqual(p.read_bytes(), raw)

    def test_bom_preserved(self):
        p = self.root / "main.ts"
        raw = codecs.BOM_UTF8 + b'const x = 1;'
        p.write_bytes(raw)
        kuai.bless(self.root, "main.ts")
        self.assertTrue(p.read_bytes().startswith(codecs.BOM_UTF8))
        kuai.remove_one(self.root, kuai.load(self.root), "main.ts")
        self.assertEqual(p.read_bytes(), raw)

    def test_js_directive_stays_effective(self):
        p = self.root / "main.cjs"
        raw = b'"use strict";\nconsole.log((function () { return this; })() === undefined);\n'
        p.write_bytes(raw)
        before = subprocess.check_output(["node", str(p)])
        kuai.bless(self.root, "main.cjs")
        self.assertEqual(subprocess.check_output(["node", str(p)]), before)

    def test_later_source_changes_survive_remove(self):
        p = self.root / "main.py"
        p.write_bytes(b'x = 1\n')
        kuai.bless(self.root, "main.py")
        p.write_bytes(p.read_bytes().replace(b'x = 1', b'x = 2'))
        kuai.remove_one(self.root, kuai.load(self.root), "main.py")
        self.assertEqual(p.read_bytes(), b'x = 2\n')

    def test_json_is_unchanged_on_refusal(self):
        p = self.root / "package.json"
        raw = b'{"name":"test"}'
        p.write_bytes(raw)
        with self.assertRaises(ValueError): kuai.bless(self.root, "package.json")
        self.assertEqual(p.read_bytes(), raw)

    def test_non_utf8_and_ascii_cookie_refused(self):
        p = self.root / "main.py"
        for raw in [b'# coding: ascii\nx = 1\n', b'x = "\xff"\n']:
            p.write_bytes(raw)
            with self.assertRaises(ValueError): kuai.bless(self.root, "main.py")
            self.assertEqual(p.read_bytes(), raw)

    def test_paths_and_symlink_refused(self):
        for path in ["../outside.py", "/tmp/outside.py", "node_modules/main.js", ".git/config"]:
            with self.assertRaises(ValueError): kuai.source_path(self.root, path)
        (self.root / "real.py").write_text('x = 1\n')
        (self.root / "link.py").symlink_to(self.root / "real.py")
        with self.assertRaises(ValueError): kuai.bless(self.root, "link.py")

    def test_markdown_frontmatter_preserved(self):
        p = self.root / "notes.md"
        raw = b'---\ntitle: test\n---\n# Hello\n'
        p.write_bytes(raw)
        kuai.bless(self.root, "notes.md")
        self.assertTrue(p.read_bytes().startswith(b'---\ntitle: test\n---\n'))
        kuai.remove_one(self.root, kuai.load(self.root), "notes.md")
        self.assertEqual(p.read_bytes(), raw)

    def test_html_doctype_preserved(self):
        p = self.root / "page.html"
        raw = b'<!DOCTYPE html><html></html>'
        p.write_bytes(raw)
        kuai.bless(self.root, "page.html")
        self.assertTrue(p.read_bytes().startswith(b'<!DOCTYPE html>'))
        kuai.remove_one(self.root, kuai.load(self.root), "page.html")
        self.assertEqual(p.read_bytes(), raw)

    def test_modified_comment_blocks_uninstall_without_partial_change(self):
        for name in ["a.py", "b.py"]:
            (self.root / name).write_text("x = 1\n")
            kuai.bless(self.root, name)
        a = (self.root / "a.py").read_bytes()
        p = self.root / "b.py"
        p.write_bytes(p.read_bytes().replace('請勿刪除'.encode(), b'modified'))
        with self.assertRaises(ValueError): kuai.uninstall(self.root)
        self.assertEqual((self.root / "a.py").read_bytes(), a)
        self.assertTrue((self.root / ".kuai-kuai/manifest.json").exists())

    def test_extra_file_blocks_uninstall(self):
        p = self.root / ".kuai-kuai/important.txt"
        p.write_text("keep")
        with self.assertRaises(ValueError): kuai.uninstall(self.root)
        self.assertEqual(p.read_text(), "keep")

    def test_restock_doctor_and_clean_uninstall(self):
        kuai.initialize(self.root)
        data = kuai.load(self.root)
        data["restock_on"] = "2000-01-01"
        kuai.save(self.root, data)
        self.assertEqual(kuai.doctor(self.root), 0)
        kuai.uninstall(self.root)
        self.assertFalse((self.root / ".kuai-kuai").exists())

if __name__ == "__main__":
    unittest.main()
