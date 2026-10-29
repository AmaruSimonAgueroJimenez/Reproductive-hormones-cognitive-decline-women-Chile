#!/usr/bin/env python3
"""Prepare and verify the public research site using Python's standard library.

The publishing copy retains the complete report prose, numerical tables, folded
code, original image bytes and Quarto runtime. Only embedded PNG src values,
a PowerPoint download anchor and an added report navigation bar may differ from
the reviewed HTML. Canonical analytical sources are never modified by this tool.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'publication_manifest.json'
PROVENANCE = ROOT / 'site_provenance.json'
IMG = re.compile(rb'<img\b[^>]*>', re.I)
SRC = re.compile(rb'\bsrc=([\'"])(.*?)\1', re.I | re.S)
BODY = re.compile(rb'<body\b[^>]*>', re.I)
POWERPOINT = {'.ppt', '.pptx', '.pptm', '.pps', '.ppsx', '.ppsm'}
FORBIDDEN = POWERPOINT | {'.parquet', '.sav', '.dta', '.sas7bdat'}
NAV_START = b'<!-- PUBLIC-RESEARCH-NAV-START -->'
NAV_END = b'<!-- PUBLIC-RESEARCH-NAV-END -->'
NAV_RE = re.compile(re.escape(NAV_START) + rb'.*?' + re.escape(NAV_END), re.S)
ANCHOR = re.compile(rb'<a\b[^>]*\bhref=([\'"])([^\'"]+)\1[^>]*>.*?</a>', re.I | re.S)
NAV = NAV_START + b'''
<style>
#research-site-nav{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem 1.15rem;padding:.75rem max(1rem,calc((100vw - 1250px)/2));border-bottom:1px solid #dbe3e8;background:#f5f8fa;font:600 .87rem/1.45 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;position:relative;z-index:3}
#research-site-nav a{color:#245d79;text-decoration:none;padding:.25rem 0;border-bottom:1px solid transparent}
#research-site-nav a:hover{border-bottom-color:currentColor}
#research-site-nav a:focus-visible{outline:3px solid #287fa8;outline-offset:4px}
#research-site-nav a:first-child{color:#183849;margin-right:.35rem}
@media(max-width:600px){#research-site-nav{font-size:.79rem;gap:.25rem .8rem;padding:.65rem 1rem}}
</style>
<nav id="research-site-nav" aria-label="Research website">
<a href="../index.html">Research home</a>
<a href="descriptive_methods_results.html">Part I: descriptive evidence</a>
<a href="reproductive_life_course.html">Part II: connected analyses</a>
<a href="access_diagnostic_recording_extension.html">Administrative extension</a>
<a href="combined_project_key_results_slides.html">Combined presentation</a>
</nav>
''' + NAV_END


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_powerpoint_links(data: bytes) -> bytes:
    marker = b'<!-- UNPUBLISHED-POWERPOINT-DOWNLOAD -->'
    separator = rb'[ \t]*(?:\xc2\xb7|&middot;|&#183;)[ \t]*'
    def replace(match: re.Match[bytes]) -> bytes:
        href = html.unescape(match[2].decode('utf-8'))
        return marker if Path(urlsplit(href).path).suffix.lower() in POWERPOINT else match[0]
    result = ANCHOR.sub(replace, data)
    # Remove one adjacent list separator with the omitted download link. Prefer
    # the preceding separator so the remaining links retain their original one.
    result = re.sub(separator + re.escape(marker), b'', result)
    result = re.sub(re.escape(marker) + separator, b'', result)
    return result.replace(marker, b'')


def normalized_html(data: bytes) -> bytes:
    data = NAV_RE.sub(b'', strip_powerpoint_links(data))
    return IMG.sub(lambda tag: SRC.sub(lambda src: b'src=' + src[1] + b'ORIGINAL-PNG' + src[1], tag[0]), data)


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.local_links: set[str] = set()
        self.resource_links: set[str] = set()
        self.external_resources: set[str] = set()
        self.images: list[str] = []
        self.slide_ids: list[str] = []
        self.tables = 0
        self.cells = 0
        self.details = 0
        self.code_folds = 0
        self.has_report_nav = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get('class') or '').split()
        self.tables += tag == 'table'
        self.cells += tag in {'td', 'th'}
        self.details += tag == 'details'
        self.code_folds += tag == 'details' and ('code-fold' in classes or 'code-fold' in (values.get('class') or ''))
        if tag == 'section' and 'slide' in classes:
            self.slide_ids.append(values.get('id') or '')
        if tag == 'nav' and values.get('id') == 'research-site-nav':
            self.has_report_nav = True
        if tag == 'img':
            self.images.append(values.get('src') or '')
        for attribute in ('href', 'src', 'poster', 'data-src', 'data-background-image'):
            value = values.get(attribute) or ''
            if not value or value.startswith(('data:', '#')):
                continue
            self.resource_links.add(value)
            parsed = urlsplit(value)
            if parsed.scheme or value.startswith('//'):
                if tag != 'a' and not (tag == 'link' and values.get('rel') in {'canonical', 'alternate'}):
                    self.external_resources.add(value)
                continue
            if parsed.path:
                self.local_links.add(value)


def parse(data: bytes) -> Document:
    result = Document()
    result.feed(data.decode('utf-8'))
    return result


def resolve_link(page: Path, value: str) -> Path:
    relative = unquote(urlsplit(value).path)
    path = (ROOT / relative.lstrip('/')) if relative.startswith('/') else (page.parent / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Unresolved public local link in {page.relative_to(ROOT)}: {value}')
    return path


def image_hash(page: Path, value: str) -> str:
    if value.startswith('data:image/png;base64,'):
        return sha(base64.b64decode(value.split(',', 1)[1], validate=True))
    if value.startswith('data:'):
        raise ValueError(f'Unexpected scientific image encoding in {page.name}')
    return sha(resolve_link(page, value).read_bytes())


def scientific_structure(page: Path, data: bytes) -> dict:
    doc = parse(data)
    return {'slides': len(doc.slide_ids), 'slide_ids': doc.slide_ids,
            'image_placements': len(doc.images),
            'image_sha256_in_order': [image_hash(page, value) for value in doc.images],
            'tables': doc.tables, 'table_cells': doc.cells,
            'details_elements': doc.details, 'folded_code_elements': doc.code_folds}


def public_files() -> list[Path]:
    files = []
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if not path.is_file() or path == MANIFEST:
            continue
        if any(part in {'.git', '.quarto', '__pycache__', '_site'} or part.endswith('_files') for part in relative.parts):
            continue
        if path.name == '.DS_Store' or path.name.endswith('.quarto_ipynb'):
            continue
        if path.is_symlink() or path.suffix.lower() in FORBIDDEN:
            raise ValueError(f'Excluded individual-data/PowerPoint file or symlink: {relative}')
        if path.stat().st_size >= 100 * 1024 * 1024:
            raise ValueError(f'File exceeds GitHub per-file limit: {relative}')
        files.append(path)
    return files


def optimize_page(page: Path, record: dict, figures: dict[str, str]) -> dict:
    original = page.read_bytes()
    image_replacements = 0
    def replace_image(tag: re.Match[bytes]) -> bytes:
        def replace_src(src: re.Match[bytes]) -> bytes:
            nonlocal image_replacements
            value = html.unescape(src[2].decode('utf-8'))
            if not value.startswith('data:image/png;base64,'):
                return src[0]
            digest = sha(base64.b64decode(value.split(',', 1)[1], validate=True))
            if digest not in figures:
                raise ValueError(f'Embedded figure lacks a reviewed original: {page.name} {digest}')
            relative = os.path.relpath(ROOT / figures[digest], page.parent).replace(os.sep, '/')
            image_replacements += 1
            return b'src=' + src[1] + html.escape(relative, quote=True).encode('utf-8') + src[1]
        return SRC.sub(replace_src, tag[0])
    result = IMG.sub(replace_image, original)
    result = strip_powerpoint_links(result)
    if record['type'] == 'report' and NAV_START not in result:
        result, added = BODY.subn(lambda body: body[0] + NAV, result, count=1)
        if added != 1:
            raise ValueError(f'Could not insert report navigation: {page.name}')
    if sha(normalized_html(result)) != record['normalized_non_delivery_bytes_sha256']:
        raise ValueError(f'Unexpected edit to report/runtime/scientific bytes: {page.name}')
    if scientific_structure(page, result) != record['structure']:
        raise ValueError(f'Figures, tables, code-folding or slide structure changed: {page.name}')
    page.write_bytes(result)
    return {'page': str(page.relative_to(ROOT)), 'image_src_replacements': image_replacements,
            'bytes_before': len(original), 'bytes_after': len(result)}


def verify_site(provenance: dict) -> dict:
    results = []
    for name, record in provenance['reviewed_pages'].items():
        page = ROOT / name
        data = page.read_bytes()
        if sha(normalized_html(data)) != record['normalized_non_delivery_bytes_sha256']:
            raise ValueError(f'Canonical scientific/runtime bytes changed: {name}')
        structure = scientific_structure(page, data)
        if structure != record['structure']:
            raise ValueError(f'Reviewed scientific structure changed: {name}')
        doc = parse(data)
        if any(value.startswith('data:') for value in doc.images):
            raise ValueError(f'Embedded scientific image copies remain in {name}')
        if record['type'] == 'report' and not doc.has_report_nav:
            raise ValueError(f'Missing site navigation in report {name}')
        for value in doc.local_links:
            resolve_link(page, value)
        if any(Path(urlsplit(value).path).suffix.lower() in POWERPOINT for value in doc.resource_links):
            raise ValueError(f'Public PowerPoint download reference remains in {name}')
        if doc.external_resources:
            raise ValueError(f'Unexpected external report runtime dependency: {name}')
        if any(marker in data for marker in (b'/Users/', b'file:///')):
            raise ValueError(f'Private filesystem link in {name}')
        qmd = page.with_suffix('.qmd')
        text = page.with_name(page.stem + '_source.txt')
        if qmd.read_bytes() != text.read_bytes():
            raise ValueError(f'Downloadable source does not equal reviewed QMD: {qmd.name}')
        if sha(qmd.read_bytes()) != record['qmd_sha256']:
            raise ValueError(f'Canonical Quarto source changed: {qmd.name}')
        results.append({'page': name, 'tables': structure['tables'], 'table_cells': structure['table_cells'],
                        'figure_placements': structure['image_placements'], 'slides': structure['slides'],
                        'local_links_verified': len(doc.local_links), 'scientific_and_runtime_bytes_preserved': True})
    index = ROOT / 'index.html'
    index_doc = parse(index.read_bytes())
    for value in index_doc.local_links:
        resolve_link(index, value)
    if any(Path(urlsplit(value).path).suffix.lower() in POWERPOINT for value in index_doc.resource_links):
        raise ValueError('PowerPoint download link in the research index')
    for digest, relative in provenance['original_pngs'].items():
        if sha((ROOT / relative).read_bytes()) != digest:
            raise ValueError(f'Original scientific PNG bytes changed: {relative}')
    return {'pages': results, 'reviewed_html_reports': 3, 'slide_decks': 2,
            'index_local_links_verified': len(index_doc.local_links),
            'original_png_hashes_verified': len(provenance['original_pngs']),
            'all_local_links_resolve': True, 'powerpoint_excluded': True}


def write_manifest(provenance: dict, verification: dict) -> None:
    payload = {'schema_version': 2,
        'scope': 'English research index, three reviewed full reports, two slide decks, original aggregate figures, source tables, reviewed Word documents and public reconstruction packages.',
        'repository': 'https://github.com/AmaruSimonAgueroJimenez/Reproductive-hormones-cognitive-decline-women-Chile',
        'scientific_sources': 'Institutional references are given in the reports. This manifest records delivery integrity and is not an original scientific source.',
        'delivery_changes': ['Replace embedded PNG img src values with relative links to byte-identical original PNGs.',
                             'Add a public report navigation bar without changing report text, tables or code.',
                             'Omit the unpublished PowerPoint download anchor from the public HTML only.'],
        'verification': verification,
        'original_source_html_sha256': {name: item['source_html_sha256'] for name, item in provenance['reviewed_pages'].items()},
        'files': [{'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                   'sha256': sha(path.read_bytes())} for path in public_files()]}
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def check_manifest() -> int:
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    files = {str(path.relative_to(ROOT)): path for path in public_files()}
    rows = {item['path']: item for item in data['files']}
    if set(files) != set(rows):
        raise ValueError('Public inventory differs from the file manifest')
    for name, path in files.items():
        if sha(path.read_bytes()) != rows[name]['sha256'] or path.stat().st_size != rows[name]['bytes']:
            raise ValueError(f'Public file differs from manifest: {name}')
    return len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify without changing any file.')
    args = parser.parse_args()
    provenance = json.loads(PROVENANCE.read_text(encoding='utf-8'))
    if args.check:
        verification = verify_site(provenance)
        print(json.dumps({'status': 'pass', 'mode': 'check', **verification,
                          'manifest_files_verified': check_manifest()}, indent=2))
        return
    changes = [optimize_page(ROOT / name, record, provenance['original_pngs'])
               for name, record in provenance['reviewed_pages'].items()]
    verification = verify_site(provenance)
    write_manifest(provenance, verification)
    print(json.dumps({'status': 'pass', 'mode': 'prepare', 'changes': changes,
                      **verification, 'manifest_files_verified': check_manifest()}, indent=2))


if __name__ == '__main__':
    main()
