"""Check published preview provenance and local documentation links."""
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class AssetTests(unittest.TestCase):
    def test_preview_manifest_matches_actual_component_sources(self):
        manifest = json.loads((ROOT / "images/manifest.json").read_text(encoding="utf-8"))
        sources = {p.stem: p for p in (ROOT / "CustomScripts").glob("*.py")}
        self.assertEqual(set(manifest), set(sources))
        for name, source in sources.items():
            with self.subTest(component=name):
                text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
                self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), manifest[name]["source_sha256"])
                function = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
                parameters = function.args.args[-len(function.args.defaults):]
                defaults = {p.arg: ast.literal_eval(v) for p, v in zip(parameters, function.args.defaults)}
                self.assertEqual(defaults, manifest[name]["defaults"])

    def test_all_preview_files_exist_and_have_valid_image_headers(self):
        manifest = json.loads((ROOT / "images/manifest.json").read_text(encoding="utf-8"))
        for name, item in manifest.items():
            with self.subTest(component=name):
                png = (ROOT / "images" / item["png"]).read_bytes()
                self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", png[16:24])
                self.assertGreaterEqual(width, 1200)
                self.assertGreaterEqual(height, 800)
                svg = ET.parse(ROOT / "images" / item["svg"]).getroot()
                self.assertEqual(svg.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertTrue((ROOT / "images/component-gallery.jpg").read_bytes().startswith(b"\xff\xd8"))

    def test_local_markdown_links_resolve(self):
        for document in [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]:
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                path = unquote(target.split("#", 1)[0])
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / path).is_file())


if __name__ == "__main__":
    unittest.main()
