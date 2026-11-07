"""Isolated regression tests for the shared build protocol; no live sources."""
from pathlib import Path
import csv
import importlib.util
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import build_runtime as runtime

PDF = b"%PDF-1.4\nfixture\n%%EOF\n"

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lecture-build-")
        self.root = Path(self.temp.name)
        self.queue = runtime.BuildControl(self.root/"product", self.root/"cache", self.root/"entry.py", "test")

    def tearDown(self):
        self.temp.cleanup()

    def enqueue(self, revision, sequence, queue=None):
        return (queue or self.queue).enqueue({"revision": revision}, sequence)[0]

    def test_latest_request_replaces_intermediate_pending_work(self):
        first = self.enqueue("first", 1)
        started, release = threading.Event(), threading.Event()
        seen=[]
        def build(snapshot, request):
            seen.append(request["revision"])
            if request["id"] == first["id"]:
                started.set()
                self.assertTrue(release.wait(5))
            return {"ok":True, "seconds":.01}
        worker=threading.Thread(target=lambda:self.queue.worker(lambda x:x,build))
        worker.start()
        self.assertTrue(started.wait(5))
        self.enqueue("middle",2)
        latest=self.enqueue("latest",3)
        release.set()
        worker.join(5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(seen,["first","latest"])
        self.assertEqual(self.queue.status()["completed"]["id"],latest["id"])

    def test_products_do_not_block_each_other(self):
        second=runtime.BuildControl(self.root/"sheets",self.root/"sheet-cache",self.root/"entry.py","sheets")
        self.enqueue("script",1)
        self.enqueue("sheets",1,second)
        started=[threading.Event(),threading.Event()]
        release=threading.Event()
        def build(index):
            def run(snapshot,request):
                started[index].set()
                self.assertTrue(release.wait(5))
                return {"ok":True}
            return run
        workers=[threading.Thread(target=lambda q=q,i=i:q.worker(lambda x:x,build(i)))
                 for i,q in enumerate([self.queue,second])]
        for worker in workers: worker.start()
        self.assertTrue(all(event.wait(5) for event in started))
        release.set()
        for worker in workers: worker.join(5)
        self.assertTrue(all(not worker.is_alive() for worker in workers))

    def test_failed_revision_is_not_retried_automatically(self):
        request=self.enqueue("broken",1)
        def fail(snapshot,request): raise ValueError("fixture failure")
        self.queue.worker(lambda x:x,fail)
        failed=self.queue.status()["failed"]
        self.assertEqual(failed["id"],request["id"])
        same,needed=self.queue.enqueue({"revision":"broken"},2)
        self.assertEqual(same["id"],request["id"])
        self.assertFalse(needed)
        self.assertTrue(Path(failed["log"]).exists())

    def test_last_successful_files_survive_invalid_pdf_and_replace_failure(self):
        a,b=self.root/"a.pdf",self.root/"b.pdf"
        a.write_bytes(PDF); b.write_bytes(PDF)
        with self.assertRaises(ValueError):
            runtime.publish({a:PDF+b"new",b:b"broken"})
        self.assertEqual(a.read_bytes(),PDF)
        updated=b"%PDF-1.4\nnew\n%%EOF\n"
        def fail_b(path,data):
            if path==b: raise PermissionError("fixture")
            runtime.atomic(path,data)
        with self.assertRaises(PermissionError):
            runtime.publish({a:updated,b:updated},replace=fail_b)
        self.assertEqual(a.read_bytes(),PDF)
        self.assertEqual(b.read_bytes(),PDF)

    def test_unchanged_publication_preserves_mtime(self):
        path=self.root/"same.pdf"
        path.write_bytes(PDF)
        stamp=path.stat().st_mtime_ns
        runtime.publish({path:PDF})
        self.assertEqual(path.stat().st_mtime_ns,stamp)

    def test_shared_snapshot_is_frozen_and_removed_inputs_are_pruned(self):
        product=self.root/"course/Skript"
        shared=product.parent/"_shared"
        product.mkdir(parents=True); shared.mkdir()
        source=product/"main.tex"; source.write_text("original",encoding="utf-8")
        dependency=shared/"units.tex"; dependency.write_text("old",encoding="utf-8")
        snapshots=runtime.Snapshots(self.root/"snapshots")
        mapping=lambda:runtime.source_mapping(product,[source])
        frozen=snapshots.capture(mapping)
        dependency.write_text("new",encoding="utf-8")
        destination=self.root/"work/Skript"
        snapshots.materialize(frozen,destination)
        self.assertEqual((destination.parent/"_shared/units.tex").read_text(),"old")
        dependency.unlink()
        current=snapshots.capture(mapping)
        snapshots.materialize(current,destination)
        self.assertFalse((destination.parent/"_shared/units.tex").exists())

    def test_legacy_and_unrelated_shared_tools_do_not_trigger_builds(self):
        product=self.root/'course/Skript'
        product.mkdir(parents=True)
        source=product/'main.tex'
        source.write_text('original',encoding='utf-8')
        snapshots=runtime.Snapshots(self.root/'snapshots')
        mapping=lambda:runtime.source_mapping(product,[source])
        baseline=snapshots.capture(mapping)
        archive=product.parent/'_shared/legacy/incoming.pdf'
        archive.parent.mkdir(parents=True)
        archive.write_bytes(PDF)
        self.assertEqual(snapshots.capture(mapping)['revision'],baseline['revision'])
        archive.write_bytes(PDF+b'new archive')
        self.assertEqual(snapshots.capture(mapping)['revision'],baseline['revision'])
        style=product.parent/'_shared/style/units.tex'
        style.parent.mkdir(parents=True)
        style.write_text('active change',encoding='utf-8')
        self.assertNotEqual(snapshots.capture(mapping)['revision'],baseline['revision'])

    def test_deleted_output_requests_repair_with_existing_engine_cache(self):
        output=self.root/"product/build/a.pdf"
        output.parent.mkdir(parents=True); output.write_bytes(PDF)
        first=self.enqueue("same",1)
        with self.queue.transaction() as state:
            state["completed"]=dict(first,ok=True,artifacts={"build/a.pdf":runtime.digest(PDF)})
        output.unlink()
        repaired,needed=self.queue.enqueue({"revision":"same"},2)
        self.assertNotEqual(repaired["id"],first["id"])
        self.assertTrue(needed)
        self.assertFalse(repaired["force"])

    def test_timing_history_uses_identical_schema(self):
        self.queue.timing("sheets","v1",1.25,True,1)
        self.queue.timing("combine","v1",.25,True,1)
        with (self.queue.cache/"timings.csv").open(encoding="utf-8") as stream:
            rows=list(csv.DictReader(stream,delimiter=";"))
        self.assertEqual([r["phase"] for r in rows],["sheets","combine"])
        self.assertEqual(set(rows[0]),{"finished","phase","revision","seconds","ok","sequence"})

    def test_save_watcher_ignores_the_shared_archive(self):
        module_path=Path(__file__).resolve().parents[2]/'Exercise Sheets/tools/watch_build.py'
        spec=importlib.util.spec_from_file_location('sheet_watch_fixture',module_path)
        watcher=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(watcher)
        product=self.root/'course/Exercise Sheets'
        product.mkdir(parents=True)
        before=watcher.snapshot(product)
        archive=product.parent/'_shared/legacy/old.pdf'
        archive.parent.mkdir(parents=True)
        archive.write_bytes(PDF)
        self.assertEqual(before,watcher.snapshot(product))
        style=product.parent/'_shared/style/units.tex'
        style.parent.mkdir(parents=True)
        style.write_text('new style',encoding='utf-8')
        self.assertNotEqual(before,watcher.snapshot(product))

if __name__=="__main__":
    unittest.main()

