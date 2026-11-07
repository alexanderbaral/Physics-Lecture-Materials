"""One German review PDF, followed by the existing cached background workers.

Labels live exclusively in PDF outlines and page labels. Page streams, boxes,
fonts and pagination are never changed by the merger.
"""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import importlib.util
import json
import re
import time

from pypdf import PdfReader, PdfWriter
import build_runtime as common

ROOT = Path(__file__).resolve().parents[2]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def adapters(root=ROOT):
    return (module(root / 'Skript/tools/build_coordinator.py', 'script_adapter'),
            module(root / 'Exercise Sheets/tools/build_coordinator.py', 'sheets_adapter'))


def sheet_registry(adapter, snapshot):
    text = adapter.snapshots().content(snapshot, 'common/config.tex')
    return re.findall(r'^\\DeclareSheet\{([a-z_]+)\}\{([a-z_]+)\}\{(\d+)\}\{([^{}]+)\}\{([^{}]+)\}\{([^{}]+)\}', text, re.M)


def changed_sheets(adapter, snapshot, baseline):
    """Conservative dependency closure, including inputs outside a sheet folder."""
    registry = sheet_registry(adapter, snapshot)
    if not baseline:
        return registry
    changed = {p for p in snapshot['files'].keys() | baseline['files'].keys()
               if snapshot['files'].get(p) != baseline['files'].get(p)}
    changed = {p for p in changed if not p.startswith(('tools/', '__build__/', 'content/chapters_en/'))}
    if not changed:
        return []
    global_change = any(p.startswith(('common/', 'content/resources/shared/', '__shared__/'))
                        or p in ('main.tex', 'latexmkrc') for p in changed)
    selected, owned = [], set()
    for sheet in registry:
        prefixes = (f'content/chapters_de/{sheet[1]}/', f'content/resources/chapters/{sheet[1]}/')
        dependencies = {p for p in snapshot['files'].keys() | baseline['files'].keys() if p.startswith(prefixes)}
        # Follow literal include/asset paths in both revisions, including deleted inputs.
        for current in (baseline, snapshot):
            pending = list(dependencies)
            visited = set()
            while pending:
                path = pending.pop()
                if path in visited or not path.endswith('.tex'):
                    continue
                visited.add(path)
                text = adapter.snapshots().content(current, path)
                for candidate in current['files']:
                    if candidate.startswith('content/') and (candidate in text or
                            (candidate.endswith('.tex') and candidate[:-4] in text)):
                        if candidate not in dependencies:
                            dependencies.add(candidate)
                            pending.append(candidate)
        owned.update(dependencies)
        if global_change or dependencies & changed:
            selected.append(sheet)
    # Never silently omit a changed resource with a dynamic/unknown include.
    if any(p.startswith('content/') and p not in owned for p in changed):
        return registry
    return selected


def stable_pair(script, sheets):
    for _ in range(4):
        first = (script.capture(), sheets.capture())
        second = (script.capture(), sheets.capture())
        if [s['revision'] for s in first] == [s['revision'] for s in second]:
            return second
    raise RuntimeError('Quellen ändern sich beim Erfassen. Bitte speichern und erneut starten.')


def outline_pages(reader):
    found = []
    def visit(items):
        for item in items:
            if isinstance(item, list):
                visit(item)
            else:
                page = reader.get_destination_page_number(item)
                if page is not None and page >= 0:
                    found.append((str(item.title), page))
    visit(reader.outline)
    return found


def script_blocks(pdfs, selection, whole=False):
    """Interleave full/cloze per section. Preserve any leading/trailing pages."""
    readers = {variant: PdfReader(BytesIO(data)) for variant, data in pdfs.items()}
    starts = {}
    for variant, reader in readers.items():
        titles = outline_pages(reader)
        positions = []
        for section in selection:
            number = f"{section['chapter']}.{section['section']}"
            matching = [page for title, page in titles if re.match(r'^' + re.escape(number) + r'(?:\s|$)', title)]
            if not matching:
                whole = True
                break
            positions.append(min(matching))
        if len(set(positions)) != len(positions):
            whole = True
        starts[variant] = positions
    entries = []
    if whole:
        for variant, reader in readers.items():
            mode = 'Lückenfassung' if variant.endswith('cloze') else 'Vollversion'
            entries.append({'title': f'Skript · {mode} (DE)', 'pdf': pdfs[variant], 'pages': None})
        return entries
    for i, section in enumerate(selection):
        number = f"{section['chapter']}.{section['section']}"
        for variant, reader in readers.items():
            mode = 'Lückenfassung' if variant.endswith('cloze') else 'Vollversion'
            positions = starts[variant]
            start = positions[i] if i else 0
            end = positions[i + 1] if i + 1 < len(positions) else len(reader.pages)
            entries.append({'title': f'Skript · Abschnitt {number} · {mode} (DE)',
                            'pdf': pdfs[variant], 'pages': list(range(start, end))})
    return entries


