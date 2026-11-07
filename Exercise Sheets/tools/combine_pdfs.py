"""Combine freshly built sheets in registry order, with one bookmark per sheet."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import hashlib
import shutil
import tempfile
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from cache_paths import CACHE_ROOT
import importlib.util
_runtime = Path(__file__).resolve().parents[2] / '_shared/tools/build_runtime.py'
_spec = importlib.util.spec_from_file_location('lecture_build_runtime', _runtime)
_common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_common)


def combine(manifest_path, output):
    entries = json.loads(Path(manifest_path).read_text(encoding='utf-8-sig'))
    if not entries:
        raise ValueError('No sheets to combine.')
    output = Path(output)
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    # Key includes ordered source bytes, bookmark titles and merger implementation.
    fingerprint = hashlib.sha256(Path(__file__).read_bytes())
    for entry in entries:
        key = {k: v for k, v in entry.items() if k != "cache_path"}
        key["path"] = entry.get("cache_path", entry["path"])
        fingerprint.update(json.dumps(key, sort_keys=True, ensure_ascii=False).encode())
        fingerprint.update(Path(entry['path']).read_bytes())
    combined_cache = CACHE_ROOT / 'combined'
    combined_cache.mkdir(exist_ok=True)
    cached = combined_cache / (fingerprint.hexdigest() + '.pdf')
    checksum = cached.with_suffix('.sha256')
    if cached.exists() and checksum.exists():
        if hashlib.sha256(cached.read_bytes()).hexdigest() == checksum.read_text():
            _common.publish({output: cached.read_bytes()})
            print(f'{output}: unchanged inputs, combined PDF reused')
            return
    with tempfile.NamedTemporaryFile(suffix='.pdf', dir=CACHE_ROOT, delete=False) as handle:
        temporary = Path(handle.name)
    writer = PdfWriter()
    expected_pages = 0
    try:
        for entry in entries:
            reader = PdfReader(entry['path'])
            writer.append(reader, outline_item=entry['title'], import_outline=False)
            expected_pages += len(reader.pages)
        writer.add_metadata({'/Title': 'Physik - Alle Übungsblätter', '/Creator': 'Exercise Sheets'})
        writer.write(temporary)
        result = PdfReader(temporary)
        if len(result.pages) != expected_pages or len(result.outline) != len(entries):
            raise ValueError('Combined PDF page or bookmark count differs.')
        _common.publish({output: temporary.read_bytes()})
        shutil.copyfile(temporary, cached)
        checksum.write_text(hashlib.sha256(cached.read_bytes()).hexdigest())
        print(f'{output}: {expected_pages} pages, {len(entries)} sheet bookmarks')
    finally:
        writer.close()
        temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest')
    parser.add_argument('output')
    args = parser.parse_args()
    combine(args.manifest, args.output)
