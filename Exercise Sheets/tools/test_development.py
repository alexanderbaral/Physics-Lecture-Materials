"""Selection, invalidation and watch-loop regression tests; no TeX required."""
import sys
sys.dont_write_bytecode = True
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from incremental_build import Planner
from watch_build import snapshot, watch


class DevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='exercise_development_test_')
        self.root = Path(self.temp.name)
        self.cache = self.root / 'cache'
        self.stage = self.cache / 'workspace'
        self.put('common/config.tex', '\n'.join(
            rf'\DeclareSheet{{{s}}}{{{s}}}{{{n}}}{{Title}}{{Title}}{{{s}/_chapter.tex}}'
            for n, s in enumerate(('alpha', 'beta'), 1)))
        for s in ('alpha', 'beta'):
            self.put(f'content/chapters_de/{s}/_chapter.tex', s)
        self.rows = []
        for variant, mode in [('de', 'off'), ('de_solutions', 'on')]:
            for s in ('alpha', 'beta', 'all_exercises'):
                if s == 'all_exercises':
                    filename = '_Übungsblatt Alle (mit Lösungen).pdf' if mode == 'on' else '_Übungsblatt Alle.pdf'
                else:
                    number = '1' if s == 'alpha' else '2'
                    filename = f'Übungsblatt {number} - Title'
                    if mode == 'on' and variant == 'de_solutions':
                        filename += ' (mit Lösungen)'
                    filename += '.pdf'
                p = self.root / f'build/{variant}/{filename}'
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'output bytes')
                self.rows.append(dict(sheet=s, language='de', solutions=mode, status='ok'))
        Planner(self.root, self.cache).finish(self.rows)

    def tearDown(self):
        self.temp.cleanup()

    def put(self, path, content):
        p = self.stage / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return p

    def plan(self):
        return Planner(self.root, self.cache).plan()

    def test_unchanged_and_missing_translation(self):
        plan = self.plan()
        self.assertTrue(plan['de/all_exercises']['reuse'])
        self.assertTrue(plan['de_solutions/all_exercises']['reuse'])
        self.assertFalse(plan['en/alpha']['reuse'])

    def test_single_chapter_invalidates_both_variants_only(self):
        self.put('content/chapters_de/alpha/task.tex', 'new task')
        plan = self.plan()
        for variant in ('de', 'de_solutions'):
            self.assertFalse(plan[f'{variant}/alpha']['reuse'])
            self.assertTrue(plan[f'{variant}/beta']['reuse'])
            self.assertFalse(plan[f'{variant}/all_exercises']['reuse'])

    def test_layout_invalidates_every_sheet(self):
        self.put('common/layout.tex', 'changed')
        plan = self.plan()
        for variant in ('de', 'de_solutions'):
            for s in ('alpha', 'beta'):
                self.assertFalse(plan[f'{variant}/{s}']['reuse'])

    def test_deleted_source_and_corrupt_output(self):
        (self.stage / 'content/chapters_de/alpha/_chapter.tex').unlink()
        (self.root / 'build/de/Übungsblatt 2 - Title.pdf').write_bytes(b'corrupt')
        plan = self.plan()
        self.assertFalse(plan['de/alpha']['reuse'])
        self.assertFalse(plan['de/beta']['reuse'])
        self.assertTrue(plan['de_solutions/beta']['reuse'])

    def test_recorder_cross_chapter_dependency(self):
        dependency = self.put('content/resources/chapters/beta/shared.tex', 'old')
        recorder = self.cache / 'latex_runs/de/alpha/20260911_000000000/alpha.fls'
        recorder.parent.mkdir(parents=True)
        recorder.write_text('INPUT ' + str(dependency))
        Planner(self.root, self.cache).finish(self.rows)
        dependency.write_text('new')
        self.assertFalse(self.plan()['de/alpha']['reuse'])

    def test_failed_build_is_not_reused(self):
        self.rows[0]['status'] = 'failed'
        Planner(self.root, self.cache).finish(self.rows)
        self.assertFalse(self.plan()['de/alpha']['reuse'])

    def test_watcher_ignores_outputs_and_tracks_deletion(self):
        before = snapshot(self.stage)
        self.put('build/de/result.pdf', 'output')
        self.assertEqual(before, snapshot(self.stage))
        (self.stage / 'content/chapters_de/alpha/_chapter.tex').unlink()
        self.assertNotEqual(before, snapshot(self.stage))

    def test_save_during_build_is_not_lost(self):
        calls = []
        class StopTest(Exception):
            pass
        def run(*args, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                self.put('content/chapters_de/alpha/task.tex', 'saved during build')
                return type('Result', (), {'returncode': 0})()
            raise StopTest()
        with patch('watch_build.subprocess.run', side_effect=run), patch('watch_build.time.sleep'):
            with self.assertRaises(StopTest):
                watch(self.stage, ['unused'])
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
