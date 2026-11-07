"""Preview first, then a single snapshot-based, coalescing full-build worker.

Only the standard library is required. State, sources and auxiliary files live
in the established local cache; build/ contains viewer-facing PDFs and SyncTeX.
The LaTeX engine remains build-engine.ps1, with main.tex as the sole body.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, ExitStack
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid


import importlib.util
_RUNTIME_PATH = Path(__file__).resolve().parents[2] / "_shared/tools/build_runtime.py"
_runtime_spec = importlib.util.spec_from_file_location("lecture_build_runtime", _RUNTIME_PATH)
common = importlib.util.module_from_spec(_runtime_spec)
_runtime_spec.loader.exec_module(common)

def control():
    return common.BuildControl(ROOT, UPDATE_CACHE, ROOT / "tools/build_coordinator.py", "script")

def snapshots():
    return common.Snapshots(UPDATE_CACHE)

ROOT = Path(__file__).resolve().parents[1]
CACHE = common.cache_root('script')
UPDATE_CACHE = CACHE / 'updates'
VARIANTS = ('build-de', 'build-de-cloze')
INPUT = re.compile(r'\\(?:input|include|CachedTikzFigure)\{([^{}]+)\}')
PYTHON_CODE = re.compile(r'\\PythonCode\s*(?:\[[^\]]*\]\s*)?\{([^{}]+)\}')


def now():
    return common.now()


def digest(data):
    return common.digest(data)


def current_project_record(record):
    """A matching source revision alone does not update relocated SyncTeX paths."""
    return bool(record and record.get('project_root') == str(ROOT))


def read_json(path, default=None):
    return common.read_json(path, default)


def atomic(path, data):
    return common.atomic(path, data)


def save_json(path, value):
    return common.save_json(path, value)


def record_timing(phase, revision, seconds, ok, sequence):
    return control().timing(phase, revision, seconds, ok, sequence)


def lock(path, blocking=True):
    return common.lock(path, blocking)


def state_transaction():
    return control().transaction()


def source_paths(root):
    paths = [p for folder in ('common', 'content') for p in (root / folder).rglob('*') if p.is_file()]
    paths += [root / name for name in ('main.tex', 'latexmkrc')]
    paths += [p for p in (root / 'tools').glob('build*') if p.is_file() and p.suffix in ('.tex', '.ps1', '.py')]
    return sorted(paths)


def capture(root=None):
    root = Path(root or ROOT)
    return snapshots().capture(lambda: common.source_mapping(root, source_paths(root)))


def manifest(revision):
    return snapshots().get(revision)


def content(snapshot, path):
    return snapshots().content(snapshot, path)


def materialize(snapshot, destination):
    return snapshots().materialize(snapshot, destination)


def sections(snapshot):
    """Resolve the actual input order, not alphabetical names or Git status."""
    result, seen = [], set()
    texts = {}

    def get_text(path):
        if path not in texts:
            texts[path] = content(snapshot, path)
        return texts[path]

    def visit(path, chapter=0):
        if path in seen:
            return
        seen.add(path)
        text = re.sub(r'(?<!\\)%[^\n]*', '', get_text(path))
        if path.endswith('/_chapter.tex'):
            chapter = len({item['chapter'] for item in result}) + 1
        if re.search(r'\\section\s*\{', text):
            dependencies = set()

            def gather(p):
                if p in dependencies:
                    return
                dependencies.add(p)
                current = get_text(p)
                for match in INPUT.finditer(current):
                    child = match[1].replace('\\ScriptLanguage', 'de')
                    if not Path(child).suffix:
                        child += '.tex'
                    dependency = dependency_relative_path(child, snapshot)
                    if dependency:
                        gather(dependency)
                for filename in PYTHON_CODE.findall(current):
                    code_path = Path(filename).as_posix()
                    if code_path in snapshot['files']:
                        dependencies.add(code_path)
                # Raster/PDF assets and caller-provided resources are covered as well.
                for candidate in snapshot['files']:
                    if candidate.startswith('content/resources/') and candidate in current:
                        gather(candidate) if candidate.endswith('.tex') else dependencies.add(candidate)

            gather(path)
            result.append({'path': path, 'chapter': chapter,
                           'section': sum(x['chapter'] == chapter for x in result) + 1,
                           'dependencies': sorted(dependencies)})
            return
        for match in INPUT.finditer(text):
            child = match[1].replace('\\ScriptLanguage', 'de')
            if child in snapshot['files'] and not child.startswith('content/resources/'):
                visit(child, chapter)

    visit('main.tex')
    return result


def affected(snapshot, baseline):
    order = sections(snapshot)
    if not baseline:
        return order, True
    changed = {p for p in snapshot['files'].keys() | baseline['files'].keys()
               if snapshot['files'].get(p) != baseline['files'].get(p)}
    # Technical orchestration changes do not alter mathematical section contents.
    changed = {p for p in changed if not ((p.startswith('tools/') or p.startswith('__build__/')) and not p.endswith('.tex'))}
    global_change = any(p.startswith(('common/', 'content/front_matter/', '__shared__/')) or p in ('main.tex', 'latexmkrc')
                        or p.endswith('/_chapter.tex') for p in changed)
    owned = set().union(*(set(s['dependencies']) for s in order)) if order else set()
    # Unknown shared input: do not silently omit an affected part of the document.
    unowned = {p for p in changed if p.startswith('content/resources/') and p not in owned}
    global_change |= bool(unowned)
    return ([s for s in order if global_change or changed.intersection(s['dependencies'])], global_change)


def context_text(snapshot, preview=False):
    label = ('Vorschau' if preview else 'Stand') + ' ' + snapshot['revision'][:8]
    if preview:
        label += ' -- Nummerierung/Verweise vorläufig'
    if preview:
        text = '\\AtBeginDocument{\\ihead*{}\\chead*{\\scriptsize\\color{black!55}' + label + '}\\global\\BrandPageDotVisibletrue}\n'
    else:
        text = '\\AtBeginDocument{\\cfoot*{\\scriptsize\\color{black!55}' + label + '}}\n'
    text += '\\hypersetup{pdfsubject={Quellstand ' + snapshot['revision'] + ', ' + snapshot['created'] + '}}\n'
    if not preview:
        text += r'''
\makeatletter
\newwrite\BuildSectionStream
\immediate\openout\BuildSectionStream=\jobname.sections
\newcommand{\BuildRecordSection}[1]{%
  \begingroup
  \def\@elt##1{\string\setcounter{##1}{\number\value{##1}}}%
  \immediate\write\BuildSectionStream{\string\BuildCheckpoint{#1}{\cl@@ckpt}}%
  \endgroup
}
\makeatother
'''
        for section in sections(snapshot):
            path = section['path']
            text += '\\expandafter\\def\\csname BuildTrack@' + path + '\\endcsname{\\BuildRecordSection{' + path + '}}\n'
            english = path.replace('content/chapters_de/', 'content/chapters_en/')
            if english != path:
                text += '\\expandafter\\def\\csname BuildTrack@' + english + '\\endcsname{\\BuildRecordSection{' + english + '}}\n'
        text += r'''
\AddToHook{file/before}{%
  \ifcsname BuildTrack@\CurrentFilePath/\CurrentFile\endcsname
    \csname BuildTrack@\CurrentFilePath/\CurrentFile\endcsname
  \fi}
'''
    return text


def executable(name):
    found = shutil.which(name)
    if not found and name == 'pwsh':
        found = shutil.which('powershell')
    if not found:
        raise RuntimeError('Programm fehlt: ' + name)
    return found


def subprocess_flags(background=False):
    if os.name != 'nt':
        return {}
    return {'creationflags': subprocess.CREATE_NO_WINDOW | (subprocess.BELOW_NORMAL_PRIORITY_CLASS if background else 0)}


def rebase_synctex(data, source):
    text = gzip.decompress(data).decode('utf-8')
    text = text.replace(source.as_posix(), ROOT.as_posix()).replace(str(source), str(ROOT))
    for legacy_name in ('_shared', '_Shared'):
        text = text.replace((source.parent / legacy_name).as_posix(), (ROOT.parent / '_shared').as_posix())
        text = text.replace(str(source.parent / legacy_name), str(ROOT.parent / '_shared'))
    return gzip.compress(text.encode('utf-8'), mtime=0)


def publish_pair(source_directory, source_root, preview_mode=False, variants=None):
    """Validate the entire pair first and restore old outputs on publication errors."""
    prepared = {}
    for variant in variants or VARIANTS:
        name = variant + ('-preview' if preview_mode else '')
        source = source_directory / name
        pdf = source.with_suffix('.pdf').read_bytes()
        if not pdf.startswith(b'%PDF-') or b'%%EOF' not in pdf[-1024:]:
            raise RuntimeError('Unvollständige PDF: ' + str(source))
        prepared[ROOT / 'build' / (name + '.synctex.gz')] = rebase_synctex(source.with_suffix('.synctex.gz').read_bytes(), source_root)
        prepared[ROOT / 'build' / (name + '.pdf')] = pdf
    common.publish(prepared, replace=atomic)



def run_full(snapshot, request):
    started = time.monotonic()
    source = UPDATE_CACHE / 'full-workspace' / 'Skript'
    materialize(snapshot, source)
    config = common.read_json(source.parent / '_shared/tools/build_variants.json', {'script_languages': ['de']})
    variants = tuple('build-' + language + suffix for language in config['script_languages'] for suffix in ('', '-cloze'))
    atomic(source / 'build-context.tex', context_text(snapshot).encode('utf-8'))
    logfile = UPDATE_CACHE / 'logs' / (request['id'] + '-full.log')
    logfile.parent.mkdir(parents=True, exist_ok=True)
    command = [executable('pwsh'), '-NoProfile', '-File', str(source / 'tools/build-engine.ps1'),
               '-SourceRoot', str(source), '-CanonicalRoot', str(ROOT)]
    command += [flag for flag, enabled in (('-Force', request.get('force')), ('-Serial', request.get('serial'))) if enabled]
    with logfile.open('wb') as log:
        result = subprocess.run(command, cwd=source, stdout=log, stderr=subprocess.STDOUT, **subprocess_flags(True))
    seconds = round(time.monotonic() - started, 2)
    if result.returncode:
        return {'ok': False, 'seconds': seconds, 'log': str(logfile)}
    # Archive the successful reference state and figure PDFs before publishing.
    # Previews only read this immutable cache, never the full engine's live cache.
    published = UPDATE_CACHE / 'published' / request['id']
    for variant in variants:
        folder = published / variant
        folder.mkdir(parents=True, exist_ok=True)
        for extension in ('.aux', '.sections'):
            shutil.copy2(CACHE / 'latex-aux' / (variant + extension), folder / (variant + extension))
        checkpoints = (folder / (variant + '.sections')).read_text(encoding='utf-8')
        if checkpoints.count('\\BuildCheckpoint') != len(sections(snapshot)):
            raise RuntimeError('Abschnittszähler fehlen; Gesamt-PDFs nicht veröffentlicht: ' + variant)
        cached = CACHE / 'tikz' / variant
        for path in cached.iterdir():
            if path.suffix in ('.pdf', '.deps', '.sha256'):
                shutil.copy2(path, folder / path.name)
        # Validate both outputs before either user-facing PDF is changed.
        pdf = (source / 'build' / (variant + '.pdf')).read_bytes()
        if not pdf.startswith(b'%PDF-') or b'%%EOF' not in pdf[-1024:]:
            raise RuntimeError('Ungültige vollständige PDF: ' + variant)
    publish_pair(source / 'build', source, variants=variants)
    artifacts = {('build/' + variant + extension): digest((ROOT / 'build' / (variant + extension)).read_bytes())
                 for variant in variants for extension in ('.pdf', '.synctex.gz')}
    return {'ok': True, 'seconds': seconds, 'log': str(logfile), 'published': str(published),
            'artifacts': artifacts}


def should_build(state):
    return common.should_build(state)


def worker():
    return control().worker(manifest, run_full)


def start_worker():
    return control().start()


def dependency_relative_path(path, snapshot):
    """Resolve relative metadata and verified inputs from an older checkout path."""
    normalized = path.replace('\\', '/')
    shared_name = None
    if normalized.startswith('__shared__/'):
        shared_name = normalized[11:]
    elif match := re.search(r'(?:^|/)_shared/(.+)$', normalized, re.IGNORECASE):
        shared_name = match[1]
    if shared_name and '..' not in shared_name.split('/'):
        candidate = '__shared__/' + shared_name
        if candidate in snapshot['files']:
            return candidate
    if '..' in normalized.split('/'):
        return None
    while normalized.startswith('./'):
        normalized = normalized[2:]
    if normalized in snapshot['files']:
        return normalized
    if not re.match(r'^(?:[A-Za-z]:|/)', normalized):
        return None
    candidates = [normalized[m.start(1):] for m in
                  re.finditer(r'(?:^|(?<=/))(common|content|tools)/', normalized, re.IGNORECASE)]
    name = normalized.rsplit('/', 1)[-1]
    if name in ('main.tex', 'latexmkrc'):
        candidates.append(name)
    matches = {candidate for candidate in candidates if candidate in snapshot['files']}
    return matches.pop() if len(matches) == 1 else None


def cached_figure_valid(snapshot, directory, figure):
    name = Path(figure).stem
    try:
        dependencies = (directory / (name + '.deps')).read_text(encoding='utf-8-sig').splitlines()
        records = []
        for path in dependencies:
            relative = dependency_relative_path(path, snapshot)
            sha = snapshot['files'].get(relative)
            if not sha:
                return False
            records.append(path + ':' + sha.upper())
        fingerprint = ':'.join((snapshot['files'][figure].upper(), 'de',
                                'true' if directory.name.endswith('cloze') else 'false',
                                digest('\n'.join(records).encode('utf-8'))))
        stored = (directory / (name + '.sha256')).read_text(encoding='utf-8-sig').strip()
        return bool(records) and stored.endswith(fingerprint) and (directory / (name + '.pdf')).exists()
    except (OSError, ValueError, KeyError):
        return False


def preview(snapshot, selection, baseline_record, sequence=0, whole_document=False, variants=None, publish=True):
    variants = variants or VARIANTS
    started = time.monotonic()
    with lock(UPDATE_CACHE / 'preview.lock'):
        source = UPDATE_CACHE / 'preview-workspace' / 'Skript'
        materialize(snapshot, source)
        atomic(source / 'build-context.tex', context_text(snapshot, True).encode('utf-8'))
        source.joinpath('build').mkdir(exist_ok=True)
        atomic(source / 'build/tikz-cache-path.tex', b'\\def\\BuildContextFile{build-context.tex}\n')
        output = UPDATE_CACHE / 'preview-output'
        output.mkdir(exist_ok=True)
        baseline_dir = Path(baseline_record['published']) if baseline_record else None

        def run(variant):
            full_aux = baseline_dir / variant / (variant + '.aux') if baseline_dir else None
            refs = '' if not full_aux else '\n'.join(line for line in full_aux.read_text(encoding='utf-8').splitlines() if line.startswith('\\newlabel'))
            references = source / (variant + '-references.tex')
            atomic(references, refs.encode('utf-8'))
            checkpoints = {}
            if baseline_dir:
                for line in (baseline_dir / variant / (variant + '.sections')).read_text(encoding='utf-8').splitlines():
                    match = re.fullmatch(r'\\BuildCheckpoint\{([^{}]+)\}\{(.*)\}', line)
                    if match:
                        checkpoints[match[1]] = match[2]
            body = ['\\StartMainMatter']
            for section in selection:
                counters = checkpoints.get(section['path'], '\\setcounter{chapter}{' + str(section['chapter']) + '}\\setcounter{section}{' + str(section['section'] - 1) + '}')
                body += ['\\clearpage', counters, '\\input{' + section['path'] + '}']
            bodyfile = source / (variant + '-preview-body.tex')
            atomic(bodyfile, ('\n'.join(body) + '\n').encode('utf-8'))
            # Only verified immutable figure PDFs are reused. Changed graphics
            # render inline during this single fast pass, with current inputs.
            reuse = []
            if baseline_dir:
                dependencies = snapshot['files'] if whole_document else {p for section in selection for p in section['dependencies']}
                for figure in sorted(p for p in dependencies if '/tikz/' in p and p.endswith('.tex')):
                    if cached_figure_valid(snapshot, baseline_dir / variant, figure):
                        source_path = '../_shared/' + figure[11:] if figure.startswith('__shared__/') else figure
                        reuse.append('\\expandafter\\def\\csname PreviewCached@' + source_path + '\\endcsname{' + (baseline_dir / variant / (Path(figure).stem + '.pdf')).as_posix() + '}')
            reuse += [r'''\RenewDocumentCommand{\CachedTikzFigure}{m}{%
\begingroup
\ifcsname PreviewCached@#1\endcsname
  \includegraphics{\csname PreviewCached@#1\endcsname}%
\else\input{#1}\fi\endgroup}''']
            setup = source / (variant + '-preview-setup.tex')
            atomic(setup, ('\n'.join(reuse) + '\n\\input{' + references.as_posix() + '}\n').encode('utf-8'))
            wrapper = ('\\def\\ScriptLanguage{de}\n\\def\\ClozeMode{' + ('true' if variant.endswith('cloze') else 'false') + '}\n'
                       + ('' if whole_document else '\\def\\ScriptPreviewBody{' + bodyfile.as_posix() + '}\n') +
                       '\\AddToHook{begindocument/before}{\\input{' + setup.as_posix() + '}}\n\\input{main.tex}\n')
            name = variant + '-preview'
            atomic(source / (name + '.tex'), wrapper.encode('utf-8'))
            env = dict(os.environ, TEXMFVAR=str(CACHE / 'texmf-cache'), TEXMFCACHE=str(CACHE / 'texmf-cache'))
            log = output / (name + '.build.log')
            command = [executable('lualatex'), '-no-shell-escape', '-halt-on-error', '-interaction=nonstopmode', '-recorder', '-synctex=1',
                       '-output-directory=' + output.as_posix(), name + '.tex']
            with log.open('wb') as stream:
                result = subprocess.run(command, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT, **subprocess_flags())
            return result.returncode, log

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, variants))
        seconds = round(time.monotonic() - started, 2)
        record_timing('preview', snapshot['revision'], seconds, not any(code for code, _ in results), sequence)
        if any(code for code, _ in results):
            raise RuntimeError(f'Vorschau fehlgeschlagen. Baudauer: {seconds} Sekunden. Logs: ' + ', '.join(str(log) for _, log in results))
        with state_transaction() as state:
            if publish and sequence >= state.get('preview', {}).get('sequence', 0):
                publish_pair(output, source, preview_mode=True, variants=variants)
                state['preview'] = {'revision': snapshot['revision'], 'sections': [s['path'] for s in selection],
                                    'seconds': seconds, 'finished': now(), 'sequence': sequence,
                                    'project_root': str(ROOT),
                                    'whole_document': whole_document,
                                    'baseline': baseline_record['revision'] if baseline_record else None}
        print(f'Vorschau: {len(selection)} Abschnitte. Baudauer: {seconds} Sekunden.', flush=True)
        return {variant: (output / (variant + '-preview.pdf')).read_bytes() for variant in variants}


def request_build(args):
    snapshot = capture()
    with state_transaction() as state:
        baseline_record = state.get('completed')
        sequence = state.get('sequence', 0) + 1
        state['sequence'] = sequence
        preview_record = state.get('preview')
    preview_missing = not current_project_record(preview_record) or any(
        not (ROOT / 'build' / (variant + '-preview' + extension)).is_file()
        for variant in VARIANTS for extension in ('.pdf', '.synctex.gz'))
    if args.command == 'update':
        selection, global_change = affected(snapshot, manifest(baseline_record['revision']) if baseline_record else None)
        if not baseline_record:
            print('Noch kein überprüfter Vollstand mit Abschnittszählern. Einmaliger Abgleich im Gesamtbau; vorhandene Grafik-Caches bleiben erhalten.', flush=True)
        elif selection or preview_missing:
            if not selection:
                selection, global_change = sections(snapshot), True
                print('Vorschau fehlt oder gehört zu einem anderen Projektpfad; einmaliger Neuaufbau aus dem aktuellen Vollstand.', flush=True)
            if global_change:
                print('Übergreifende Änderung: ausnahmsweise vollständige Vorschau einschließlich Kapitelanfängen/Vorspann; längere Laufzeit.', flush=True)
            preview(snapshot, selection, baseline_record, sequence, global_change)
        else:
            print('Keine neuen Abschnittsänderungen seit dem erfolgreichen Gesamtbau; offene Vorschau bleibt erhalten.', flush=True)
    request, needed = control().enqueue(snapshot, sequence, force=args.force, serial=args.serial)
    if needed:
        for variant in VARIANTS:
            if not any((CACHE / 'tikz' / variant).glob('*.pdf')):
                print('ACHTUNG: Kein Grafik-Cache für ' + variant + '. Der Gesamt-Kaltbau kann mehrere Minuten dauern.', flush=True)
        start_worker()
        print('Gesamtbau vorgemerkt: ' + snapshot['revision'][:8] + ' (Status: tools/build-update.ps1 -Status).', flush=True)
    else:
        print('Gesamtstand bereits abgeschlossen; kein weiterer Bau gestartet.', flush=True)
    if args.wait:
        while True:
            with state_transaction() as state:
                record = next((state.get(key) for key in ('completed', 'failed') if state.get(key, {}).get('id') == request['id']), None)
                superseded = (state.get('desired', {}).get('id') != request['id']
                              and (state.get('running') or {}).get('id') != request['id'])
            if record:
                print('Baudauer: ' + str(record.get('seconds', 'nicht verfügbar')) + ' Sekunden.', flush=True)
                print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)
                return 0 if record['ok'] else 1
            if superseded:
                print('Auftrag durch neueren vorgemerkten Stand ersetzt.', flush=True)
                return 0
            time.sleep(.5)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('update', 'full', 'worker', 'status', 'clean', 'ack', 'resume'))
    parser.add_argument('--wait', action='store_true')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--serial', action='store_true')
    args = parser.parse_args()
    UPDATE_CACHE.mkdir(parents=True, exist_ok=True)
    if args.command == 'worker':
        worker()
    elif args.command == 'status':
        with state_transaction() as state:
            report = dict(state)
        report['project_root'] = str(ROOT)
        report['source_matches_full'] = bool(current_project_record(report.get('completed'))
                                             and capture()['revision'] == report['completed']['revision'])
        report['cache'] = str(CACHE)
        with lock(UPDATE_CACHE / 'worker.lock', blocking=False) as available:
            report['worker_active'] = not available
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == 'ack':
        with state_transaction() as state:
            state['notified'] = {key: state.get(key, {}).get('id') for key in ('completed', 'failed')}
    elif args.command == 'resume':
        start_worker()
    elif args.command == 'clean':
        raise RuntimeError('Cache-Löschung im Hintergrundbetrieb deaktiviert. Erst laufende Bauten abschließen; Cache nur gezielt nach ausdrücklicher Freigabe löschen.')
    else:
        return request_build(args)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr, flush=True)
        sys.exit(1)
