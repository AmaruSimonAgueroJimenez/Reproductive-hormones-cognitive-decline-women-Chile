#!/usr/bin/env python3
"""Prepare or verify the public slide HTML without changing scientific content.

Python standard library only. The only permitted HTML edits are replacement of
PNG image src data URIs by relative URLs to byte-identical original PNG files.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "docs/combined_project_key_results_slides.html"
MANIFEST = ROOT / "publication_manifest.json"
EXPECTED = {"slides": 29, "image_placements": 24, "original_figures": 15, "tables": 3, "table_cells": 36}
IMG = re.compile(rb"<img\b[^>]*>", re.IGNORECASE)
SRC = re.compile(rb"\bsrc=(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)
FORBIDDEN = {".ppt", ".pptx", ".pptm", ".pps", ".ppsx", ".ppsm", ".doc", ".docx", ".parquet", ".sav", ".dta", ".sas7bdat"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Deck(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slide_ids: list[str] = []
        self.images: list[str] = []
        self.figure_links: set[str] = set()
        self.local_links: set[str] = set()
        self.resource_links: set[str] = set()
        self.cells = 0
        self.tables = 0
        self.external_resources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "section":
            self.slide_ids.append(values.get("id") or "")
        if tag == "img":
            self.images.append(values.get("src") or "")
        self.cells += tag in {"td", "th"}
        self.tables += tag == "table"
        for attribute in ("src", "href", "poster", "data-src", "data-background-image"):
            value = values.get(attribute) or ""
            if not value or value.startswith(("data:", "#")):
                continue
            self.resource_links.add(value)
            if urlsplit(value).scheme or value.startswith("//"):
                if tag != "a":
                    self.external_resources.append(value)
                continue
            self.local_links.add(value)
            if tag == "a" and value.lower().endswith(".png"):
                self.figure_links.add(value)


def parse(data: bytes) -> Deck:
    result = Deck()
    result.feed(data.decode("utf-8"))
    return result


def resolve_link(value: str) -> Path:
    path = (DECK.parent / unquote(value.split("#", 1)[0].split("?", 1)[0])).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Local link leaves the presentation directory: {value}")
    if not path.is_file():
        raise ValueError(f"Missing local presentation file: {value}")
    return path


def figure_map(deck: Deck) -> dict[str, str]:
    figures: dict[str, str] = {}
    for link in sorted(deck.figure_links):
        path = resolve_link(link)
        if path.suffix.lower() != ".png":
            raise ValueError("Only original PNG figures may replace embedded images.")
        figures[digest(path.read_bytes())] = link
    if len(figures) != EXPECTED["original_figures"]:
        raise ValueError("Expected 15 distinct original figure hashes.")
    return figures


def image_hash(value: str) -> str:
    if value.startswith("data:image/png;base64,"):
        return digest(base64.b64decode(value.split(",", 1)[1], validate=True))
    if value.startswith("data:"):
        raise ValueError("Unexpected embedded image format.")
    return digest(resolve_link(value).read_bytes())


def masked_images(data: bytes) -> bytes:
    """Canonical bytes proving that nothing outside img src values changed."""
    return IMG.sub(lambda match: SRC.sub(lambda src: b"src=" + src[1] + b"ORIGINAL-PNG" + src[1], match[0]), data)


def verify(data: bytes, require_optimized: bool) -> dict:
    deck = parse(data)
    actual = {"slides": len(deck.slide_ids), "image_placements": len(deck.images), "original_figures": len(set(map(image_hash, deck.images))), "tables": deck.tables, "table_cells": deck.cells}
    if actual != EXPECTED:
        raise ValueError(f"Presentation structure differs from the reviewed deck: {actual}")
    if deck.slide_ids != [f"slide-{i}" for i in range(1, 30)]:
        raise ValueError("Slide order or anchors changed.")
    originals = figure_map(deck)
    if set(map(image_hash, deck.images)) != set(originals):
        raise ValueError("Images differ from the original figure downloads.")
    for value in deck.local_links:
        resolve_link(value)
    if deck.external_resources:
        raise ValueError(f"Unexpected external runtime resource: {deck.external_resources}")
    if require_optimized and any(value.startswith("data:") for value in deck.images):
        raise ValueError("The HTML still contains embedded PNG copies.")
    text = data.decode("utf-8")
    for private_path in ("/Users/", "/Volumes/", "file:///"):
        if private_path in text:
            raise ValueError("A private filesystem path appears in the presentation.")
    if any(Path(urlsplit(value).path).suffix.lower() in {".ppt", ".pptx", ".pptm", ".pps", ".ppsx", ".ppsm", ".doc", ".docx"} for value in deck.resource_links):
        raise ValueError("An Office document reference appears in the presentation.")
    qmd = ROOT / "docs/combined_project_key_results_slides.qmd"
    source = ROOT / "docs/combined_project_key_results_slides_source.txt"
    if qmd.read_bytes() != source.read_bytes():
        raise ValueError("Downloadable source does not exactly match the QMD.")
    return {**actual, "all_local_links_resolve": True, "qmd_download_exact": True, "original_pngs_exact": True}


def public_files() -> list[Path]:
    paths = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_file() or path == MANIFEST:
            continue
        if any(part in {".git", ".quarto", "__pycache__"} or part.endswith("_files") for part in relative.parts):
            continue
        if path.name == ".DS_Store" or path.name.endswith(".quarto_ipynb"):
            continue
        if path.suffix.lower() in FORBIDDEN:
            raise ValueError(f"Excluded data or Office file found: {relative}")
        paths.append(path)
    return paths


def write_manifest(source_data: bytes, output_data: bytes, replaced: int, verification: dict) -> None:
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    source_hash = digest(source_data)
    if replaced == 0 and digest(output_data) == previous.get("html_delivery_sha256"):
        source_hash = previous.get("source_embedded_html_sha256", source_hash)
    originals = figure_map(parse(output_data))
    payload = {
        "schema_version": 1,
        "scope": "Combined two-part presentation source, aggregate figure PNGs and online HTML only; underlying analyses and source records are not included.",
        "intended_repository": "https://github.com/AmaruSimonAgueroJimenez/Reproductive-hormones-cognitive-decline-women-Chile",
        "source_embedded_html_sha256": source_hash,
        "html_delivery_sha256": digest(output_data),
        "optimization": {
            "method": "Replace only embedded PNG img src values with relative URLs to byte-identical original PNGs.",
            "image_placements": 24,
            "unique_originals": 15,
            "non_image_src_bytes_sha256": digest(masked_images(output_data)),
            "all_other_html_bytes_preserved": True,
        },
        "verification": verification,
        "original_figures": [{"path": str(resolve_link(link).relative_to(ROOT)), "sha256": sha} for sha, link in sorted(originals.items(), key=lambda item: item[1])],
        "files": [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path.read_bytes())} for path in public_files()],
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_manifest() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    listed = {row["path"]: row for row in manifest["files"]}
    current = {str(path.relative_to(ROOT)): path for path in public_files()}
    if set(listed) != set(current):
        raise ValueError("Public file inventory differs from the manifest.")
    for name, path in current.items():
        if digest(path.read_bytes()) != listed[name]["sha256"] or path.stat().st_size != listed[name]["bytes"]:
            raise ValueError(f"File hash or size differs from the manifest: {name}")
    if manifest["html_delivery_sha256"] != digest(DECK.read_bytes()):
        raise ValueError("Presentation HTML hash differs from the manifest.")
    return len(current)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without modifying files.")
    args = parser.parse_args()
    source_data = DECK.read_bytes()
    if args.check:
        verification = verify(source_data, require_optimized=True)
        print(json.dumps({"status": "pass", "mode": "check", **verification, "manifest_files_verified": check_manifest()}, indent=2))
        return
    verify(source_data, require_optimized=False)
    originals = figure_map(parse(source_data))
    replaced = 0

    def replace_tag(match: re.Match[bytes]) -> bytes:
        def replace_src(src: re.Match[bytes]) -> bytes:
            nonlocal replaced
            value = html.unescape(src[2].decode("utf-8"))
            if not value.startswith("data:image/png;base64,"):
                return src[0]
            relative_url = originals[image_hash(value)]
            replaced += 1
            return b"src=" + src[1] + html.escape(relative_url, quote=True).encode("utf-8") + src[1]
        return SRC.sub(replace_src, match[0])

    output_data = IMG.sub(replace_tag, source_data)
    if masked_images(source_data) != masked_images(output_data):
        raise ValueError("An HTML byte outside an image src changed.")
    verification = verify(output_data, require_optimized=True)
    temporary = DECK.with_suffix(".html.preparing")
    temporary.write_bytes(output_data)
    temporary.replace(DECK)
    write_manifest(source_data, output_data, replaced, verification)
    print(json.dumps({"status": "pass", "mode": "prepare", **verification, "embedded_png_placements_replaced": replaced, "html_bytes_before": len(source_data), "html_bytes_after": len(output_data), "manifest_files_verified": check_manifest()}, indent=2))


if __name__ == "__main__":
    main()