def merge(entries):
    writer = PdfWriter()
    for entry in entries:
        reader = PdfReader(BytesIO(entry['pdf']))
        start = len(writer.pages)
        pages = entry.get('pages')
        writer.append(reader, pages=pages, outline_item=entry['title'], import_outline=True)
        # Viewer labels identify the variant without placing anything on the page.
        selected = pages if pages is not None else list(range(len(reader.pages)))
        for offset, page in enumerate(selected):
            writer.set_page_label(start + offset, start + offset,
                                  prefix=entry['title'] + ' · ' + reader.page_labels[page])
    writer.add_metadata({'/Title': 'Änderungsvorschau',
                         '/Subject': 'DE-Vorschau. Abschnittsumbrüche und Verweise können vorläufig sein.'})
    writer.page_mode = '/UseOutlines'
    output = BytesIO()
    writer.write(output)
    data = output.getvalue()
    common.validate_pdf(data)
    if len(PdfReader(BytesIO(data)).pages) != len(writer.pages):
        raise ValueError('Seitenzahl der Vorschau stimmt nicht.')
    writer.close()
    return data


def script_preview_blocks(adapter, snapshot, selection, full, sequence, whole, variants):
    # Initial installation/optional cloze need not re-typeset unchanged material.
    if full and full.get('artifacts'):
        changed, _ = adapter.affected(snapshot, adapter.snapshots().get(full['revision']))
        paths = {v: adapter.ROOT / 'build' / (v + '.pdf') for v in variants}
        valid = not changed and all(p.exists() and common.digest(p.read_bytes()) ==
            full['artifacts'].get('build/' + v + '.pdf') for v, p in paths.items())
        if valid:
            pdfs = {v: p.read_bytes() for v, p in paths.items()}
            if whole or len(selection) == len(adapter.sections(snapshot)):
                return script_blocks(pdfs, selection, whole=True)
            entries = []
            for section in selection:
                number = f"{section['chapter']}.{section['section']}"
                for variant, data in pdfs.items():
                    reader = PdfReader(BytesIO(data))
                    outline = outline_pages(reader)
                    start = next((p for t,p in outline if re.match(r'^' + re.escape(number) + r'(?:\s|$)', t)), None)
                    if start is None:
                        break
                    end = min([p for t,p in outline if p > start and re.match(r'^\d+(?:\.\d+)?\s', t)]
                              + [len(reader.pages)])
                    mode = 'Lückenfassung' if variant.endswith('cloze') else 'Vollversion'
                    entries.append({'title': f'Skript · Abschnitt {number} · {mode} (DE)',
                                    'pdf': data, 'pages': list(range(start, end))})
            if len(entries) == len(selection) * len(variants):
                return entries
    pdfs = adapter.preview(snapshot, selection, full, sequence, whole, variants, False)
    return script_blocks(pdfs, selection, whole)


def schedule(adapter, snapshot, options=None):
    queue = adapter.control()
    with queue.transaction() as state:
        sequence = state.get('sequence', 0) + 1
        state['sequence'] = sequence
    request, needed = queue.enqueue(snapshot, sequence, options)
    if needed:
        if hasattr(adapter, 'VARIANTS'):
            for variant in adapter.VARIANTS:
                if not any((adapter.CACHE / 'tikz' / variant).glob('*.pdf')):
                    print(f'ACHTUNG: Kein Grafik-Cache für {variant}. Der erste Vollbau kann länger dauern.', flush=True)
        elif not any((adapter.CACHE / 'latex_runs').glob('*/*/*/*.fdb_latexmk')):
            print('ACHTUNG: Kein Blatt-Cache. Der erste Blattbau kann länger dauern.', flush=True)
        queue.start()
    return queue, request, needed


