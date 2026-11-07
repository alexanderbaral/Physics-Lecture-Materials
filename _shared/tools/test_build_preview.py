"""Joint preview regression tests, with no production cache or TeX mutations."""
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject, RectangleObject
import build_preview as preview


def pdf():
    writer = PdfWriter()
    for i in range(2):
        page = writer.add_blank_page(595, 842)
        page.cropbox = RectangleObject([10, 20, 585, 822])
        stream = DecodedStreamObject()
        stream.set_data(f'q 0 0 1 RG {20+i*10} 50 m 80 120 l S Q'.encode())
        page[NameObject('/Contents')] = writer._add_object(stream)
        writer.add_outline_item(f'5.{i+1} Section', i)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class PreviewTests(unittest.TestCase):
    def test_merge_preserves_every_page_stream_and_box(self):
        original = pdf()
        result = preview.merge([{'title': 'Skript · Vollversion (DE)', 'pdf': original},
                                {'title': 'Übungsblatt · Mit Lösungen (DE)', 'pdf': original}])
        before, after = PdfReader(BytesIO(original)), PdfReader(BytesIO(result))
        self.assertEqual(len(after.pages), 4)
        for i, page in enumerate(after.pages):
            self.assertEqual(page.get_contents().get_data(), before.pages[i % 2].get_contents().get_data())
            self.assertEqual(page.mediabox, before.pages[i % 2].mediabox)
            self.assertEqual(page.cropbox, before.pages[i % 2].cropbox)
        self.assertIn('Vollversion', after.page_labels[0])
        self.assertIn('Mit Lösungen', after.page_labels[2])
        self.assertEqual(after.page_mode, '/UseOutlines')

    def test_full_and_cloze_are_consecutive_per_section(self):
        blocks = preview.script_blocks({'build-de': pdf(), 'build-de-cloze': pdf()},
                                       [{'chapter': 5, 'section': 1}, {'chapter': 5, 'section': 2}])
        self.assertEqual([b['pages'] for b in blocks], [[0], [0], [1], [1]])
        self.assertIn('5.1 · Vollversion', blocks[0]['title'])
        self.assertIn('5.1 · Lückenfassung', blocks[1]['title'])

    def test_unknown_outline_keeps_all_pages(self):
        blocks = preview.script_blocks({'build-de': pdf()}, [{'chapter': 7, 'section': 1}])
        self.assertIsNone(blocks[0]['pages'])

    def test_changed_sheet_and_cross_chapter_dependency(self):
        texts = {'common/config.tex': '\n'.join(
            rf'\DeclareSheet{{{sid}}}{{{sid}}}{{{i}}}{{Title}}{{Title}}{{{sid}/_chapter.tex}}'
            for i, sid in enumerate(('alpha', 'beta'), 1)),
            'content/chapters_de/alpha/_chapter.tex': r'\input{content/chapters_de/beta/shared.tex}',
            'content/chapters_de/beta/shared.tex': 'old'}
        old = {'files': {p: value for p, value in texts.items()}}
        new = {'files': dict(old['files'], **{'content/chapters_de/beta/shared.tex': 'new'})}
        adapter = SimpleNamespace(snapshots=lambda: SimpleNamespace(content=lambda s, p: s['files'].get(p, '')))
        self.assertEqual([s[0] for s in preview.changed_sheets(adapter, new, old)], ['alpha', 'beta'])
        technical = {'files': dict(old['files'], **{'tools/new.py': 'code'})}
        self.assertEqual(preview.changed_sheets(adapter, technical, old), [])

    def test_joint_update_reuse_and_optional_cloze(self):
        self.exercise_update()

    def test_failed_preview_preserves_previous_pdf_and_baseline(self):
        self.exercise_update(fail=True)

    def exercise_update(self, fail=False):
        with tempfile.TemporaryDirectory(prefix='joint-preview-test-') as temp:
            root = Path(temp)
            events = []
            content = pdf()
            section = {'path': 'section.tex', 'chapter': 5, 'section': 1}
            sheet = ('alpha', 'alpha', '1', 'Title', 'Title', 'alpha/_chapter.tex')
            old = {'revision': 'old', 'files': {}}
            script_snapshot = {'revision': 'script-new', 'files': {'section.tex': 'new'}}
            sheet_snapshot = {'revision': 'sheets-new', 'files': {
                'common/config.tex': r'\DeclareSheet{alpha}{alpha}{1}{Title}{Title}{alpha/_chapter.tex}'}}
            manifests = {'old': old, 'script-new': script_snapshot, 'sheets-new': sheet_snapshot}
            snapshots = SimpleNamespace(get=manifests.get, content=lambda s, p: s['files'].get(p, ''))
            control = SimpleNamespace(status=lambda: {'completed': {'revision': 'old'}})
            def script_preview(snapshot, selection, full, sequence, whole, variants, publish):
                events.append(('script-preview', variants))
                if fail:
                    raise RuntimeError('TeX error')
                return {v: content for v in variants}
            def sheet_preview(snapshot, request):
                events.append(('sheet-preview', request['options']))
                return {'pdfs': {'build/de/off.pdf': content, 'build/de_solutions/on.pdf': content}}
            script = SimpleNamespace(UPDATE_CACHE=root/'cache', capture=lambda: script_snapshot,
                control=lambda: control, snapshots=lambda: snapshots, sections=lambda s: [section],
                affected=lambda s, b: ([] if s['revision'] == b['revision'] else [section], False),
                preview=script_preview)
            sheets = SimpleNamespace(CACHE=root/'cache', capture=lambda: sheet_snapshot, control=lambda: control,
                                     snapshots=lambda: snapshots, run_full=sheet_preview)
            def schedule(*args):
                self.assertTrue((root/'build/Vorschau.pdf').exists())
                events.append(('background',))
                return None, None, False
            target = root/'build/Vorschau.pdf'
            if fail:
                target.parent.mkdir(parents=True)
                target.write_bytes(content)
            with patch.object(preview, 'adapters', return_value=(script, sheets)), \
                 patch.object(preview, 'module', return_value=SimpleNamespace(sheet_output_filename=lambda s,l,m: m+'.pdf')), \
                 patch.object(preview, 'schedule', side_effect=schedule):
                if fail:
                    with self.assertRaisesRegex(RuntimeError, 'TeX error'):
                        preview.update(root)
                    self.assertEqual(target.read_bytes(), content)
                    self.assertNotIn(('background',), events)
                    self.assertFalse((root/'cache/joint-preview/state.json').exists())
                    return
                preview.update(root)
                state = json.loads((root/'cache/joint-preview/state.json').read_text(encoding='utf-8'))
                self.assertEqual(len(state['blocks']), 3)
                self.assertEqual(state['sheets'], ['alpha'])
                self.assertEqual(state['sheet_baseline'], 'sheets-new')
                self.assertEqual(events[0], ('script-preview', ('build-de',)))
                stamp = target.stat().st_mtime_ns
                events.clear()
                preview.update(root)
                self.assertEqual(events, [('background',), ('background',)])
                self.assertEqual(target.stat().st_mtime_ns, stamp)
                preview.update(root, cloze=True)
                state = json.loads((root/'cache/joint-preview/state.json').read_text(encoding='utf-8'))
                self.assertEqual(len(state['blocks']), 4)
                self.assertTrue(state['cloze'])


if __name__ == '__main__':
    unittest.main()
