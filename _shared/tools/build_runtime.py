"""Shared local build control: snapshots, queues, publication and timing.

Each document type keeps its established cache and independent worker.
"""
from __future__ import annotations
from contextlib import contextmanager, ExitStack
from datetime import datetime
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
import uuid

def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default

def cache_root(product):
    if product == 'sheets' and (override := os.environ.get('EXERCISE_SHEETS_CACHE')):
        return Path(override)
    paths = read_json(Path(__file__).with_name('cache_paths.json'))
    return Path(os.environ.get('USERPROFILE', str(Path.home()))) / paths[product]


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_bytes(data)
    try:
        for attempt in range(20):
            try:
                os.replace(temporary, path)
                return
            except PermissionError:
                if attempt == 19:
                    raise
                time.sleep(.1)
    finally:
        temporary.unlink(missing_ok=True)

def save_json(path, value):
    atomic(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

@contextmanager
def lock(path, blocking=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+b")
    acquired = False
    try:
        while True:
            try:
                stream.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except OSError:
                if not blocking:
                    break
                time.sleep(.1)
        yield acquired
    finally:
        if acquired:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_UN)
        stream.close()

def validate_pdf(data):
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
        raise ValueError("Incomplete PDF; last successful output retained.")

def publish(prepared, replace=None):
    """Validate all PDFs, atomically replace each file, roll back on failure."""
    replace = replace or atomic
    prepared = {Path(path): data for path, data in prepared.items()}
    for path, data in prepared.items():
        if path.suffix.lower() == ".pdf":
            validate_pdf(data)
    old = {path: path.read_bytes() if path.exists() else None for path in prepared}
    written = []
    try:
        for path, data in prepared.items():
            if old[path] == data:
                continue
            replace(path, data)
            written.append(path)
    except Exception:
        for path in reversed(written):
            if old[path] is None:
                path.unlink(missing_ok=True)
            else:
                atomic(path, old[path])
        raise

def source_mapping(root, product_paths):
    root = Path(root)
    result = {p.relative_to(root).as_posix(): p for p in product_paths}
    shared = root.parent / "_shared"
    if shared.is_dir():
        entries = [p for p in shared.iterdir() if p.name.lower() not in {"legacy", "tools"}]
        candidates = [p for entry in entries for p in ([entry] if entry.is_file() else entry.rglob("*"))]
        for path in candidates:
            if (path.is_file() and not any(part.startswith(".") or part == "__pycache__"
                                          for part in path.relative_to(shared).parts)
                    and path.suffix.lower() not in {".md", ".pyc"}):
                result["__shared__/" + path.relative_to(shared).as_posix()] = path
    common = root.parent / "_shared" / "tools"
    for name in ("build_runtime.py", "build-cache.ps1", "build_variants.json", "cache_paths.json", "latexmk_common.pl"):
        path = common / name
        if path.is_file():
            result["__build__/" + name] = path
    return result

class Snapshots:
    def __init__(self, cache):
        self.cache = Path(cache)

    def capture(self, mapping):
        for attempt in range(4):
            files = {}
            for relative, path in mapping().items():
                data = Path(path).read_bytes()
                sha = digest(data)
                files[relative] = sha
                blob = self.cache / "objects" / sha
                if not blob.exists():
                    atomic(blob, data)
            verified = {relative: digest(Path(path).read_bytes()) for relative, path in mapping().items()}
            if files == verified:
                revision = digest(json.dumps(files, sort_keys=True).encode())
                location = self.cache / "manifests" / (revision + ".json")
                if location.exists():
                    return read_json(location)
                snapshot = {"revision": revision, "created": now(), "files": files}
                save_json(location, snapshot)
                return snapshot
            time.sleep(.2)
        raise RuntimeError("Sources changed while taking the snapshot; save and request again.")

    def get(self, revision):
        return read_json(self.cache / "manifests" / (revision + ".json"))

    def content(self, snapshot, path):
        sha = snapshot["files"].get(path)
        return (self.cache / "objects" / sha).read_text(encoding="utf-8-sig") if sha else ""

    def materialize(self, snapshot, destination, hardlinks=False):
        destination = Path(destination).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        roots = {"__shared__": destination.parent / "_shared",
                 "__build__": destination.parent / "_shared" / "tools"}
        def target(relative):
            parts = relative.split("/")
            base = roots.get(parts[0], destination)
            rest = parts[1:] if parts[0] in roots else parts
            if not rest or any(part in ("", "..", ".") for part in rest):
                raise ValueError(relative)
            path = base.joinpath(*rest).resolve()
            if not path.is_relative_to(base.resolve()):
                raise ValueError(relative)
            return path
        previous = read_json(destination / ".snapshot.json", {"files": {}})
        for relative in previous["files"].keys() - snapshot["files"].keys():
            target(relative).unlink(missing_ok=True)
        for relative, sha in snapshot["files"].items():
            path = target(relative)
            if path.exists() and digest(path.read_bytes()) == sha:
                continue
            blob = self.cache / "objects" / sha
            path.parent.mkdir(parents=True, exist_ok=True)
            if hardlinks and not path.exists():
                try:
                    os.link(blob, path)
                    continue
                except OSError:
                    pass
            atomic(path, blob.read_bytes())
        save_json(destination / ".snapshot.json", snapshot)

def should_build(state):
    desired = state.get("desired")
    return bool(desired and desired["id"] not in
                ((state.get("completed") or {}).get("id"), (state.get("failed") or {}).get("id")))

class BuildControl:
    def __init__(self, root, cache, entry, product):
        self.root, self.cache, self.entry = Path(root), Path(cache), Path(entry)
        self.product = product
        self.cache.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def transaction(self):
        with lock(self.cache / "state.lock"):
            state = read_json(self.cache / "state.json", {})
            yield state
            save_json(self.cache / "state.json", state)

    def timing(self, phase, revision, seconds, ok, sequence):
        try:
            with lock(self.cache / "timings.lock"):
                path = self.cache / "timings.csv"
                header = not path.exists() or not path.stat().st_size
                with path.open("a", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream, delimiter=";")
                    if header:
                        writer.writerow(("finished", "phase", "revision", "seconds", "ok", "sequence"))
                    writer.writerow((now(), phase, revision, seconds, ok, sequence))
        except OSError as error:
            print("Timing log: " + str(error), file=sys.stderr, flush=True)

    def enqueue(self, snapshot, sequence, options=None, force=False, serial=False):
        options = options or {}
        with self.transaction() as state:
            request = {"id": str(sequence) + "-" + snapshot["revision"][:12],
                       "revision": snapshot["revision"], "sequence": sequence,
                       "requested": now(), "force": force, "serial": serial,
                       "project_root": str(self.root), "product": self.product, "options": options}
            known = next((state.get(key) for key in ("completed", "failed", "desired")
                          if (state.get(key) or {}).get("revision") == snapshot["revision"]
                          and (state.get(key) or {}).get("project_root") == str(self.root)
                          and (state.get(key) or {}).get("options", {}) == options), None)
            if known and not force:
                artifacts = known.get('artifacts', {})
                valid = all((self.root / p).is_file() and digest((self.root / p).read_bytes()) == sha
                            for p, sha in artifacts.items())
                if valid:
                    request = known
            if sequence >= state.get("desired_sequence", 0):
                state["desired"], state["desired_sequence"] = request, sequence
            return request, should_build(state)

    def mark_initial(self, request, details=None):
        with self.transaction() as state:
            state["initial_ready"] = dict(request, finished=now(), details=details or {})

    def worker(self, get_snapshot, run):
        with ExitStack() as locks:
            if not locks.enter_context(lock(self.cache / "worker.lock", blocking=False)):
                return
            while True:
                with self.transaction() as state:
                    if not should_build(state):
                        state["running"] = None
                        locks.close()
                        return
                    request = state["desired"].copy()
                    request["project_root"] = str(self.root)
                    state["desired"] = request.copy()
                    state["running"] = dict(request, pid=os.getpid(), started=now())
                started = time.monotonic()
                try:
                    result = run(get_snapshot(request["revision"]), request)
                except Exception as error:
                    log = self.cache / "logs" / (request["id"] + "-error.log")
                    atomic(log, traceback.format_exc().encode("utf-8"))
                    result = {"ok": False, "error": str(error), "log": str(log)}
                result.setdefault("seconds", round(time.monotonic() - started, 2))
                self.timing("full", request["revision"], result["seconds"], result["ok"], request["sequence"])
                with self.transaction() as state:
                    record = dict(request, **result, finished=now())
                    state["completed" if result["ok"] else "failed"] = record
                    state["running"] = None
                    state.setdefault("history", []).append(record)
                    state["history"] = state["history"][-20:]

    def start(self):
        with lock(self.cache / "worker.lock", blocking=False) as available:
            if not available:
                return
        command = [sys.executable, str(self.entry), "worker"]
        options = {}
        if os.name == "nt":
            options["creationflags"] = (subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS
                 | subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_BREAKAWAY_FROM_JOB)
        else:
            options["start_new_session"] = True
        with (self.cache / "worker.log").open("ab") as log:
            subprocess.Popen(command, cwd=self.root, stdin=subprocess.DEVNULL,
                             stdout=log, stderr=log, **options)

    def wait(self, request, initial=False):
        while True:
            with self.transaction() as state:
                terminal = next((state.get(key) for key in ("completed", "failed")
                                 if (state.get(key) or {}).get("id") == request["id"]), None)
                ready = state.get("initial_ready") or {}
                if terminal:
                    return terminal
                if initial and ready.get("id") == request["id"]:
                    return dict(ready, ok=True, background=True)
                if ((state.get("desired") or {}).get("id") != request["id"]
                        and (state.get("running") or {}).get("id") != request["id"]):
                    return dict(request, ok=True, superseded=True)
            time.sleep(.2)

    def status(self):
        with self.transaction() as state:
            result = dict(state)
        with lock(self.cache / "worker.lock", blocking=False) as available:
            result["worker_active"] = not available
        result.update(product=self.product, project_root=str(self.root), cache=str(self.cache))
        return result

