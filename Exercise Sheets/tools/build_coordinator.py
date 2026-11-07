"""Exercise-sheet adapter for the shared local build controller."""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lecture_build_runtime", ROOT.parent / "_shared/tools/build_runtime.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
CACHE = common.cache_root('sheets')
UPDATE_CACHE = CACHE / "updates"

def control():
    return common.BuildControl(ROOT, UPDATE_CACHE, ROOT / "tools/build_coordinator.py", "sheets")

def snapshots():
    return common.Snapshots(UPDATE_CACHE)

def source_paths():
    paths = [ROOT / "main.tex", ROOT / "latexmkrc"]
    for folder in ("common", "content", "tools"):
        paths += [p for p in (ROOT / folder).rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    return paths

def capture():
    return snapshots().capture(lambda: common.source_mapping(ROOT, source_paths()))

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_full(snapshot, request):
    # Preview and background work share the established engine/Planner caches.
    # Hold one cross-process lock through publication and Planner updates.
    with common.lock(UPDATE_CACHE / 'phase.lock'):
        return _run_full(snapshot, request)

def _run_full(snapshot, request):
    started = time.monotonic()
    source = UPDATE_CACHE / "sources" / snapshot["revision"] / "Exercise Sheets"
    snapshots().materialize(snapshot, source, hardlinks=True)
    output = UPDATE_CACHE / "outputs" / request["id"]
    output.mkdir(parents=True, exist_ok=True)
    options = request.get("options") or {}
    languages = ["de", "en"] if options.get("language") == "all" else [options.get("language", "de")]
    approval = common.read_json(source.parent / '_shared/tools/build_variants.json',
                                {'sheet_languages': {'de': ['*'], 'en': []}})['sheet_languages']
    if options.get('language') == 'approved':
        languages = [language for language, ids in approval.items() if ids]
    modes = ["off", "on"] if options.get("solutions") == "both" else [options.get("solutions", "both")]
    if modes == ["both"]:
        modes = ["off", "on"]
    ps = shutil.which("pwsh") or shutil.which("powershell")
    if not ps:
        raise RuntimeError("PowerShell is missing.")
    log = UPDATE_CACHE / "logs" / (request["id"] + "-full.log")
    log.parent.mkdir(parents=True, exist_ok=True)
    command = [ps, "-NoProfile", "-File", str(source / "tools/build-engine.ps1"),
               "-SourceRoot", str(source), "-PublishedRoot", str(ROOT), "-OutputRoot", str(output),
               "-Language", options.get("language", "de"), "-Solutions", options.get("solutions", "both"),
               "-Jobs", str(options.get("jobs", 4)), "-Python", sys.executable, "-SkipCombine"]
    sheets = options.get("sheets", ["all"])
    command += ["-Sheet", ",".join(sheets)]
    if request.get("force"):
        command += ["-Force"]
    else:
        command += ["-Warm"]
    if sheets == ["all"] and not request.get("force"):
        command += ["-Incremental"]
    env = dict(os.environ, EXERCISE_SHEETS_CACHE=str(CACHE))
    with log.open("wb") as stream:
        result = subprocess.run(command, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError("Blattbau fehlgeschlagen; letzte erfolgreiche PDFs erhalten. Log: " + str(log))
    timing = common.read_json(output / "engine_result.json")
    rows = timing["results"]
    if isinstance(rows, dict):
        rows = [rows]
    if not rows or any(row["status"] != "ok" for row in rows):
        raise RuntimeError("Not all requested sheet variants succeeded. Log: " + str(log))
    prepared = {}
    for row in rows:
        target = (ROOT / row["detail"]).resolve()
        if not target.is_relative_to((ROOT / "build").resolve()):
            raise ValueError("Invalid output: " + row["detail"])
        prepared[target] = (output / row["detail"]).read_bytes()
    common.publish(prepared)
    sheet_seconds = round(time.monotonic() - started, 2)
    control().timing("sheets", request["revision"], sheet_seconds, True, request["sequence"])
    control().mark_initial(request, {"outputs": [str(p.relative_to(ROOT)) for p in prepared],
                                     "seconds": sheet_seconds})
    planner_module = load_module(source / "tools/incremental_build.py", "frozen_sheet_plan")
    planner = planner_module.Planner(ROOT, CACHE)
    planner.finish(rows)
    planner.save_hashes()
    if options.get('preview_only'):
        return {'ok': True, 'seconds': sheet_seconds, 'log': str(log), 'output': str(output),
                'rows': rows, 'pdfs': {p.relative_to(ROOT).as_posix(): data for p, data in prepared.items()}}
    complete = True
    registry = planner.sheets()
    plan = planner.plan()
    combined = {}
    combined_rows = []
    combine_start = time.monotonic()
    for language in languages:
        language_registry = [s for s in registry if options.get('language') != 'approved'
                             or '*' in approval.get(language, []) or s[0] in approval.get(language, [])]
        for mode in modes:
            variant = language + ("_solutions" if mode == "on" else "")
            entries = []
            for sheet in language_registry:
                relative = f"build/{variant}/" + planner_module.sheet_output_filename(sheet, language, mode)
                current = output / relative
                if not current.exists():
                    if not plan[f"{variant}/{sheet[0]}"]["reuse"]:
                        complete = False
                        break
                    current = ROOT / relative
                title = ("Blatt" if language == "de" else "Sheet") + " " + sheet[2] + " - " + (sheet[3] if language == "de" else sheet[4]).replace("~", " ")
                entries.append({"path": str(current), "cache_path": relative, "title": title})
            if not entries or len(entries) != len(language_registry):
                continue
            relative = f"build/{variant}/" + planner_module.combined_output_filename(language, mode)
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            listing = output / (variant + "-combined.json")
            common.save_json(listing, entries)
            with log.open("ab") as stream:
                result = subprocess.run([sys.executable, "-B", str(source / "tools/combine_pdfs.py"),
                                         str(listing), str(destination)], cwd=source, env=env,
                                        stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError("Sammel-PDF fehlgeschlagen; letzte erfolgreiche Ausgabe erhalten. Log: " + str(log))
            combined[ROOT / relative] = destination.read_bytes()
            combined_rows.append({"sheet": "all_exercises", "language": language,
                                  "solutions": mode, "status": "ok"})
    common.publish(combined)
    planner.finish(combined_rows) if combined_rows else None
    planner.save_hashes()
    control().timing("combine", request["revision"], round(time.monotonic() - combine_start, 2),
                     True, request["sequence"])
    artifacts = {p.relative_to(ROOT).as_posix(): common.digest(data)
                 for p, data in {**prepared, **combined}.items()}
    return {"ok": True, "seconds": round(time.monotonic() - started, 2), "log": str(log),
            "complete": complete, "sheet_seconds": sheet_seconds, "artifacts": artifacts,
            "sheets_rebuilt": sum(not r.get("unchanged", False) for r in rows),
            "sheets_reused": sum(bool(r.get("unchanged")) for r in rows),
            "latex_passes": sum(r.get("latex_passes", 0) for r in rows)}

def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["update", "full", "worker", "status", "resume", "ack"])
    parser.add_argument("--language", choices=["de", "en", "all", "approved"], default="de")
    parser.add_argument("--solutions", choices=["off", "on", "both"], default="both")
    parser.add_argument("--sheet", action="append")
    parser.add_argument("--jobs", type=int, default=4, choices=range(1, 17))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    queue = control()
    if args.command == "worker":
        queue.worker(snapshots().get, run_full)
        return 0
    if args.command == "resume":
        queue.start()
        return 0
    if args.command == "ack":
        with queue.transaction() as state:
            state["notified"] = {k: (state.get(k) or {}).get("id") for k in ["completed", "failed"]}
        return 0
    if args.command == "status":
        state = queue.status()
        completed = state.get("completed") or {}
        state["source_matches_full"] = bool(completed.get("project_root") == str(ROOT)
                and completed.get("complete", True) and capture()["revision"] == completed.get("revision"))
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    snapshot = capture()
    with queue.transaction() as state:
        sequence = state.get("sequence", 0) + 1
        state["sequence"] = sequence
    options = {"language": args.language, "solutions": args.solutions,
               "sheets": args.sheet or ["all"], "jobs": args.jobs}
    request, needed = queue.enqueue(snapshot, sequence, options, force=args.force)
    if not needed:
        result = queue.wait(request)
        print(('PDFs bereits aktuell. ' if result['ok'] else 'Dieser Quellstand ist fehlgeschlagen. ')
              + f'Pruefung: {round(time.monotonic() - started, 2)} Sekunden.', flush=True)
        if not result['ok']:
            print('Log: ' + str(result.get('log', '')), flush=True)
        return 0 if result['ok'] else 1
    if needed:
        if not any((CACHE / "latex_runs").glob("*/*/*/*.fdb_latexmk")):
            print("ACHTUNG: Kein vorhandener Blatt-Cache; der erste Bau kann laenger dauern.", flush=True)
        queue.start()
        print("Blattbau vorgemerkt: " + snapshot["revision"][:8], flush=True)
    result = queue.wait(request, initial=not (args.wait or args.command == 'full'))
    if result.get("superseded"):
        print("Auftrag durch neueren Stand ersetzt.", flush=True)
    elif result.get("background"):
        print(f"Blatt-PDFs aktualisiert: {result['details']['seconds']} Sekunden. Sammel-PDFs folgen im Hintergrund.", flush=True)
    else:
        print("Baudauer: " + str(result.get("seconds", 0)) + " Sekunden.", flush=True)
        print("PDFs aktuell." if result["ok"] else "Bau fehlgeschlagen. Log: " + str(result.get("log", "")), flush=True)
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(str(error), file=sys.stderr, flush=True)
        sys.exit(1)