def update(root=ROOT, cloze=False, wait=False):
    started = time.monotonic()
    script, sheets = adapters(root)
    cache = script.UPDATE_CACHE / 'joint-preview'
    target = root / 'build/Vorschau.pdf'
    timing = common.BuildControl(root, cache, __file__, 'preview')
    # Serialize foreground requests only. Full workers keep their own locks and
    # frozen sources; they never write this PDF or block script preview rendering.
    with common.lock(cache / 'request.lock'):
        previous = common.read_json(cache / 'state.json', {})
        snapshots = stable_pair(script, sheets)
        full = [a.control().status().get('completed') for a in (script, sheets)]
        baseline = []
        for name, adapter, completed in zip(('script', 'sheets'), (script, sheets), full):
            revision = previous.get('script' if name == 'script' else 'sheet_baseline') or (completed or {}).get('revision')
            baseline.append(adapter.snapshots().get(revision) if revision else None)
        selection, whole = script.affected(snapshots[0], baseline[0])
        selected_sheets = changed_sheets(sheets, snapshots[1], baseline[1])
        missing = not target.exists() or common.digest(target.read_bytes()) != previous.get('pdf_sha256')
        if not selection and not selected_sheets and (missing or cloze != previous.get('cloze', False)):
            paths = previous.get('sections', [])
            if not paths:
                paths = (script.control().status().get('preview') or {}).get('sections', [])
            selection = [s for s in script.sections(snapshots[0]) if s['path'] in paths]
            ids = previous.get('sheets', [])
            selected_sheets = [s for s in sheet_registry(sheets, snapshots[1]) if s[0] in ids]
            if not selection and not selected_sheets:
                selection = script.sections(snapshots[0])[:1]
            print('Vorschau aus der zuletzt betrachteten Auswahl wiederherstellen.', flush=True)
        entries = []
        preview_needed = bool(selection or selected_sheets)
        variants = ('build-de', 'build-de-cloze') if cloze else ('build-de',)
        sequence = previous.get('sequence', 0) + 1
        revision = common.digest(json.dumps([s['revision'] for s in snapshots]).encode())
        try:
            if selection and not full[0]:
                print('Noch kein geprüfter Skript-Vollstand. Erste Vorschau ohne Grafikreferenzen kann länger dauern.', flush=True)
            if selected_sheets and not any((sheets.CACHE / 'latex_runs').glob('*/*/*/*.fdb_latexmk')):
                print('ACHTUNG: Kein Blatt-Cache. Der erste Blattbau kann länger dauern.', flush=True)
            with ThreadPoolExecutor(max_workers=2) as pool:
                script_future = pool.submit(script_preview_blocks, script, snapshots[0], selection, full[0],
                                            sequence, whole, variants) if selection else None
                sheet_request = {'id': 'preview-' + str(sequence) + '-' + revision[:12],
                                 'sequence': sequence, 'revision': snapshots[1]['revision'],
                                 'options': {'language': 'de', 'solutions': 'both',
                                             'sheets': [s[0] for s in selected_sheets],
                                             'jobs': 4, 'preview_only': True}}
                sheet_future = pool.submit(sheets.run_full, snapshots[1], sheet_request) if selected_sheets else None
                if script_future:
                    entries.extend(script_future.result())
                if sheet_future:
                    result = sheet_future.result()
                    names = module(root / 'Exercise Sheets/tools/incremental_build.py', 'sheet_names')
                    for sheet in selected_sheets:
                        for mode, variant, label in [('off', 'de', 'Aufgaben'), ('on', 'de_solutions', 'Mit Lösungen')]:
                            relative = f'build/{variant}/' + names.sheet_output_filename(sheet, 'de', mode)
                            entries.append({'title': f'Übungsblatt {sheet[2]} · {label} (DE)',
                                            'pdf': result['pdfs'][relative]})
            if entries:
                data = merge(entries)
                common.publish({target: data})
                previous.update(pdf_sha256=common.digest(data), cloze=cloze,
                                sections=[s['path'] for s in selection], sheets=[s[0] for s in selected_sheets],
                                blocks=[e['title'] for e in entries])
            previous.update(script=snapshots[0]['revision'],
                            sequence=sequence, finished=common.now())
            # Keep the sheet revision separate from the list of preview sheet IDs.
            previous['sheet_baseline'] = snapshots[1]['revision']
            common.save_json(cache / 'state.json', previous)
        except Exception:
            timing.timing('preview', revision, round(time.monotonic() - started, 2), False, sequence)
            raise
        seconds = round(time.monotonic() - started, 2)
        timing.timing('preview' if preview_needed else 'check', revision, seconds, True, sequence)
        print(('Gemeinsame Vorschau veröffentlicht' if entries else 'Keine neuen Inhaltsänderungen; Vorschau bleibt erhalten')
              + f'. Dauer: {seconds} Sekunden.', flush=True)
        print(str(target), flush=True)
        jobs = [schedule(script, snapshots[0]), schedule(sheets, snapshots[1],
                {'language': 'approved', 'solutions': 'both', 'sheets': ['all'], 'jobs': 4})]
        if any(needed for _, _, needed in jobs):
            print('Freigegebene Vollfassungen werden mit den vorhandenen Caches im Hintergrund aktualisiert.', flush=True)
        else:
            print('Keine neuen Vollbauten erforderlich.', flush=True)
        for queue, request, needed in jobs:
            if not needed and queue is not None:
                failed = queue.status().get('failed') or {}
                if failed.get('id') == request['id']:
                    print('Dieser Vollstand ist fehlgeschlagen; kein automatischer Wiederholungsbau. Log: '
                          + failed.get('log', ''), flush=True)
                    return 1
    if wait:
        for queue, request, needed in jobs:
            if not needed:
                print(f'{queue.product}: bereits aktuell, kein neuer Bau.', flush=True)
                continue
            result = queue.wait(request)
            print(f"{queue.product}: {result.get('seconds', 0)} Sekunden."
                  + ('' if result['ok'] else ' Fehler: ' + result.get('log', '')), flush=True)
            if not result['ok']:
                return 1
    return 0
