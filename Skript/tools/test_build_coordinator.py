"""Isolated regression tests; never modifies teaching sources or real PDFs."""
import argparse
import importlib.util
import json
import gzip
import os
from pathlib import Path
import tempfile
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor
import time
import unittest
from unittest.mock import patch

import build_coordinator as build


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        build.CACHE.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='script-build-test-', dir=build.CACHE)
        self.root = Path(self.temporary.name)
        self.patches = [patch.object(build, 'UPDATE_CACHE', self.root / 'cache'),
                        patch.object(build, 'ROOT', self.root / 'project')]
        for item in self.patches:
            item.start()
        build.ROOT.mkdir()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.temporary.cleanup()

    def snapshot(self, **overrides):
        contents = {
            'main.tex': r'\input{content/chapters_de/test/_chapter.tex}',
            'content/chapters_de/test/_chapter.tex': r'\chapter{Test}\input{content/chapters_de/test/a/_section.tex}\input{content/chapters_de/test/b/_section.tex}',
            'content/chapters_de/test/a/_section.tex': r'\section{A}\CachedTikzFigure{content/resources/test/tikz/figure.tex}',
            'content/chapters_de/test/b/_section.tex': r'\section{B} Original',
            'content/resources/test/tikz/figure.tex': 'original figure',
            'latexmkrc': '',
        }
        contents.update(overrides)
        for relative, text in contents.items():
            target = build.ROOT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
        return build.capture(build.ROOT)

    def test_multi_section_changes_and_figure_mapping(self):
        baseline = self.snapshot()
        first = self.snapshot(**{'content/resources/test/tikz/figure.tex': 'changed figure'})
        self.assertEqual([s['section'] for s in build.affected(first, baseline)[0]], [1])
        latest = self.snapshot(**{'content/resources/test/tikz/figure.tex': 'changed figure',
                                  'content/chapters_de/test/b/_section.tex': r'\section{B} changed'})
        self.assertEqual([s['section'] for s in build.affected(latest, baseline)[0]], [1, 2])
        self.assertEqual([s['section'] for s in build.affected(latest, first)[0]], [2])
        self.assertEqual(build.affected(latest, latest)[0], [])

    def test_code_file_change_selects_the_section_that_displays_it(self):
        fixtures = {
            'content/chapters_de/test/a/_section.tex':
                r'\section{A}\PythonCode{content/chapters_de/test/a/vector.py}',
            'content/chapters_de/test/b/_section.tex':
                r'\section{B}\PythonCode[Einheitsvektor]{content/chapters_de/test/b/vector.ipynb}',
            'content/chapters_de/test/a/vector.py': 'print(1)',
            'content/chapters_de/test/b/vector.ipynb': '{"cells": []}',
        }
        baseline = self.snapshot(**fixtures)
        for section, path in enumerate(list(fixtures)[2:], start=1):
            with self.subTest(path=path):
                latest = self.snapshot(**{**fixtures, path: fixtures[path] + '\n'})
                selected, broad = build.affected(latest, baseline)
                self.assertFalse(broad)
                self.assertEqual([item['section'] for item in selected], [section])

    def test_snapshot_keeps_original_bytes(self):
        frozen = self.snapshot()
        self.snapshot(**{'content/resources/test/tikz/figure.tex': 'newer'})
        destination = self.root / 'frozen'
        build.materialize(frozen, destination)
        self.assertEqual((destination / 'content/resources/test/tikz/figure.tex').read_text(), 'original figure')
        before = (destination / 'main.tex').stat().st_mtime_ns
        build.materialize(frozen, destination)
        self.assertEqual((destination / 'main.tex').stat().st_mtime_ns, before)

    def test_global_change_selects_all(self):
        baseline = self.snapshot()
        latest = self.snapshot(**{'common/config.tex': 'shared change'})
        selected, broad = build.affected(latest, baseline)
        self.assertTrue(broad)
        self.assertEqual(len(selected), 2)

    def figure_cache(self, snapshot, dependencies, variant='build-de'):
        folder = self.root / 'figures' / variant
        folder.mkdir(parents=True, exist_ok=True)
        figure = 'content/resources/test/tikz/figure.tex'
        records = [stored + ':' + snapshot['files'][relative].upper()
                   for stored, relative in dependencies]
        fingerprint = ':'.join((snapshot['files'][figure].upper(), 'de',
                                'true' if variant.endswith('cloze') else 'false',
                                build.digest('\n'.join(records).encode('utf-8'))))
        (folder / 'figure.pdf').write_bytes(b'%PDF-test-cache')
        (folder / 'figure.deps').write_text('\n'.join(p for p, _ in dependencies), encoding='utf-8')
        (folder / 'figure.sha256').write_text(fingerprint, encoding='utf-8')
        return folder

    def powershell_fingerprint(self, recorder):
        script = r'''
$ErrorActionPreference = 'Stop'
. $env:SCRIPT_BUILD_TEST_CACHE_HELPER
$fixture = [Console]::In.ReadToEnd() | ConvertFrom-Json
$projectRoot = $fixture.project
$CanonicalRoot = $projectRoot
$fileHashes = @{}
$fingerprint = Get-TikzDependencyFingerprint $fixture.recorder
@{fingerprint=$fingerprint; dependencies=[System.IO.File]::ReadAllLines(
    [System.IO.Path]::ChangeExtension($fixture.recorder, '.deps'))} | ConvertTo-Json -Compress
'''
        result = subprocess.run(
            [build.executable('pwsh'), '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script],
            input=json.dumps({'project': str(build.ROOT), 'recorder': str(recorder)}),
            text=True, capture_output=True, timeout=20,
            env=dict(os.environ, SCRIPT_BUILD_TEST_CACHE_HELPER=str(Path(__file__).with_name('build-cache.ps1'))))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_relative_figure_cache_and_dependency_changes(self):
        frozen = self.snapshot(**{'common/config.tex': 'original settings'})
        figure = 'content/resources/test/tikz/figure.tex'
        dependencies = [(figure, figure), ('common/config.tex', 'common/config.tex')]
        folder = self.figure_cache(frozen, dependencies)
        self.assertTrue(build.cached_figure_valid(frozen, folder, figure))
        changed = self.snapshot(**{'common/config.tex': 'new settings'})
        self.assertFalse(build.cached_figure_valid(changed, folder, figure))

    def test_legacy_absolute_figure_cache_survives_checkout_move(self):
        frozen = self.snapshot(**{'common/config.tex': 'settings'})
        figure = 'content/resources/test/tikz/figure.tex'
        old_root = 'D:\\old checkout\\Mathematik 1\\Skript_Tex\\'
        dependencies = [(old_root + path.replace('/', '\\'), path)
                        for path in (figure, 'common/config.tex')]
        for variant in build.VARIANTS:
            folder = self.figure_cache(frozen, dependencies, variant)
            self.assertTrue(build.cached_figure_valid(frozen, folder, figure))
        changed = self.snapshot(**{'common/config.tex': 'changed after the move'})
        self.assertFalse(build.cached_figure_valid(changed, folder, figure))

    def test_dependency_path_rejects_traversal_and_unknown_relative_prefix(self):
        frozen = self.snapshot()
        figure = 'content/resources/test/tikz/figure.tex'
        self.assertIsNone(build.dependency_relative_path('../' + figure, frozen))
        self.assertIsNone(build.dependency_relative_path('unknown/' + figure, frozen))

    def test_powershell_reuses_legacy_cache_and_records_relative_inputs(self):
        frozen = self.snapshot(**{'common/config.tex': 'settings'})
        figure = 'content/resources/test/tikz/figure.tex'
        dependencies = [('D:/old checkout/' + path, path) for path in (figure, 'common/config.tex')]
        folder = self.figure_cache(frozen, dependencies)
        record = self.powershell_fingerprint(folder / 'figure.fls')
        stored = (folder / 'figure.sha256').read_text()
        self.assertEqual(record['fingerprint'], stored.rsplit(':', 1)[-1])
        self.assertEqual(record['dependencies'], [path for path, _ in dependencies])
        recorder = self.root / 'fresh.fls'
        recorder.write_text('\n'.join('INPUT ' + str(build.ROOT / path)
                                      for path in (figure, 'common/config.tex')), encoding='utf-8')
        fresh = self.powershell_fingerprint(recorder)
        self.assertEqual(set(fresh['dependencies']), {figure, 'common/config.tex'})
        portable = self.figure_cache(frozen, [(path, path) for path in fresh['dependencies']])
        self.assertEqual(fresh['fingerprint'], (portable / 'figure.sha256').read_text().rsplit(':', 1)[-1])

    def test_relocated_publication_gets_new_full_request_for_same_sources(self):
        frozen = self.snapshot()
        with build.state_transaction() as state:
            state['completed'] = {'id': 'old', 'revision': frozen['revision'], 'project_root': 'D:/old checkout'}
            state['failed'] = None
        args = argparse.Namespace(command='update', force=False, serial=False, wait=False)
        with patch.object(build, 'capture', return_value=frozen), patch.object(build, 'preview') as preview, \
                patch.object(build, 'start_worker') as start, patch('builtins.print'):
            self.assertEqual(build.request_build(args), 0)
        self.assertTrue(preview.call_args.args[-1])
        start.assert_called_once()
        with build.state_transaction() as state:
            self.assertNotEqual(state['desired']['id'], 'old')
            self.assertEqual(state['desired']['project_root'], str(build.ROOT))

    def test_missing_previews_are_restored_without_another_full_build(self):
        frozen = self.snapshot()
        with build.state_transaction() as state:
            state['completed'] = {'id': 'current', 'revision': frozen['revision'], 'project_root': str(build.ROOT)}
        args = argparse.Namespace(command='update', force=False, serial=False, wait=False)
        with patch.object(build, 'capture', return_value=frozen), patch.object(build, 'preview') as preview, \
                patch.object(build, 'start_worker') as start, patch('builtins.print'):
            self.assertEqual(build.request_build(args), 0)
        preview.assert_called_once()
        start.assert_not_called()

    def test_publication_is_valid_only_for_its_checkout(self):
        self.assertFalse(build.current_project_record({'revision': 'same'}))
        self.assertFalse(build.current_project_record({'project_root': 'D:/old checkout'}))
        self.assertTrue(build.current_project_record({'project_root': str(build.ROOT)}))

    def test_worker_coalesces_and_does_not_overlap(self):
        frozen = self.snapshot()
        started, release = threading.Event(), threading.Event()
        calls, active = [], []

        def fake_full(snapshot, request):
            active.append(request['id'])
            self.assertEqual(len(active), 1)
            calls.append(request['id'])
            if request['id'] == 'A':
                started.set()
                self.assertTrue(release.wait(5))
            active.pop()
            return {'ok': True, 'seconds': .01, 'published': 'test'}

        def put(identifier):
            with build.state_transaction() as state:
                state['desired'] = {'id': identifier, 'revision': frozen['revision'],
                                    'sequence': ord(identifier) - ord('A') + 1}

        put('A')
        with patch.object(build, 'run_full', fake_full):
            worker = threading.Thread(target=build.worker)
            worker.start()
            self.assertTrue(started.wait(5))
            put('B')
            put('C')
            # A second process/thread cannot launch a competing full engine.
            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(build.worker).result(timeout=2)
            release.set()
            worker.join(5)
            self.assertFalse(worker.is_alive())
        self.assertEqual(calls, ['A', 'C'])
        with build.state_transaction() as state:
            self.assertEqual(state['completed']['id'], 'C')
            self.assertEqual(state['completed']['project_root'], str(build.ROOT))
            self.assertIsNone(state['running'])

    def test_failure_is_not_retried_and_preserves_baseline(self):
        frozen = self.snapshot()
        with build.state_transaction() as state:
            state.update(completed={'id': 'good'}, desired={'id': 'bad', 'revision': frozen['revision'], 'sequence': 1})
        with patch.object(build, 'run_full', return_value={'ok': False, 'seconds': .01}) as runner:
            build.worker()
            build.worker()
            self.assertEqual(runner.call_count, 1)
        with build.state_transaction() as state:
            self.assertEqual(state['completed']['id'], 'good')
            self.assertEqual(state['failed']['id'], 'bad')

    def test_atomic_replacement(self):
        target = self.root / 'output.pdf'
        build.atomic(target, b'old')
        build.atomic(target, b'new')
        self.assertEqual(target.read_bytes(), b'new')
        self.assertEqual(list(self.root.glob('*.tmp')), [])

    def test_pair_publication_rolls_back_on_error(self):
        outputs = build.ROOT / 'build'
        outputs.mkdir()
        source = self.root / 'staging'
        source.mkdir()
        for variant in build.VARIANTS:
            (outputs / (variant + '.pdf')).write_bytes(b'old PDF')
            (outputs / (variant + '.synctex.gz')).write_bytes(b'old map')
            (source / (variant + '.pdf')).write_bytes(b'%PDF-1.5\nnew\n%%EOF')
            (source / (variant + '.synctex.gz')).write_bytes(gzip.compress(b'new map'))
        original_atomic = build.atomic
        def fail_once(path, data):
            if path.name == 'build-de-cloze.pdf' and data.startswith(b'%PDF'):
                raise PermissionError('simulated locked viewer')
            original_atomic(path, data)
        with patch.object(build, 'atomic', fail_once):
            with self.assertRaises(PermissionError):
                build.publish_pair(source, source)
        for variant in build.VARIANTS:
            self.assertEqual((outputs / (variant + '.pdf')).read_bytes(), b'old PDF')
            self.assertEqual((outputs / (variant + '.synctex.gz')).read_bytes(), b'old map')


if __name__ == '__main__':
    unittest.main(verbosity=2)
